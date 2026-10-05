import re

ABBREVIATIONS = {
    "e.g",
    "i.e",
    "etc",
    "vs",
    "dr",
    "mr",
    "mrs",
    "no",
    "fig",
    "rs",
    "approx",
    "st",
    "jr",
}

CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
PARA_SPLIT = re.compile(r"\n\s*\n")
HEADING = re.compile(r"^#{1,6}\s+.+")
SENT_SPLIT = re.compile(r'(?<=[.!?…])["\')\]]?\s+(?=["\'(\[]?[A-Z0-9])')

MIN_WORDS = 4

def split_sentences(paragraph: str) -> list[str]:
    """Split one paragraph into sentences. Not perfect on purpose"""
    pieces = [p.strip() for p in SENT_SPLIT.split(paragraph) if p.strip()]

    merged = []
    for piece in pieces:
        if merged:
            last = re.findall(r"[\w.]+$", merged[-1])
            if last and last[0].rstrip(".").lower() in ABBREVIATIONS:
                merged[-1] += " " + piece
                continue
        merged.append(piece)

    sentences = []
    for piece in merged:
        if sentences and len(piece.split()) < MIN_WORDS:
            sentences[-1] += " " + piece
        else:
            sentences.append(piece)
    return sentences


def split_post(content: str) -> list[dict]:
    """Post content in → list of chunks out.
    Each chunk: {text, para_index, sent_index, section, is_code}"""
    chunks = []

    # Pulls code blocks out FIRST so nothing ever splits them.
    # Replaces with placeholders so positions stay stable.
    code_blocks = []

    def stash(match):
        code_blocks.append(match.group(0))
        return f"CODEBLOCK_{len(code_blocks) - 1}"

    content = CODE_FENCE.sub(stash, content)

    section = ""
    para_index = 0

    # Paragraphs = blank-line separated
    for para in PARA_SPLIT.split(content):
        para = para.strip()
        if not para:
            continue

        # Heading → context for the NEXT sentences, not a chunk itself
        if HEADING.match(para):
            section = para.lstrip("#").strip()
            para_index += 1
            continue

        # A paragraph that IS a code block → one atomic chunk
        if re.fullmatch(r"CODEBLOCK_\d+", para):
            idx = int(para.split("_")[1])
            chunks.append(
                {
                    "text": code_blocks[idx],
                    "para_index": para_index,
                    "sent_index": 0,
                    "section": section,
                    "is_code": True,
                }
            )
            para_index += 1
            continue

        # Normal paragraph → sentence chunks
        for sent_index, sentence in enumerate(split_sentences(para)):
            chunks.append(
                {
                    "text": sentence,
                    "para_index": para_index,
                    "sent_index": sent_index,
                    "section": section,
                    "is_code": False,
                }
            )
        para_index += 1

    return chunks
