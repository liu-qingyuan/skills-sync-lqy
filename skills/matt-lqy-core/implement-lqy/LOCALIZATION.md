# implement-lqy localization

- Upstream skill: `implement`
- Upstream path: `upstream/mattpocock/skills/engineering/implement`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/implement-zh`
- LQY installable path: `skills/matt-lqy-core/implement-lqy`
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- LQY policy: delegate the complete review lifecycle to `$code-review-lqy` as the single source of truth; oversized work ships a green increment and returns for re-splitting.
- Design gate: invoke `$codebase-design-lqy` only when a Ticket changes Module, Interface, Seam, or knowledge ownership.
