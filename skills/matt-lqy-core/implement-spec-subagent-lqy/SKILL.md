---
name: implement-spec-subagent-lqy
description: 显式使用子 agent 实施一个已批准 Spec；独立 worktrees 并行处理可执行 Tickets，单一整合者验证并交付。Ralph 仍是默认入口。
disable-model-invocation: true
---

# 子 agent 实施 Spec

仅在用户明确选择本入口时实施指定 Spec，不启动 Ralph。规划确认或发布 Tickets 不是实施授权；Ralph iteration 内不能调用本入口。缺少 Spec/Tickets 或 tracker 配置时提示对应前置 skill，然后停止。

## 并行与隔离

使用当前会话实际可用的子 agent 能力，按其工具约定并行派发独立任务、收取结果；不预设平台、工具名或调用参数。先派发可独立推进的任务，不逐票派发后立即等待。

每个 worker 使用独立 worktree；不假设派发自动隔离，首次写入前核对实际路径、分支和起点 SHA。主线程是唯一整合者；worker 不嵌套派发实现或 review agents。无法并行或隔离时说明阻塞，不静默切换执行入口。

## 执行

1. 完整读取指定父 Spec 及其关联 Tickets。`## Git` 仍表示最终**集成分支**，父子三字段必须一致；临时工作分支不改这个合同。确认集成 worktree 干净、有正确 upstream，且没有 Ralph/其它整合者同时消费该批任务。无法确认独占则停止。

2. 在集成 worktree 运行已安装 `ralph-plan-lqy` 的 `scripts/check_ready_issue_unblocked.py <N>`，只派发本 Spec 的 open + `ready-for-agent` 具体 Ticket：`0` 可派发，`2` 跳过，`1/3` 停止。不使用 assignee 领取，不绕过 publication gate。frontier 中的真实依赖、共享契约、写入与测试资源风险仍须核查；不安全的任务留待串行。

3. 对未派发的独立 frontier 创建 worker，使用集成分支当前已验证 HEAD 为起点。交付合同包含 Ticket/Spec 指针、实际 worktree/分支、起点完整 SHA、授权范围及项目规则。worker 读取并执行 `implement-lqy` 的**受委派 worker**纪律：只实现一票、做 TDD/聚焦验证并本地 commit；不 push、改 issue 或启动其它实施入口。不同 worktree 隔离文件，不代表共享数据库、构建缓存或服务也已隔离。

4. 任一 worker 返回即收完整结果：Ticket 编号、实际路径/分支、起点 SHA、commit SHA、变更范围、测试命令/结果与阻塞状态。核对真实 Git 变更和起点祖先关系，不以摘要代替验证。worker 失败或 Oversized 时停止派发，保留现场和未完成状态；已有 worker 先交回可确认的结果，不盲目重复派发。

5. 由整合者**串行合并**候选提交；记录合并前 HEAD 为该票 review fixed point。冲突或不确定内容停止，不能 reset/rebase/force-push。在主线程读取并执行 `code-review-lqy`，沿用每票预算与停止规则，不要求 worker 再派发 reviewers。运行整合后的相关完整测试、Feature 记录门禁及验收；通过后由整合者 push、评论证据并关闭该 Ticket。未合入、未验证或未 push 不算完成，不能释放依赖。

6. 每交付一票就刷新 frontier 并补空闲名额，**不等待整批**；运行中的 worker 继续。全部 Tickets 交付后做 Spec 整体验收，通过才关闭父 Spec。尚有 open Tickets 而无可执行前沿时报告阻塞，不宣称完成。最终不另启一轮无预算的 review。

## 收口

报告集成分支/HEAD、已交付与剩余 Tickets、验证及私有 worktrees。关闭已完成的子 agent 会话；分支/worktree 默认保留，仅按用户明确清理授权删除已合入且干净的本次资产。中断恢复先核对 agents、Git 与 issue 证据，不重新派发仍在运行的票。本 skill 是执行约定，不提供额外调度服务或运行时锁。
