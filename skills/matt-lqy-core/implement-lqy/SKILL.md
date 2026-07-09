---
name: implement-lqy
description: 根据 spec 或一组 issues 实现一项工作。
---

实施用户指定的 spec 或 issue 中描述的工作。

spec 可以作为实现规格和验收上下文；如果用户只传入一个 spec 父 issue，且它明显还需要拆成多个独立任务，不要直接把整个 spec 当作一个实现任务。先使用 /to-tickets-lqy 拆分，或要求用户指定要实现的子 Ticket。

## Mermaid 设计图 Gate

开始实现前，先按 `$mermaid-gate-lqy` 完成当前 issue 的设计图 gate；需要图时补齐当前/目标 Mermaid 图，不需要图时说明原因。gate 满足后再写代码。

尽可能在预先商定的接缝处使用 /tdd-lqy。

定期运行类型检查，定期运行单个测试文件，最后运行一次完整的测试套件。

完成后，使用 /code-review-lqy 来检查工作。

写 issue 评论、完成摘要或关闭说明前，遵守 `docs/agents/issue-tracker.md` 的语言约定；没有约定时默认使用中文。

多行 `gh issue comment` 使用 heredoc 或 `--body-file`，避免 shell 展开 `$(...)`。

收尾：

- 完成：提交到当前分支并 push 到当前分支的 upstream；评论 commit hash、push 状态、验证结果和摘要；关闭 issue。
- 未完成但有完整增量：先提交并 push 到当前分支的 upstream；评论已完成、push 状态、剩余工作和下一步。
- 如果当前分支没有 upstream，先停止并说明需要用户确认远程分支；不要猜测或自动创建远程分支。
