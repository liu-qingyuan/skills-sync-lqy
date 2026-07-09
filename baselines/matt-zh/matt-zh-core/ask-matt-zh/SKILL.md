---
name: ask-matt-zh
description: 询问当前情境应该使用哪个 skill 或工作流。这是本仓库 skills 的中文路由器。用于用户不确定该用哪个 Matt Pocock 工作流，或想让 AI 帮忙选择 grill、triage、to-spec、tdd、handoff 等流程时。
---

# Ask Matt

你不需要记住每个 skill，所以来问。

**flow** 是穿过多个 skills 的路径。大多数路径沿一条**主流程**前进，并有两个**入口**并入它。其他内容要么是独立 skill，要么是运行在底下的 vocabulary layer。

## 主流程：idea → ship

大多数工作会走这条路线：你有一个想法，并希望把它构建出来。

1. **`/grill-with-docs-zh`** — 通过追问 sharpen idea。当你**有代码库**时从这里开始：它是有状态的，会把学到的东西保留在 `CONTEXT.md` 和 ADR 中。（没有代码库？用 `/grill-me-zh`，见 Standalone。两者都运行同一个 `/grilling-zh` primitive；`grill-with-docs-zh` 是留下记录的版本。）
2. **分支 — 能否在对话中解决每个问题？** 如果某个问题需要可运行答案（state、business logic、必须看到的 UI），就通过 **`/handoff-zh`** 在两个方向上桥接，绕到 prototype：
   - **`/handoff-zh`** 导出，然后打开一个指向该文件的新会话；
   - **`/prototype-zh`** 用一次性代码回答问题；
   - **`/handoff-zh`** 带回你学到的内容，并从原始 idea 线程引用它。
3. **分支 — 这是 multi-session build 吗？**
   - **是** → **`/to-spec-zh`**（把线程变成 spec），然后 **`/to-tickets-zh`** 把它拆成 tracer-bullet Ticket，每个 Ticket 声明自己的 **blocking edges**。本地 tracker 上，这是按顺序手动处理的 `tickets.md`；真实 tracker 上，edges 会变成原生 blocking links，因此 blocker 完成后任何可领取 Ticket 都可以被抓取。每个 Ticket 启动一次 **`/implement-zh`**，并且**在 Ticket 之间清空上下文**。
   - **否** → 在同一个上下文窗口里直接 **`/implement-zh`**。

无论哪条路，**`/implement-zh`** 都通过内部驱动 **`/tdd-zh`** 构建每个 issue：一次一个 red-green slice。结束时运行 **`/code-review-zh`**，对 diff 做 Standards + Spec 双轴 review，然后 commit。只想 test-first 构建一个具体行为而不需要完整 spec 时，直接使用 **`/tdd-zh`**；想针对固定点审查 branch 或 PR 时，直接使用 **`/code-review-zh`**。

### Context hygiene

步骤 1-3 保持在**一个不间断的上下文窗口**中：不要在 `/to-tickets-zh` 前 compact 或清空。这样 grilling、spec 和 Ticket 都建立在同一组思考上。每个 `/implement-zh` 再从 Ticket 开始 fresh。

限制是 **[smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)**：也就是模型仍能敏锐推理的窗口（顶级模型约 120k token）。如果会话在 `/to-tickets-zh` 前接近这个限制，不要继续硬推；用 `/handoff-zh` 在新线程继续。

## 入口

这些起始情况会产生工作，然后并入主流程。

- **Bug 和请求堆积** → **`/triage-zh`**。它让 issues 穿过 triage roles，并产出 agent-ready issues，之后由 **`/implement-zh`** 接手。

  triage 只适用于**不是你创建的** issues：bug reports、incoming feature requests、任何原始输入。`/to-tickets-zh` 产出的 Ticket 已经是 ready-for-agent，因此**不要 triage 它们**。

- **Something's broken** → **`/diagnosing-bugs-zh`**。用于难处理的问题：初看解决不了的 bug、间歇性 flake、在两个 known-good states 之间混入的 regression。它在拥有一个会因为_这个_ bug 已经变红的 tight feedback loop 之前拒绝理论化，然后用 regression test 修复。post-mortem 如果发现真正问题是没有好 seam 锁住 bug，它会交给 **`/improve-codebase-architecture-zh`**。

