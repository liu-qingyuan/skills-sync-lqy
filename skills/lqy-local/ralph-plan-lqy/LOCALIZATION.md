# ralph-plan-lqy localization

- Origin: 自建 skill（2026-07-03），用于 Open Ralph + GitHub issue backlog
- References: [open-ralph-wiggum](https://github.com/Th0rgal/open-ralph-wiggum) CLI 文档；Matt Pocock AFK Ralph 模式（[mattpocock/ai-engineer-workshop-2026-project](https://github.com/mattpocock/ai-engineer-workshop-2026-project) 的 `ralph/afk.sh` + `ralph/prompt.md`）
- 语言：SKILL.md 与 `templates/issue-backlog-prompt.md` 均为中文本地化版本；frontmatter description 保留中英混合以兼顾触发匹配
- 标签词汇与 `$triage-lqy` 对齐：`ready-for-agent` / `ready-for-human`
- 自带脚本：`scripts/check_ready_issue_unblocked.py`，作为只读 branch-aware eligibility gate，统一检查 `## Git`、当前 branch、base commit、`## Blocked by` 和跨 branch 依赖
- 共享模块：`scripts/git_contract.py`，严格解析正文最后一个 `## Git` section
- Workspace provision：`scripts/provision_workspace.py`，按 exact branch 创建或复用 worktree、检查 base drift/clean HEAD/path 并建立同名 upstream
- Worker lock：`scripts/run_locked_ralph.py`，在 Ralph 生命周期内持有每个 worktree 的 `.ralph/worker.lock`
- Policy: self-contained；上游 CLI flag 变化时同步更新参数说明
