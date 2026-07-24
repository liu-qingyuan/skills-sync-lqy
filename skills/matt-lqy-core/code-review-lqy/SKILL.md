---
name: code-review-lqy
description: 从固定点（commit、branch、tag 或 merge-base）开始沿 Standards 和 Spec 两轴审查变更。用于审查 branch、PR、WIP 或“review since X”。
---

# Code Review

只审查当前 Ticket 相对 fixed point 的变更：

- **Standards**：直接违反仓库规则或引入可观察回归。
- **Spec**：遗漏、错误实现或超出来源 issue / spec。

默认使用中文。issue tracker 配置见 `docs/agents/issue-tracker.md`；缺失时运行 `$setup-matt-pocock-skills-lqy`。

## 流程

1. **固定范围**：没有 fixed point 就询问；引用无效或 diff 为空就停止。记录 `git status --short`、`git diff <fixed-point>` 和 `git log <fixed-point>..HEAD --oneline`，并取得来源 spec。没有 spec 时只跑 Standards。
2. **Broad review**：有 spec 时把审查分成 Standards 和 Spec 两部分，每部分由一个独立的只读 `general-purpose` agent 检查；两个 agents 在一条消息中并行启动并分别报告。无 spec 时只启动 Standards agent。每个 `max_turns: 6`，最多 250 字。记录 agent IDs。reviewer 禁止使用 GitNexus、index/graph 查询或 `Agent`。
3. **修复**：只有带明确 contract、可观察失败、安全、数据损坏或 cleanup 证据的 `Critical` / `High` findings 阻塞。修复必须是满足原验收的最小改动；禁止 optional hardening、新场景、新抽象或扩大 Ticket。`Medium`、`Low` 和 heuristic 只写简短 follow-up，不继续调查。
4. **Focused closure**：仅在有 blocking findings 时，并行 resume 原来的 agents；每个 `max_turns: 3`。只判断原 findings 为 `closed` / `open`，不得重扫完整 diff；只有修复直接引入的 `Critical` / `High` 问题可以继续阻塞。
5. **停止**：总 review Agent 调用上限为 4，失败调用也计入。resume 失败不得启动替代 reviewer；所有 reviewers 禁止调用 `Agent`。closure 后禁止第三轮或“最终 review”。

Broad review 分别输出 `## Standards` 和 `## Spec`；closure 使用对应的 `Closure` 标题。若实现已超出一个新上下文或横跨多个不相关模块，输出 `Oversized`，不要建议继续扩建。
