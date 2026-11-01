# codebase-design-lqy localization

- Upstream skill: `codebase-design`
- Upstream path: `upstream/mattpocock/skills/engineering/codebase-design`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/codebase-design-zh`
- LQY installable path: `skills/matt-lqy-core/codebase-design-lqy`
- Source commit (original import): `d574778f94cf620fcc8ce741584093bc650a61d3`
- Upstream reviewed commit: `49dd158d1076134a641b33efb035946536778336` (selective LQY adaptation; not a verbatim copy)
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- LQY clarification: retain surface checks, expose every fact callers need, centralize design knowledge, reject temporal decomposition, and keep use-case policy out of general mechanisms.
- Complexity and contracts: diagnose change amplification, cognitive load and hidden impact; state preconditions, postconditions and observable invariants. Orthogonality concerns implementation changes under a preserved contract, not zero coupling. Pull complexity inward only when the module owns it; semantic error elimination must preserve the agreed contract. No fixed design-time quota or unverified book-page citations.
- Progressive review: keep evidence-based red flags in `DESIGN-REVIEW.md`, including tactical patches, logical grouping, structural traversal and shared mutable knowledge. Fluent/value access and a shared database are not automatic violations; do not create forwarding layers merely to satisfy syntax rules.
- Deepening: establish the preserved contract and migration surface before merging; dependency categories guide testing, not automatic consolidation. Replace only subsumed implementation tests while preserving unique regressions and adapter contracts.
- Design twice: keep three parallel interface designs, constrain them to current needs, and compare caller usability before internal structure.
