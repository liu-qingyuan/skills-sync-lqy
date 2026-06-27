# Matt Pocock upstream mirror

- Repository: https://github.com/mattpocock/skills
- Source commit synced: `5d78bd0903420f97c791f834201e550c765699f8`
- Mirrored skills: 35
- Directory policy: keep Matt Pocock's two-level layout under `skills/<category>/<skill-name>`.

## Mirrored skills

### Engineering

- `ask-matt` ← `skills/engineering/ask-matt`
- `codebase-design` ← `skills/engineering/codebase-design`
- `diagnosing-bugs` ← `skills/engineering/diagnosing-bugs`
- `domain-modeling` ← `skills/engineering/domain-modeling`
- `grill-with-docs` ← `skills/engineering/grill-with-docs`
- `implement` ← `skills/engineering/implement`
- `improve-codebase-architecture` ← `skills/engineering/improve-codebase-architecture`
- `prototype` ← `skills/engineering/prototype`
- `resolving-merge-conflicts` ← `skills/engineering/resolving-merge-conflicts`
- `setup-matt-pocock-skills` ← `skills/engineering/setup-matt-pocock-skills`
- `tdd` ← `skills/engineering/tdd`
- `to-issues` ← `skills/engineering/to-issues`
- `to-prd` ← `skills/engineering/to-prd`
- `triage` ← `skills/engineering/triage`

### Productivity

- `grill-me` ← `skills/productivity/grill-me`
- `grilling` ← `skills/productivity/grilling`
- `handoff` ← `skills/productivity/handoff`
- `teach` ← `skills/productivity/teach`
- `writing-great-skills` ← `skills/productivity/writing-great-skills`

### Personal

- `edit-article` ← `skills/personal/edit-article`
- `obsidian-vault` ← `skills/personal/obsidian-vault`

### Misc

- `git-guardrails-claude-code` ← `skills/misc/git-guardrails-claude-code`
- `migrate-to-shoehorn` ← `skills/misc/migrate-to-shoehorn`
- `scaffold-exercises` ← `skills/misc/scaffold-exercises`
- `setup-pre-commit` ← `skills/misc/setup-pre-commit`

### In progress

- `decision-mapping` ← `skills/in-progress/decision-mapping`
- `loop-me` ← `skills/in-progress/loop-me`
- `review` ← `skills/in-progress/review`
- `writing-beats` ← `skills/in-progress/writing-beats`
- `writing-fragments` ← `skills/in-progress/writing-fragments`
- `writing-shape` ← `skills/in-progress/writing-shape`

### Deprecated

- `design-an-interface` ← `skills/deprecated/design-an-interface`
- `qa` ← `skills/deprecated/qa`
- `request-refactor-plan` ← `skills/deprecated/request-refactor-plan`
- `ubiquitous-language` ← `skills/deprecated/ubiquitous-language`

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

`npx skills@latest` reads `.claude-plugin/marketplace.json` for display groups. Keep that file in sync whenever skills are added, moved, or removed.
