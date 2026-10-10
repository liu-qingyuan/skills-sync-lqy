---
name: implement-lqy
description: "实现一个指定 Ticket 或已授权 Ralph worker 选中的任务，遵循公开 Seam 的 TDD、预算化双轴 review 和单上下文停止规则。"
---

实施用户指定或已获用户授权的 Ralph worker 选定的一个 Ticket。收到编号或 URL 时，先按 tracker 契约获取完整正文、标签和评论，并说明标题；引用有歧义就询问。父 spec 仍需拆分时，提示用户先运行 `$to-tickets-lqy` 或指定子 Ticket，不自动发布或启动循环。

实现前满足当前 Ticket 的 `$mermaid-gate-lqy`。Ticket 改变 Module、Interface、Seam 或知识归属时，先使用 `$codebase-design-lqy`；否则不要为了流程加载完整设计审查。尽可能在商定接缝处读取并执行 `tdd-lqy` 的 `SKILL.md`；沿用 spec 中已确认的 Seam，只有真实歧义才询问。实现中运行聚焦测试，完成后运行相关完整测试套件。

## Feature 当前事实

若有 `.feature-docs/run`，读取并执行 `docs/agents/feature-docs.md`，只维护本任务相关能力；不替代测试或双轴 review。未启用则保持原流程，提示显式 setup。

## Review

完成验证后，按 skills 列表中的实际路径读取并完整执行 `$code-review-lqy` 的 `SKILL.md`；不假设存在 `Skill` tool。fixed point、双轴 reviewer、blocking 标准、focused closure、调用预算和停止规则均以该 skill 为唯一来源；review 与门禁通过后继续完成 Ticket。

## Oversized Stop

若实现已超出一个新上下文，或 broad review 暴露大量跨模块 findings，停止扩建。提交一个行为完整、测试通过的增量，记录剩余拆分并保持 issue open；不要增加 harness、抽象或 reviewer 来强行收敛。

遵守 `docs/agents/issue-tracker.md` 的语言约定。多行 `gh issue comment` 使用 heredoc 或 `--body-file`。

- 完成：启用记录门禁的项目先通过 `check --staged`，commit 后通过 `check --ref HEAD`；然后 push，评论 hash、验证结果和摘要，关闭 issue。
- Oversized 或有完整增量：同步当前能力与剩余；通过已启用的记录门禁后 commit/push，评论已完成内容和拆分建议，不关闭 issue。
- 没有 upstream：停止并要求用户确认，不要创建远程分支。
