---
name: implement-spec-subagent-lqy
description: 使用子 agent 安全并行实施已授权 Spec；工作区按项目约定与风险选择，由单一整合者验证交付。Ralph 仍是默认入口。
disable-model-invocation: true
---

# 子 agent 实施 Spec

用户授权并行实施该 Spec 后运行，也可由承接授权的主流程派发，无需逐票重复请求授权。优先从当前对话确定已批准的 Spec；不能唯一确定时才询问 issue 编号或 URL。规划确认或发布 Tickets 不是实施授权，不与其它实施流程消费同一批任务或嵌套启动另一调度器。缺少 Spec/Tickets 或 tracker 配置时提示对应前置 skill，然后停止。

## 并行与工作区

使用当前会话实际可用的子 agent 能力，按其工具约定并行派发独立任务、收取结果；不预设平台、工具名或调用参数，不逐票派发后立即等待。

遵循项目约定：明确不相交的小任务可共享 worktree；需要独立提交或滚动整合时优先独立 worktree。先核查实际写入文件与测试/构建/服务资源，不假设派发自动隔离，也不靠 worktree 消除共享契约或数据冲突。无法安全并行的部分串行，不自行改变项目的分支/worktree 约定。

主线程是唯一整合者。worker 可在本票范围内委派只读查证，不再拆派实施、不扩大范围、不绕过 review 预算。正式 review 与最终交付由整合者负责。

## 执行

1. 完整读取 Spec 与关联 Tickets。`## Git` 仍是最终集成目标，父子三字段必须一致；临时工作分支不改合同。开始前确认集成 worktree 干净、有正确 upstream，且该批任务只有一个整合者；不能确认则先协调。

2. 在集成 worktree 运行已安装 `ralph-plan-lqy` 的 `scripts/check_ready_issue_unblocked.py <N>`，只派发本 Spec 的 open + `ready-for-agent` 具体 Ticket：`0` 可派发，`2` 跳过，`1/3` 停止。不使用 assignee 领取，不绕过 publication gate；结合真实依赖和资源风险选择安全 frontier。

3. 派发时给出 Ticket/Spec 指针、实际工作区、写入范围、已验证起点与项目规则。worker 读取并执行 `implement-lqy` 的**受委派 worker**纪律：一票实现、TDD/聚焦验证并交回证据。共享工作区不操作 Git/index；独立 worktree 可本地 commit，不 push 或改 issue。

4. 收完整结果并核对真实变更：Ticket、实际文件、验证命令/结果、阻塞状态；独立提交还须核对分支、起点与 commit SHA。失败或 Oversized 保留现场与未完成状态，不盲目重复派发或扩建。整合者明确本次交付的 Tickets/文件，并记录 review fixed point；其它工作不混入本批次。

5. 独立 worktree 的候选由整合者**串行合并**；共享工作区的写入须**全部结束或已协调暂停**，然后固定交付批次快照。在同一快照上读取并执行 `code-review-lqy`、运行相关完整测试/构建、Feature 门禁和验收；保留其双轴预算与停止规则。review、修复、验证及 Git 交付期间不得恢复该工作区的并发写入。冲突、范围不明或门禁失败时停止交付，不 reset/rebase/force-push。

6. 通过后由整合者 commit/push、评论证据并关闭对应 Tickets；未验证或未 push 不能释放依赖。刷新 frontier 后补空闲名额；独立工作区不等待整批，共享工作区收口后再恢复写入。全部 Tickets 交付并通过 Spec 整体验收才关闭父 Spec；仍有 open Tickets 而无可执行前沿时报告阻塞，不另启无预算的最终 review。

## 收口

报告目标分支/HEAD、已交付与剩余 Tickets、验证及保留现场。只关闭已完成的子 agent 会话；分支/worktree 默认保留，仅按用户明确清理授权删除已合入且干净的本次资产。恢复前核对 agents、Git 与 issue 证据，不重复派发仍在运行的票。本 skill 是执行约定，不提供调度服务或运行时锁。
