"""
Question in -> {answer, sources} out.
The "G" in RAG: retrieve -> number the sources -> prompt -> LLM -> response.
The view only validates input and calls ask(); all RAG logic lives here.
"""

import logging
import os

from openai import OpenAI

from rag.citations import build_sources
from rag.retrieval import retrieve
from rest_framework.response import Response
from rest_framework import status

# The mini model name from YOUR OpenAI dashboard. Override in .env with OPENAI_MODEL=...
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

NOT_FOUND = "not found"  # exact string: tests and Thursday's eval compare to this
K = 5

MAX_DISTANCE = 0.80

#so gate 2 can compare strings.
PROMPT_RULES = """\
You are a RAG assistant. Follow these rules:
- Use only the numbered sources below
- Do not use outside knowledge
- If the answer is not in the sources, reply with exactly: not found
- Refer to sources as [1], [2], [3]
- Keep the answer short"""

logger = logging.getLogger(__name__)

_client = None  # created on first use (see _get_client)


class AskError(Exception):
    """
    An outside service (Voyage, the vector search, OpenAI) failed.
    The message is safe to show users; the real error goes to the log.
    """


def _get_client() -> OpenAI:
    """
    One shared client, created lazily. OpenAI() raises immediately if
    OPENAI_API_KEY is missing; creating it at import time would crash
    blog/api/views.py - and with it the WHOLE API, not just ask_ai.
    """
    global _client
    if _client is None:
        _client = OpenAI()  # reads OPENAI_API_KEY from the environment
    return _client


def build_prompt(question: str, sources: list[dict]) -> str:
    """Rules + question + numbered sources, in the Step 3 format."""
    lines = [
        f"[{n}] {s['sentence']} (Post: {s['post']}, Section: {s['section'] or 'none'})"
        for n, s in enumerate(sources, start=1)
    ]
    return f"{PROMPT_RULES}\n\nQuestion: {question}\n\nSources:\n" + "\n".join(lines)


def _call_llm(prompt: str) -> str:
    """Prompt in -> the model's reply text out. The ONLY function that talks to the LLM."""
    try:
        response = _get_client().chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # same question -> same answer; makes the eval repeatable
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        return Response(
            {"error": "Answer service unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def _is_not_found(reply: str) -> bool:
    """'not found', 'Not found.', ' NOT FOUND ' all count."""
    return reply.strip().rstrip(".").lower() == NOT_FOUND


def ask(question: str) -> dict:
    """The full pipeline. Returns {"answer": str, "sources": list[dict]}."""
    not_found = {"answer": NOT_FOUND, "sources": []}

    try:
        hits = retrieve(question, k=K)  # Voyage embed + vector search
    except Exception as exc:
        logger.exception("Retrieval failed for question: %r", question)
        raise AskError("Search is unavailable right now. Please try again.") from exc

    # Gate 1 - BEFORE the LLM: nothing close enough -> don't pay for a call.
    if not hits or hits[0]["distance"] > MAX_DISTANCE:
        return not_found

    sources = build_sources(hits)
    try:
        reply = _call_llm(build_prompt(question, sources))
    except Exception as exc:
        logger.exception("LLM call failed for question: %r", question)
        raise AskError("The answer service is unavailable right now. Please try again.") from exc

    # Gate 2 - AFTER the LLM: the model refused -> no sources either.
    if _is_not_found(reply):
        return not_found

    return {"answer": reply, "sources": sources}
