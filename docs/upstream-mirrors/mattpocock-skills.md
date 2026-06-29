# Matt Pocock upstream mirror

- Repository: https://github.com/mattpocock/skills
- Source commit synced: `5d78bd0903420f97c791f834201e550c765699f8`
- Mirrored skills: 35
- Directory policy: keep Matt Pocock's two-level layout under `upstream/mattpocock/skills/<category>/<skill-name>` so the English mirror is not displayed by `npx skills@latest add liu-qingyuan/skills-sync-lqy`.

## Mirrored skills

### Engineering

- `ask-matt` ← `upstream/mattpocock/skills/engineering/ask-matt`
- `codebase-design` ← `upstream/mattpocock/skills/engineering/codebase-design`
- `diagnosing-bugs` ← `upstream/mattpocock/skills/engineering/diagnosing-bugs`
- `domain-modeling` ← `upstream/mattpocock/skills/engineering/domain-modeling`
- `grill-with-docs` ← `upstream/mattpocock/skills/engineering/grill-with-docs`
- `implement` ← `upstream/mattpocock/skills/engineering/implement`
- `improve-codebase-architecture` ← `upstream/mattpocock/skills/engineering/improve-codebase-architecture`
- `prototype` ← `upstream/mattpocock/skills/engineering/prototype`
- `resolving-merge-conflicts` ← `upstream/mattpocock/skills/engineering/resolving-merge-conflicts`
- `setup-matt-pocock-skills` ← `upstream/mattpocock/skills/engineering/setup-matt-pocock-skills`
- `tdd` ← `upstream/mattpocock/skills/engineering/tdd`
- `to-issues` ← `upstream/mattpocock/skills/engineering/to-issues`
- `to-prd` ← `upstream/mattpocock/skills/engineering/to-prd`
- `triage` ← `upstream/mattpocock/skills/engineering/triage`

### Productivity

- `grill-me` ← `upstream/mattpocock/skills/productivity/grill-me`
- `grilling` ← `upstream/mattpocock/skills/productivity/grilling`
- `handoff` ← `upstream/mattpocock/skills/productivity/handoff`
- `teach` ← `upstream/mattpocock/skills/productivity/teach`
- `writing-great-skills` ← `upstream/mattpocock/skills/productivity/writing-great-skills`

### Personal

- `edit-article` ← `upstream/mattpocock/skills/personal/edit-article`
- `obsidian-vault` ← `upstream/mattpocock/skills/personal/obsidian-vault`

### Misc

- `git-guardrails-claude-code` ← `upstream/mattpocock/skills/misc/git-guardrails-claude-code`
- `migrate-to-shoehorn` ← `upstream/mattpocock/skills/misc/migrate-to-shoehorn`
- `scaffold-exercises` ← `upstream/mattpocock/skills/misc/scaffold-exercises`
- `setup-pre-commit` ← `upstream/mattpocock/skills/misc/setup-pre-commit`

### In progress

- `decision-mapping` ← `upstream/mattpocock/skills/in-progress/decision-mapping`
- `loop-me` ← `upstream/mattpocock/skills/in-progress/loop-me`
- `review` ← `upstream/mattpocock/skills/in-progress/review`
- `writing-beats` ← `upstream/mattpocock/skills/in-progress/writing-beats`
- `writing-fragments` ← `upstream/mattpocock/skills/in-progress/writing-fragments`
- `writing-shape` ← `upstream/mattpocock/skills/in-progress/writing-shape`

### Deprecated

- `design-an-interface` ← `upstream/mattpocock/skills/deprecated/design-an-interface`
- `qa` ← `upstream/mattpocock/skills/deprecated/qa`
- `request-refactor-plan` ← `upstream/mattpocock/skills/deprecated/request-refactor-plan`
- `ubiquitous-language` ← `upstream/mattpocock/skills/deprecated/ubiquitous-language`

## Frontmatter compatibility

Some upstream frontmatter keys are omitted from local `SKILL.md` files because this repository validates skills with Codex `quick_validate.py`.

- `ask-matt`: omitted `disable-model-invocation`
- `decision-mapping`: omitted `disable-model-invocation`
- `edit-article`: omitted `disable-model-invocation`
- `grill-me`: omitted `disable-model-invocation`
- `grill-with-docs`: omitted `disable-model-invocation`
- `handoff`: omitted `argument-hint`, `disable-model-invocation`
- `implement`: omitted `disable-model-invocation`
- `improve-codebase-architecture`: omitted `disable-model-invocation`
- `loop-me`: omitted `argument-hint`, `disable-model-invocation`
- `prototype`: omitted `disable-model-invocation`
- `setup-matt-pocock-skills`: omitted `disable-model-invocation`
- `teach`: omitted `argument-hint`, `disable-model-invocation`
- `to-issues`: omitted `disable-model-invocation`
- `to-prd`: omitted `disable-model-invocation`
- `triage`: omitted `disable-model-invocation`
- `ubiquitous-language`: omitted `disable-model-invocation`
- `writing-beats`: omitted `disable-model-invocation`
- `writing-fragments`: omitted `disable-model-invocation`
- `writing-great-skills`: omitted `disable-model-invocation`
- `writing-shape`: omitted `disable-model-invocation`

## Installer grouping

The English mirror is intentionally outside top-level `skills/`. `npx skills@latest` recursively discovers installable skills from `skills/`, so moving English upstream copies back under `skills/` will make them visible to users. Keep `.claude-plugin/marketplace.json` in sync for installable LQY/local groups only.

When syncing a newer upstream commit, update this mirror first, merge relevant changes into `baselines/matt-zh/matt-zh-*/*-zh`, then adapt the installable `skills/matt-lqy-*/*-lqy` layer. Report upstream changes, baseline changes, and any LQY adaptation that still needs manual review.
