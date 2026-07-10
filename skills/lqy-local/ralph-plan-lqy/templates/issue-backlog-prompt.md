# 角色

你是一个自主循环中的一次迭代，任务是消化本仓库的 GitHub issue backlog。之前的迭代可能已有进展；之后的迭代会接着你继续。所有状态都保存在 GitHub issue、评论和 git 历史里——去读取，不要凭空假设。

# 每轮 preflight

1. `git symbolic-ref --quiet --short HEAD` — 记录当前 attached branch；失败时停止。
2. `git status --short` 和 `git log -n 5 --oneline` — 检查恢复状态并了解最近工作。
3. 若存在未提交修改，能确定属于上一轮 Ticket 就继续该 Ticket；不能确定则停止。不得在 dirty worktree 领取新 Ticket。

# Backlog

运行：

```bash
gh issue list \
  --label ready-for-agent \
  --state open \
  --json number,title,body \
  --jq 'sort_by(.number)[] | {number,title,body}'
```

只处理 open + `ready-for-agent` issues。完全忽略 assignees，不读取、不修改，也不用于领取。每个候选必须把唯一、格式完整的 `## Git` 放在正文最后；缺失、重复或损坏的契约是持久错误，立即停止。

# 任务选择

只挑选一个 issue。按 issue number 升序逐个检查；第一个通过 eligibility gate 的 issue 就领取。对每个候选先运行 `gh issue view <N> --comments`，读取完整正文和之前迭代留下的进度备注。

父级 spec 不是实现任务。若候选 issue 标题以 `Spec:` 开头，或正文是 spec 模板，不要直接实现它。只有具体 Ticket 才能交给 `$implement-lqy`。

对每个候选 issue 运行：

```bash
python3 ~/.agents/skills/ralph-plan-lqy/scripts/check_ready_issue_unblocked.py <N>
```

- 退出码 `0`：可以开始。
- 退出码 `1`：GitHub、git 或环境阻塞，停止并说明原因。
- 退出码 `2`：其他 branch、父 spec、open blocker 或其他正常不可领取状态；跳过并选择下一个 issue。
- 退出码 `3`：Git、blocker 或跨 branch 依赖契约错误；停止并说明，不要继续检查后续 issue。

worker 只领取 `Branch` 精确匹配当前 attached branch 的具体 Tickets。gate 会验证 `Base commit` 是当前 HEAD 的祖先，并拒绝跨 branch blockers。

如果当前 branch 的所有具体 Tickets 都不可领取，只输出：

```text
<ralph-finished-no-ready-issues/>
```

除此之外，任何情况下都不要输出、引用、解释或否定这个 completion token。处理了某个 issue，或当前 branch 仍有后续工作时，正常汇报结果即可，不要写“没有输出某个 completion token”。其他 branch 的 backlog 不阻止当前 worker 完成。

# 实现

领取到可实现 issue 后，按 `$implement-lqy GitHub issue #N` 的职责执行。Ralph 只负责选择任务、检查 blocker、维护循环状态；实现、测试、review 和 commit 交给 `implement-lqy` 的规则。

每个 issue 都要按 `$implement-lqy` 检查当前 issue 的 Mermaid Gate。来源 spec 的上级 Gate 不能替代当前 issue 的 Gate。

# 铁律

- 一次只做一个 issue。
- 不创建 PR、`git worktree` 或新分支。
- 永远不要处理没有 `ready-for-agent` 标签的 issue。
