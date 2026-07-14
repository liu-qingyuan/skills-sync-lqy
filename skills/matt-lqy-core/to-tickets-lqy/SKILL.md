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

如果目标是 GitHub 且 Tickets 将进入 Ralph `ready-for-agent` backlog，必须引用一个标题以 `Spec:` 开头、正文最后包含有效 `## Git` 的父 spec。没有父 spec 时停止并要求先运行 `$to-spec-lqy`；不要从对话或当前 checkout 自行发明 Git 契约。

### 2. 探索代码库

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

### 4. 设计图 Gate

对每个 Ticket 单独按 `$mermaid-gate-lqy` 判断和实施。这里判断该 Ticket 自身的局部变化；如果来源 spec 已经有上级 Mermaid Gate，不要把它当作本 Ticket 的 gate。

### 5. 设计终审

在向用户给出 Ticket 方案或执行任何发布前，必须审核完整 Ticket 草稿，并按结果直接修订：

- 用 `$codebase-design-lqy` 检查各 Ticket 是否落在清晰的 Module、Interface 和 Seam 上，避免浅模块、不必要的 Adapter 和没有架构收益的 prefactor。
- 用 `$gitnexus` 检查索引状态；可用时查看相关代码的 context 和 impact，并用源码与测试确认关键结论。索引缺失或过期时先建立或刷新；工具不可用时回退到源码检查并说明。
- 用 `$simple` 合并重复 Ticket，删除虚假 blocker、过早抽象和不必要步骤，同时保留 vertical slice、契约与验收标准。

三项都要实际执行，不能只在结果中提及 skill 名称。终审完成后才可给出方案或继续发布。

### 6. 追问用户

把提议拆分呈现为编号列表。对每个 Ticket 显示：

- **Title**：简短、描述性的名称
- **Blocked by**：哪些其他 Ticket 必须先完成（如有）
- **What it delivers**：该 Ticket 打通的端到端行为
- **Mermaid Gate**：该 Ticket 按 `$mermaid-gate-lqy` 的判断

询问用户：

- 粒度是否合适？太粗还是太细？
- blocking edges 是否正确，每个 Ticket 是否只依赖真正阻塞它的 Ticket？
- 是否应该合并或进一步拆分任何 Ticket？

迭代到用户批准拆分。

### 7. 发布 Ticket 到已配置 tracker

发布批准后的 Ticket。**如何发布**取决于 `$setup-matt-pocock-skills-lqy` 配置的 tracker；Ticket 内容相同，只有 blocking edges 的表达形式不同：

- **本地文件** → 在仓库根目录写一个 `tickets.md`，所有 Ticket 按依赖顺序排列（blocker 在前），每个 Ticket 的 `Blocked by` 列出它依赖的标题。使用下面的文件模板。
- **GitHub Ralph-ready** → 必须使用下面的 Git-bound Ticket-set publisher；不要逐个手工创建或提前应用 `ready-for-agent`。
- **其他真实 issue tracker 或明确不进入 Ralph backlog 的 GitHub 工作** → 每个 Ticket 按依赖顺序创建。平台有原生 blocking / sub-issue 关系时使用原生能力；否则在每个 Ticket 的 `Blocked by` 中列出 blocking issues。按 tracker 自身约定应用 triage 标签。

不要关闭或修改任何 parent issue。

#### GitHub Ralph-ready Ticket set

先为每个 Ticket 准备一个 Markdown body file。草稿只包含以下三个唯一、有序且非空的 section；不要写 `## Parent`、`## Blocked by` 或 `## Git`，这些持久契约由 publisher 统一生成：

```markdown
## What to build

...

## Acceptance criteria

- [ ] ...

## Mermaid Gate

该 Ticket 按 `$mermaid-gate-lqy` 得出的判断和所需图。
```

再创建一个 JSON manifest。`tickets` 必须按依赖顺序排列；同一组内的 blocker 使用先前 Ticket 的 `id`，已存在的同 branch blocker 使用 `#<issue-number>`：

```json
{
  "tickets": [
    {
      "id": "contract",
      "title": "建立公开 contract",
      "body_file": "contract.md",
      "blocked_by": []
    },
    {
      "id": "consumer",
      "title": "接入 contract consumer",
      "body_file": "consumer.md",
      "blocked_by": ["contract", "#123"]
    }
  ]
}
```

