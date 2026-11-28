# Git 托管平台

> 调查时间为 2026-10，不保证信息仍是最新。先用此文了解方向，再自行研究当前选项：产品、价格、限制和 beta 状态变化很快。

## 类型

### 一体化平台

Git host 内置 Ticket tracker、充当 orchestrator 的 CI 系统和托管 runner，共用事件流与权限模型。一款产品填满 Git host、Ticket tracker、orchestrator 和 runner，其 CI run 页面通常也足以充当 observability platform。每个 PR、review、label 和 check 事件既是 webhook 也是原生 trigger，因此这一类的 trigger 种类最丰富。

**适用场景**：工厂起步规模小、代码已托管在此、用户想要一张账单和一套登录。这对应 [SKILL.md](SKILL.md) 中“全部在 GitHub”的设计。供应商也提供自家 agent，它们可能与用户的 run 竞争，也可以作为其中一类 run 接入。

- [GitHub](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)：默认选择；Issues、Actions、Apps 和规模最大的集成生态。
- [GitLab](https://about.gitlab.com/pricing/)：issue、merge request、CI/CD 与 runner 一体，支持 SaaS 或自托管。

### 套件中的 Git host

作为大型套件一个模块销售的 Git host，Ticket tracker 是通过链接和 webhook 连接的同套件产品（Jira、Azure Boards）。Tracker 事件从第二条事件流抵达，orchestrator 需要汇合两种事件来源。

**适用场景**：组织已经运行该套件，人们在 Jira 或 Azure Boards 工作。工厂继承这一 tracker 作为人类交互界面。

- [Bitbucket Cloud](https://support.atlassian.com/bitbucket-cloud/docs/api-request-limits/)：Atlassian 的 Git host，搭配 Jira 和 Bitbucket Pipelines。
- [Azure DevOps (Azure Repos)](https://learn.microsoft.com/en-us/azure/devops/integrate/concepts/rate-limits)：Repos、Boards、Pipelines 和 Entra 身份处于同一组织中，因此填满四个槽位。
- [AWS CodeCommit](https://aws.amazon.com/blogs/devops/aws-codecommit-returns-to-general-availability/)：使用 IAM 身份的纯 Git host；需搭配外部 tracker 和 CI。

### 自托管 Git host

运行在用户自有基础设施上的 Git host，常与 orchestrator、runner 处于同一网络。运营者设定速率限制，因此上限取决于硬件。用户负责所填槽位的升级、备份与正常运行时间。

**适用场景**：代码必须留在本地或隔离网络、用户不想支付席位费、SaaS API 配额限制了繁忙工厂。Forgejo 和 Gitea 适合小团队，内置 issue 与兼容 GitHub Actions 的 CI；GitLab self-managed 和 GitHub Enterprise Server 适合组织，并保留 Apps 与 service account。

- [Forgejo](https://forgejo.org/2026-10-release-v17-0/)：社区治理的轻量平台，包含 Forgejo Actions。
- [Gitea](https://about.gitea.com/)：轻量，包含 Gitea Actions；也出售托管版。
- [GitLab self-managed](https://about.gitlab.com/install/) 和 [GitHub Enterprise Server](https://docs.github.com/en/enterprise-server@latest)：部署于用户自有设施的完整平台。

### Review 优先与去中心化 Git host

Review 模型不采用分支与 PR 的 Git host：逐 commit 的 patchset 与标签投票，或分布在用户运营节点间的联邦仓库。大多数工厂工具假设 PR，预计需要自行构建更多连接代码。在 Gerrit，自动检查 run 由 bot 身份投出 `Verified`，人投出 `Code-Review`。

**适用场景**：团队本来就这样 review，或更重视联邦化而非生态。

- [Gerrit](https://www.gerritcodereview.com/)：通过标签投票 review patchset；Android 与 Chromium 的模式。
- [Tangled](https://blog.tangled.org/ci/)：基于 AT Protocol 的 Git 托管，支持 stacked PR 和自有 CI runner。

### Agent 原生 Git host

以 agent 为主要作者构建的新 Git host：高 commit 吞吐量、无需 clone 的服务器端读取、按 agent 归属。整个类型截至 2026-10 仍属早期，关卡和速率限制可能尚未公开：向供应商询问。

**适用场景**：工厂针对一个大型仓库运行许多并发 run，clone 时间或 API 限额成为主要成本。先在单个仓库的镜像上试点，并保留 GitHub 作为后备。

- [Cursor Origin](https://cursor.com/origin)：来自 Graphite 团队，支持 GitHub 同步及签名的 PR、review、push webhook。
- [GitLab next-gen SCM](https://about.gitlab.com/blog/gitlab-next-gen-scm/)：重建的 GitLab 后端，提供免 clone 的 agent API。

### Run 使用的 Git 存储

无头、API 优先、可按千计创建的 Git 仓库：有分支、commit 和 diff，没有 PR、review 或关卡。它们只填半个槽位，每次 run 使用短期的仓库专属 token。

**适用场景**：run 需要便宜的一次性工作仓库或 fork（每 Ticket 一个 fork、agent 工作状态），PR 最终仍落在上文完整的 Git host。

- [Cloudflare Artifacts](https://www.cloudflare.com/product/artifacts/)：基于 Workers 的 Git 兼容存储；每个任务 fork 一份基线。
- [Pierre code.storage](https://code.storage/docs)：带临时分支的白标 Git API。

## 深入研究

根据下列问题核查每个候选：

1. **Trigger**：哪些事件（PR 创建、push、提交 review、添加 label、check 完成）以 webhook 送达 orchestrator？投递是否签名？
2. **身份**：run 能否以专属 bot 或 app 身份行动？这决定归属、自动 review run 能否批准另一个身份编写的 PR，以及 run 自身的 push 是否触发下一 run。
3. **关卡**：用户当前方案和仓库可见性是否支持必需检查、必需审批、分支保护？bot 能否列入绕过名单？
4. **速率限制**：所有 runner 上的 run 共用多少 API 配额？按哪个单位（installation、token、user、workspace）计算？如何扩展？
5. **已填槽位**：同一产品还覆盖 Ticket tracker、orchestrator、runner、observability platform 中哪些？

从一手来源寻找答案：REST API 与 webhook 参考、速率限制页面、价格和方案对比页面、access token 或 app 文档、changelog 或发布说明。

最易过期的是 beta/preview 状态（尤其 agent 原生和 Git 存储类型）、速率限制数值、关卡由哪个方案解锁，以及收购、关停、重启后是否可用。例如截至 2026-10，AWS CodeCommit 已重新对新客户开放，Bitbucket Data Center 仅作为与 Cloud 搭售的混合许可证出售。

## 持久注意事项

在设计依赖它们之前，仍需核实：

- **GitHub `GITHUB_TOKEN` 会中断链。** 内置 Actions token 引发的事件不会启动新 workflow run（`workflow_dispatch` 和 `repository_dispatch` 除外）；run 用它 push 后，下一 run 会无声停止。应从第一天起为 run 配置 GitHub App 身份。
- **关卡往往需要付费方案。** 截至 2026-10，私有仓库中的 GitHub rulesets 需要 Pro、Team 或 Enterprise；GitLab approval rules 需要 Premium；强制执行的 Bitbucket merge checks 需要 Premium。
- **速率限制按身份计算，bot 类型会影响额度。** 截至 2026-10，GitHub App installation 每小时 5,000 次请求，对比 `GITHUB_TOKEN` 的 1,000 次；Bitbucket user token 保持基本额度，access token 可以扩容；Azure DevOps 随 bot access level 提升额度。
- **套件 tracker 意味着两条事件流。** Orchestrator 自己汇合 Git host 与 Ticket tracker 的事件。
