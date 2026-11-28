---
name: software-factory-zh
description: 设计软件工厂的共同语言：它运行的任务与接入的服务。
disable-model-invocation: true
---

**软件工厂**是一个 agent 系统，将 Ticket、PR 和定期任务转化为已合并、部署到用户选择的远程基础设施上的代码。本 skill 提供设计软件工厂时使用的语言。讨论或白板设计工厂时只使用下列术语；用户使用 _Avoid_ 下的词时，指出规范术语。

## 任务与运行

**Task（任务）**：
工厂执行的一类工作，只定义一次、可运行多次：review、explore、implement、ratchet。任务可以针对 Ticket、PR 或整个代码库。
_Avoid_：用 job、workflow、action 称呼任务。CI 供应商的 workflow 文件及其 jobs 是接入任务的地方，不是任务本身。

**Trigger（触发器）**：
启动一次 run 的事件：Ticket tracker 或 Git host 的变更、orchestrator 中的时钟，或另一轮 run。

**Run（运行）**：
在一个 runner 上执行一次任务，从触发到结束，视为黑盒。一次 run 可以直接触发后续 run、经 orchestrator 逻辑触发，或通过修改 Ticket tracker / Git host 触发。run 从不等待人：它先结束，人之后对 Ticket tracker 或 Git host 的修改再触发新的 run。
_Avoid_：session

**Runner（运行器）**：
执行 run 的一次性机器。即便机器本身长时间运行，上面的内容也不会跨 run 存活：run 对先前运行的唯一记忆位于 Ticket tracker、Git host 和 orchestrator。
_Avoid_：server、host、box、compute、sandbox

## 服务

**Ticket tracker（Ticket 跟踪器）**：
Ticket 所在处，也是工厂的人类交互界面：人通过创建 Ticket 安排工作，在评论中与 agent 交谈，对 Ticket 的修改触发 run。
_Avoid_：issue tracker、ticket manager、project board

**Ticket source（Ticket 来源）**：
在工厂外部向 Ticket tracker 创建 Ticket 的任何东西：反馈按钮、监测器、错误跟踪器、收件箱。
_Avoid_：data source、trigger source、intake

**Git host（Git 托管平台）**：
分支、PR 与 review 所在处。
_Avoid_：code host、forge、repo

**Orchestrator（编排器）**：
接收 trigger、在 runner 上启动 run、记录哪些 run 已排队/正在执行/已结束的组件。
_Avoid_：dispatcher、scheduler、control plane

**Observability platform（可观测性平台）**：
runner 向其发送日志、trace 和状态，让人看见每次 run 内部发生什么。可选：填充 runner 或 orchestrator 槽位的产品通常已经展示足够信息。除非有内容写入 Ticket tracker 或 Git host，否则 run 不会根据平台上的信息作决策。
_Avoid_：observability、logs、monitoring、dashboard

## 设计工厂

设计分为两半：**服务**（每个槽位由一种产品填充）和**任务**（其 run 使工作流经这些服务）。

从用户的问题而非工厂出发：未经 triage 的 Ticket、等待自动 review 的 PR、需要迁移到更严格的自动检查、没人读的 bug 报告。当用户提出问题或不知道要建什么时，阅读 [EXAMPLE-TASKS.md](EXAMPLE-TASKS.md) 查找解决常见问题的任务。

### 慢慢启动

每个 trigger 都是加速器。只有油门没有刹车会变成劣质产出大炮。三种刹车是：

- **自动检查**：每次 run 必须通过的确定性关卡（类型、lint、测试）。
- **自动 review**：独立 run 根据代码库标准和（若有）Ticket 冷读 diff。
- **人工 review**：合并 PR 前由人阅读；人工发现的问题转化为新的自动检查及更精准的自动 review。

一次只增加一个自动 trigger，起初限流（每十份 bug 报告一份、每天一次的时钟），每个 PR 都有人 review。刹车赢得信任后逐步放开；每条 run 循环最多重试几次，然后交给人。

### 填满每个槽位

每项服务是一个槽位。一款产品可填多个槽位，一台服务器可承载多个服务。并排比较三种设计：

| 服务 | 全部在 GitHub | Linear Ticket | 自建 tracker |
| --- | --- | --- | --- |
| Ticket tracker | GitHub Issues | Linear | 自建 app |
| Ticket source | 反馈按钮 | 反馈按钮、监测器 | 反馈按钮、监测器 |
| Git host | GitHub | GitHub | GitHub |
| Orchestrator | GitHub Actions | 自建服务器 + 数据库 | 自建 app |
| Runner | Actions runner | Actions、E2B、Daytona 或 VPS | 自建 app 或 sandbox |
| Observability platform | 无：Actions run 页面已足够 | LLM trace 平台 | 自建 app |

用户为槽位挑选产品时，先阅读对应调查了解方向，再自行研究当前选项；每份调查都按类型归类选项，列出决定该槽位的问题：

- [TICKET-TRACKERS.md](TICKET-TRACKERS.md)
- [GIT-HOSTS.md](GIT-HOSTS.md)
- [RUNNERS.md](RUNNERS.md)
- [OBSERVABILITY-PLATFORMS.md](OBSERVABILITY-PLATFORMS.md)

购买服务，构建任务：任务承载用户的设计，服务是通用的。优先使用现成的 Ticket tracker：稳定、人人熟悉，也便于让外部用户参与。

### 质询每项任务

对每项任务回答：

1. 什么触发它？
2. 它做什么，读取和写入哪些服务？
3. 它接下来触发什么？
4. 人在何处重新介入？
5. 什么防止两个 run 做同一份工作？

对每个 Ticket source 回答：什么防止它重复创建同一 Ticket？

每个槽位都指定了产品（或为 observability platform 明确决定不使用），且每项任务与 Ticket source 都回答了所有问题，设计才算完成。
