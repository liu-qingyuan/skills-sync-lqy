---
name: implement-lqy
description: 根据 spec 或一组 issues 实现一项工作。
---

实施用户指定的一个 Ticket。父 spec 仍需拆分时，先使用 `$to-tickets-lqy` 或要求用户指定子 Ticket。

实现前满足当前 Ticket 的 `$mermaid-gate-lqy`。Ticket 改变 Module、Interface、Seam 或知识归属时，先使用 `$codebase-design-lqy`；否则不要为了流程加载完整设计审查。尽可能在商定接缝处使用 `$tdd-lqy`。实现中运行聚焦测试，完成后运行相关完整测试套件。

## Review

完成验证后，读取并完整执行 `$code-review-lqy`。fixed point、双轴 reviewer、blocking 标准、focused closure、调用预算和停止规则均以该 skill 为唯一来源；review 与门禁通过后继续完成 Ticket。

## Oversized Stop

若实现已超出一个新上下文，或 broad review 暴露大量跨模块 findings，停止扩建。提交一个行为完整、测试通过的增量，记录剩余拆分并保持 issue open；不要增加 harness、抽象或 reviewer 来强行收敛。

遵守 `docs/agents/issue-tracker.md` 的语言约定。多行 `gh issue comment` 使用 heredoc 或 `--body-file`。

- 完成：commit/push，评论 hash、验证结果和摘要，关闭 issue。
- Oversized 或有完整增量：commit/push，评论已完成内容和拆分建议，不关闭 issue。
- 没有 upstream：停止并要求用户确认，不要创建远程分支。
