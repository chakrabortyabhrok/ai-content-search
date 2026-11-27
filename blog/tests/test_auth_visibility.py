"""
Who can use ask_ai, and who can see drafts.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from blog.models import Post

User = get_user_model()

ASK_URL = "/api/posts/ask_ai/"


@pytest.mark.django_db
def test_ask_ai_no_token(mocker):
    ask = mocker.patch("blog.api.views.ask")
    client = APIClient()

    res = client.post(ASK_URL, {"question": "hello"}, format="json")

    assert res.status_code == 401
    ask.assert_not_called()


@pytest.mark.django_db
def test_ask_ai_valid_token(mocker):
    User.objects.create_user(username="u", password="pass12345")
    client = APIClient()

    login = client.post("/api/token/", {"username": "u", "password": "pass12345"}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    # Patch where the view looks it up, not rag.answer.ask, or the real APIs run.
    ask = mocker.patch(
        "blog.api.views.ask", return_value={"answer": "ok", "sources": []}
    )

    res = client.post(ASK_URL, {"question": "hello"}, format="json")

    assert res.status_code == 200
    assert res.data == {"answer": "ok", "sources": []}
    ask.assert_called_once_with("hello")


@pytest.fixture
def posts():
    Post.objects.create(
        title="Live post", slug="live-post", content="Hello.", status="published"
    )
    Post.objects.create(
        title="Secret draft", slug="secret-draft", content="Not yet.", status="draft"
    )


@pytest.mark.django_db
def test_draft_not_in_list(posts):
    res = APIClient().get("/api/posts/")

    assert res.status_code == 200
    slugs = [post["slug"] for post in res.data["results"]]
    assert slugs == ["live-post"]


@pytest.mark.django_db
def test_draft_detail_404(posts):
    res = APIClient().get("/api/posts/secret-draft/")

    assert res.status_code == 404


@pytest.mark.django_db
def test_published_detail_200(posts):
    res = APIClient().get("/api/posts/live-post/")

    assert res.status_code == 200
    assert res.data["slug"] == "live-post"


@pytest.mark.django_db
def test_html_draft_page_404(posts):
    res = APIClient().get("/blog/secret-draft/")

    assert res.status_code == 404
