---
name: amis-pixel-implementation
description: Implement or fix Amis macOS SwiftUI interfaces from Figma with measured visual and interaction fidelity. Use when a Figma node must be reproduced in Amis, when SwiftUI geometry, typography, icons, semantic variables, hover, focus, disabled, accessibility, recording, or finalizing states must match, or when retained AutomationCLI evidence is needed to verify a visual change.
---

# Amis Pixel Implementation

Turn a Figma node into measured Amis SwiftUI behavior. Treat generated
React/Tailwind as structural reference only; the Figma screenshot, node
properties, variable bindings, product behavior, and repository conventions are
the contract.

## Required Sources

- Use `$amis-variables` for every Amis color or semantic-variable decision.
- Use the official Figma read tools. Pass `clientLanguages: "swift"` and
  `clientFrameworks: "swiftui"` to `get_design_context`.
- Prefer Xcode MCP for Apple build, test, diagnosis, and documentation when it is
  available.
- Use `$amis-test` for repository automation and retained evidence. Read
  `docs/testing/automation.md` before selecting a command; do not invoke raw
  `AutomationCLI`.

## 1. Freeze Scope

- Record the exact Figma URL, file key, node ID, visual state, and target window
  size.
- Record the SwiftUI View and ViewModel in scope.
- List product exceptions that must remain even when absent from the crop.
- List required states such as default, hover, focus, pressed, disabled,
  loading, recording, finalizing, error, light, or dark.
- Do not widen a visual task into unrelated architecture or product changes.

## 2. Build A Figma Ledger

Call `get_design_context` first. If the node is a page/canvas and codegen fails,
use `get_metadata` to find the concrete frame, then retry. Call
`get_variable_defs` on the concrete target.

Record before editing:

- parent and child dimensions, alignment, padding, spacing, and responsive rules;
- semantic variables, raw-value exceptions, opacity, border, radius, blur,
  material, blend mode, and shadow;
- font family, size, weight, width, line height, truncation, and alignment;
- icon node, SF Symbol name or asset source, rendering mode, tint, frame, and hit
  target;
- state-specific differences and transition behavior;
- accessibility label, help text, keyboard behavior, and stable identifier;
- preserved product exceptions.

Use [references/figma-contract-checklist.md](references/figma-contract-checklist.md)
as the ledger and evidence format.

## 3. Inspect Existing SwiftUI

- Find the current View, ViewModel, Models, centralized design tokens, icon
  sources, accessibility identifiers, and relevant tests before editing.
- Reuse existing Modules and Interfaces. Do not create one shallow wrapper per
  Figma frame.
- Keep View presentation and user-intent forwarding separate from ViewModel
  state and business rules.
- Capture or inspect the current app at the same window size and state as Figma.
  Classify mismatches by structure, geometry, variables, typography, assets,
  effects, interaction, and preserved exceptions.

## 4. Implement In SwiftUI

### Layout

- Use `HStack`, `VStack`, `ZStack`, `Grid`, alignment guides, `Spacer`,
  `.padding`, `.frame`, `.layoutPriority`, and stable min/max constraints to
  express the design hierarchy.
- Use exact point values for fixed macOS chrome and fixed-format controls when
  Figma defines them. Keep flexible content responsive with max widths,
  priorities, truncation, and multiline behavior.
- Reserve `.offset` and absolute overlays for genuinely anchored decoration or
  effects. Do not use them to repair normal content flow.
- Keep hit targets and visual frames distinct when the design requires a small
  glyph inside a larger interactive control.

### Variables And Effects

- Map Figma bindings through `$amis-variables` and centralized Swift tokens.
- Preserve raw opacity, shadow, blur, material, and blend properties as explicit
  node facts; do not turn them into global colors without evidence.
- Keep Apple Appearance, Vibrant, Liquid Glass, Menu, and Sizes variables
  platform-scoped. Use native AppKit or SwiftUI behavior when it matches the
  deployment target and measured design; otherwise centralize the compatibility
  style instead of duplicating effect stacks in Views.

### Typography

- For fixed desktop chrome, match Figma's SF Pro point size, named weight, width,
  and line behavior directly with SwiftUI system fonts.
- Use `.fontWidth` for verified expanded, condensed, or compressed SF Pro axes.
- Do not copy CSS line-height or letter-spacing mechanically. Verify baseline,
  wrapping, truncation, and rendered height in SwiftUI.
- Preserve a non-system font only when the project contains it and the design
  requires it; otherwise surface the missing dependency instead of silently
  substituting.

### Icons And Assets

- Use the exact SF Symbol name surfaced by Figma or an existing repository icon
  when it represents the design. Never infer an SF Symbol from a codepoint.
- Verify `symbolRenderingMode`, font/weight, fill or stroke behavior, semantic
  tint, frame, and active/inactive state.
- Import a Figma asset only when no native or existing asset matches. Inspect the
  exported dimensions and content so an active indicator, unrelated canvas, or
  extra whitespace is not shipped accidentally.
- Do not use emoji or a text glyph as a silent substitute for a required icon.

### macOS Interaction And Accessibility

- Implement the Figma-specified hover, focus, pressed, disabled, keyboard, and
  Escape behavior. Do not assume iOS touch behavior.
- Add `.help` for unfamiliar icon controls and English accessibility labels for
  P0 user-facing UI.
- Use stable `.accessibilityIdentifier(...)` values for automation. Do not make
  tests depend on screen coordinates or translated visible copy.
- Ensure dynamic content, labels, progress, and state icons cannot resize or
  overlap fixed controls.

## 5. Verify From The Highest Interface

- Test ViewModel behavior through user intents and observable state; do not test
  private SwiftUI helpers.
- Test centralized formatters, layout metrics, and state mappings when they are
  stable public behavior. Avoid brittle reflection into SwiftUI's private tree.
- Build and run the narrowest relevant workflow. Use Xcode MCP first when
  available; use `$amis-test` for canonical local automation and retained
  `.xcresult`, Accessibility, timeline, diagnostic, and screenshot artifacts.
- Match the Figma state, window dimensions, display scale, content fixture, and
  appearance before comparing screenshots.
- Treat screenshots as diagnostic evidence, not an automatic pixel-golden pass.
  Inspect the retained image and supporting state/Accessibility evidence.
- Verify every required transition, not only the initial frame.
- Re-read the latest evidence after each visual change. Fix the implementation
  or explain why a recorded Figma fact is inapplicable; do not weaken the ledger
  silently.

## Stop Conditions

Stop and report rather than guess when the target node is ambiguous, the
required asset is unavailable, the Figma state is missing, the requested visual
conflicts with an explicit product exception, or the deployment target cannot
support the assumed platform effect.

## Completion

Before reporting completion, confirm that the ledger is resolved, semantic
variables and icons are traceable to Figma, required interaction states work,
the relevant build/tests pass, retained evidence has been inspected, and any
remaining difference has a concrete rationale.