运行 publisher：

```bash
python3 ~/.agents/skills/to-tickets-lqy/scripts/publish_ticket_set.py \
  --repo <repo-path> \
  --parent <parent-spec-issue-number> \
  --manifest <tickets-manifest.json> \
  [--allow-base-drift]
```

publisher 负责完整事务：

- 回读 open 父 spec，并通过 `ralph-plan-lqy` 的共享 contract validator 验证唯一且最终的 `## Git`。
- 读取同一父 spec 的既有子 Tickets；若已有 ready 子 Ticket，则用它确认冻结 contract，并要求父 spec 与全部既有子 Tickets 完整一致。没有 ready 子 Ticket 时使用父 spec 当前 contract。
- 验证每个外部 blocker 具有有效 Git 契约且 `Branch` 与冻结 contract exact match；同 branch 下不同 `Base branch` 或 `Base commit` 可以形成依赖。跨 branch blocker、未知或逆序的内部 blocker 都在写入前停止。
- 调用共享 provisioner fetch `Base branch`、检查 base drift，并创建或复用 branch/worktree/upstream。provision 失败时不创建 Ticket。
- 先创建一个无 ready label 的同 branch publication gate issue，再按依赖顺序创建全部无 ready label 的 Tickets；publisher 统一生成 `## Parent`、包含 publication gate 和真实依赖的 `## Blocked by`，以及最终 `## Git`。
- 回读并验证 gate 与整组 Ticket 的标题、正文、open 状态、Mermaid Gate 和 Git 契约；全部通过后才按反向依赖顺序应用 `ready-for-agent` 并回读确认。
- 所有 ready 状态确认后，最后关闭 publication gate，使整组 frontier 同时变为可领取。任何创建、回读、label 或 label rollback API 失败都会让 gate 保持 open；即使部分 Ticket 已带 ready label，Ralph 仍会因 open gate 跳过它们。

如果 provisioner 报告 `base drift`，停止并向用户展示记录的旧 SHA、远程新 SHA 和相关提交摘要，等待明确选择。选择保留旧 SHA 时，在用户明确批准后从头重新运行 publisher 并添加 `--allow-base-drift`；该路径仍只接受 clean、base-ancestor、upstream/remote 同步的目标 branch。选择新 SHA 时先由用户明确批准更新父 spec 的 `Base commit`，然后不带 flag 从头重新验证。不要静默刷新父 spec，也不要默认绕过 drift gate。

worktree dirty 时，由 agent 完成可确认的改动，验证并 commit/push 后重跑 publisher。仅在意图不明时询问用户；禁止 stash、reset、`git clean` 或临时 workspace 绕过 gate。

部分创建、回读或标签失败时，publication gate 保持 open，所有已创建 issues 都不可领取；其中部分 Ticket 可能已经带 `ready-for-agent`，不要手工关闭 gate、补标签或关闭/修改父 spec。修复原因后重新规划如何处理这些 draft issues，避免重复发布。

<tickets-file-template>

# Tickets: <short name of the work>

一句话总结这些 Ticket 要构建什么。如有来源 spec，引用它。

Work the **frontier**：任何 blocker 全部完成的 Ticket。对纯线性链条来说，就是从上到下。

## <Ticket title>

**What to build:** 从用户视角描述该 Ticket 打通的端到端行为；不要写逐层实现列表。

**Blocked by:** 阻塞该 Ticket 的其他 Ticket 标题，或 `None — can start immediately`。

**Mermaid Gate:** 按 `$mermaid-gate-lqy` 记录该 Ticket 的判断；需要图时放入或链接当前/目标图，不需要图时说明原因。

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

## Mermaid Gate

按 `$mermaid-gate-lqy` 记录该 Ticket 的判断。需要图时放入或链接当前/目标图；不需要图时说明原因。

## Blocked by

- 每个 blocking Ticket 的引用，或 `None — can start immediately`。

</issue-template>

无论哪种形式，都避免写具体文件路径或代码片段；它们很快会过时。例外：如果 prototype 产出的片段比散文更精确地编码了决策（状态机、reducer、schema、type shape），可以内联并简短说明它来自 prototype。只保留决策密集的部分，不要放工作 demo，只放重要部分。

用 `/implement-lqy` 一次处理 frontier 上的一个 Ticket；Ticket 之间清空上下文。
</content>
