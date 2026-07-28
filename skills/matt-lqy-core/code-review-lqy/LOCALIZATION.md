# code-review-lqy localization

- Upstream skill: `code-review`
- Upstream path: `upstream/mattpocock/skills/engineering/code-review`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/code-review-zh`
- LQY installable path: `skills/matt-lqy-core/code-review-lqy`
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- Migration: replaces deleted `skills/matt-lqy-in-progress/review-lqy`; no compatibility alias is kept.
- LQY simplification: keeps the fixed-point and parallel Standards/Spec contract, forbids a third design-smell axis, and blocks only on evidence-backed Critical/High findings.
- LQY clean gate: after Broad Review accepts the implementation direction and any minimal blocking fixes pass focused verification, freezes the current fixed-point changed-files scope and runs `$clean` once; oversized work stops before cleanup.
- LQY review budget: one broad dual-axis review plus at most one focused closure using the same agents; cleanup changes trigger closure, which checks only original findings and post-broad Critical/High regressions. Four review Agent calls maximum, with no further review cycle.
