---
name: pr-lqy
description: "编写或更新 PR 正文：用最小视觉摘要解释变化，给出 Before/After 验证证据，并说明回滚难度与影响范围。"
metadata:
  credits:
    author: Dex Horthy
    skill: show-me
    url: https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md
---

# PR 正文

只负责正文，不负责创建、发布、合并 PR，也不改变 Ralph 的 issue / Git 契约或直接 commit/push 策略。

读取项目明确指定的领域术语表；新项目默认 `GLOSSARY.md`。用项目词汇简短表达，不重复 diff 已经说明的细节。

```markdown
## Summary

<最小图、伪代码、调用树、文件树或 diff 草图>

## Evidence

- **Before:** <修改前的实际行为或失败测试>
- **After:** <修改后的实际行为或通过测试>

## Merge Danger

**Door:** <one-way 或 two-way>

**Blast Radius:** <受影响的调用方、数据或功能>
```

## Summary

选能解释关键变化的最小视图：算法用伪代码，调用顺序用调用树，职责用文件树，交互关系用 Mermaid，已有结构的局部变化用 diff。不要为格式同时生成所有视图；必要文字紧邻它支持的视觉。

## Evidence

引用真实执行的命令、结果、测试或截图。视觉变化优先使用已有环境能提供的前后截图；非视觉变化用最相关测试和运行结果。

没有执行的检查明确写“未验证”和原因；不编造修改前结果，不为补证据破坏真实数据或生产代码。展示凭据时只隐藏展示副本中的真实秘密值，保留原始证据和本地复现输入。

## Merge Danger

- **two-way**：能低成本回滚，并说明回滚方式。
- **one-way**：涉及数据删除、外部不可逆操作或高成本恢复，说明不可逆部分。
- **Blast Radius**：指出具体影响范围；信息不足就写未知，不用“改动小”代替分析。

只写足够让人判断的证据与风险，不增加发布、安全整改或完整工程流程。
