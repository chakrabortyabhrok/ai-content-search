---
title: High-Performance Markdown Rendering in React with Syntax Highlighting
category: Frontend
status: published
---
## Render once, highlight only what is visible
A documentation page can contain dozens of code blocks. Highlighting every block on the main thread while the page loads creates a noticeable pause. The practical approach is to parse the markdown once, render the static parts immediately, and highlight code blocks only when they enter the viewport or after the first paint.

Most markdown libraries already produce a tree or a list of tokens. Walk that tree, emit ordinary React elements for paragraphs and headings, and emit a lightweight placeholder for each code block. The placeholder holds the raw source and the language; the heavy highlighter runs later.

## Lazy highlighting with a small component
A dedicated `CodeBlock` component receives the source and language. It starts by showing the plain text inside a `<pre>`. After mount, or when an `IntersectionObserver` reports that the block is near the viewport, it calls the highlighter and replaces the content with the highlighted markup.

Choose a highlighter that can run on a subset of languages and that supports a “highlight only these lines” mode if you need line emphasis. Load the highlighter itself with a dynamic import so it does not appear in the main bundle.

```jsx
function CodeBlock({ code, language }) {
  const [html, setHtml] = useState(null);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        import("shiki").then(({ codeToHtml }) => {
          codeToHtml(code, { lang: language, theme: "github-dark" })
            .then(setHtml);
        });
        observer.disconnect();
      }
    });
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [code, language]);

  return (
    <div ref={ref}>
      {html ? (
        <div dangerouslySetInnerHTML={{ __html: html }} />
      ) : (
        <pre><code>{code}</code></pre>
      )}
    </div>
  );
}
```

## Caching and theme switches
Identical code blocks appear more than once across a docs site. A simple in-memory map keyed by language + source + theme avoids repeating the same highlight work in a single session. For a static site the map can live at module scope; for a larger app it can be a small Zustand slice or a React cache.

When the user toggles between light and dark themes, only the visible code blocks need to be re-highlighted. Clear the cache entries for the old theme and let the intersection observers fire again for blocks currently on screen. Blocks that have scrolled out of view keep their old HTML until they return.

## Streaming and partial content
If the page itself streams in (for example from a chat-style renderer), treat each complete fenced block as soon as its closing backticks arrive. Incomplete blocks stay as plain text. This keeps the highlighter from running on partial source that would only be replaced a moment later.

## What good looks like
The first paint shows readable text and plain code blocks with almost no delay. Highlighted colors appear a moment later, starting with the blocks in view. Switching themes updates the visible blocks without re-parsing the entire markdown tree. If the main bundle still contains the full highlighter, or if scrolling past many code blocks causes repeated highlight work for the same source, the dynamic import or the cache key needs another look.