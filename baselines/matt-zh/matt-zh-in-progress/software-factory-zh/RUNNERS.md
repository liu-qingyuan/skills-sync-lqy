# Runner

> 调查时间为 2026-10，不保证信息仍是最新。先用此文了解方向，再自行研究当前选项：产品、价格、限制和 beta 状态变化很快。

Runner 是**一次性的**：每次 run 都在干净的机器上启动，不留下任何状态。五类产品能填充此槽位，主要差异在于谁拥有 agent loop 和机器：

| 类型 | Agent loop | 机器 | 同时填充 |
| --- | --- | --- | --- |
| CI runner | 自己的，在 CI job 中 | CI 厂商的或自己的 | orchestrator、observability platform |
| MicroVM API | 自己的，在 orchestrator 或 runner 上 | 供应商的 | 无 |
| 内置 agent 平台 | 供应商的 | 供应商的 | 部分 orchestrator、observability platform |
| 自带 worker | 供应商的 | 自己的 | 部分 orchestrator、observability platform |
| 自有 VPS 或容器 | 自己的 | 自己的 | 无 |

Runner 按 run 选择：review run 使用便宜的 CI runner，implementer run 使用 microVM，是正常设计。

## CI runner

每个 CI job 启动全新 VM 或 pod，由 Git host 自带的 workflow 引擎管理；agent CLI 是 job 中的一步。Orchestrator 通过 workflow trigger（issue、PR、定时、手动 dispatch）启动 run，并通过 concurrency group 防止两个 run 同时处理同一 Ticket。托管 runner 天生一次性；自托管 runner 通过 ephemeral 模式达成这一点：每 job 一个 pod，运行后删除。按分钟计费。

**适用场景**：Git host 是 GitHub 或 GitLab，所有 trigger 都是 Git host 事件或时钟；workflow 文件就是 orchestrator，run 页面就是 observability platform，一款产品填三个槽位。

