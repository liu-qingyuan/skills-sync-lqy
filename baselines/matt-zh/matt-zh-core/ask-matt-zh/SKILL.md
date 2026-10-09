---
name: ask-matt-zh
description: 询问当前情况适合哪个 Skill 或流程；本仓库 Skill 的路由入口。
disable-model-invocation: true
---

# 问 Matt

不必记住所有 Skill，直接问。

说明某个 Skill 做什么或建议跳过步骤前，先读它的 `SKILL.md`：这里的摘要仅用于定位。

**流程**是穿过一组 Skill 的路径。多数路径沿同一**主流程**前进，两条**入口支线**汇入它；其余是独立工具或底层共享词汇。

## 主流程：想法 → 交付

多数工作的路线：你有一个想法，希望把它构建出来。

1. **`/grill-with-docs-zh`** 通过访谈打磨想法。只要**身处工作目录**，就从这里开始：它会把学到的东西记入 `GLOSSARY.md` 和 ADR。没有工作目录时改用 `/grill-me-zh`（见独立工具）。两者都运行 `/grilling-zh`，但前者留下书面记录；有仓库可记录时它更合适。
2. **分支：能靠对话解决所有问题吗？**如果某个问题需要可运行的答案（状态、业务逻辑、必须亲眼看到的 UI），借助双向 **`/handoff-zh`** 转入原型（原型在独立目录，这正是 handoff 的适用情形；见“阶段边界”）：
   - 使用 **`/handoff-zh`** 输出，再用其文件打开新会话；
   - 用 **`/prototype-zh`** 以临时代码回答问题；
   - 再用 **`/handoff-zh`** 带回发现，在原讨论中引用它。
3. **分支：这项构建要跨多个会话吗？**
   - **要** → **`/to-spec-zh`** 将对话整理成 spec，再用 **`/to-tickets-zh`** 拆成 tracer-bullet Ticket，每个声明阻塞关系。之后有两种执行方式：
     - 每个 Ticket 用一次 **`/implement-zh`**，中间用 **`/clear`** 清空上下文。本地 tracker 的每个 Ticket 是 `.scratch/<feature>/issues/` 中的独立文件，人工按依赖顺序处理；真实 tracker 用原生阻塞关系，阻塞项完成的 Ticket 即可领取。每个 Ticket 自成一体，因此上一项的上下文可以丢弃。
     - 用 **`/implement-spec-zh`** 一次处理整个 spec：将 Ticket 看成**任务图**，在可执行的**前沿**上并行派发实现 subagent，最后汇总到一个**集成分支**。如果更愿意协调构建而非逐项亲自驱动，选这个方式。
   - **不要** → 在当前上下文直接运行 **`/implement-zh`**。

   两种方式都借助 **`/tdd-zh`** 开发（逐个红绿切片），并以 **`/code-review-zh`** 对 diff 做 Standards + Spec 两轴审查。`/implement-zh` 为每个 Ticket 运行二者；`/implement-spec-zh` 的实现 subagent 各自执行 TDD，最后对集成分支整体 review 一次。如果只想测试先行实现具体行为，直接用 **`/tdd-zh`**；若要从固定点 review 分支或 PR，直接用 **`/code-review-zh`**。

   工作提交为 PR 时，**`/pr-zh`** 整理正文：用最小视觉元素展示变化、给出前后对比证据、判断是单向门还是双向门。它允许模型自行调用，因此 Agent 撰写 PR 时会主动使用。

4. **`/retro-zh`** 闭环。构建后（尤其是不顺利时），回看会话，提出改善 Agent **环境**而非代码的建议：导航指针、自动检查、`/code-review-zh` 执行的编码标准、引导文件、工具。机械错误变为确定性检查；判断问题变为编码标准。下一次构建从更好的环境开始。

### 上下文卫生

步骤 1–3 保持**连续的上下文窗口**（`/to-tickets-zh` 前不要 compact 或 clear），让追问、spec 与 Ticket 使用同一份思路。每项 `/implement-zh` 从对应 Ticket 开启新上下文。复盘当前会话应在清空前运行 `/retro-zh`；清空后则向它提供原会话日志。

