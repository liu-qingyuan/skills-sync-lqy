---
name: code-review-lqy
description: 从固定点（commit、branch、tag 或 merge-base）开始沿两个轴审查变更：Standards 和 Spec。用于用户想审查 branch、PR、WIP 变更或“review since X”时。
---

对 `HEAD` 和用户提供的固定点之间的 diff 做两轴审查：

- **Standards** — 代码是否符合此仓库记录的 coding standards？
- **Spec** — 代码是否忠实实现了来源 issue / PRD / spec？

两个轴都作为**并行 sub-agent**运行，避免彼此污染上下文；然后此 skill 聚合它们的发现。

issue tracker 应该已经提供；如果缺少 `docs/agents/issue-tracker.md`，请运行 `$setup-matt-pocock-skills-lqy`。

issue、PR、comment 和完成摘要默认使用中文。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。

## 流程

### 1. 固定 fixed point

用户提供的内容就是 fixed point：commit SHA、branch 名称、tag、`main`、`HEAD~5` 等。如果用户没有指定，就询问。

只捕获一次 diff 命令：`git diff <fixed-point>...HEAD`（三点，所以比较对象是 merge-base）。同时记录 `git log <fixed-point>..HEAD --oneline` 的提交列表。

继续之前，确认 fixed point 能解析（`git rev-parse <fixed-point>`），并且 diff 非空。错误引用或空 diff 应该在这里失败，而不是在两个并行 sub-agent 里失败。

### 2. 识别 spec 来源

按顺序查找来源 spec：

1. commit message 中的 issue 引用（`#123`、`Closes #45`、GitLab `!67` 等）— 通过 `docs/agents/issue-tracker.md` 中的工作流获取。
2. 用户作为参数传入的路径。
3. `docs/`、`specs/` 或 `.scratch/` 下与 branch 名称或 feature 匹配的 PRD/spec 文件。
4. 如果什么都没找到，询问用户 spec 在哪里。如果用户说没有，**Spec** sub-agent 跳过并报告 `no spec available`。

### 3. 识别 standards 来源

仓库中任何记录代码应该如何编写的内容，例如 `CODING_STANDARDS.md` 或 `CONTRIBUTING.md`。

除了仓库记录的内容，Standards 轴始终携带下面的 **smell baseline**：一组固定的 Fowler code smells（_Refactoring_, ch.3），即使仓库没有任何文档也适用。两条规则约束它：

- **仓库规则优先。** 已记录的仓库 standard 总是胜出；如果仓库明确认可了 baseline 会标记的写法，就抑制该 smell。
- **始终是 judgment call。** 每个 smell 都是带标签的 heuristic（如 `possible Feature Envy`），不是硬性违规；和此处任何 standard 一样，跳过工具已经强制执行的内容。

每个 smell 按“它是什么 → 如何修复”阅读；把它们匹配到 diff：

- **Mysterious Name** — 函数、变量或类型名称不能说明它做什么或持有什么。→ 重命名；如果找不到诚实的名字，说明设计含混。
- **Duplicated Code** — 同样的逻辑形状出现在多个 hunk 或文件中。→ 提取共享形状，由两处调用。
- **Feature Envy** — 方法读取另一个对象的数据多于读取自身数据。→ 把方法移动到它羡慕的数据上。
- **Data Clumps** — 同一组字段或参数反复一起出现，像一个类型在等待出生。→ 打包成一个类型并传递它。
- **Primitive Obsession** — primitive 或 string 代替了值得拥有自身类型的领域概念。→ 给该概念一个小类型。
- **Repeated Switches** — 对同一类型的相同 `switch`/`if` cascade 在变更中重复出现。→ 用 polymorphism 替换，或让两个位置共享一张 map。
- **Shotgun Surgery** — 一个逻辑变化迫使 diff 在许多文件中分散编辑。→ 把一起变化的东西收进一个模块。
- **Divergent Change** — 一个文件或模块因为多个无关原因被编辑。→ 拆分，让每个模块只因一种原因变化。
- **Speculative Generality** — 添加了 spec 不需要的 abstraction、参数或 hook。→ 删除它；inline 回去，直到有真实需要。
- **Message Chains** — 长 `a.b().c().d()` 导航，caller 不该依赖这条路。→ 在第一个对象上用一个方法隐藏这段穿行。
- **Middle Man** — class 或 function 主要只是继续 delegate。→ 切掉它，直接调用真实目标。
- **Refused Bequest** — subclass 或 implementer 忽略或覆盖了继承来的大部分东西。→ 去掉 inheritance，改用 composition。

### 4. 并行生成两个 sub-agent

启动两个 sub-agent：一个检查 Standards，一个检查 Spec。若当前环境没有 sub-agent，就分开执行两个检查，并保持两个轴的发现互不合并。

**Standards sub-agent prompt** 包括：

- 完整 diff 命令和提交列表。
- 第 3 步找到的 standards-source 文件列表，**加上第 3 步的 smell baseline 全文**；sub-agent 没有其他方式访问它。
- Brief：`用中文报告。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。Per file/hunk where relevant: (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words.`

**Spec sub-agent prompt** 包括：

- diff 命令和提交列表。
- spec 的路径或获取到的内容。
- Brief：`用中文报告。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words.`

如果缺少 spec，跳过 Spec sub-agent，并在最终报告中说明。

### 5. 聚合

在 `## Standards` 和 `## Spec` 标题下呈现两份报告，可以逐字或轻微清理。**不要**合并或重新排序 findings；这两个轴是故意分开的（见 _Why two axes_）。

用一行 summary 结尾：每个轴的 findings 总数，以及每个轴内部最严重的问题（如有）。不要跨轴选出单个 winner；分离就是为了避免这种重排。

## Why two axes

一个变更可能通过一个轴，同时在另一个轴失败：

- 遵循每条 standard 但实现了错误内容的代码 → **Standards pass, Spec fail.**
- 完全按 issue 要求实现但破坏项目约定的代码 → **Spec pass, Standards fail.**

分开报告能防止一个轴遮蔽另一个轴。
