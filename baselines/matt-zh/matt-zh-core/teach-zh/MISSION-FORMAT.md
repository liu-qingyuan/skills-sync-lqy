# MISSION.md 格式

`MISSION.md` 位于 workspace 根目录，记录用户学习这个主题的原因。每个教学决策（下一步教什么、推荐哪些资源、设计哪些练习）都应追溯到它。

## 模板

```md
# Mission: {Topic}

## Why
{1-3 sentences. The concrete real-world goal the user is chasing. What changes in their life or work when they have this skill? Avoid abstract framings like "to understand X"; push for the underlying outcome.}

## Success looks like
- {A specific, observable thing the user will be able to do}
- {Another specific thing}
- {…}

## Constraints
- {Time, budget, prior commitments, learning preferences, anything that bounds the approach}

## Out of scope
- {Adjacent topics the user explicitly does not want to chase right now, protecting the zone of proximal development}
```

## 规则

- **每个 workspace 一个使命。** 用户想学两个不相关的主题，就应使用两个 workspace。
- **具体胜过抽象。** “十月之前跑一次半程马拉松”胜过“变得更健康”；“向团队交付一个 Rust CLI”胜过“学习 Rust”。
- **追问模糊表达。** 如果用户说不清为什么，先访谈再写。一个糟糕的使命比没有使命更糟。
- **现实变化时修订。** 使命会变化。用户目标改变时更新文件，不要让过时的使命继续指导未来课程。
- **保持简短。** 如果 `MISSION.md` 超过一屏，它就不再是指南针，而开始变成计划。
