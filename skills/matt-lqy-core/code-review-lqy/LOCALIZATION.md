# code-review-lqy localization

- Upstream skill: `code-review`
- Upstream path: `upstream/mattpocock/skills/engineering/code-review`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/code-review-zh`
- LQY installable path: `skills/matt-lqy-core/code-review-lqy`
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- Migration: replaces deleted `skills/matt-lqy-in-progress/review-lqy`; no compatibility alias is kept.
- LQY simplification: keeps the official fixed-point and parallel Standards/Spec contract, while moving the Fowler smell baseline to `references/fowler-smells.md`.
