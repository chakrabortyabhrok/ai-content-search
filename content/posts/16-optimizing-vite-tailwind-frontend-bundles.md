---
title: Optimizing Vite and Tailwind Frontend Bundles
category: Frontend
status: published
---
## Bundle size is a loading-time problem
A large JavaScript bundle delays the first render. On a documentation or dashboard site the delay is noticeable on slower connections. Vite already tree-shakes and code-splits, but Tailwind and careless imports can still ship unused CSS and JavaScript. The goal is a small initial payload and lazy-loaded routes for everything else.

Measure first. Run `vite build` and inspect the output, or use the rollup-plugin-visualizer to see which modules occupy the most bytes. Fix the largest items before tuning smaller ones.

## Tailwind content paths and purging
Tailwind generates utilities only for classes it finds in your source files. If the content paths in the config are too narrow, classes used in markdown or in dynamically built strings disappear in production. If the paths are too wide, the build scans unnecessary files and slows down.

List every directory that contains class names: components, pages, and any markdown renderer. Avoid scanning node_modules. After a correct config, the production CSS file usually drops from several hundred kilobytes to well under fifty.

```js
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
    "./src/content/**/*.md",
  ],
  theme: { extend: {} },
  plugins: [],
};
```

## Code splitting and dynamic imports
Route-level code splitting is the biggest win. Each page becomes its own chunk that loads only when the user navigates to it. In React Router this is a dynamic import inside the route definition. Shared components stay in the main chunk; page-specific charts or editors move to their own chunks.

Heavy libraries follow the same pattern. A syntax highlighter or a markdown parser used on only a few pages should be imported dynamically so it does not appear in the initial bundle. Vite handles the chunking automatically once the import is dynamic.

## Asset and dependency hygiene
Import only the functions you need from utility libraries. A default import of an entire icon pack or date library pulls in code you never call. Prefer packages that support tree-shaking, and check the bundle visualizer after adding any new dependency.

Images and fonts belong in the build pipeline. Vite hashes them and can inline very small ones. Large images should be compressed and served in modern formats. Unused font weights and styles should be removed from the CSS.

## What good looks like
The initial JavaScript and CSS together stay under 150 kilobytes gzipped for a typical docs or dashboard landing view. Navigating to a heavy page loads an additional chunk instead of blocking the first paint. After removing an unused component, the corresponding code disappears from the production build. If the main bundle still contains a syntax highlighter or a large icon set that appears on only one route, the dynamic import or the Tailwind content path needs another pass.