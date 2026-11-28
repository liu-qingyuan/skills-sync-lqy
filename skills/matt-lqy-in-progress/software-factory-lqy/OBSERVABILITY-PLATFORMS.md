# 可观测性平台

> 调查时间为 2026-10，不保证信息仍是最新。先用此文了解方向，再自行研究当前选项：产品、价格、限制和 beta 状态变化很快。

用于填充 observability platform 槽位，或明确决定不使用。类型按**人需要看到 run 内部的什么**来划分：日志、agent trace（每次模型调用和工具调用都是 span），或与用户系统其余部分连接起来的 trace。自托管和 SaaS 横跨后面三类。当 run 需要根据平台观测采取行动时，让平台成为 Ticket source：监测器创建 Ticket，run 再读取它。

## Runner 如何接入

所有类型通过五种接入方式之一接收数据。填槽位时要同时指出产品与接入方式。

- **Harness OTel**：agent harness 自己导出 OpenTelemetry。Claude Code 和 Claude Agent SDK 需要 `CLAUDE_CODE_ENABLE_TELEMETRY=1` 加 `OTEL_*` 变量，prompt 和工具输出需要明确启用；Codex CLI 在 `config.toml` 中使用 `[otel]` 块。（[Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/observability)、[Claude Code](https://code.claude.com/docs/en/monitoring-usage)、[Codex config](https://developers.openai.com/codex/config-advanced)）
- **Platform push**：模型平台替你发送 trace，例如 Claude Managed Agents 将其推到 Claude Console 中配置的 OTLP 目标。（[Claude docs](https://platform.claude.com/docs/en/manage-claude/opentelemetry/api)）
- **SDK wrapper**：runner 代码里调用一次，例如 LangSmith 的 `configure_claude_agent_sdk()`。
- **Hook plugin**：Claude Code hook 在每次 Stop 时读取会话记录并发送，例如 Langfuse 的 Claude Code 插件。
- **Gateway**：runner 的模型 base URL 指向日志代理。不改 runner 代码，但只能看到模型调用：harness 内部的工具调用不可见。

OpenTelemetry 是共用传输格式：harness OTel 和 platform push 都能送入任何 OTLP 后端。GenAI 语义约定（`invoke_agent`、`chat`、`execute_tool` spans）仍在形成中，预计 span 名称会变化。（[OTel GenAI agent spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans)）

## 类型 1：无（runner 或 orchestrator 产品展示的信息足够）

**是什么**：人直接在 runner 或 orchestrator 已有界面查看 run：CI run 页面、sandbox 控制台、作为 run artifact 保存的 agent 会话记录。无需自建接入方式，自托管程度与 runner 一样，成本已包含其中。

**适用场景**：每天只有少量 run、只有一个人查看，问题仅是“是否失败、打印了什么？”大多数工厂从这里起步；需要跨 run 搜索、汇总每次 run 的 token/成本、保留时间超过 runner 时再扩展。

**起点**：[GitHub Actions run logs](https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization)、[E2B sandbox logs and metrics](https://e2b.dev/docs)、[Daytona sandbox telemetry](https://www.daytona.io/docs/en/observability/otel-collection/)、[OpenAI Agents SDK traces](https://openai.github.io/openai-agents-python/tracing/)。Sandbox 产品通常也能通过 OTLP 转发同样的数据，作为迁移到类型 2 的路径。

**核实**：各 runner 产品保留多少天；某些 sandbox 保留时间很短（截至 2026-10，Daytona 为 3 天）。

## 类型 2：LLM 与 agent trace 平台

**是什么**：以 agent trace 为核心的后端：每个 run 是模型调用与工具调用组成的树，含 token 成本、prompt 和 session，通常还提供 eval 和 dataset。

**适用场景**：人需要跨多次 run 追问“agent 为什么这么做？”；retro run 或人要比较运行结果；需要每次 run 的 token 开支汇总。自托管开源平台可以将会话记录留在内部。

**类型特征**：接收 harness OTel、SDK wrapper 或 hook plugin，通常也支持 platform push。按数据量计费，agent run 会产生很多 span（每次工具调用一个），因此按 run 而不是按 request 预算。

**起点**：[Langfuse](https://langfuse.com/pricing) 与 [Arize Phoenix](https://phoenix.arize.com)（开源、可自托管）、[LangSmith](https://www.langchain.com/pricing-langsmith)、[Braintrust](https://www.braintrust.dev/pricing)。

**核实**：免费档限制、计费单位（trace、span、unit 或 GB；Braintrust 在 2026-03 改按 GB 计费）、哪档允许自托管、当前所有权。

## 类型 3：通用 APM 与日志后端

**是什么**：用户已有的可观测性栈（所有服务的日志、指标和分布式 trace），增加 agent 或 LLM 视图。

**适用场景**：团队已经为它付费；run 需要与应用本身的 trace 关联（Agent SDK 传播 `TRACEPARENT`，使 run 嵌在其调用者的 trace 内）；或已有 monitor Ticket source 从它读取数据。

**类型特征**：harness OTel 直接发送到厂商的 OTLP endpoint。按 GB、event 或 host 计费；工厂的数据量可能只是已有账单上的零头，也可能在新账单上带来惊喜。

**起点**：[Datadog Agent Observability](https://www.datadoghq.com/product/llm-observability/)、[Grafana Cloud](https://grafana.com/pricing/)、[Honeycomb](https://www.honeycomb.io/pricing)、[SigNoz](https://signoz.io/pricing/)（开源）。

**核实**：agent 视图是 GA 还是 preview，哪些 harness 有配置指南，免费档的数据量。

## 类型 4：记录请求的 LLM gateway

**是什么**：runner 与模型供应商之间的代理，记录每个请求和响应，同时提供路由、密钥、预算和缓存。

**适用场景**：用户需要每次 run 的开支上限，或为多个 runner 共用密钥库，顺带获得日志；或 harness 本身无法导出。它只看得到模型调用，工具调用需搭配类型 2 或 3。

**起点**：[LiteLLM Proxy](https://docs.litellm.ai/docs/proxy/logging)（开源，转发日志到 Langfuse 或 OTel）、[Portkey](https://portkey.ai/pricing)。

**核实**：SaaS 是否按请求计费；产品是否仍积极维护（截至 2026-10，Helicone 在被收购后进入维护模式）。

## 深入研究

根据决定该槽位的问题核查各候选：

1. **Runner 或 orchestrator 展示的是否已足够？** 对照人所需的跨 run 搜索、每 run 成本和留存期，与 run 页面或 sandbox 控制台提供的内容。若足够，明确选择“无”。
2. **Agent harness 如何导出 trace？** 查明 harness 支持五种方式中的哪些，产品接收哪些；确认工具调用是否成为 span，prompt 和工具输出是否需明确启用。
3. **能否自托管？** 许可证、允许自托管的档位以及运行环境；会话记录必须留在内部时尤其重要。
4. **成本形状如何？** 计费单位、免费档、假设每次工具调用一个 span 的每 run 估算，再乘以每天的 run 数量。
5. **留存时间多长？** 各档保留天数，对比 run 失败时人需要回溯多久。

**答案来源**：厂商价格页面（单位、档位、留存）；对应 harness 的厂商集成文档；harness 自身监控文档（导出内容、哪些 flag 仍为 beta）；OpenTelemetry GenAI 语义约定；产品仓库（许可证和发布动态）；厂商 changelog 或博客（所有权变化）。

**最易过期**：免费档限制和价格；beta/preview 标记（Claude Code trace export、Console platform push、厂商 agent 视图）；所有权与维护状态；计费单位；保留天数；GenAI span 名称。
