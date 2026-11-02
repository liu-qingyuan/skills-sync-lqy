---
name: to-spec-lqy
disable-model-invocation: true
description: 把已有讨论整理为最小充分的 spec 并发布到项目 issue tracker；不重新访谈。
---

该 skill 会基于当前对话上下文和对代码库的理解产出一份 spec。不要重新访谈用户，只综合你已经知道的信息。

以**最小充分**为准：只写会影响范围、取舍或验收的信息，不以篇幅或故事数量为目标。目标、关键业务假设、必要契约与验证边界清楚后停止扩写；未确认的事实保留为未知，不补写成承诺。

issue tracker 和 triage 标签词汇表应该已经提供；如果没有，提示用户显式运行 `$setup-matt-pocock-skills-lqy`。

issue 标题、正文、评论和完成摘要默认使用中文。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。

## 流程

1. 如果还没有探索仓库，先探索当前代码、测试和项目明确指定的术语表（新项目默认 `GLOSSARY.md`）；不自动更名旧 CONTEXT。spec 使用该表词汇并尊重相关 ADR。事实自己查，只有真实歧义才询问用户。

2. 画出这个功能将在哪些 seam 上测试。优先使用已有 seam，而不是创建新 seam。尽可能使用最高层 seam。如果确实需要新 seam，把它提议在你能找到的最高位置。代码库中的 seam 越少越好；理想数量是 1。

向用户核实这些 seam 是否符合他们预期。

3. 按 `$mermaid-gate-lqy` 判断整份 spec 的上级设计图 gate。这里记录跨 Ticket 的整体架构、接口、流程或状态变化；不替代每个 Ticket 自己的 Mermaid Gate。

4. 使用下面的模板编写 spec。各节只写当前相关内容，确无内容写“无”或“不适用”，不为填满模板扩写。issue 标题必须使用 `Spec: <短标题>`，表示这是父级 spec，不是可直接实现的 Ticket。

5. 在给出最终方案或发布前，按 `$codebase-design-lqy`、`$gitnexus` 和 `$simple` 审核完整 spec 草稿。终审最多启动一个只读 review agent，合并检查范围、业务假设与验证证据、架构、依赖、contract 和测试；它必须应用 `$simple`，并可自行使用 `$gitnexus`，只返回审查意见，不修改文件或实施。根据结果修订草稿后再继续。

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

   linked worktree 自动共享 Git config 和 ignore 规则。provisioner 还会把源 worktree 中 ignored/untracked 的 `.codex/config.toml` regular file 复制到目标相同路径；tracked 配置仍由 Git checkout。它不复制其他 ignored 内容，也不覆盖不同配置或跟随 symlink。

   后续从 `workspace.path` 启动新的 Codex 会话并信任该 worktree，项目 MCP 才会加载；`xcrun mcpbridge` 会在新会话中重新连接当前 Xcode。不要复制 Codex trust、Xcode PID 或 session ID。

8. LQY 保持 GitHub Issues-only，不静默换成 PR 或本地 Markdown tracker；明确不进入 Ralph backlog 的 GitHub 记录不强制添加 `## Git`，也不调用上述 publisher。

9. 完成后只提醒用户下一步调用 `$to-tickets-lqy`，然后停止；不自动拆分 Tickets 或实施。

<spec-template>

## Problem Statement

从用户视角说明问题、当前影响与成功结果；区分已有事实和会改变方案的关键业务假设。

## Solution

从用户视角描述当前范围内的最小解决方案，以及它依赖哪些关键业务假设；会改变范围、取舍或验收的未知先澄清。

## User Stories

只列支撑当前目标和验收的必要故事，合并同一参与者、目标与收益的重复表述：

1. 作为 <参与者>，我希望 <能力>，以便 <收益>。

不枚举假想角色或未来功能。纯技术维护可说明保护的已有行为，不虚构终端用户故事。

## Implementation Decisions

只列影响当前范围的已确认决策，按实际变化选写，不逐项补全：

- 模块职责、接口及必要的 schema、API contract 或交互变化
- 合理并行的模块职责、必须先明确的共享契约及串行原因；不为并行硬拆模块，执行方式留到实施阶段由用户选择
- 关键技术澄清与架构取舍

不要包含具体文件路径或代码片段。它们很快可能过时。

例外：如果 prototype 产出的代码片段比散文更精确地编码了决策（状态机、reducer、schema、type shape），可以把它内联到相关决策中，并简短说明它来自 prototype。只保留决策密集的部分，不要放工作 demo，只放重要部分。

## Testing Decisions

只列本次相关的验证决策，不铺开测试用例清单：

- 通过哪些公开 seam 验证外部行为、必要合同与失败路径；按需引用已有测试先例，不测试实现细节
- 关键业务假设的验证方式与可观察判据
- 验证输入的来源、代表性及未覆盖情形；区分合成、回放和真实业务样本
- 验证配置与拟上线配置的关键差异、可复用项及必要切换条件；验证专用样本、限额或开关不能默认为上线默认值

技术验证通过不等于业务验收或可上线。代表性或拟上线配置未验证时，明确写出“未验证”、还缺什么证据，以及它对当前验收结论或上线的限制；技术切片可只承诺已验证条件下的行为。

## Mermaid Gate

按 `$mermaid-gate-lqy` 记录整份 spec 的上级判断。需要图时放入或链接当前/目标 Mermaid 图；不需要图时说明原因。这里覆盖整体设计，不替代每个 Ticket 的 Mermaid Gate。

## Out of Scope

描述本 spec 范围外的事项。

## Further Notes

只补充会影响实施或验收、且前文未表达的信息；否则写“无”。

</spec-template>

GitHub Ralph-ready spec 在模板内容之后追加唯一且最终的 `## Git`；不要把它插入模板中间。
