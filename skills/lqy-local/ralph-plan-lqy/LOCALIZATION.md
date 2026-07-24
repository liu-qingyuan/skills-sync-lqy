# ralph-plan-lqy localization

- Origin: 自建 skill（2026-07-03），用于 Open Ralph + GitHub issue backlog
- References: [open-ralph-wiggum](https://github.com/Th0rgal/open-ralph-wiggum) CLI 文档；Matt Pocock AFK Ralph 模式（[mattpocock/ai-engineer-workshop-2026-project](https://github.com/mattpocock/ai-engineer-workshop-2026-project) 的 `ralph/afk.sh` + `ralph/prompt.md`）
- 语言：SKILL.md 与 `templates/issue-backlog-prompt.md` 均为中文本地化版本；frontmatter description 保留中英混合以兼顾触发匹配
- 标签词汇与 `$triage-lqy` 对齐：`ready-for-agent` / `ready-for-human`
- 自带脚本：`scripts/check_ready_issue_unblocked.py`，作为只读 branch-aware eligibility gate，统一检查 `## Git`、当前 branch、base commit、`## Blocked by` 和跨 branch 依赖
- 共享模块：`scripts/git_contract.py`，严格解析正文最后一个 `## Git` section
- Producer adapter：`scripts/producer_adapter.py`，为 `to-spec-lqy`、`to-tickets-lqy` 和 `triage-lqy` 统一绑定显式 repository context、调用 `gh`/共享脚本并验证 typed JSON protocol
- Spec Git resolver：`scripts/resolve_spec_git.py`，显式输入优先，否则从 `--repo` 所在 attached worktree branch/remote upstream 解析父 spec contract，detached 或无 remote upstream 时回退 remote default，并在发布前拒绝 branch collision
- Workspace provision：`scripts/provision_workspace.py`，按 exact branch 创建或复用 worktree，继承共享 Git config/ignore rules，并只为 ignored/untracked `.codex/config.toml` 提供拒绝覆盖与 symlink 的 local-config allowlist
- Dirty recovery：producer agent 完成并提交可确认的改动后重试；意图不明才询问，禁止绕过 gate
- Worker lock：`scripts/run_locked_ralph.py`，在 Ralph 生命周期内持有每个 worktree 的 `.ralph/worker.lock`
- 端到端验证：`tests/test_branch_workflow_e2e.py` 使用临时 bare remote、两个真实 worktrees 和 `gh` stub 验证 branch-local selection、锁隔离、`.ralph/`/dirty state 隔离、commits/upstream pushes、completion 与契约错误
- Backlog policy：完全忽略 assignees，不使用 assignee claim；PR 不进入 Ralph issue backlog；完成后不自动清理 branch/worktree
- Agent policy：直接调用即用 Pi + `run_ralph` 执行，明确要求规划时除外；无工具时回退 locked Pi CLI；`PI_RUN_RALPH_WORKER=1` 禁止嵌套循环
- Review budget：每个 Ticket 最多一次双轴 broad review 和一次复用原 agents 的 focused closure，共 4 次 review Agent 调用；oversized work 提交绿色增量后退回 `needs-triage`
- Policy: self-contained；上游 CLI flag 变化时同步更新参数说明
