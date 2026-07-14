# Current Main Chat Variables

Verified from Figma file `J5mW5w9JnAvF1qg4UQaO0K`, page `784:6`
(`7.13-MainChat 聊天框+反馈框`). The semantic collection is
`Amis V1.0 色卡`, with modes `V1.0_light` and `V1.0_dark`.

## Contents

- [Semantic Collection](#semantic-collection)
- [Core Color](#core-color)
- [Current Node Bindings](#current-node-bindings)
- [SwiftUI Mapping Audit](#swiftui-mapping-audit)
- [Non-Amis Variables And Raw Values](#non-amis-variables-and-raw-values)

## Semantic Collection

### Bg

| Variable | Light | Dark |
| --- | --- | --- |
| `Bg/Primary` | `Neutral/White` | `Neutral/12` |
| `Bg/Secondary` | `Neutral/1` | `Neutral/10` |
| `Bg/Tertiary` | `Neutral/2` | `Neutral/9` |
| `Bg/Quaternary` | `Neutral/3` | `Neutral/7` |
| `Bg/Always-White` | `Neutral/White` | `Neutral/White` |

### Line

| Variable | Light | Dark |
| --- | --- | --- |
| `Line/Gutter/Gutter` | `Neutral/3` | `Neutral/11` |
| `Line/Border/Subtle` | `Neutral/2` | `Neutral/11` |
| `Line/Border/Strong` | `Neutral/3` | `Neutral/7` |
| `Line/Divider/Divider` | `Neutral/2` | `Neutral/11` |
| `Line/Divider/Strong` | `Neutral/2` | `Neutral/8` |
| `Line/Divider/Short Divider` | `Neutral/4` | `Neutral/7` |

### Text

| Variable | Light | Dark |
| --- | --- | --- |
| `Text/Text-Primary` | `Neutral/12` | `Neutral/White` |
| `Text/Text-Secondary` | `Neutral/6` | `Neutral/5` |
| `Text/Text-Tertiary` | `Neutral/5` | `Neutral/6` |
| `Text/Text-Tips` | `Neutral/4` | `Neutral/7` |
| `Text/Text-Disable` | `Neutral/4` | `Neutral/7` |
| `Text/Text-Brand` | `Brand/6` | `Brand/5` |
| `Text/Always-White` | `Neutral/White` | `Neutral/White` |
| `Text/Inverse-Primary` | `Neutral/White` | `Neutral/12` |
| `Text/Always-Black` | `Neutral/12` | `Neutral/12` |
| `Text/Text-Success` | `GreenFunct/6` | `GreenFunct/6` |

### Icon

| Variable | Light | Dark |
| --- | --- | --- |
| `Icon/Icon-Primary` | `Neutral/8` | `Neutral/White` |
| `Icon/Icon-Secondary` | `Neutral/7` | `Neutral/4` |
| `Icon/Icon-Tertiary` | `Neutral/6` | `Neutral/5` |
| `Icon/Icon-Quaternary` | `Neutral/5` | `Neutral/6` |

### Link

| Variable | Light | Dark |
| --- | --- | --- |
| `Link/1` | `Brand/1` | `#8573FF0D` |
| `Link/2` | `Brand/2` | `#8573FF1A` |
| `Link/3` | `Brand/3` | `#8573FF4D` |
| `Link/4` | `Brand/4` | `#8573FF80` |
| `Link/5` | `Brand/5` | `#8573FFB2` |
| `Link/Default` | `Brand/6` | `Brand/5` |
| `Link/Pressed` | `Brand/7` | `Brand/7` |
| `Link/Disable` | `Brand/3` | `Brand/9` |

### Layer

| Variable | Light | Dark |
| --- | --- | --- |
| `Layer/1` | `Neutral/White` | `Neutral/10` |
| `Layer/2` | `Neutral/2` | `Neutral/11` |
| `Layer/4` | `Neutral/2` | `Neutral/8` |
| `Layer/Active` | `Neutral/White` | `Neutral/7` |

### Function

| Variable | Light | Dark |
| --- | --- | --- |
| `Function/success` | `GreenTrade/6` | `GreenTrade/6` |
| `Function/success-Soft` | `GreenTrade/1` | `GreenTrade/10` |
| `Function/Fail` | `RedTrade/6` | `RedTrade/6` |
| `Function/Fail-Soft` | `RedTrade/1` | `RedTrade/10` |
| `Function/Hot` | `RedFunct/6` | `RedFunct/6` |
| `Function/Star` | `Yellow/6` | `Yellow/6` |

### Chart

| Variable | Light | Dark |
| --- | --- | --- |
| `Chart/Chart-1` | `RedTrade/5` | `RedTrade/5` |
| `Chart/Chart-2` | `RedTrade/3` | `RedTrade/3` |
| `Chart/Chart-3` | `GreenTrade/5` | `GreenTrade/5` |
| `Chart/Chart-4` | `GreenTrade/3` | `GreenTrade/3` |
| `Chart/Chart-6` | `Promotion/Blue` | `Promotion/Blue` |

## Core Color

| Alias | Value | Alias | Value |
| --- | --- | --- | --- |
| `Neutral/White` | `#FFFFFF` | `Neutral/1` | `#FAFAFA` |
| `Neutral/2` | `#F2F3F4` | `Neutral/3` | `#DFE0E2` |
| `Neutral/4` | `#C4C7CA` | `Neutral/5` | `#A0A3A7` |
| `Neutral/6` | `#84888C` | `Neutral/7` | `#484B51` |
| `Neutral/8` | `#303236` | `Neutral/9` | `#18191B` |
| `Neutral/10` | `#131516` | `Neutral/11` | `#1F2023` |
| `Neutral/12` | `#070808` | `Brand/1` | `#F9F8FF` |
| `Brand/2` | `#F3F1FF` | `Brand/3` | `#DAD5FF` |
| `Brand/4` | `#C2B9FF` | `Brand/5` | `#AA9DFF` |
| `Brand/6` | `#8573FF` | `Brand/7` | `#7868E5` |
| `Brand/9` | `#5D51B2` | `GreenFunct/6` | `#2BC235` |
| `GreenTrade/1` | `#EAF9EB` | `GreenTrade/3` | `#ADEDCE` |
| `GreenTrade/5` | `#57D4A0` | `GreenTrade/6` | `#2BC287` |
| `GreenTrade/10` | `#092117` | `RedTrade/1` | `#FEEEED` |
| `RedTrade/3` | `#FF9EA3` | `RedTrade/5` | `#FC5B6F` |
| `RedTrade/6` | `#F74B60` | `RedTrade/10` | `#341C1D` |
| `RedFunct/6` | `#F7594B` | `Yellow/6` | `#FEBE00` |
| `Promotion/Blue` | `#16D9D9` |  |  |

## Current Node Bindings

| Node | Verified bindings or exceptions |
| --- | --- |
| `784:429` Default Chat | `Bg/Secondary`, Text Primary/Secondary/Tertiary, Icon Primary/Tertiary, Link Default/Disable, Border/Subtle, Gutter, Short Divider |
| `784:721` Recording | Adds `Icon/Icon-Secondary` and `Bg/Tertiary` |
| `784:884` Cancel hover | Adds `Bg/Quaternary`; cancel glyph uses `Icon/Icon-Tertiary` |
| `822:540` Metrics | Uses the current Amis variables plus Apple Appearance, Vibrant, Liquid Glass, and Menu variables |
| `822:663` Composer | `Text/Text-Secondary`, `Icon/Icon-Tertiary`, `Bg/Always-White`, `Link/Disable`, `Line/Gutter/Gutter` |

Exact current bindings:

- Composer border `822:664`: `Line/Gutter/Gutter`.
- Composer surface `822:664`: raw `rgba(255,255,255,0.75)`, not `Bg/*`.
- Placeholder `822:668` and model label `822:674`: `Text/Text-Secondary`.
- Disabled Send `822:680`: `Link/Disable`; Send glyph `822:681`:
  `Bg/Always-White`.
- Recording button `784:865`: `Bg/Tertiary`; glyph `784:866`:
  `Icon/Icon-Primary`.
- Recording overlay `784:872`: `Bg/Tertiary`.
- Cancel hover `784:1043`: `Bg/Quaternary`; glyph `784:1044`:
  `Icon/Icon-Tertiary`.
- Metrics popover labels under `822:765`: `Text/Text-Primary`.

## SwiftUI Mapping Audit

Existing candidates in `DesignTokens.swift` must still be checked by role and
value:

| Figma variable | Existing Swift candidate | Audit note |
| --- | --- | --- |
| `Bg/Secondary` | `.amisPageBg`, `.amisBubbleBg` | Both currently resolve correctly; prefer one role-specific alias at a call site |
| `Bg/Tertiary` | `.amisToolPillBg` | Value matches; name is too specific for unrelated surfaces |
| `Bg/Quaternary` | `.amisTrackBg` | Value matches; do not use the track-specific name for hover without a semantic alias |
| `Line/Gutter/Gutter` | `.amisInputBorder` | Matches current Composer use |
| `Line/Divider/Short Divider` | `.amisHairline` | Value matches |
| `Text/Text-Primary` | `.amisTextPrimary` | Current Swift value is `#111317`, but Figma resolves to `#070808`; update centrally before reuse |
| `Text/Text-Secondary` | `.amisTextSecondary` | Matches |
| `Text/Text-Tertiary` | `.amisTextTertiary` | Matches |
| `Icon/Icon-Primary` | `.amisIconPrimary` | Matches |
| `Icon/Icon-Secondary` | none | Add a centralized semantic alias when needed |
| `Icon/Icon-Tertiary` | none | Do not reuse a text alias merely because the light value matches |
| `Link/Default` | `.amisAccent` | Value matches; preserve the link/action role in naming where practical |
| `Link/Disable` | none | Add a centralized semantic alias when needed |

## Non-Amis Variables And Raw Values

- Apple `Labels/*`, Vibrant Labels/Fills, Liquid Glass, Menu, and Sizes coexist
  with Amis variables. Keep them platform-scoped.
- The Composer's 75% white surface, Cloud badge blue, window controls, code-block
  literals, menu glass tint, shadows, blur, and blend modes include raw or
  non-Amis values. Preserve exact target-node evidence and report the mapping gap.
- Current target frames are light-mode visual fixtures. Dark aliases are verified
  collection definitions, not proof of dark composition or material fidelity.
