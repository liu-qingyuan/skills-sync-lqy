---
name: amis-variables
description: Apply the Amis V1.0 design system semantic variables for product design and UI implementation. Use when Codex needs to choose or reference Amis surface/background, border/divider, text, or icon tokens; preserve light and dark mode values, usage rules, and pairing tables; never hardcode hex values when these semantic variables apply.
---

# Amis V1.0 Design Variables — Surface, Border, Text & Icon

Use this skill when designing with the Amis V1.0 design system. It teaches which semantic variables to apply for backgrounds, borders, text, and icons — in both light and dark modes.

All variables reference Core Color aliases (e.g. `Neutral/12`, `Brand/6`). Never hardcode hex values; always use the semantic token.

---

## Bg (Surface / Background)

| Token | Light | Dark | When to use |
|---|---|---|---|
| `Bg/Primary` | Neutral/White | Neutral/12 | Main page/screen background |
| `Bg/Secondary` | Neutral/1 | Neutral/10 | Cards, panels, slightly elevated surfaces |
| `Bg/Tertiary` | Neutral/2 | Neutral/9 | Nested containers, input backgrounds |
| `Bg/Quaternary` | Neutral/3 | Neutral/7 | Hover states, subtle fills |
| `Bg/Inverse-Primary` | Neutral/12 | Neutral/White | Dark surface on light bg (tooltips, toasts) |
| `Bg/Inverse-Secondary` | Neutral/9 | Neutral/1 | Secondary inverse surface |
| `Bg/Inverse-Tertiary` | Neutral/11 | Neutral/2 | Tertiary inverse surface |
| `Bg/Always-Black` | Neutral/12 | Neutral/12 | Always dark regardless of mode (overlays) |
| `Bg/Always-White` | Neutral/White | Neutral/White | Always light regardless of mode |
| `Bg/Mask` | Alpha/Black/50 | Alpha/Black/70 | Modal/drawer scrim overlay |

**Rules:**
- Use `Bg/Primary` → `Secondary` → `Tertiary` → `Quaternary` for layering depth (each step is one level deeper/elevated)
- Use `Bg/Inverse-*` for reversed-theme surfaces (e.g. dark tooltip on light page)
- Use `Bg/Mask` only for full-screen overlays behind modals/drawers
- Never use `Always-Black` / `Always-White` unless the surface must ignore theme (e.g. brand splash)

---

## Line (Border & Divider)

| Token | Light | Dark | When to use |
|---|---|---|---|
| `Line/Border/Subtle` | Neutral/2 | Neutral/11 | Default card/container border, low emphasis |
| `Line/Border/Strong` | Neutral/3 | Neutral/7 | Focused inputs, selected states, high-emphasis borders |
| `Line/Divider/Divider` | Neutral/2 | Neutral/11 | Full-width section dividers |
| `Line/Divider/Short Divider` | Neutral/4 | Neutral/7 | Short/inset dividers, list item separators with more contrast |
| `Line/Divider/Strong` | Neutral/2 | Neutral/8 | Strong section separation |
| `Line/Gutter/Gutter` | Neutral/3 | Neutral/11 | Layout gutters, grid lines |

**Rules:**
- Default border → `Border/Subtle`; use `Border/Strong` only for active/focused/selected states
- Default divider → `Divider/Divider`; use `Divider/Short Divider` for inset list separators needing more visual weight
- `Gutter` is for layout structure only, not component borders

---

## Text

| Token | Light | Dark | When to use |
|---|---|---|---|
| `Text/Text-Primary` | Neutral/12 | Neutral/White | Body copy, headings, default readable text |
| `Text/Text-Secondary` | Neutral/6 | Neutral/5 | Supporting text, subtitles, metadata |
| `Text/Text-Tertiary` | Neutral/5 | Neutral/6 | Placeholder text, captions, low-priority labels |
| `Text/Text-Tips` | Neutral/4 | Neutral/7 | Helper text, hints, very low emphasis |
| `Text/Text-Disable` | Neutral/4 | Neutral/7 | Disabled state text |
| `Text/Text-Brand` | Brand/6 | Brand/5 | Links, brand-colored labels, active tab text |
| `Text/Brand-White` | Brand/6 | Neutral/White | Brand text that inverts on dark mode |
| `Text/Text-Error` | RedFunct/6 | RedFunct/6 | Error messages, validation failures |
| `Text/Text-Warning` | Orange/6 | Orange/5 | Warning messages |
| `Text/Text-Success` | GreenFunct/6 | GreenFunct/6 | Success messages, confirmations |
| `Text/Inverse-Primary` | Neutral/White | Neutral/12 | Text on inverse/dark surfaces |
| `Text/Always-Black` | Neutral/12 | Neutral/12 | Text that must stay dark regardless of mode |
| `Text/Always-White` | Neutral/White | Neutral/White | Text that must stay light regardless of mode |

**Rules:**
- Hierarchy: `Primary` → `Secondary` → `Tertiary` → `Tips` (decreasing emphasis)
- `Disable` and `Tips` use the same color — `Disable` is for interactive disabled states, `Tips` is for passive helper text
- Use semantic status tokens (`Error`/`Warning`/`Success`) only for feedback states, never for decoration
- `Inverse-Primary` pairs with `Bg/Inverse-Primary` surfaces
- Never use `Always-*` unless the text must ignore theme switching

---

## Icon

| Token | Light | Dark | When to use |
|---|---|---|---|
| `Icon/Icon-Primary` | Neutral/8 | Neutral/White | Default icons, high-emphasis actions |
| `Icon/Icon-Secondary` | Neutral/7 | Neutral/4 | Supporting icons, secondary actions |
| `Icon/Icon-Tertiary` | Neutral/6 | Neutral/5 | Low-emphasis icons, decorative |
| `Icon/Icon-Quaternary` | Neutral/5 | Neutral/6 | Subtle/disabled-adjacent icons |

**Rules:**
- Match icon emphasis to adjacent text: `Icon-Primary` with `Text-Primary`, `Icon-Secondary` with `Text-Secondary`, etc.
- Use `Icon-Primary` for interactive icons (buttons, nav items)
- Use `Icon-Tertiary` / `Icon-Quaternary` for decorative or contextual icons that shouldn't compete with content

---

## Quick Reference: Pairing Rules

| Context | Bg | Border | Text | Icon |
|---|---|---|---|---|
| Default card | `Bg/Secondary` | `Border/Subtle` | `Text-Primary` | `Icon-Primary` |
| Focused input | `Bg/Primary` | `Border/Strong` | `Text-Primary` | `Icon-Secondary` |
| Disabled element | `Bg/Tertiary` | `Border/Subtle` | `Text-Disable` | `Icon-Quaternary` |
| Modal overlay | `Bg/Primary` + `Bg/Mask` | — | `Text-Primary` | `Icon-Primary` |
| Tooltip (dark) | `Bg/Inverse-Primary` | — | `Text/Inverse-Primary` | — |
| Error state | `Bg/Primary` | `Border/Strong` | `Text-Error` | — |
| Brand CTA | `Bg/Primary` | — | `Text/Text-Brand` | `Icon-Primary` |
