def format_citations(hits: list[dict]) -> list[str]:
    """
    Turn retrieval hits into unique, ordered citation strings.
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