起点：
- [GitHub Actions](https://docs.github.com/en/actions/reference/limits)：全 GitHub 工厂的默认选择；[价格](https://docs.github.com/en/billing/reference/actions-runner-pricing)。
- [Claude Code GitHub Action](https://code.claude.com/docs/en/github-actions)：在 workflow 中运行 Claude Code。
- [GitLab hosted runners](https://docs.gitlab.com/ci/runners/hosted_runners/linux/)：每 job 一个临时 VM。
- [Actions Runner Controller](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller)：用户 Kubernetes 上自托管，每 job 一个临时 pod。

## MicroVM API

一次 SDK 调用约一秒内创建隔离 microVM（供应商称“sandbox”）；orchestrator 向其中执行命令，或在里面启动 agent CLI。按 vCPU 与 RAM 使用秒数计费。Orchestrator 为每次 run 创建一个、结束时销毁，并设置超时作为最终保护。供应商也销售持久化（暂停/恢复、快照、磁盘）；工厂将它当作缓存，run 间记忆仍保存在 Ticket tracker、Git host 和 orchestrator 中。

**适用场景**：工厂自有 orchestrator（服务器或队列），希望无需管理机器即可运行大量短暂并行的 run。比较最长 run 时间、并发上限以及等待模型期间是否计费：截至 2026-10，Vercel 仅按活跃 CPU 计费，因此等待模型的成本几乎为零。

起点：[E2B](https://e2b.dev/pricing)、[Daytona](https://www.daytona.io/pricing)、[Modal Sandboxes](https://modal.com/docs/guide/sandboxes)、[Vercel Sandbox](https://vercel.com/docs/vercel-sandbox/pricing)。

## 内置 agent 平台

包含 runner 的托管 coding agent：供应商为每次 run 配置全新 VM 或容器、运行自己的 agent loop、推送分支或 PR。只有分支存活下来。Run 可以由 Git host 或 Ticket tracker 中的 @提及或分配、聊天消息、定期任务或 HTTP 调用启动，因此平台填充了 orchestrator 的大部分职责；会话视图填充 observability platform。费用包含在席位费或订阅费中，或按 run 计费。

**适用场景**：用户希望组件尽可能少，并愿意使用供应商的 agent。确认 trigger 覆盖用户的 Ticket tracker。

起点：
- [Claude Code cloud](https://code.claude.com/docs/en/claude-code-on-the-web)，有用于 cron、API 和 GitHub 事件 trigger 的 [scheduled tasks](https://code.claude.com/docs/en/routines)。
- [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)：API 优先；针对环境创建 run 并流式传送事件。
- [Codex cloud](https://developers.openai.com/codex/cloud)：每项任务一个容器。
- [Copilot coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)：将 issue 分配给 Copilot；其 runner 是 GitHub Actions runner。

## 自带 worker

内置平台保留 agent loop 与 run 队列，但工具调用在用户托管的 worker 上执行。Worker 向供应商发起出站轮询，领取并执行 run，然后退出：与自托管 CI runner 同样的形态。一次性隔离由用户负责：使用 Kubernetes 或 microVM API 运行 worker，确保每次 run 都获得新磁盘。成本为供应商席位费或使用费加上用户的机器费用。

**适用场景**：用户想使用内置 agent，但 run 必须访问私有网络、数据留在自有机器，或使用定制硬件。

起点：[Claude Code self-hosted environments](https://code.claude.com/docs/en/self-hosted-environments)、[Cursor self-hosted pool](https://cursor.com/docs/cloud-agent/self-hosted-pool)、[Copilot coding agent on ARC](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)。

## 自有 VPS 或容器

用户租赁或运营机器，每次 run 使用全新容器（或机器）：机器可能存活数月，容器只运行一次。最长运行时间取决于 orchestrator 设置的 deadline。通过 `docker run --rm`、设置 `ttlSecondsAfterFinished: 0` 的 Kubernetes Job，或结束时销毁机器实现一次性；任何缓存都放在下一次 run 视为可选的路径。按月固定计费或按运行秒数计费。

**适用场景**：run 较长、持续且繁重，每小时成本占主导，或已有服务器托管 orchestrator。

起点：[Fly Machines](https://docs.fly.io/machines/overview)（[价格](https://docs.fly.io/about/pricing)）、[Hetzner Cloud](https://www.hetzner.com/cloud/) 搭配 Docker、[Kubernetes Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)。

## 深入研究

### 决定该槽位的问题

拿工厂的实际 run 对照每个候选：

1. **Orchestrator 如何启动 runner？** Workflow trigger、SDK 调用、@提及、HTTP 调用，或由 worker 领取供应商队列？是否适配设计已经选定的 orchestrator？
2. **最长 run 时间及并发上限？** 查看默认 timeout、各方案档位的最高限制及达到上限时会怎样。与设计中最长 run 和最忙时的突发量比较。
3. **成本形状？** 按分钟、按 vCPU 和 RAM 秒数、只算活跃 CPU、按 run、按席位，还是月费？等待模型是否计费？模型 token 包含在内还是额外收费？
4. **如何实现一次性？** 默认全新、ephemeral flag，还是 orchestrator 自行清理？有哪些持久化能力，能否限定为缓存？
5. **Run 可访问什么？** 私有网络、出站 firewall 或 allowlist、secret 如何到达 runner、还有谁能读取它们？
6. **还能填充哪些槽位？** 计算作为 orchestrator 能读取哪些 trigger，以及其 run 页面或会话记录对 observability platform 的覆盖。

### 答案在哪

- 供应商的**限制或配额页面**、**价格页面**，优先于营销首页。
- **SDK 或 API 参考**中的创建调用：timeout、生命周期和网络参数。
- **安全或网络文档**中的 firewall、allowlist 和 secret 处理。
- **Changelog 或发布说明**中的 beta、preview、GA 状态和方案门槛（Team、Enterprise）。
- CI runner 要查 Git host 的**计费文档**。

### 哪些最快过期

- **价格与免费额度。** 截至 2026-10，GitHub 宣布对自托管 runner 按分钟收费，后来又推迟。
- **Beta、preview、early-access 状态**以及哪些方案解锁功能。截至 2026-10，Claude Managed Agents 与 Claude Code self-hosted environments 都处于 beta。
- 各档位的**默认 timeout 和最长 run 时间**。
- 内置平台的**trigger 集成**：哪些 Ticket tracker 和聊天工具能启动 run。
- **启动耗时**是供应商主张；若重要，请自行测量。

上述类型特征（谁拥有 loop、谁拥有机器、填充哪些槽位）变化较慢，可信度高于本文中的任何数值。
