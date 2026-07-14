---
name: to-spec-lqy
description: 把当前对话上下文整理成 spec 并发布到项目 issue tracker；不重新访谈，只综合已有讨论。
---

该 skill 会基于当前对话上下文和对代码库的理解产出一份 spec。不要重新访谈用户，只综合你已经知道的信息。

issue tracker 和 triage 标签词汇表应该已经提供；如果没有，请运行 `$setup-matt-pocock-skills-lqy`。

issue 标题、正文、评论和完成摘要默认使用中文。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。

## 流程

1. 如果还没有探索仓库，先探索仓库以理解代码库当前状态。在整份 spec 中使用项目的领域词汇表，并尊重你触及区域的 ADR。

2. 画出这个功能将在哪些 seam 上测试。优先使用已有 seam，而不是创建新 seam。尽可能使用最高层 seam。如果确实需要新 seam，把它提议在你能找到的最高位置。代码库中的 seam 越少越好；理想数量是 1。

向用户核实这些 seam 是否符合他们预期。

3. 按 `$mermaid-gate-lqy` 判断整份 spec 的上级设计图 gate。这里记录跨 Ticket 的整体架构、接口、流程或状态变化；不替代每个 Ticket 自己的 Mermaid Gate。

4. 使用下面的模板编写 spec。issue 标题必须使用 `Spec: <短标题>`，表示这是父级 spec，不是可直接实现的 Ticket。

5. 在给出最终方案或发布前，必须使用 `$codebase-design-lqy`、`$gitnexus` 和 `$simple` 审核并简化完整 spec 草稿；根据结果修订后再继续。

6. 如果目标是 GitHub 且该 spec 将产生 Ralph `ready-for-agent` Tickets，使用已安装的 `ralph-plan-lqy` 建立 Git 契约。缺少该依赖时停止，不要自行解析 Markdown 或猜测 Git 状态。

   先解析契约：

   ```bash
   python3 ~/.agents/skills/ralph-plan-lqy/scripts/resolve_spec_git.py \
     --repo <当前工作区的 exact-worktree-root> \
     [--branch <用户显式指定的目标 branch>] \
     [--base-branch <用户显式指定的 remote/base>]
   ```

   - 显式 `Branch` / `Base branch` 优先。
   - 解析前先用 `git rev-parse --show-toplevel` 和 `git symbolic-ref --quiet --short HEAD` 检查当前工作区；`--repo` 必须传当前工作区所在 worktree 的根目录，不得替换成 primary/main worktree。
   - 未显式指定 `Branch` 时，使用该 worktree 当前 attached branch。该 branch 有 remote upstream 时，未显式指定的 `Base branch` 使用 upstream；没有 remote upstream 时回退 remote default。detached worktree 才同时回退 remote default。
   - resolver 会 fetch base ref 并返回完整 `Base commit`；branch、worktree 和 upstream 由下一步 publisher 统一 provision。
   - 缺少可用 remote upstream/remote default、无 remote 或 branch collision 等无法形成确定契约的状态必须停止。

   把 resolver 返回值渲染为正文唯一的 `## Git`，并确保它是正文最后一个 section。父 spec 不写 `## Blocked by`：

   ```markdown
   ## Git

   - Branch: `<branch>`
   - Base branch: `<base_branch>`
   - Base commit: `<base_commit>`
   ```

7. GitHub Ralph-ready 父 spec 必须通过本 skill 的 publisher 发布。先把完整正文写入 body file，再运行：

   ```bash
   python3 ~/.agents/skills/to-spec-lqy/scripts/publish_spec_issue.py \
     --repo <repo-path> \
     --title "Spec: <短标题>" \
     --body-file <spec-body-file>
   ```

   publisher 的所有 `gh` 与共享脚本调用都绑定到 `--repo` 指定的目标仓库，不依赖调用者 cwd。它先检查模板和 Git 契约，再调用共享 provisioner 创建或复用 exact branch 的同级 worktree 与 upstream；provision 失败时不创建 issue。随后创建**不带** `ready-for-agent` 的 issue，回读并重复验证，最后才应用 `ready-for-agent`。成功输出包含 `workspace.path`，后续工作使用该 exact worktree。

   linked worktree 自动共享仓库 Git config、`.git/info/exclude` 和全局 excludes，tracked `.gitignore` 也随 checkout 生效。不要复制 ignored 文件内容；其中可能包含 secrets、缓存或构建产物。仓库另有明确 bootstrap 命令时，只在返回的 worktree 中运行该命令。

8. PR、本地 Markdown tracker 和明确不进入 Ralph backlog 的工作流保留各自原生发布方式，不强制添加 `## Git`，也不调用上述 publisher。

<spec-template>

## Problem Statement

从用户视角描述用户面对的问题。

## Solution

从用户视角描述问题的解决方案。

## User Stories

一份很长的编号用户故事列表。每条用户故事格式为：

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

这份用户故事列表应该非常广，覆盖该功能的所有方面。

## Implementation Decisions

已做出的实现决策列表。可以包括：

- 将构建或修改的模块
- 将修改的模块接口
- 开发者给出的技术澄清
- 架构决策
- schema 变更
- API contract
- 具体交互

不要包含具体文件路径或代码片段。它们很快可能过时。

例外：如果 prototype 产出的代码片段比散文更精确地编码了决策（状态机、reducer、schema、type shape），可以把它内联到相关决策中，并简短说明它来自 prototype。只保留决策密集的部分，不要放工作 demo，只放重要部分。

## Testing Decisions

已做出的测试决策列表。包括：

- 什么构成好的测试：只测试外部行为，不测试实现细节
- 哪些模块会被测试
- 测试先例：代码库中类似类型的测试

## Mermaid Gate

按 `$mermaid-gate-lqy` 记录整份 spec 的上级判断。需要图时放入或链接当前/目标 Mermaid 图；不需要图时说明原因。这里覆盖整体设计，不替代每个 Ticket 的 Mermaid Gate。

## Out of Scope

描述本 spec 范围外的事项。

## Further Notes

该功能的任何进一步说明。

</spec-template>

GitHub Ralph-ready spec 在模板内容之后追加唯一且最终的 `## Git`；不要把它插入模板中间。
