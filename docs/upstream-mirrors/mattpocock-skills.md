# Matt Pocock upstream mirror

- Repository: https://github.com/mattpocock/skills
- Active source commit: `49dd158d1076134a641b33efb035946536778336`
- Frozen legacy source commit: `d574778f94cf620fcc8ce741584093bc650a61d3`
- Mirrored skills: 46 (38 active, 8 frozen legacy). The per-skill `UPSTREAM_MATTOCOCK.md` Status and Source commit are authoritative; legacy copies are retained, not silently upgraded. Reviewed late commits `8267225` and `49dd158`: only the uninstalled Wizard template and retro's out-of-scope note changed; installed retro already always loads writing-for-agents.
- Directory policy: keep Matt Pocock's two-level layout under `upstream/mattpocock/skills/<category>/<skill-name>` so the English mirror is not displayed by `npx skills@latest add liu-qingyuan/skills-sync-lqy`.

## Mirrored skills

### Engineering

- `ask-matt` ← `upstream/mattpocock/skills/engineering/ask-matt`
- `code-review` ← `upstream/mattpocock/skills/engineering/code-review`
- `codebase-design` ← `upstream/mattpocock/skills/engineering/codebase-design`
- `diagnosing-bugs` ← `upstream/mattpocock/skills/engineering/diagnosing-bugs`
- `domain-modeling` ← `upstream/mattpocock/skills/engineering/domain-modeling`
- `grill-with-docs` ← `upstream/mattpocock/skills/engineering/grill-with-docs`
- `implement` ← `upstream/mattpocock/skills/engineering/implement`
- `implement-spec` ← `upstream/mattpocock/skills/engineering/implement-spec`
- `improve-codebase-architecture` ← `upstream/mattpocock/skills/engineering/improve-codebase-architecture`
- `pr` ← `upstream/mattpocock/skills/engineering/pr`
- `prototype` ← `upstream/mattpocock/skills/engineering/prototype`
- `research` ← `upstream/mattpocock/skills/engineering/research`
- `resolving-merge-conflicts` ← `upstream/mattpocock/skills/engineering/resolving-merge-conflicts` (Frozen legacy)
- `retro` ← `upstream/mattpocock/skills/engineering/retro`
- `setup-matt-pocock-skills` ← `upstream/mattpocock/skills/engineering/setup-matt-pocock-skills`
- `tdd` ← `upstream/mattpocock/skills/engineering/tdd`
- `to-spec` ← `upstream/mattpocock/skills/engineering/to-spec`
- `to-tickets` ← `upstream/mattpocock/skills/engineering/to-tickets`
- `triage` ← `upstream/mattpocock/skills/engineering/triage`
- `wayfinder` ← `upstream/mattpocock/skills/engineering/wayfinder`
- `wizard` ← `upstream/mattpocock/skills/engineering/wizard` (baseline in core; not installed in LQY)

### Productivity

- `grill-me` ← `upstream/mattpocock/skills/productivity/grill-me`
- `grilling` ← `upstream/mattpocock/skills/productivity/grilling`
- `handoff` ← `upstream/mattpocock/skills/productivity/handoff`
- `teach` ← `upstream/mattpocock/skills/productivity/teach`
- `to-questionnaire` ← `upstream/mattpocock/skills/productivity/to-questionnaire`
- `wait-what` ← `upstream/mattpocock/skills/productivity/wait-what`
- `writing-for-agents` ← `upstream/mattpocock/skills/productivity/writing-for-agents`
- `writing-great-skills` ← `upstream/mattpocock/skills/productivity/writing-great-skills` (Frozen legacy)

### Personal

- `edit-article` ← `upstream/mattpocock/skills/personal/edit-article` (Frozen legacy)
- `obsidian-vault` ← `upstream/mattpocock/skills/personal/obsidian-vault` (Frozen legacy)

### Misc

- `git-guardrails-claude-code` ← `upstream/mattpocock/skills/misc/git-guardrails-claude-code`
- `migrate-to-shoehorn` ← `upstream/mattpocock/skills/misc/migrate-to-shoehorn`
- `scaffold-exercises` ← `upstream/mattpocock/skills/misc/scaffold-exercises`
- `setup-pre-commit` ← `upstream/mattpocock/skills/misc/setup-pre-commit`

### In progress

- `chief-of-staff` ← `upstream/mattpocock/skills/in-progress/chief-of-staff`
- `claude-handoff` ← `upstream/mattpocock/skills/in-progress/claude-handoff`
- `loop-me` ← `upstream/mattpocock/skills/in-progress/loop-me`
- `setup-ts-deep-modules` ← `upstream/mattpocock/skills/in-progress/setup-ts-deep-modules`
- `writing-beats` ← `upstream/mattpocock/skills/in-progress/writing-beats`
- `writing-fragments` ← `upstream/mattpocock/skills/in-progress/writing-fragments`
- `writing-shape` ← `upstream/mattpocock/skills/in-progress/writing-shape`

### Deprecated

- `design-an-interface` ← `upstream/mattpocock/skills/deprecated/design-an-interface` (Frozen legacy)
- `qa` ← `upstream/mattpocock/skills/deprecated/qa` (Frozen legacy)
- `request-refactor-plan` ← `upstream/mattpocock/skills/deprecated/request-refactor-plan` (Frozen legacy)
- `ubiquitous-language` ← `upstream/mattpocock/skills/deprecated/ubiquitous-language` (Frozen legacy)

## Frontmatter compatibility

Pi uses `disable-model-invocation` for explicit-only invocation. Codex uses `agents/openai.yaml` policy; keep both in sync where applicable. The local repository validator accepts these metadata fields; do not omit flags to satisfy the system `quick_validate.py`. An authorized Ralph worker may explicitly load the installed `implement-lqy`; batch scheduling remains Ralph's responsibility, not a new skill-level dispatcher.

## Installer grouping

The English mirror is intentionally outside top-level `skills/`. `npx skills@latest` recursively discovers installable skills from `skills/`, so moving English upstream copies back under `skills/` will make them visible to users. Keep `.claude-plugin/marketplace.json` in sync for installable LQY/local groups only.

The mirror and baseline each retain 46 skills (38 active, 8 Frozen legacy); 38 Matt LQY skills are installed (35 retained + `pr`, `retro`, `writing-for-agents`). Together with 15 local skills, the installer exposes 53. Do not auto-delete old personal skills: frozen legacy LQY copies remain explicitly invocable. `wizard` (mirror engineering, baseline core), `chief-of-staff`, and `implement-spec` have no LQY install copy.

When syncing a newer upstream commit, update this mirror first, merge relevant changes into `baselines/matt-zh/matt-zh-*/*-zh`, then selectively adapt the installable `skills/matt-lqy-*/*-lqy` layer. Preserve baseline fidelity to upstream (do not backfill Ralph customizations); preserve local LQY policy and separate original import Source commit from Upstream reviewed commit. Report upstream changes, baseline changes, and any LQY adaptation still needing manual review.
