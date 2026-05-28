---
name: figma-pixel-implementation
description: Implement or fix frontend UI to match a Figma design with one-to-one fidelity. Use when the user provides a Figma URL/node and asks to reproduce, restore, compare, pixel match, fix visual differences, preserve product exceptions, or avoid mistakes in colors, sizes, spacing, icons, typography, shadows, and visual E2E verification.
---

# Figma Pixel Implementation

Use this skill to turn a Figma node into a measured implementation, not a subjective approximation.

## Operating rule

Do not declare success from a visual screenshot threshold alone. Extract Figma facts, implement from those facts, then verify with DOM/style/geometry contracts plus screenshot evidence.

## Workflow

### 1. Freeze scope and exceptions

- Record the exact Figma URL, `fileKey`, and `nodeId`.
- Record product exceptions explicitly, e.g. “keep existing storage footer” or “preserve newly added nav item”.
- Treat exceptions as first-class acceptance criteria, not as permission to ignore the rest of Figma.

### 2. Inspect Figma deeply

- Fetch Figma data for the target node with enough depth to expose nested text, images, fills, effects, and layouts.
- Extract an implementation ledger before editing:
  - container width/height/x/y,
  - background colors and border colors,
  - row/button widths, heights, radii, x/y offsets,
  - active/inactive text colors and font weights,
  - typography family, size, line-height,
  - icon node IDs, sizes, colors, and active/inactive variants,
  - state-to-asset mapping: which icon/SVG is used when active, inactive, hover, disabled, and after navigation,
  - shadows/effects,
  - bottom controls and avatars.
- If using Figma MCP image export, export the actual node IDs for icons/frames. Beware exports that include extra canvas or active indicators; inspect SVG dimensions/viewBox before using.

### 3. Compare existing UI before editing

- Capture the current rendered UI at the same viewport and state as Figma.
- Inspect DOM boxes and computed styles for candidate elements.
- Make a mismatch list by category: structure, color, size, position, typography, icons/assets, state behavior, preserved exceptions.

### 4. Implement with exact facts

- Prefer Figma-exported SVG/vector assets over emoji or approximate icon libraries.
- Treat active and inactive icons as separate state assets. Do not use a purple/active SVG as the default icon; wire rendering so only the selected item receives the active asset/color.
- Use exact Figma colors when the target is explicit, e.g. `#F5F5F7`, `#FAFAFA`, `#EDE9FF`, `#6B4EFF`, `#8573FF`, `#666`, `#999`, `#111`.
- Match dimensions and offsets directly for fixed chrome: widths, heights, row spacing, icon slots, active indicators, dot positions, radii.
- Avoid double backgrounds: if an exported active SVG already contains its active background, do not also add an active CSS background around it.
- Avoid wrapper drift: padding/gap on wrappers changes Figma coordinates. If a Figma button is `36×36` at a known x/y, ensure the DOM clickable box is also `36×36`, not `36×36` plus wrapper padding.
- Preserve requested existing sections. Do not remove product-specific UI just because it is absent from the Figma crop.

### 5. Verify with contracts, not only snapshots

Add or update tests to assert exact Figma-derived facts:

- width/height/x/y for main containers,
- background and text colors via computed style,
- font-weight, font-size, line-height,
- icon count/type and no emoji glyph regressions,
- active/inactive state colors, weights, and icon asset URLs or SVG fill/stroke colors,
- state transitions: after selecting another item, the previously active icon returns to the inactive asset/color,
- active dot/indicator dimensions and position,
- preservation of explicitly requested exceptions.

Use screenshots as evidence, but keep DOM/style contracts as the guardrail against false positives from loose screenshot thresholds.

### 6. Iterate from failures

- If a contract fails, fix the implementation or the selector; do not weaken the contract without explaining why the Figma fact is not applicable.
- Re-open the latest screenshot after every visual edit.
- If a test aggregates failures into a release report, inspect the report JSON too; a Playwright run can pass while the custom release gate records blockers.

## Common mistakes to prevent

- Using a shallow Figma read and missing nested colors/sizes.
- Treating a snapshot match as proof when the baseline fixture was generated from the current wrong UI.
- Exporting a whole Figma frame as an icon and accidentally including unrelated active bars or whitespace.
- Swapping icon assets because the Figma node name is generic like “Button” or “Text”. Verify SVG path/size.
- Importing an active purple SVG as the default icon, so an inactive item stays purple even when the row/text state is neutral.
- Only testing the initial selected row and missing state transitions where the previous icon must revert to inactive.
- Leaving theme variables like `var(--brand-primary)` when Figma requires a specific color.
- Adding wrapper padding/gaps that move icons away from Figma x/y positions.
- Removing existing product UI that the user explicitly asked to keep.
- Checking visible text after collapsing a sidebar; assert preservation before collapse or re-expand first.

## Completion checklist

Before final response, verify:

- Figma ledger exists in notes/test comments/report.
- All requested exceptions are preserved.
- Assets are from correct Figma nodes and inspected for size/viewBox.
- Active/inactive icon assets are mapped and tested for both initial state and click/navigation transitions.
- DOM/style/geometry contracts pass.
- Visual E2E screenshot evidence is saved.
- Typecheck/lint/structure/diff checks pass when applicable.
- Remaining visual differences are listed with rationale.

See `references/figma-contract-checklist.md` for a compact checklist and sample Playwright helpers.
