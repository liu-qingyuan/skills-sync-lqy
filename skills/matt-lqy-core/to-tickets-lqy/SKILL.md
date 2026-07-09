---
name: to-tickets-lqy
description: 把计划、spec 或当前对话拆成一组 tracer-bullet Ticket；每个 Ticket 声明 blocking edges，并发布到已配置 tracker。
---

# To Tickets

把计划、spec 或对话拆成一组 **Ticket**：tracer-bullet vertical slice，每个 Ticket 都声明哪些其他 Ticket 会 **block** 它。

issue tracker 和 triage 标签词汇表应该已经提供；如果没有，请运行 `$setup-matt-pocock-skills-lqy`。

issue 标题、正文、评论和完成摘要默认使用中文。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。

## 流程

### 1. 收集上下文

从对话上下文中已有的信息开始。如果用户把引用作为参数传入（spec 路径、issue 编号或 URL），从 issue tracker 获取它并完整阅读正文和评论。

### 2. 探索代码库（可选）

如果还没有探索代码库，先探索以理解代码当前状态。Ticket 标题和描述应该使用项目领域词汇表，并尊重你触及区域的 ADR。

寻找 prefactor 的机会，让实现更容易。“Make the change easy, then make the easy change.”

### 3. 起草 vertical slices

把工作拆成 **tracer bullet** Ticket。

<vertical-slice-rules>

- 每个 slice 都切出一条窄但完整的路径，贯穿每一层（schema、API、UI、tests）；这是 vertical，不是某一层的 horizontal slice
- 完成后的 slice 可以独立 demo 或验证
- 每个 slice 的大小都应该能放进一个新的上下文窗口
- 任何 prefactoring 都应该先完成

</vertical-slice-rules>

给每个 Ticket 标出它的 **blocking edges**：哪些其他 Ticket 必须先完成，它才能开始。没有 blocker 的 Ticket 可以立即开始。

**宽 refactor 是 vertical slicing 的例外。** 宽 refactor 指一个机械变化（例如重命名一列、重新定义共享 symbol 类型）影响整个代码库，导致一次编辑会打破成千上万的调用点，没有任何 vertical slice 能保持绿色。不要强行做成 tracer bullet；把它排成 **expand-contract**。先 expand：把新形式放在旧形式旁边，保证现有代码不坏。然后按 blast radius 分批迁移调用点（按 package、目录等），每批一个 Ticket，block 在 expand 之后，并通过旧形式仍存在来保持每批 CI 绿色。最后 contract：所有调用点迁完后删除旧形式，这个 Ticket block 在所有迁移批次之后。如果连单个批次都无法独立保持绿色，仍保留这个顺序，但让这些批次共享一个 integration branch，并全部 block 到最后的 integrate-and-verify Ticket；绿色只在最后承诺。

### 4. 设计图 Gate（可选）

按 `$mermaid-gate-lqy` 的要求进行判断和实施。

### 5. 追问用户

把提议拆分呈现为编号列表。对每个 Ticket 显示：

- **Title**：简短、描述性的名称
- **Blocked by**：哪些其他 Ticket 必须先完成（如有）
- **What it delivers**：该 Ticket 打通的端到端行为

询问用户：

- 粒度是否合适？太粗还是太细？
- blocking edges 是否正确，每个 Ticket 是否只依赖真正阻塞它的 Ticket？
- 是否应该合并或进一步拆分任何 Ticket？

迭代到用户批准拆分。

### 6. 发布 Ticket 到已配置 tracker

发布批准后的 Ticket。**如何发布**取决于 `$setup-matt-pocock-skills-lqy` 配置的 tracker；Ticket 内容相同，只有 blocking edges 的表达形式不同：

- **本地文件** → 在仓库根目录写一个 `tickets.md`，所有 Ticket 按依赖顺序排列（blocker 在前），每个 Ticket 的 `Blocked by` 列出它依赖的标题。使用下面的文件模板。
- **真实 issue tracker（GitHub、Linear 等）** → 每个 Ticket 发布为一个 issue，按依赖顺序创建（blocker 在前），这样每个 Ticket 的 blocking edges 可以引用真实标识符。平台有原生 blocking / sub-issue 关系时使用原生能力；否则在每个 Ticket 的 `Blocked by` 中列出 blocking issues。除非另有说明，应用 `ready-for-agent` triage 标签；这些 Ticket 按构造就是 agent-grabbable。

不要关闭或修改任何 parent issue。

<tickets-file-template>

# Tickets: <short name of the work>

一句话总结这些 Ticket 要构建什么。如有来源 spec，引用它。

Work the **frontier**：任何 blocker 全部完成的 Ticket。对纯线性链条来说，就是从上到下。

## <Ticket title>

**What to build:** 从用户视角描述该 Ticket 打通的端到端行为；不要写逐层实现列表。

**Blocked by:** 阻塞该 Ticket 的其他 Ticket 标题，或 `None — can start immediately`。

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

## <Ticket title>

...

</tickets-file-template>

<issue-template>

## Parent

issue tracker 上 parent issue 的引用（如果来源是已有 issue；否则省略此节）。

## What to build

从用户视角描述该 Ticket 打通的端到端行为；不要写逐层实现。

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- 每个 blocking Ticket 的引用，或 `None — can start immediately`。

</issue-template>

无论哪种形式，都避免写具体文件路径或代码片段；它们很快会过时。例外：如果 prototype 产出的片段比散文更精确地编码了决策（状态机、reducer、schema、type shape），可以内联并简短说明它来自 prototype。只保留决策密集的部分，不要放工作 demo，只放重要部分。

用 `/implement-lqy` 一次处理 frontier 上的一个 Ticket；Ticket 之间清空上下文。
</content>
