---
name: code-review-lqy
description: 从固定点（commit、branch、tag 或 merge-base）开始沿 Standards 和 Spec 两轴审查变更；Broad Review 后在固定范围内运行 $clean，并对修复与清理做 Focused Closure。用于审查 branch、PR、WIP 或“review since X”。
---

# Code Review

只审查当前 Ticket 相对 fixed point 的变更：

- **Standards**：直接违反仓库规则或引入可观察回归。
- **Spec**：遗漏、错误实现或超出来源 issue / spec。

不得增加第三审查轴或主动加载通用设计 smell checklist；架构问题只有在直接违反仓库 Standards 或来源 Spec，并有具体影响证据时才作为 finding。`$clean` 是 Broad Review 后的受限变换，不是新的审查轴，其发现不得追加为 reviewer findings。只读约束仅适用于 reviewer agents；主流程可以按步骤 3 和 4 修改工作区。

默认使用中文。issue tracker 配置见 `docs/agents/issue-tracker.md`；缺失时运行 `$setup-matt-pocock-skills-lqy`。

## 流程

1. **固定范围**：没有 fixed point 就询问；引用无效或 diff 为空就停止。记录 `git status --short`、`git diff <fixed-point>`、`git diff --name-only <fixed-point>` 和 `git log <fixed-point>..HEAD --oneline`，并取得来源 spec。没有 spec 时只跑 Standards。
2. **Broad Review**：有 spec 时把审查分成 Standards 和 Spec 两部分，每部分由一个独立的只读 `general-purpose` agent 检查；两个 agents 在一条消息中并行启动并分别报告。无 spec 时只启动 Standards agent。每个 `max_turns: 6`，最多 250 字。记录 agent IDs。每个 reviewer 必须明确报告其轴的实现方向为 `accepted` 或 `wrong`；缺少明确结论不得进入 Clean gate。reviewer 禁止使用 GitNexus、index/graph 查询或 `Agent`。
3. **判定与修复**：只有带明确 contract、可观察失败、安全、数据损坏或 cleanup 证据的 `Critical` / `High` findings 阻塞。修复必须是满足原验收的最小改动；禁止 optional hardening、新场景、新抽象或扩大 Ticket。`Medium`、`Low` 和 heuristic 只写简短 follow-up，不继续调查。实现方向错误、修复需要跨入新上下文或结果为 `Oversized` 时停止，不运行 `$clean`。
4. **Clean gate**：没有 blocking findings，或 blocking fixes 已完成且聚焦验证通过后，重新记录 `git diff --name-only <fixed-point>`，将此时的 changed-files 列表冻结为 file list scope，并运行一次 `$clean`。`$clean` 不得新增范围；如果清理必须改变行为、公开合同、依赖或范围外文件，停止并向用户确认。清理后重新运行相关验证，并记录 `$clean` 是否产生变更及其报告。
5. **Focused Closure**：存在 blocking fixes 或 `$clean` 产生变更时，并行 resume 原来的 agents；每个 `max_turns: 3`。只判断原 findings 为 `closed` / `open`，并检查 Broad Review 后的修复与清理是否在原 Standards/Spec 轴上直接引入新的 `Critical` / `High` 问题；不得重扫未变的原始 diff，也不得新增 `Medium`、`Low` 或 heuristic findings。没有 blocking fixes 且 `$clean` 未产生变更时跳过 closure。
6. **停止**：总 review Agent 调用上限为 4，失败调用也计入。resume 失败不得启动替代 reviewer；所有 reviewers 禁止调用 `Agent`。closure 后禁止第三轮或“最终 review”。

Broad Review 分别输出 `## Standards` 和 `## Spec`；Closure 使用对应的 `Closure` 标题。若实现已超出一个新上下文或横跨多个不相关模块，输出 `Oversized`，不要建议继续扩建。
