---
name: to-spec-lqy
description: 把当前对话上下文整理成 spec 并发布到项目 issue tracker；不重新访谈，只综合已有讨论。
---

该 skill 会基于当前对话上下文和对代码库的理解产出一份 spec。不要重新访谈用户，只综合你已经知道的信息。

issue tracker 和 triage 标签词汇表应该已经提供；如果没有，请运行 `$setup-matt-pocock-skills-lqy`。

issue 标题、正文、评论和完成摘要默认使用中文。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。

## 流程

1. 如果还没有探索仓库，先探索仓库以理解代码库当前状态。在整份 spec 中使用项目的领域词汇表，并尊重你触及区域的 ADR。

2. 画出这个功能将在哪些 seam 上测试。优先使用已有 seam，而不是创建新 seam。尽可能使用最高层 seam。如果确实需要新 seam，把它提议在你能找到的最高位置。代码库中的 seam 越少越好；理想数量是 1。

向用户核实这些 seam 是否符合他们预期。

3. 按 `$mermaid-gate-lqy` 判断整份 spec 的上级设计图 gate。这里记录跨 Ticket 的整体架构、接口、流程或状态变化；不替代每个 Ticket 自己的 Mermaid Gate。

4. 使用下面的模板编写 spec，然后发布到项目 issue tracker。应用 `ready-for-agent` triage 标签；不需要额外 triage。

<spec-template>

## Problem Statement

从用户视角描述用户面对的问题。

## Solution

从用户视角描述问题的解决方案。

## User Stories

一份很长的编号用户故事列表。每条用户故事格式为：

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

这份用户故事列表应该非常广，覆盖该功能的所有方面。

## Implementation Decisions

已做出的实现决策列表。可以包括：

- 将构建或修改的模块
- 将修改的模块接口
- 开发者给出的技术澄清
- 架构决策
- schema 变更
- API contract
- 具体交互

不要包含具体文件路径或代码片段。它们很快可能过时。

例外：如果 prototype 产出的代码片段比散文更精确地编码了决策（状态机、reducer、schema、type shape），可以把它内联到相关决策中，并简短说明它来自 prototype。只保留决策密集的部分，不要放工作 demo，只放重要部分。

## Testing Decisions

已做出的测试决策列表。包括：

- 什么构成好的测试：只测试外部行为，不测试实现细节
- 哪些模块会被测试
- 测试先例：代码库中类似类型的测试

## Mermaid Gate

按 `$mermaid-gate-lqy` 记录整份 spec 的上级判断。需要图时放入或链接当前/目标 Mermaid 图；不需要图时说明原因。这里覆盖整体设计，不替代每个 Ticket 的 Mermaid Gate。

## Out of Scope

描述本 spec 范围外的事项。

## Further Notes

该功能的任何进一步说明。

</spec-template>
