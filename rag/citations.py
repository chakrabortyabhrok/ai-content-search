def format_citations(hits: list[dict]) -> list[str]:
    """
    Turn retrieval hits into unique, ordered citation strings.

    Each string should contain:
    - post title
    - section
    - position (para_index, sent_index)
    - the exact sentence
    - a link like /posts/<slug>/

    Rules:
    - same post + para_index + sent_index -> keep only one
    - same post, different sentence       -> keep both
    - lowest distance (strongest) first
    """

    citations = []
    seen = set()  # addresses already cited

    # Strongest first. sorted() returns a NEW list, so the caller's list is untouched.
    # Sorting before de-duplicating means the copy we keep is the best-scoring one.
    for hit in sorted(hits, key=lambda h: h["distance"]):
        # One sentence's unique address (mirrors the UniqueConstraint in models.py).
        address = (hit["post_slug"], hit["para_index"], hit["sent_index"])
        if address in seen:
            continue
        seen.add(address)

        # TODO(later): blog/urls.py serves posts at /blog/<slug>/, so this 404s for now.
        link = f"/posts/{hit['post_slug']}/"
        section = hit["section"] or "(no section)"
        number = len(citations) + 1  # not the loop counter: skips would leave gaps

        citations.append(
            f"[{number}] {hit['post_title']} — {section} "
            f"(para {hit['para_index']}, sentence {hit['sent_index']})\n"
            f'    "{hit["hit"]}"\n'
            f"    {link}"
        )

    return citations


# Shell test without the API — fake hits by hand:
#   a = {"hit": "A", "post_slug": "p1", "para_index": 0, "sent_index": 0,
#        "post_title": "T", "section": "S", "distance": 0.3}
#   b = dict(a, distance=0.5)                 # same sentence, worse score
#   c = dict(a, sent_index=1, distance=0.4)   # same post, different sentence
#   for line in format_citations([b, c, a]): print(line)
#   -> 2 citations: [1] is a, [2] is c. b is dropped.
#
# Real test:
#   from rag.retrieval import retrieve
#   from rag.citations import format_citations
#   for c in format_citations(retrieve("How is pgvector used for similarity search?")):
#       print(c)
