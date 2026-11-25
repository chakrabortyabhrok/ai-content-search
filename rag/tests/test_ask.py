"""
Endpoint tests for POST /api/posts/ask_ai/.

Every outside service is mocked: no Voyage call, no OpenAI call, no database.
(pytest-django blocks DB access unless a test asks for it - so if any of these
tests ever touched the database by accident, it would fail loudly.)

Run:  pytest rag/tests/test_ask.py -v
"""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from rag.answer import NOT_FOUND

URL = "/api/posts/ask_ai/"

# One hit in exactly the shape retrieve() returns (see rag/retrieval.py _to_dict).
FAKE_HIT = {
    "hit": "The demo password for the staging box is river-stone-19.",
    "before": None,
    "after": "That line exists so retrieval can be tested.",
    "section": "What a good demo looks like",
    "post_title": "Building Sentence-Level RAG in Django",
    "post_slug": "building-sentence-level-rag-in-django",
    "distance": 0.3,
    "para_index": 5,
    "sent_index": 0,
}


@pytest.fixture
def client():
    """A client that is already logged in (ask_ai requires IsAuthenticated)."""
    api_client = APIClient()
    # force_authenticate skips the JWT check entirely: every request from this
    # client counts as `user`. The user is never saved, so still no database.
    api_client.force_authenticate(user=get_user_model()(username="tester"))
    return api_client


def ask_ai(client, body):
    """POST a JSON body to the endpoint."""
    return client.post(URL, body, format="json")


# 0. Auth: no token -> 401, and no paid work happens

def test_no_token_is_401():
    with patch("blog.api.views.ask") as ask:
        response = APIClient().post(URL, {"question": "Anything?"}, format="json")

    assert response.status_code == 401
    ask.assert_not_called()


def test_invalid_token_is_401():
    unauth = APIClient()
    unauth.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
    with patch("blog.api.views.ask") as ask:
        response = unauth.post(URL, {"question": "Anything?"}, format="json")

    assert response.status_code == 401
    ask.assert_not_called()


# 1. Happy path

def test_happy_path_returns_answer_and_sources(client):
    with patch("rag.answer.retrieve", return_value=[FAKE_HIT]), patch(
        "rag.answer._call_llm", return_value="The password is river-stone-19 [1]."
    ) as llm:
        response = ask_ai(client, {"question": "What is the staging password?"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "The password is river-stone-19 [1]."
    assert data["sources"] == [
        {
            "post": "Building Sentence-Level RAG in Django",
            "section": "What a good demo looks like",
            "sentence": "The demo password for the staging box is river-stone-19.",
            "link": "/blog/building-sentence-level-rag-in-django/",
            "score": 0.7,  # 1 - distance
        }
    ]
    # The model really got the numbered source in its prompt.
    prompt = llm.call_args.args[0]
    assert "[1] The demo password for the staging box is river-stone-19." in prompt
    assert "Question: What is the staging password?" in prompt


# 2. Empty retrieval 

def test_empty_retrieval_is_not_found_and_skips_llm(client):
    with patch("rag.answer.retrieve", return_value=[]), patch("rag.answer._call_llm") as llm:
        response = ask_ai(client, {"question": "best biryani in bangalore"})

    assert response.status_code == 200
    assert response.json() == {"answer": NOT_FOUND, "sources": []}
    llm.assert_not_called()  # gate 1 saved a paid call


# 3. Voyage failure 

def test_voyage_failure_is_controlled_502(client):
    # Patched where retrieve() LOOKS IT UP (rag.retrieval), not where it's defined.
    # The real retrieve() runs and crashes on its first line that calls Voyage.
    with patch(
        "rag.retrieval.embed_query", side_effect=RuntimeError("Voyage rate limit")
    ), patch("rag.answer._call_llm") as llm:
        response = ask_ai(client, {"question": "What is the staging password?"})

    assert response.status_code == 502
    assert response.json() == {"error": "Search is unavailable right now. Please try again."}
    assert "Voyage rate limit" not in response.content.decode()  # no internals leaked
    llm.assert_not_called()


# 4. OpenAI failure 

def test_openai_failure_is_controlled_502(client):
    with patch("rag.answer.retrieve", return_value=[FAKE_HIT]), patch(
        "rag.answer._call_llm", side_effect=RuntimeError("OpenAI timeout")
    ):
        response = ask_ai(client, {"question": "What is the staging password?"})

    assert response.status_code == 502
    assert response.json() == {
        "error": "The answer service is unavailable right now. Please try again."
    }
    assert "OpenAI timeout" not in response.content.decode()


# 5. Empty / invalid question

@pytest.mark.parametrize(
    "body",
    [{}, {"question": ""}, {"question": "   "}, {"question": None}, {"question": 123}],
    ids=["missing", "empty", "whitespace", "null", "number"],
)
def test_invalid_question_is_400(client, body):
    # ask() is patched only to PROVE validation stops the request before it.
    with patch("blog.api.views.ask") as ask:
        response = ask_ai(client, body)

    assert response.status_code == 400
    assert "error" in response.json()
    ask.assert_not_called()


# Extra: the other two refusal paths

def test_question_too_long_is_400(client):
    with patch("blog.api.views.ask") as ask:
        response = ask_ai(client, {"question": "x" * 501})

    assert response.status_code == 400
    ask.assert_not_called()


def test_far_away_hits_are_not_found(client):
    """Gate 1: hits exist, but even the best is beyond MAX_DISTANCE."""
    far_hit = dict(FAKE_HIT, distance=0.95)
    with patch("rag.answer.retrieve", return_value=[far_hit]), patch(
        "rag.answer._call_llm"
    ) as llm:
        response = ask_ai(client, {"question": "What is the capital of France?"})

    assert response.json() == {"answer": NOT_FOUND, "sources": []}
    llm.assert_not_called()


def test_model_refusal_returns_no_sources(client):
    """Gate 2: the model says not found -> sources must be empty too."""
    with patch("rag.answer.retrieve", return_value=[FAKE_HIT]), patch(
        "rag.answer._call_llm", return_value="Not found."
    ):
        response = ask_ai(client, {"question": "What is the staging password?"})

    assert response.json() == {"answer": NOT_FOUND, "sources": []}
