---
name: implement-lqy
description: 根据 spec 或一组 issues 实现一项工作。
---

实施用户指定的一个 Ticket。父 spec 仍需拆分时，先使用 `$to-tickets-lqy` 或要求用户指定子 Ticket。

实现前满足当前 Ticket 的 `$mermaid-gate-lqy`；尽可能在商定接缝处使用 `$tdd-lqy`。实现中运行聚焦测试，完成后运行相关完整测试套件。

## Review

按 `$code-review-lqy` 执行一次 broad 双轴 review（2 agents）；reviewer 不使用 GitNexus。只修复有证据的 `Critical` / `High` findings，而且必须使用满足原验收的最小改动；`Medium`、`Low`、heuristic 和 optional hardening 写成 follow-up。

有 blocking findings 时，最多进行一次 focused closure，只 resume 原来的 2 agents。每个 Ticket 最多 4 次 review Agent 调用，失败也计入；closure 后禁止第三轮 reviewer 或重扫完整 diff。blocking findings 关闭且门禁通过后立即 commit/push/close。

## Oversized Stop

若实现已超出一个新上下文，或 broad review 暴露大量跨模块 findings，停止扩建。提交一个行为完整、测试通过的增量，记录剩余拆分并保持 issue open；不要增加 harness、抽象或 reviewer 来强行收敛。

遵守 `docs/agents/issue-tracker.md` 的语言约定。多行 `gh issue comment` 使用 heredoc 或 `--body-file`。

- 完成：commit/push，评论 hash、验证结果和摘要，关闭 issue。
- Oversized 或有完整增量：commit/push，评论已完成内容和拆分建议，不关闭 issue。
- 没有 upstream：停止并要求用户确认，不要创建远程分支。
