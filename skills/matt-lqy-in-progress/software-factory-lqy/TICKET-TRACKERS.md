# Ticket 跟踪器

> 调查时间为 2026-10，不保证信息仍是最新。先用此文了解方向，再自行研究当前选项：产品、价格、限制和 beta 状态变化很快。

Ticket tracker 是工厂的人类交互界面。下列每类都是起点：阅读它是什么、工厂何时选择它，然后按[Researching further](#researching-further)中的问题核查示例。

## 类型

### 1. Git host 内置 tracker

内置于 Git host 的 tracker，Ticket、分支和 PR 共用同一产品、权限模型和身份。工厂规模小、团队本就在 Git host 工作或仓库公开时选择。即“全部在 GitHub”设计：Git host 的 CI 无需连接代码便可填充 orchestrator 槽位。标签是可靠的路由方式，因为状态存在于独立看板上。外部开发者在代码所在地创建 Ticket；非开发者需要账户，因此由反馈按钮通过 API 创建。自托管 Git host 也自带 tracker。

- [GitHub Issues](https://docs.github.com/en/copilot/concepts/agents/about-third-party-agents)：默认选择；支持把任务分配给 Copilot、Claude 和 Codex。
- [GitLab Issues](https://about.gitlab.com/blog/how-to-use-a-work-item-created-trigger/)：从 work item 触发 Duo Agent Platform 流程。
- [Forgejo](https://forgejo.org/2026-10-release-v17-0/)：自托管，兼容 Actions。

核实：哪些 agent 分配能力仍是 preview、哪些方案包含它们；原生 agent 读取后续评论还是仅在分配时读取 Ticket（截至 2026-10，Copilot 仅在分配时读取）。

### 2. Agent 原生开发 tracker

面向软件团队的独立 SaaS tracker，agent 可作为一等 assignee，具有 agent API 与自有 coding agent。产品、客服或设计人员安排工作、团队已在该工具工作，或需要精致的 triage 和规划视图时选择。对应“Linear Ticket”设计。状态与 workflow 是一等对象，因此“移到 Ready”是干净的 trigger。Agent 作为 app user 接收人的委派，run 可把进度流式写入 Ticket。此类原生 agent 能力最深入，因此也能部分填充 orchestrator 和 runner 槽位。

- [Linear](https://linear.app/developers/agents)：最适合 agent 的 tracker。
- [Jira](https://support.atlassian.com/jira-software-cloud/docs/collaborate-on-work-items-with-ai-agents/)：由状态触发的 agent；适合已使用 Atlassian 的组织。
- [Shortcut](https://www.shortcut.com/help/integrations/using-ai-agents)：分配 story 或在评论中提及 agent。
- [YouTrack](https://www.jetbrains.com/youtrack/)：workflow-as-code；可自托管。

核实：agent API 的状态（截至 2026-10，Linear 仍是 developer preview）；原生 agent run 如何计量和收费；agent 席位费用；agent webhook 确认期限；客户可访问的表单在哪档解锁；自托管版本的生命周期结束日期。

### 3. 开源开发 tracker

可运行于自有基础设施、同时提供云版的 Linear 风格 tracker。数据必须留在内部（隔离网络、受监管）或用户想阅读、修改 tracker 源码但仍可以购买服务时选择。通过状态、标签和自定义属性进行路由，方式类似类型 2；原生 agent 则较新。

- [Plane](https://developers.plane.so/dev-tools/agents/overview)：类似 Linear；每 app 一个 bot user；agent 在评论中回复。
- [Huly](https://github.com/hcengineering/huly-selfhost)：提供双向 GitHub 同步的一体化工作空间；运维成本较高。
- [OpenProject](https://www.openproject.org/)：成熟、传统的项目管理工具。

核实：agent 功能状态（截至 2026-10，Plane 为 beta）、哪个版本有访客角色和收集表单、许可证、自托管栈的运营成本。

### 4. 通用工作工具

数据库或任务清单兼作 tracker 的工作管理/文档工具。服务非工程团队，或 Ticket 多为内容、运营和研究而非代码时选择。表单是其强项：任何有链接的人都能创建 Ticket。路由通过灵活的数据库属性实现，因此每个工厂都要自定 schema。开发上下文（diff、PR）在 Git host 上，需多点一次。仅 SaaS。

- [Notion](https://www.notion.com/help/custom-agents)：数据库即 tracker；agent 在数据库变更时启动。
- [Asana](https://asana.com/product/ai/ai-teammates)：AI Teammates 接手分配给它们的任务。
- [ClickUp](https://clickup.com/brain/cloud-agents)：Cloud Agents 在任务讨论串返回 PR。
- [Trello](https://developer.atlassian.com/cloud/trello/guides/rest-api/webhooks/)：看板与列表；webhook 加 Butler 自动化。

核实：webhook 延迟和粒度（截至 2026-10，Notion 会批量发送内容变更，延迟一两分钟）；哪个方案包含 agent。

### 5. 仓库原生 tracker

Ticket 作为仓库中的文件（JSONL、Markdown）保存，agent 通过 CLI 或 MCP server 编辑，像代码一样合并。一个开发者在本地驱动 agent 并希望把计划放入 Git 时，或把它用作真实 tracker 旁的 run 工作记忆时选择。推送到 Git host 是唯一 trigger，因此 orchestrator 要通过文件 diff 找出变化。身份来自 Git host。外部人创建 Ticket 需要 commit 或 PR，在所有类型中最不方便；有其他人开始创建 Ticket 时，工厂通常转用 Git host tracker。

- [Beads](https://github.com/steveyegge/beads)：带依赖关系的 JSONL；run 可以领取下一个未受阻 Ticket。
- [Backlog.md](https://github.com/MrLesk/Backlog.md)：有 Kanban 视图和 MCP server 的 Markdown 任务。

### 6. 自建

工厂自有 app 在自己的数据库中存放 Ticket，通常与 orchestrator 并置。对应“自建 tracker”设计。Tracker *就是*产品（内部平台、面向客户的客服工厂），或现成模型均不合用时选择。Trigger 变为函数调用；以下问题中的每项特征都需要编写并维护代码，这也是 skill 倾向购买服务的原因。带 webhook 的 [Airtable](https://airtable.com/developers/web/api/webhooks-overview) base 是半自建的折中方案。

## Researching further

用以下问题核查每个候选；它们决定这个槽位：

- **Trigger**：哪些 Ticket 变动（创建、打标签、改状态、分配、评论、提及）发出 webhook/event 让 orchestrator 转化为 run？速度与粒度如何？
- **路由**：run 能读取哪些标签、状态或字段来判断类别（explore、implement、rework）？
- **讨论串**：人能否在评论中回答 agent，回复会不会触发下一 run？
- **身份**：是否有 API 和 bot 身份，让 run 以自己身份行动、人能区分 agent 与同事？bot 是否要占席位？
- **原生 agent**：Ticket 能否直接分配给 agent？支持哪些 agent、在哪档、如何计量？它读取分配时的 Ticket，还是整条讨论串？
- **外部创建**：Ticket source 或客户如何创建 Ticket：表单、邮件、聊天、API？在哪档解锁？
- **托管**：仅 SaaS 还是可自托管，许可证是什么？

答案应来自一手来源：API 与 webhook 参考（事件列表、payload、投递与重试规则）、agent/app 开发者文档、价格及方案对比表、changelog 或发布说明。优先于博客和对比网站。

最易过期的依次为：agent 功能及 preview/beta 状态、agent 计量和额度价格、agent 与表单的方案门槛、速率限制，以及收购、关停、自托管版生命周期结束日期。Webhook 事件列表与路由模型变化相对较慢。

## 持久注意事项

依赖之前仍应逐一核实：

- **GitHub `GITHUB_TOKEN` 陷阱**：默认 `GITHUB_TOKEN` 所作修改不会触发新的 workflow run。由 run 给 Ticket 加标签或评论以触发下一 run 时，应使用 GitHub App token。
- **仅在分配时读取上下文**：有些原生 agent 只在分配时读取 Ticket，因此后续上下文应放在 PR 上。
- **Agent webhook 要求快速确认**：orchestrator 立刻确认，再启动 run。
- **通用工作工具会批量发送 webhook**：事件较晚才抵达；需要及时启动 run 的工厂应在属性变更时触发，或选择另一类型。
