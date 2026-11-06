---
title: Custom Markdown Parser and Frontmatter in Python
category: Content
status: published
---
## Why a small parser is enough
A full markdown library is convenient, but it often hides the exact steps that turn a file into a post. For a CMS that only needs frontmatter plus a few headings and code blocks, a short custom parser is easier to reason about and easier to test. It also keeps the dependency list small.

The parser’s job is simple. Read the raw file, split the frontmatter from the body, turn the frontmatter into a dictionary, then walk the body to extract headings and fenced code blocks. Everything else can stay as plain text or be passed to a minimal renderer later.

## Splitting frontmatter
Frontmatter sits between two lines of three dashes. The parser finds the first pair of those markers, takes the text between them, and parses it as YAML or as a simple key-value list. The remaining text is the body.

A few rules keep the split reliable. The opening dashes must be at the start of the file. There must be a closing pair. If either is missing, the file is treated as having no frontmatter and the whole content becomes the body. This matches what most static-site tools already expect.

```python
def split_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw_meta, body = parts[1], parts[2]
    meta = {}
    for line in raw_meta.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, body.lstrip("\n")
```

## Walking the body
After the frontmatter is removed, the body is scanned line by line. A line that starts with one or more hash marks becomes a heading. The number of hashes is the level; the rest of the line is the title. A line that starts with three backticks begins a code block. The parser then collects every following line until it sees another line of three backticks. The language hint after the opening backticks is stored with the block.

Headings and code blocks are recorded with their starting line numbers. Later code can use those numbers to build a table of contents or to show “edit this section” links. Sentences and paragraphs are left untouched so a separate sentence splitter can still run if the project needs sentence-level search.

## What stays out of the parser
The parser does not render HTML. It does not resolve links or images. It does not validate that every required frontmatter key is present. Those steps belong in later layers. The parser only turns one markdown file into a small, predictable data structure: a metadata dictionary, a list of headings, a list of code blocks, and the raw body text.

## What good looks like
A file with valid frontmatter yields a clean dictionary and a body that starts at the first real content line. A file without frontmatter still parses and simply returns an empty metadata dictionary. Adding a new heading or a new code block never requires a change to the parser itself. If the same file sometimes loses its title or sometimes includes the closing dashes in the body, the split logic needs another look before any rendering code is written.