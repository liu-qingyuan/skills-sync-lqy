# codebase-design-lqy localization

- Upstream skill: `codebase-design`
- Upstream path: `upstream/mattpocock/skills/engineering/codebase-design`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/codebase-design-zh`
- LQY installable path: `skills/matt-lqy-core/codebase-design-lqy`
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- LQY clarification: retain surface checks, expose every fact callers need, hide implementation mechanisms behind stable semantic coupling, and reject temporal decomposition by execution order.
