# code-review-lqy localization

- Upstream skill: `code-review`
- Upstream path: `upstream/mattpocock/skills/engineering/code-review`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/code-review-zh`
- LQY installable path: `skills/matt-lqy-core/code-review-lqy`
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- Migration: replaces deleted `skills/matt-lqy-in-progress/review-lqy`; no compatibility alias is kept.
- LQY simplification: keeps the fixed-point and parallel Standards/Spec contract, drops the generic smell checklist, and blocks only on evidence-backed Critical/High findings.
- LQY review budget: one broad dual-axis review plus at most one focused closure using the same agents; four review Agent calls maximum, with no further review cycle.
