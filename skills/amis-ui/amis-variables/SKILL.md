---
name: amis-variables
description: Apply the current Amis Figma semantic variables in macOS SwiftUI design and implementation. Use when Codex needs to inspect a Figma node's bound background, line, text, icon, link, layer, function, or chart variables; map those bindings into centralized Amis SwiftUI Color and ShapeStyle tokens; preserve the selected Figma mode; or distinguish Amis variables from Apple Appearance, Vibrant, Liquid Glass, Menu, and raw design values.
---

# Amis Variables

Use the target Figma node as the source of truth. The current semantic collection
is still named `Amis V1.0 色卡`, but its actual 48-token contents and current
Main Chat bindings supersede the previous skill text.

## Inspect The Target

1. Freeze the exact Figma file, node, visual state, and mode.
2. Call `get_design_context` for layout and property bindings.
3. Call `get_variable_defs` on the concrete frame or component. Page canvas
   `784:6` is only an index and may return no variable selection; drill into the
   relevant child such as `784:429`, `784:721`, `784:884`, `822:540`, or
   `822:663`.
4. Read [references/current-main-chat-variables.md](references/current-main-chat-variables.md)
   when working on Main Chat, Composer, Voice Input, or Output Metrics.
5. Record raw values only as verification evidence. Implement the bound semantic
   variable whenever one exists.

## Apply Precedence

Use this order when evidence differs:

1. The exact variable bound to the target node and state.
2. The target frame's selected Figma mode.
3. The current Figma collection aliases in the bundled reference.
4. An existing centralized Swift token only when its role and resolved value
   match the Figma evidence.
5. A raw value only when Figma leaves that property unbound; record it as a
   design exception rather than inventing a new global variable.

Target bindings override generic usage heuristics. For example, Composer node
`822:664` deliberately uses `Line/Gutter/Gutter` as its component border, and
node `822:668` deliberately uses `Text/Text-Secondary` for the placeholder.

## Keep Variable Systems Distinct

- Treat `Bg/*`, `Line/*`, `Text/*`, `Icon/*`, `Link/*`, `Layer/*`,
  `Function/*`, and `Chart/*` as Amis semantic variables.
- Treat Apple `Labels/*`, Vibrant Fills/Labels, Liquid Glass, Menu, and Sizes as
  platform or component variables. Preserve their semantics; do not rename them
  into Amis tokens.
- Treat literals, opacity, blend mode, material, blur, and shadow as explicit
  node properties unless Figma binds them to a variable.
- Do not reintroduce names absent from the current 48-token collection. In
  particular, the current collection has no `Bg/Inverse-*`, `Bg/Always-Black`,
  `Bg/Mask`, `Text/Brand-White`, `Text/Text-Error`, or `Text/Text-Warning`.

## Map Into SwiftUI

- Keep SwiftUI Views on centralized semantic aliases from `DesignTokens.swift`;
  do not scatter Figma hex values through View code.
- Match both meaning and value before reusing a legacy alias. Update the
  centralized alias or add one clear semantic alias when the current code is
  stale or missing the Figma role.
- Keep AppKit-backed adaptive colors or native materials for Apple appearance
  variables. Do not emulate platform semantics with fixed light-mode RGB.
- Preserve alpha, material, blur, blend, and shadow separately from the base
  color token.
- Add a short token comment with the source Figma variable and node when a
  mapping is new or non-obvious.
- Mirror reusable `Color` tokens onto `ShapeStyle` only when the repository's
  existing shorthand pattern benefits multiple call sites.

## Handle Modes Correctly

The collection defines `V1.0_light` and `V1.0_dark`, and the bundled reference
records both alias mappings. The inspected Main Chat frames are light-mode
fixtures. Do not claim dark visual fidelity from alias definitions alone; use a
dark target frame or an explicit mode switch before verifying composition,
materials, contrast, or effects.

## Verify

- Confirm the implemented semantic role and resolved value against the target
  node, not only against the reference table.
- Check light and dark behavior when both modes are in scope.
- Verify interaction-state bindings independently: default, hover, focused,
  pressed, disabled, recording, and finalizing may use different variables.
- Report any raw design value that still lacks an Amis semantic variable instead
  of silently promoting it into the token system.
