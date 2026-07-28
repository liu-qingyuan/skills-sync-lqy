# tdd-lqy localization

- Upstream skill: `tdd`
- Upstream path: `upstream/mattpocock/skills/engineering/tdd`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/tdd-zh`
- LQY installable path: `skills/matt-lqy-core/tdd-lqy`
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- LQY design: each RED/GREEN cycle extends a smallest coherent current Interface instead of creating feature-specific production shape.
- Testing architecture: `TEST-STRATEGY.md` owns the former TEA layer/mock/contract decisions; mechanical refactoring-smell rules are removed.
