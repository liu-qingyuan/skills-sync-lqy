# architecture-flow asset bundle

Local/offline React Flow renderer used by `scripts/scaffold-architecture-web.py` for interactive architecture diagrams.

Build source:

```bash
npm install
npm run build
```

Generated sites copy `dist/architecture-flow.js` and `dist/architecture-flow.css` into their local `assets/` directory and embed graph payload JSON page-locally so `file://` viewing does not require `fetch()`.
