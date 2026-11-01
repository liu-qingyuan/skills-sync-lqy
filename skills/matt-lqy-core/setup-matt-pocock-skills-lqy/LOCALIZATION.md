# setup-matt-pocock-skills-lqy localization

- Upstream skill: `setup-matt-pocock-skills`
- Upstream path: `upstream/mattpocock/skills/engineering/setup-matt-pocock-skills`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/setup-matt-pocock-skills-zh`
- LQY installable path: `skills/matt-lqy-core/setup-matt-pocock-skills-lqy`
- Source commit (original import): `d574778f94cf620fcc8ce741584093bc650a61d3`
- Upstream reviewed commit: `49dd158d1076134a641b33efb035946536778336` (selective LQY adaptation; not a verbatim copy)
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- LQY policy: zero-question defaults only — GitHub Issues, canonical triage labels, single-context domain docs, Chinese output, root `AGENTS.md`, and local Feature records. Use upstream setup for tracker/layout customization.
- Feature tooling is self-contained; paths/fingerprint bind facts, not review results. The gate defaults on in setup and authorized implementation delivery, including existing uninitialized projects, without a separate activation marker. Empty projects or failing business tests defer installation without inventing records; the delivery owner enables the first tested capability before review. Explicit opt-outs and hook conflicts are respected; read-only work and skill synchronization do not install hooks. Independent workers may review separate pages; one integrator owns installation and shared Git/build writes. Legacy records, scope, and custom hooks are preserved; gates are not locks or business tests.
