---
title: React State Management for a Documentation UI with Zustand
category: Frontend
status: published
---
## Local state is not enough
A documentation site has several pieces of UI state that many components need at once: the current theme, whether the sidebar is open, the search modal visibility, and the active heading for the table of contents. Passing these values through props quickly becomes noisy. Context works, but it often causes extra re-renders when any value changes.

Zustand keeps the store outside the React tree. Components subscribe only to the slices they use. A theme toggle re-renders the header and the code blocks that care about colors; it does not re-render the entire page content.

## What belongs in the store
Keep the store small and flat. Theme, sidebar open/closed, search open/closed, and the current scroll heading are good candidates. Do not put the full list of posts or the markdown content in Zustand. Those belong in the router loader, in React Query, or in ordinary component state loaded from the build.

Derived values can be computed inside selectors. The store holds the raw “sidebarOpen” boolean; a selector can return the CSS class string if that is convenient. Actions are plain functions that call `set`. No reducers or action-type constants are required.

```jsx
import { create } from "zustand";

export const useDocsStore = create((set) => ({
  theme: "light",
  sidebarOpen: true,
  searchOpen: false,
  toggleTheme: () => set((s) => ({ theme: s.theme === "light" ? "dark" : "light" })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSearchOpen: (open) => set({ searchOpen: open }),
}));
```

## Selectors and re-renders
Always select the smallest piece you need. `useDocsStore(s => s.theme)` re-renders the component only when the theme changes. Selecting the whole store re-renders on every update. For several fields, return an object from the selector or use a shallow compare helper so the component still skips renders when nothing it cares about has changed.

Actions can be selected once and stored in a ref or called directly; they are stable. This keeps event handlers from causing extra renders.

## Persistence and side effects
Theme is a common value to persist. Zustand’s persist middleware writes the chosen fields to localStorage and rehydrates them on load. Limit persistence to the theme (and maybe sidebar preference). Search open state and scroll position should reset on each visit.

Side effects such as applying a class to the document element belong in a small subscriber or in a layout effect that reads the theme. The store itself stays free of direct DOM calls so it remains easy to test.

## What good looks like
Toggling the theme updates every themed component without a visible flash or a full-page re-render. Opening the search modal does not reset the sidebar or the scroll position. Adding a new piece of UI state requires only a few lines in the store and a selector in the component that needs it. If a component re-renders on every keystroke in the search box, or if the theme flickers on refresh because persistence was omitted, the selector granularity or the persist configuration needs another look.