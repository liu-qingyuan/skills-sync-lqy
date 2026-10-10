# implement-lqy localization

- Upstream skill: `implement`
- Upstream path: `upstream/mattpocock/skills/engineering/implement`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/implement-zh`
- LQY installable path: `skills/matt-lqy-core/implement-lqy`
- Source commit (original import): `d574778f94cf620fcc8ce741584093bc650a61d3`
- Upstream reviewed commit: `49dd158d1076134a641b33efb035946536778336` (selective LQY adaptation; not a verbatim copy)
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- LQY policy: delegate the complete review lifecycle to `$code-review-lqy` as the single source of truth; oversized work ships a green increment and returns for re-splitting.
- Authorized Ralph worker may explicitly load this skill; Ralph alone schedules batches, without a new dispatch layer.
- Design gate: invoke `$codebase-design-lqy` only when a Ticket changes Module, Interface, Seam, or knowledge ownership.
- Enabled projects maintain current Feature facts and pass the shared index/commit record gate; projects without setup keep the existing workflow. Record freshness does not replace tests or review.
