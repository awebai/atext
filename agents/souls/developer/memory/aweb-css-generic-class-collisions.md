# aweb.css defines many short generic classes — prefix app-local page classes

The shared design system `aweb.css` (served by the aweb-naapp toolkit) already
defines a lot of short, generic class names: `.roster` (display: grid), `.tag`,
`.card`, `.meta`, `.step`, `.flow`, `.tier`, `.badge`, and more. If an app page
reuses one of those names for its own component, it silently inherits the design
system's rule — e.g. a `<table class="roster">` picked up `display: grid` and its
columns broke (thead/tbody stopped sharing column widths; `table-layout: fixed`
had no effect because the element was no longer a table box).

Rule, recorded by the coordinator as the convention for app-local naapp page
classes: **prefix every app-local page class** (e.g. `browse-` for library's
browse pages: `browse-roster`, `browse-tag`, `browse-blueprint-card`,
`browse-specs`...). The one intentional exception is a class that is a shared
contract with another layer — e.g. `.markdown-body`, emitted by the markdown
sanitizer and styled by the page layer.

How to catch it before it bites: grep the served `aweb.css` (and
`naapp-components.css`) for each new class name; a `getComputedStyle(el).display`
check in Playwright surfaces an inherited rule fast. Diagnose an
inexplicably-styled element by iterating `document.styleSheets` for rules whose
selector `el.matches()` and that set the surprising property.
