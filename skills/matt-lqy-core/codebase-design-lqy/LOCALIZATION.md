# codebase-design-lqy localization

- Upstream skill: `codebase-design`
- Upstream path: `upstream/mattpocock/skills/engineering/codebase-design`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/codebase-design-zh`
- LQY installable path: `skills/matt-lqy-core/codebase-design-lqy`
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- LQY clarification: retain surface checks, expose every fact callers need, centralize design knowledge, reject temporal decomposition, and keep use-case policy out of general mechanisms.
- Progressive review: add individually approved design red flags to `DESIGN-REVIEW.md`; keep the core skill as the conditional loader.
- Design twice: keep three parallel interface designs, constrain them to current needs, and compare caller usability before internal structure.
