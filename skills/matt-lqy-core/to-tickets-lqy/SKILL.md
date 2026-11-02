---
name: to-tickets-lqy
disable-model-invocation: true
description: 把已有计划、spec 或对话拆为最小充分、可独立验证的 Ticket，声明真实依赖并发布到 issue tracker。
---

# To Tickets

把已有计划拆为**最小充分**的 tracer-bullet Ticket：每票一个可观察结果与真实 blocking edges，不以数量或篇幅为目标，不复制整份 spec。

issue tracker 和 triage 标签词汇表应该已经提供；如果没有，提示用户显式运行 `$setup-matt-pocock-skills-lqy`。

issue 标题、正文、评论和完成摘要默认使用中文。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。

## 流程

### 1. 收集上下文

从对话开始；给出 spec、issue 或 URL 引用时，完整读取对应正文和评论。

如果目标是 GitHub 且 Tickets 将进入 Ralph `ready-for-agent` backlog，必须引用一个标题以 `Spec:` 开头、正文最后包含有效 `## Git` 的父 spec。没有父 spec 时停止并要求先运行 `$to-spec-lqy`；不要从对话或当前 checkout 自行发明 Git 契约。

### 2. 探索代码库

按需查阅代码现状、项目术语表与相关 ADR，沿用领域词汇；只识别真正阻塞当前切片的 prefactor。

### 3. 起草 vertical slices

把工作拆成 **tracer bullet** Ticket。

<vertical-slice-rules>

- 每票一个可观察结果，只贯穿实际涉及的层，不强制 schema/API/UI。
- 可独立 demo 或验证；影响方案的关键业务假设先窄验证，依赖结论的实现不提前定案。
- 每票能放进一个新的上下文窗口。
- 不按用户故事、章节或技术层机械拆票；合并重复工作，保留必要契约、失败行为和测试。
- 仅做必要 prefactor；能随切片完成就不另拆票，必须先做的才是 blocker。

</vertical-slice-rules>

验收复用已有约束，仅补本票判据。按需注明输入代表性、验证与上线配置差异及未验证项；技术跑通不等于业务或上线验收，关键缺口先澄清。

标出真实 **blocking edges**，不按编号或发布顺序制造依赖；没有 blocker 不等于可安全并发。

在纵向切片和独立验收前提下识别**合理并行**：核查共享契约、共享写入及数据库/构建/测试冲突，风险写入现有 `What to build`，不新增契约字段。实施时仍核查实际文件与资源，不为并行横切技术层。

**宽 refactor 例外：** 机械变更影响大量调用点、无法保持纵向切片绿色时，用 **expand-contract**：先并存新旧形式，再按 blast radius（package/目录）分批迁移，最后删除旧形式。每批一票，依赖 expand；contract 依赖全部迁移，每批 CI 保持绿色。若单批也无法保持绿色，各批共享 integration branch，最终 integrate-and-verify Ticket 依赖全部批次，只在最终验收承诺绿色。

### 4. 设计图 Gate

对每个 Ticket 单独按 `$mermaid-gate-lqy` 判断和实施。这里判断该 Ticket 自身的局部变化；如果来源 spec 已经有上级 Mermaid Gate，不要把它当作本 Ticket 的 gate。

### 5. 设计终审

在给出 Ticket 方案或发布前，按 `$codebase-design-lqy`、`$gitnexus` 和 `$simple` 审核并修订草稿，检查范围、假设、架构、依赖、契约与验证。最多启动一个只读 review agent，应用 `$simple`，只返回审查意见，不修改文件或实施。

### 6. 追问用户

把提议拆分呈现为编号列表。对每个 Ticket 显示：

- **Title**：简短、描述性的名称
- **Blocked by**：哪些其他 Ticket 必须先完成（如有）
- **What it delivers**：该 Ticket 的可观察结果或要验证的关键假设
- **Mermaid Gate**：该 Ticket 按 `$mermaid-gate-lqy` 的判断
- 可并行的 frontier，以及需要串行的依赖或资源原因

核实粒度、真实依赖及合并/拆分，迭代到用户批准。

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

worktree dirty 时，只处理本阶段已授权的改动，验证并 commit/push 后重跑 publisher；不得借此实施 Ticket 或接手其它业务改动。无法在此范围内处理时停止并询问用户；禁止 stash、reset、`git clean` 或临时 workspace 绕过 gate。

部分创建、回读或标签失败时，publication gate 保持 open，所有已创建 issues 都不可领取；其中部分 Ticket 可能已经带 `ready-for-agent`，不要手工关闭 gate、补标签或关闭/修改父 spec。修复原因后重新规划如何处理这些 draft issues，避免重复发布。

<tickets-file-template>

# Tickets: <short name of the work>

一句话总结这些 Ticket 要构建什么。如有来源 spec，引用它。

Work the **frontier**：任何 blocker 全部完成的 Ticket。对纯线性链条来说，就是从上到下。

## <Ticket title>

**What to build:** 描述本票的可观察行为或要验证的关键假设，引用相关约束；不要写逐层实现列表。

**Blocked by:** 阻塞该 Ticket 的其他 Ticket 标题，或 `None — can start immediately`。

**Mermaid Gate:** 按 `$mermaid-gate-lqy` 记录该 Ticket 的判断；需要图时放入或链接当前/目标图，不需要图时说明原因。

- [ ] 本票必要的可观察结果及验证条件。

## <Ticket title>

...

</tickets-file-template>

<issue-template>

## Parent

issue tracker 上 parent issue 的引用（如果来源是已有 issue；否则省略此节）。

## What to build

描述本票的可观察行为或要验证的关键假设，引用相关约束；不要写逐层实现。

## Acceptance criteria

- [ ] 本票必要的可观察结果及验证条件。

## Mermaid Gate

按 `$mermaid-gate-lqy` 记录该 Ticket 的判断。需要图时放入或链接当前/目标图；不需要图时说明原因。

## Blocked by

- 每个 blocking Ticket 的引用，或 `None — can start immediately`。

</issue-template>

不写具体文件路径或代码；仅当 prototype 的状态机、schema、type shape 等比文字更精确时，内联决策片段并注明来源，不放 demo。

Ralph 是默认批量入口；用户可显式选择 `$implement-spec-subagent-lqy` 处理安全独立的 frontier。发布后停止；提示用户选择单 Ticket、Ralph 或子 agent 实施，不自动实施或启动循环。
</content>
