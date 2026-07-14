# ralph-plan-lqy localization

- Origin: 自建 skill（2026-07-03），用于 Open Ralph + GitHub issue backlog
- References: [open-ralph-wiggum](https://github.com/Th0rgal/open-ralph-wiggum) CLI 文档；Matt Pocock AFK Ralph 模式（[mattpocock/ai-engineer-workshop-2026-project](https://github.com/mattpocock/ai-engineer-workshop-2026-project) 的 `ralph/afk.sh` + `ralph/prompt.md`）
- 语言：SKILL.md 与 `templates/issue-backlog-prompt.md` 均为中文本地化版本；frontmatter description 保留中英混合以兼顾触发匹配
- 标签词汇与 `$triage-lqy` 对齐：`ready-for-agent` / `ready-for-human`
- 自带脚本：`scripts/check_ready_issue_unblocked.py`，作为只读 branch-aware eligibility gate，统一检查 `## Git`、当前 branch、base commit、`## Blocked by` 和跨 branch 依赖
- 共享模块：`scripts/git_contract.py`，严格解析正文最后一个 `## Git` section
- Producer adapter：`scripts/producer_adapter.py`，为 `to-spec-lqy`、`to-tickets-lqy` 和 `triage-lqy` 统一绑定显式 repository context、调用 `gh`/共享脚本并验证 typed JSON protocol
- Spec Git resolver：`scripts/resolve_spec_git.py`，显式输入优先，否则从 `--repo` 所在 attached worktree branch/remote upstream 解析父 spec contract，detached 或无 remote upstream 时回退 remote default，并在发布前拒绝 branch collision
- Workspace provision：`scripts/provision_workspace.py`，按 exact branch 创建或复用 worktree、默认严格检查 base drift，并只在用户显式选择旧 SHA 后允许 clean、ancestor-valid、upstream/remote 同步的 advanced target
- Worker lock：`scripts/run_locked_ralph.py`，在 Ralph 生命周期内持有每个 worktree 的 `.ralph/worker.lock`
- 端到端验证：`tests/test_branch_workflow_e2e.py` 使用临时 bare remote、两个真实 worktrees 和 `gh` stub 验证 branch-local selection、锁隔离、`.ralph/`/dirty state 隔离、commits/upstream pushes、completion 与契约错误
- Backlog policy：完全忽略 assignees，不使用 assignee claim；PR 不进入 Ralph issue backlog；完成后不自动清理 branch/worktree
- Policy: self-contained；上游 CLI flag 变化时同步更新参数说明
