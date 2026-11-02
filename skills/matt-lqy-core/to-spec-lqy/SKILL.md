---
name: to-spec-lqy
disable-model-invocation: true
description: 把已有讨论整理为最小充分的 spec 并发布到项目 issue tracker；不重新访谈。
---

**最小充分**：综合已有讨论与代码事实，只写影响范围、取舍或验收的信息，不以篇幅或故事数量为目标。足够决策和验收就停止扩写；关键缺口先澄清，不重新访谈或补写未知事实。

issue tracker 和 triage 标签词汇表应该已经提供；如果没有，提示用户显式运行 `$setup-matt-pocock-skills-lqy`。

issue 标题、正文、评论和完成摘要默认使用中文。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。

## 流程

1. 按需查阅代码、测试、项目术语表（新项目默认 `GLOSSARY.md`）与相关 ADR；沿用领域词汇，不自动更名旧 CONTEXT。事实自己查，真实歧义才问用户。

2. 标出并向用户核实测试 seam：优先已有、最高层位置，尽量少（理想为 1）；新增时也放在最高合适处。

3. 按 `$mermaid-gate-lqy` 判断整体设计图 gate，覆盖跨 Ticket 的变化，不替代各 Ticket 的 gate。

4. 按模板写父 spec，标题为 `Spec: <短标题>`，不是可直接实现的 Ticket。无内容的节写“无”或“不适用”，不凑模板。

5. 在给出最终方案或发布前，按 `$codebase-design-lqy`、`$gitnexus` 和 `$simple` 审核并修订草稿，检查范围、假设、架构、依赖、契约与验证。最多启动一个只读 review agent，应用 `$simple`，只返回审查意见，不修改文件或实施。

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

用户的问题、当前影响与成功结果；区分事实和关键业务假设。

## Solution

用户视角的最小解决方案及关键取舍。

## User Stories

只列验收所需故事，合并重复目标，不枚举假想角色或未来功能。技术维护说明保护的行为，不虚构故事。

1. 作为 <参与者>，我希望 <能力>，以便 <收益>。

## Implementation Decisions

只列已确认的模块职责、接口、schema/API/交互与架构取舍。按需说明合理并行、共享契约和串行原因，不为并行拆模块；执行方式留待实施阶段选择。

不写具体文件路径或代码；仅当 prototype 的状态机、schema、type shape 等比文字更精确时，内联决策片段并注明来源，不放 demo。

## Testing Decisions

按需列出：

- 公开 seam 的外部行为、合同与失败路径；引用已有测试先例，不测试实现细节。
- 业务假设的判据、验证输入来源与代表性；区分合成/回放/真实样本，注明未覆盖部分。
- 验证配置与拟上线配置的差异、复用和切换条件；验证专用值不默认带上线。

技术验证通过不等于业务验收或可上线；未验证项须说明缺失证据及验收/上线限制。

## Mermaid Gate

记录上级 gate 结论：需要时嵌入或链接当前/目标 Mermaid 图，不需要则说明原因。

## Out of Scope

描述本 spec 范围外的事项。

## Further Notes

仅补充影响实施或验收的遗漏信息，否则写“无”。

</spec-template>

GitHub Ralph-ready spec 在模板内容之后追加唯一且最终的 `## Git`；不要把它插入模板中间。
