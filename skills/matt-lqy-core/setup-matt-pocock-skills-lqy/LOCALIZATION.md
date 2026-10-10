# setup-matt-pocock-skills-lqy localization

- Upstream skill: `setup-matt-pocock-skills`
- Upstream path: `upstream/mattpocock/skills/engineering/setup-matt-pocock-skills`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/setup-matt-pocock-skills-zh`
- LQY installable path: `skills/matt-lqy-core/setup-matt-pocock-skills-lqy`
- Source commit (original import): `d574778f94cf620fcc8ce741584093bc650a61d3`
- Upstream reviewed commit: `49dd158d1076134a641b33efb035946536778336` (selective LQY adaptation; not a verbatim copy)
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- LQY policy: zero-question defaults only — GitHub Issues, canonical triage labels, single-context domain docs, Chinese output, root `AGENTS.md`, and local Feature records. Use upstream setup for tracker/layout customization.
- Feature tooling is self-contained; records use status/paths/reviewed_code plus a Markdown title, with read-compatible legacy records. Explicit setup preserves records, scope, and custom hooks; gates do not replace tests.
