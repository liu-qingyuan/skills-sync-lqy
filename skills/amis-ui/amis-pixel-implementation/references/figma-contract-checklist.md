# Amis SwiftUI Figma Contract Checklist

Use this ledger before editing and update it with verification evidence.

## Design Ledger

| Area | Figma node and fact | SwiftUI surface | Variable or asset | State | Verification |
| --- | --- | --- | --- | --- | --- |
| Root | node, target size, crop | View/window | background variable | light/dark | retained screenshot |
| Container | width, height, radius, border | named View | Amis variable | default/focus | screenshot and layout metric |
| Text | family, size, weight, line behavior | Text/TextEditor | text variable | placeholder/content | fixture screenshot |
| Icon | node, symbol/asset, frame | Image/Button | icon variable | default/hover/disabled | AX action and screenshot |
| Interaction | trigger and terminal state | ViewModel intent | n/a | hover/focus/Escape/etc. | ViewModel and E2E evidence |
| Exception | product UI retained | owning View | existing token | all relevant states | visibility and behavior |

## Figma Extraction

- [ ] Exact URL, file key, node ID, state, mode, and target window size recorded.
- [ ] `get_design_context` read with Swift/SwiftUI client metadata.
- [ ] Concrete frame found through `get_metadata` when the URL points at a page.
- [ ] `get_variable_defs` read for the concrete target.
- [ ] Screenshot inspected in addition to generated structural code.
- [ ] Parent and child dimensions, padding, spacing, alignment, and constraints recorded.
- [ ] Typography, icons, effects, opacity, radius, borders, and shadows recorded.
- [ ] Default, hover, focus, pressed, disabled, loading, and feature-specific states mapped.
- [ ] Product exceptions listed explicitly.

## SwiftUI Review

- [ ] Existing View, ViewModel, Models, design tokens, assets, and tests inspected.
- [ ] View depends on ViewModel state and forwards user intents only.
- [ ] No shallow wrapper was added solely to mirror a Figma frame name.
- [ ] Fixed chrome uses stable point geometry; flexible content has responsive constraints.
- [ ] Text wrapping, truncation, baseline, and longest localized English fixture fit.
- [ ] Colors use `$amis-variables` and centralized Swift aliases.
- [ ] Raw values are documented node exceptions rather than duplicated globals.
- [ ] SF Symbols use exact names and rendering modes; imported assets are inspected.
- [ ] Hover, focus, disabled, Escape, pointer target, `.help`, and VoiceOver behavior are covered.
- [ ] Stable accessibility identifiers exist for automated interactions.

## Verification Route

Read `docs/testing/automation.md` and choose the narrowest available command.
Run it through `$amis-test`; never call raw `AutomationCLI`.

```bash
python3 .agents/skills/amis-test/scripts/amis_test.py run \
  --timeout-seconds 1800 <command> --retention all

python3 .agents/skills/amis-test/scripts/amis_test.py inspect --run latest
```

When the selected run contains a native result bundle:

```bash
python3 .agents/skills/amis-test/scripts/amis_test.py verify-xcresult \
  --run latest --timeout-seconds 60
```

Do not invent a feature-specific E2E command that is absent from the guide.
Screenshots under retained Scenario evidence are diagnostic, not automatic
pixel-golden assertions.

## Evidence Review

- [ ] Build/test exit status and complete referenced logs inspected.
- [ ] Latest retained screenshot opened at the expected app-window dimensions.
- [ ] Accessibility tree, Scenario timeline, result, and diagnostics inspected when present.
- [ ] Initial and transition states both checked.
- [ ] No coordinate clicks or translated-copy selectors were introduced.
- [ ] Remaining differences are listed with their Figma fact and rationale.
