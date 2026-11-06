---
title: React Vite Tailwind Docs UI Architecture
category: Frontend
status: published
---
## One layout, many pages
A documentation site is mostly the same layout repeated. A fixed sidebar, a top bar with search and theme toggle, and a content area that scrolls. Building that layout once and reusing it for every page keeps the UI consistent and the code small.

In React the layout is a single component that receives the current page as children. The sidebar reads a simple navigation array and highlights the active route with the router. The content area does nothing except render whatever page is passed to it. This separation means a new docs page is just a new route and a new markdown or component file. The chrome around it never changes.

```jsx
function DocsLayout({ children }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  );
}
```

## Vite for speed, Tailwind for consistency
Vite starts in under a second and hot-reloads instantly. That matters when you are constantly tweaking spacing and colors in a docs site. Tailwind removes the need for custom CSS files for layout and spacing. Utility classes live next to the markup, so a developer can see exactly how a sidebar or callout is styled without hunting through stylesheets.

The important rule is to keep the design tokens in one place. Define colors, font sizes, and spacing once in the Tailwind config. Every component then uses those tokens. When the brand color changes, one edit updates the entire site. Avoid one-off arbitrary values unless the design truly needs them. Arbitrary values make later redesigns painful.

## Components that stay small
Break the UI into three layers. Layout components own the overall structure: sidebar, header, content wrapper. Shared components own repeated pieces: code block, callout, table of contents, search modal. Page components own only the unique content of that page. A page component should rarely exceed a few dozen lines. If it grows larger, extract another shared component.

Code blocks and callouts appear on almost every page, so they deserve their own components. The code block component receives the language and the source, then renders the highlighted output. The callout component receives a type (note, warning, tip) and the children. Both can be used from markdown via a simple custom renderer or from ordinary JSX. Either way the visual result is identical.

## Navigation and search
The sidebar navigation is data, not hard-coded links. A single JavaScript array or a small JSON file lists every section and page. The sidebar component maps over that array. Adding a new page means adding one object to the array and creating the corresponding route. No other file needs to change.

Search can be client-side for a modest number of pages. A small index built at build time stores titles, headings, and a short excerpt for every page. The search modal filters that index as the user types. For larger sites the same index can be sent to a lightweight backend, but most personal or project docs sites never need that step.

## What good looks like
A new page can be added by creating one file and one navigation entry. Changing the primary color or the sidebar width updates every page without further edits. The hot-reload cycle stays under a second even after dozens of components. If adding a page requires touching the layout component, or if styles are scattered across many CSS files, the architecture has started to drift and needs a small cleanup.