边界是[高效上下文区](https://www.aihero.dev/ai-coding-dictionary/smart-zone)：模型仍能敏锐推理的窗口（当前先进模型约 150k Token）。若在 `/to-tickets-zh` 前接近边界，不要勉强继续；在最近的阶段边界 `/compact` 后继续（见“阶段边界”）。

## 入口支线

从某种初始状况生成工作，并汇入主流程。

- **Bug 和请求堆积** → **`/triage-zh`**。它推动 Issue 经过 triage 角色，生成供 Agent 领取的 Issue，之后由 **`/implement-zh`** 处理。

  Triage 只处理**不是你自己创建**的原始 Issue：Bug 报告、外部功能请求等。`/to-tickets-zh` 生成的 Ticket 已可供 Agent 领取，**无需再 triage**。

- **出现故障** → **`/diagnosing-bugs-zh`**。用于一眼无法定位的 bug、偶发失败、在两个已知正常状态之间出现的回归。它先建立**紧凑反馈循环**（一个能对*这个* bug 报红灯的命令），再做假设，并以回归测试修复。修复后在同一会话用 **`/retro-zh`** 追问如何预防；若真正的问题是缺少适当接缝，则交给 **`/improve-codebase-architecture-zh`**。

- **庞大而模糊的工作：绿地项目或大功能，超过单次会话容量** → **`/wayfinder-zh`**，这里认知负担最高的流程。当通往目的地的路线还看不见时，它在 Issue tracker 上绘制**决策 Ticket**的共享地图，一次解决一项，产出**决策而非交付物**，直到路线清楚。`/grill-with-docs-zh` 处理能放入一个会话的想法；wayfinder 更慢、更复杂，只用于真正太大的工作，绝不用于范围清晰的功能。

  地图厘清后，**交接而非直接构建**：回到主流程的 **`/to-spec-zh`**，把链接中的决策汇总成可构建计划，再按常规执行 `/to-tickets-zh` 和 `/implement-zh`。直接从地图跳到 `/implement-zh` 会遗漏链接里的细节；只有工作确实变得足够小时才能跳过 spec。

## 代码库健康

不是功能开发，而是维护。

- **`/improve-codebase-architecture-zh`** 在空闲时调查使代码库更适合 Agent 工作的机会，发现**加深模块的机会**。选择一个候选会*产生一个想法*，可带入主流程的 `/grill-with-docs-zh`。前者做调查，后面的 **`/codebase-design-zh`** 提供设计候选时需要的工具和词汇。

## 底层词汇

两个可由模型调用的参考 Skill，各自是其领域词汇的单一事实来源。当问题在于**措辞**而非流程时，可直接使用；也可以由上层 Skill 按需调用。

- **`/domain-modeling-zh`**：打磨项目*领域*语言，质疑模糊或多义术语（例如 account 同时指三种事物），用 ADR 记录难以逆转的决定。这是 `/grill-with-docs-zh` 保持 `GLOSSARY.md` 为清晰术语表的主动工作。
- **`/codebase-design-zh`**：用于设计模块*结构*的深模块词汇（模块、接口、深度、接缝、适配器、杠杆、局部性）：在干净接缝上的小接口背后隐藏大量行为。`/tdd-zh` 与 `/improve-codebase-architecture-zh` 都使用这些词汇。

## 阶段边界

**阶段**是会话中的一段工作：追问、实现、QA。两阶段的**边界**有五个选项，这是本地图中最难判断的选择：

- **继续**：留在原处，没有成本或损失。
- **`/clear`**：当前上下文对下一步无关时清空窗口。
- **`/handoff-zh`**：写可携带的 Markdown 文件。仅用于**新的 Agent 运行环境**、**新目录**、交给**同事**，或**阶段中途**分叉旁支任务；收益是可携带性。
- **Subagent**：给独立上下文一个聚焦任务，并取回报告。
- **`/compact`**：压缩当前上下文，以摘要开启新会话；这是决策树底部的**默认选项**，不是第一个选择。

阅读 [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) 了解有序决策树：五个问题、各分支依据，以及为何第一手资料的损失使得**继续**必须先被排除。只在阶段**边界**决定；中途继续或把剩余工作拆给 subagent。

## 独立工具

不在主流程上：

- **`/grill-me-zh`**：与 `/grill-with-docs-zh` 相同的持续追问，但**无状态**：不保存本地文件，也不生成 `GLOSSARY.md`。只在**不处于工作目录**时用它打磨计划、设计或文字；在工作目录中选择会留下书面记录的 `/grill-with-docs-zh`。
- **`/grilling-zh`**：访谈原语，逐轮推进前沿；Agent 负责查事实，用户负责作决策。`/grill-me-zh` 与 `/grill-with-docs-zh` 是两种具名入口，`/triage-zh`、`/wayfinder-zh` 和 `/improve-codebase-architecture-zh` 也会内部使用。仅当想不加包装地访谈时直接调用。
- **`/prototype-zh`**：用小型临时程序回答一个设计问题，例如状态模型是否合理、UI 应如何呈现。临时性约束代码写法，并非承诺删除产物：答案融入正式代码，原型则作为**第一手资料**留在从 main 分出的 `prototype/<name>` 分支，由实现 Issue 指向它。它是主流程步骤 2 的支线，也可用于其他无法纸上讨论清楚的问题。
- **`/research-zh`**：委派**后台 Agent**从**第一手来源**调查问题，在仓库留一份带引用的 Markdown 文件。它做研究时继续其他工作；成果送入 `/grill-with-docs-zh` 帮助思考，而不是替代思考。
- **`/to-questionnaire-zh`**：当关键知识不在你或代码库中，而在**其他人**手中时，起草问卷请其回答。这是 `/grill-me-zh` 的反向做法：访谈用户的**发送需求**（发给谁、需要什么），而不是代替接收者回答主题。反馈成为 `/grill-with-docs-zh` 或 `/to-spec-zh` 的材料。
- **`/wizard-zh`**：用于只有**人**能执行的步骤，例如配置基础设施、凭据或 CI secret，操作陌生第三方控制台，执行一次性迁移或切换。它生成交互式 bash 脚本，逐个打开 URL、捕获值、写入 `.env` 与 GitHub secrets，避免每次重新向 Agent 解释流程。模型可主动调用，但若 Agent 自己能完成，就应该自己完成；仅在人确实必须参与时使用。
- **`/wait-what-zh`**：上一条信息没听明白时用于纠正。对话中途、其他 Skill 内都可调用，让 Agent 补足背景，用简单语言和 `GLOSSARY.md` 统一词汇重新解释。它是事后补救；`/grill-with-docs-zh` 提前约定共同语言，是预防术语障碍的办法。
- **`/teach-zh`**：以当前目录为有状态工作区，跨多个会话学习概念。
- **`/writing-for-agents-zh`**：为 Agent 撰写 Skill、AGENTS.md 和被指针引用的文档时的参考。

## 前提

首次使用工程流程前运行 **`/setup-matt-pocock-skills-zh`**，配置其他 Skill 所依赖的 Issue tracker、triage 标签与领域文档布局。也支持自定义 Issue tracker。
