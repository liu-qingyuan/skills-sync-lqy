---
name: implement-spec-zh
description: 根据 /to-spec-zh 和 /to-tickets-zh 的产物实现代码。
disable-model-invocation: true
---

你已获得一份 spec。它应当关联一组描述如何实现该 spec 的 Ticket。

Issue tracker 应已配置；否则请告诉用户运行 `/setup-matt-pocock-skills-zh`。

目标是在同一个**集成分支**完整实现 spec，并按照 Issue tracker 的流程关闭每个 Ticket。

Ticket 不是步骤列表，而是带有阻塞关系的**任务图**。因此始终存在一批可领取的 Ticket，称为**前沿**（frontier）。

与 subagent 之间应保持简洁沟通。主要使用指向 spec、Ticket、研究笔记和先前 commit 的**上下文指针**，不要重复指针所指的信息。

条件允许时，让**实现 subagent**在后台运行，以提高并行度。

## 步骤

1. 阅读 spec 和 Ticket，理解任务图。

2. （可选）使用**探索 subagent**完成 Ticket 所需的代码库或外部文档探索。确保它能保存文件：将 Markdown 笔记保存在仓库外、所有后续 subagent 均可访问的目录中，以便**实现 subagent**专注于实现。

3. 创建集成分支。如果 Issue tracker 通过 PR 关闭工作，或用户要求 PR，那么在步骤 5 第一次合并后创建草稿 PR（没有领先于 main 的 commit 时无法创建），并将其标记为关闭 spec 和 Ticket。

4. 让**实现 subagent**分别在独立 worktree 和独立分支实现每个 Ticket。每个实现 subagent：
   - 开始前确认 worktree 基于集成分支，否则重置到集成分支；
   - 调用 Skill 工具并指定 `tdd-zh` 来实现 Ticket；
   - 报告完成前，将集成分支的最新提交合并到自己的分支。

5. 每有一个**实现 subagent**完成，就使用**合并 subagent**将其成果合并进集成分支。

6. 若可用 Ticket 的**前沿**改变，就启动更多**实现 subagent**处理新 Ticket，最大化并行度。

7. 全部 Ticket 完成后，在集成分支调用 Skill 工具并指定 `code-review-zh`。用一个**实现 subagent**修复所有 review 发现的问题。

8. 若存在草稿 PR，将其标记为可供 review；否则按 Issue tracker 的流程关闭各 Ticket，并报告集成分支。

9. 清理所有**实现 subagent**的 worktree。
