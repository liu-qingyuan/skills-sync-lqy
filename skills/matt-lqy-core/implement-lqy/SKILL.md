---
name: implement-lqy
description: 根据 PRD 或一组 issues 实现一项工作。
---

实施用户指定的 PRD 或 issue 中描述的工作。

PRD 可以作为实现规格和验收上下文；如果用户只传入一个 PRD 父 issue，且它明显还需要拆成多个独立任务，不要直接把整个 PRD 当作一个实现任务。先使用 /to-issues-lqy 拆分，或要求用户指定要实现的子 issue。

## Mermaid 设计图 Gate

开始实现前，先判断当前 issue 是否需要 Mermaid 图。

- 需要图：会改变架构边界、公共接口、adapter contract、状态机、主要调用流程或跨模块依赖。
- 不需要图：纯文档、调研记录、文案或无接口变化的小修。

如果需要图，先使用 /mermaid-visualizer，并把图放到 issue 正文、issue comment 或 PR 描述中，再开始实现。必须提供 4 张图，顺序如下：

- 架构/调用关系图：模块边界、接口、adapter、跨模块依赖和“谁调用谁”。
- 时序图：一次请求、一次工具调用或一次业务流程的时间顺序。
- 状态图：状态机、生命周期、任务状态或可回退流程。
- 类图：局部类/接口结构；范围只覆盖本 issue 涉及的模块，避免画全项目类图。

如果不需要图，在 issue comment 或 PR 描述中说明原因，再继续。

实现中如果接口、状态机、依赖方向或调用流程与图不一致，先更新图，再继续实现。完成前确认保留的图反映最终实现。

尽可能在预先商定的接缝处使用 /tdd-lqy。

定期运行类型检查，定期运行单个测试文件，最后运行一次完整的测试套件。

完成后，使用 /review-lqy 来检查工作。

写 issue 评论、完成摘要或关闭说明前，遵守 `docs/agents/issue-tracker.md` 的语言约定；没有约定时默认使用中文。

多行 `gh issue comment` 使用 heredoc 或 `--body-file`，避免 shell 展开 `$(...)`。

收尾：

- 完成：提交到当前分支并 push 到当前分支的 upstream；评论 commit hash、push 状态、验证结果和摘要；关闭 issue。
- 未完成但有完整增量：先提交并 push 到当前分支的 upstream；评论已完成、push 状态、剩余工作和下一步。
- 如果当前分支没有 upstream，先停止并说明需要用户确认远程分支；不要猜测或自动创建远程分支。
