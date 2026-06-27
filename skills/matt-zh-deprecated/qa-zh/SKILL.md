---
name: qa-zh
description: 交互式 QA 会话：用户用对话方式报告 bug 或问题，agent 创建 GitHub issues，并在后台探索代码库获得上下文和领域语言。
---

# 质量保证会议

运行交互式 QA 会话。用户描述他们遇到的问题。您澄清、探索代码库的上下文，并提交持久的、以用户为中心的 GitHub 问题，并使用项目的领域语言。

## 对于用户提出的每个问题

### 1. 倾听并稍微澄清

让用户用自己的话描述问题。提出**最多 2-3 个简短的澄清问题**，重点关注：

- 他们的预期与实际发生的情况
- 重现步骤（如果不明显）
- 是持续的还是间歇的

不要过度采访。如果描述足够清晰，可以归档，请继续。

### 2.在后台探索代码库

与用户交谈时，在后台启动代理 (subagent_type=Explore) 以了解相关区域。我们的目标不是找到解决办法，而是：

- 了解该领域使用的领域语言（检查 UBIQUITOUS_LANGUAGE.md）
- 了解该功能的用途
- 识别面向用户的行为边界

此上下文可以帮助您编写更好的问题 - 但问题本身不应引用特定文件、行号或内部实现细节。

### 3. 评估范围：单一问题还是细分问题？

在提交之前，确定这是一个**单一问题**还是需要**分解**为多个问题。

发生故障时：

- 修复跨越多个独立区域（例如“表单验证错误并且成功消息丢失并且重定向被破坏”）
- 不同的人可以并行处理明显不同的关注点
- 用户描述了具有多种不同故障模式或症状的事物

在以下情况下保留为单一问题：

- 一种行为在某个地方是错误的
- 这些症状都是由相同的根本行为引起的

### 4. 提交 GitHub 问题

使用“gh issues create”创建问题。不要要求用户先查看——只需归档并共享 URL。

问题必须是**持久的**——在重大重构之后它们仍然应该有意义。从用户的角度来写。

#### 对于单个问题

使用这个模板：
```
## What happened

[Describe the actual behavior the user experienced, in plain language]

## What I expected

[Describe the expected behavior]

## Steps to reproduce

1. [Concrete, numbered steps a developer can follow]
2. [Use domain terms from the codebase, not internal module names]
3. [Include relevant inputs, flags, or configuration]

## Additional context

[Any extra observations from the user or from codebase exploration that help frame the issue — e.g. "this only happens when using the Docker layer, not the filesystem layer" — use domain language but don't cite files]
```
#### 对于故障（多个问题）

按依赖顺序创建问题（首先是阻止者），以便您可以引用实际问题编号。

对每个子问题使用此模板：
```
## Parent issue

#<parent-issue-number> (if you created a tracking issue) or "Reported during QA session"

## What's wrong

[Describe this specific behavior problem — just this slice, not the whole report]

## What I expected

[Expected behavior for this specific slice]

## Steps to reproduce

1. [Steps specific to THIS issue]

## Blocked by

- #<issue-number> (if this issue can't be fixed until another is resolved)

Or "None — can start immediately" if no blockers.

## Additional context

[Any extra observations relevant to this slice]
```
创建故障时：

- **优先选择许多较薄弱的问题，而不是少数较严重的问题** - 每个问题都应该是独立可修复和可验证的
- **诚实地标记阻塞关系** — 如果问题 B 在问题 A 解决之前确实无法测试，请这么说。如果它们是独立的，请将两者标记为“无 - 可以立即开始”
- **按依赖顺序创建问题**，以便您可以在“阻止者”中引用实际问题编号
- **最大化并行性** - 目标是多个人（或代理）可以同时处理不同的问题

#### 所有发行机构的规则

- **没有文件路径或行号** - 这些都过时了
- **使用项目的域语言**（检查 UBIQUITOUS_LANGUAGE.md 如果存在）
- **描述行为，而不是代码** - “同步服务无法应用补丁”而不是“applyPatch() 在第 42 行抛出”
- **复制步骤是强制性的** - 如果您无法确定它们，请询问用户
- **保持简洁** - 开发人员应该能够在 30 秒内阅读该问题

归档后，打印所有问题 URL（总结阻塞关系）并询问：“下一期，还是我们完成了？”

### 5. 继续会话

继续下去，直到用户说他们完成了。每个问题都是独立的——不要将它们分批处理。