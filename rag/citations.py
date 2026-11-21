from django.urls import reverse


def _unique_hits(hits: list[dict]) -> list[dict]:
    """Strongest first, one per sentence address. Shared by both functions below."""
    unique = []
    seen = set()  # addresses already kept
    # Sorting BEFORE de-duplicating means the copy we keep is the best-scoring one.
    for hit in sorted(hits, key=lambda h: h["distance"]):
        # One sentence's unique address (mirrors the UniqueConstraint in models.py).
        address = (hit["post_slug"], hit["para_index"], hit["sent_index"])
        if address in seen:
            continue
        seen.add(address)
        unique.append(hit)
    return unique


def build_sources(hits: list[dict]) -> list[dict]:
    """
    Hits -> the ONE numbered source list used by BOTH the prompt and the JSON.
    Source n in the prompt ([n]) is sources[n - 1] in the response.

    Each source: {post, section, sentence, link, score}
    """
    return [
        {
            "post": hit["post_title"],
            "section": hit["section"],
            "sentence": hit["hit"],
            "link": reverse("blog:post_detail", kwargs={"slug": hit["post_slug"]}),
            "score": round(1 - hit["distance"], 4),  # similarity: higher = closer
        }
        for hit in _unique_hits(hits)
    ]


def format_citations(hits: list[dict]) -> list[str]:
    """
    Turn retrieval hits into unique, ordered citation strings.
    """

    citations = []

    for hit in _unique_hits(hits):
        # TODO(later): blog/urls.py serves posts at /blog/<slug>/, so this 404s for now.
        link = f"/posts/{hit['post_slug']}/"
        section = hit["section"] or "(no section)"
        number = len(citations) + 1  # not the loop counter: skips would leave gaps

        citations.append(
            f"[{number}] {hit['post_title']} - {section} "
            f"(para {hit['para_index']}, sentence {hit['sent_index']})\n"
            f'    "{hit["hit"]}"\n'
            f"    {link}"
        )

    return citations