- **巨大而模糊的 effort：greenfield 项目或大型 feature build，大到一个会话装不下** → **`/wayfinder-zh`**。当从当前状态到 destination 的路还看不见时，它在 issue tracker 上绘制一张共享 map，一次解决一个调查 Ticket，产出**决策，而不是交付物**，直到迷雾被推开、路线清楚。然后它并入主流程的 **`/to-spec-zh`**（如果最后发现足够小，也可以直接到 **`/implement-zh`**）。`/grill-with-docs-zh` 用来 sharpen 一个会话能装下的 idea；wayfinder 用来处理装不下的 idea。

## Codebase health

不是 feature work，而是维护。

- **`/improve-codebase-architecture-zh`** — 有空时运行，让代码库持续适合 agent 操作。它会发现**模块加深机会**；选中一个会_产生一个 idea_，再带入主流程的 `/grill-with-docs-zh`。它负责调查候选项；**`/codebase-design-zh`**（见下）负责设计被选中的那个。

## Vocabulary underneath

两个 model-invoked references 运行在其他 skills 下面，分别是自身 vocabulary 的 single source of truth。当问题出在**词**而不是流程时，可以直接调用它们；也可以让上面的 skills 拉取它们。

- **`/domain-modeling-zh`** — sharpen 项目的 domain language：挑战模糊术语，解决 overloaded word（例如 “account” 同时承担三种含义），把难以逆转的决策记录为 ADR。它是 `/grill-with-docs-zh` 用来保持 `CONTEXT.md` 干净 glossary 的主动 discipline。
- **`/codebase-design-zh`** — deep-module vocabulary（module、interface、depth、seam、adapter、leverage、locality），用于设计模块的形状：用小 interface 在干净 seam 后隐藏大量行为。`/tdd-zh` 和 `/improve-codebase-architecture-zh` 都使用这套语言。

## Crossing sessions

- **`/handoff-zh`** — 当 thread 已满，或你需要分支出去（例如进入 `/prototype-zh` 会话）时，把对话压缩成 markdown 文件。不要原地继续；**打开新会话并引用该文件**来携带上下文。它是在上下文窗口之间双向移动的桥。想要**新会话**但需要**保留当前对话**时使用。
- **`/compact`**（built-in）— 留在**同一个对话**里，让较早 turns 被 summary。适合在阶段之间有意中断、且不介意丢失逐字历史时使用。不要在阶段中途 compact；agent 可能丢失方向。`/handoff-zh` 是 fork；`/compact` 是 continue。

## Standalone

完全在主流程之外。

- **`/grill-me-zh`** — 和 `/grill-with-docs-zh` 一样的追问，但用于你**没有代码库**的时候。无状态：不在本地保存内容，也不构建 `CONTEXT.md`。用于 sharpen 任何不属于仓库的 plan 或 design。
- **`/prototype-zh`** — 一个小型一次性程序，用来回答一个 design question：这个 state model 是否合理，或者 UI 应该长什么样。它从一开始就是 throwaway：保留答案，删除代码。它是主流程第 2 步里的 detour，但任何纸面上难以解决的设计问题都可以用它。
- **`/research-zh`** — 把阅读工作交给**后台 agent**：它针对 **primary sources** 调查一个问题，然后在仓库里留下带引用的 Markdown 文件。你可以在它阅读时继续工作。它产出的文件要带入 `/grill-with-docs-zh` 的主流程；research feeding thinking，不替代 thinking。
- **`/teach-zh`** — 使用当前目录作为有状态 workspace，跨多个会话学习一个概念。
- **`/writing-great-skills-zh`** — 写好和编辑好 skills 的参考。

## Precondition

**`/setup-matt-pocock-skills-zh`** — 第一次运行工程 flow 之前先运行它，配置其他 skills 假设的 issue tracker、triage labels 和 doc layout。自定义 issue tracker 也可以。
