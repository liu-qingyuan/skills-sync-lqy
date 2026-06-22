---
name: tea
description: TEA，Testing Engineering Architect。用于测试工程架构、测试分层、contract test、E2E 边界、architecture check、回归保护、bugfix 验证和 CI 质量门禁。重点是通过公开行为、Interface、Seam、Adapter、Domain/Event/Contract 模型测试，避免脆弱的实现细节耦合。
---

# tea

使用 TEA 判断测什么、在哪一层测、什么不能 mock、测试如何保护架构。输出保持简短，并给出验证证据或验证缺口。

## 短流程

1. **Identify behavior**：明确要验证的外部行为或契约。
2. **Choose level**：在 4 类测试中选择：unit、integration、contract、E2E。
3. **Protect seam**：围绕调用方依赖的 Interface、Seam、Adapter 或 Contract 设计测试。
4. **Avoid brittle tests**：避免绑定私有 helper、临时内部拆分或 mock 调用次数。
5. **Verify in CI**：明确验证命令和质量门禁；可运行时直接运行。

## Interface as test surface

- 测试公开行为，不测试私有实现。
- 测试 contract，不只测试 mock 交互。
- 测试 seam，不测试临时内部拆分。
- 测试 Adapter 的转换边界，避免外部协议污染业务测试。
- 好测试应允许 Implementation 改变，同时保护 Interface 不变。

## 编程思想到测试保护面

这些对应关系是风险判断，不是固定测试流程。TEA 按风险选择最轻测试层；不是每一层都强制补测试，也不是每次都要产出契约文档、图或 E2E。架构图只能作为边界、依赖和契约判断的补充证据，不能替代 contract/integration test 或 architecture check。

| 思想层级 | TEA 保护什么 | 常用验证方式 |
| --- | --- | --- |
| 过程式编程 | 输入输出行为正确。 | unit / smoke |
| 面向对象编程 | 公开行为稳定，内部可重构。 | unit through public interface |
| 接口抽象 / 依赖倒置 | seam/adapter 不泄漏实现细节。 | integration / contract |
| 领域驱动设计 | 业务不变量、状态变化、用例结果。 | unit / integration |
| 事件驱动架构 | 事件 payload、顺序、幂等、兼容性。 | schema / contract / integration |
| 策略治理 / 可观测 / 可演进架构 | 依赖方向、策略、质量门禁、关键路径。 | architecture check / smoke / critical E2E |

## 4 类测试

| 类型 | 适用场景 | 不负责 |
| --- | --- | --- |
| Unit 单元测试 | 纯领域逻辑、稳定小 Interface、无外部依赖的规则。 | 不验证数据库、网络、provider、真实协议。 |
| Integration 集成测试 | 模块协作、真实配置、真实依赖或接近真实的 fake，验证 Adapter 转换边界。 | 不覆盖所有用户路径。 |
| Contract 契约测试 | API、event、tool protocol、provider、schema、service contract 的边界兼容性。 | 不负责 UI 流程，不测试内部实现。 |
| E2E 端到端测试 | 关键用户路径或端到端业务链路。 | 不覆盖所有细节，不替代 unit/integration/contract。 |

Architecture check、static analysis、smoke、canary 是质量门禁/上线验证，不是第 5 类测试。

## 测试应该服务架构

- 业务测试不应理解 provider、transport、storage、framework 或 tool 内部细节。
- Adapter 测试应证明外部 contract 与内部模型之间的转换。
- Contract test 应保护契约模型和事件模型：payload 形状、状态码/事件名、版本、兼容性和错误行为。
- 契约层优先复用已有 contract definition，并选择最轻的验证方式：schema validation、API/integration test、provider verification，或必要时 Pact。
- 架构检查应在技术栈支持时强制依赖方向。
- 回归测试应先能复现已观察到的 bug，再通过真实公开表面验证修复。

## Contract layer

- 契约层包含两件事：**contract definition** 和 **contract testing**。
- Contract definition 默认沿用项目已有格式：OpenAPI/AsyncAPI YAML、JSON Schema、schema YAML、Zod/TypeScript type、Protobuf、custom YAML/JSON 或其他 typed contract。
- 非 HTTP 边界也是契约边界：LLM/Agent 调 CLI、tool protocol、JSON over stdin/stdout、exit code/stderr、event/message 都应定义输入、输出、错误和版本契约。
- Contract testing 是验证实现是否符合契约；默认先用 schema validation、API/CLI/integration test、provider verification 或项目已有工具。
- CLI/tool JSON 默认用 YAML/JSON Schema/Zod/TypeScript type + 真实 CLI integration test，验证 exit code、stdout JSON、stderr 和 error shape。
- Pact 不是默认契约格式，也不是契约层必选项；官方核心适合 HTTP 和 message integrations，不要假设 Pact 原生一等支持 CLI spawn/stdout/stderr。
- 只有需要保护 consumer 真实依赖、consumer/provider 独立开发/版本/发布时，才考虑 Pact；CLI/tool 场景若使用 Pact，应建模为 message contract 或明确的 adapter/plugin。
- 如果 YAML/schema/typed contract + integration/API/CLI/E2E 已能覆盖风险，不要引入 Pact。
- 需要 Pact consumer test、provider verification、自建 Pact Broker 或 can-i-deploy 时，再使用 `pact` skill。

## 什么时候不要 mock

- 不要 mock 掉真正要验证的 contract。
- 不要 mock 掉 Adapter 转换逻辑。
- 不要 mock 掉当前测试目标的关键集成边界。
- 不要为了让测试好写而改变生产架构。

## 什么时候可以 mock / fake / stub

- 外部不稳定系统。
- 高成本服务。
- 难以构造的失败场景。
- 非当前测试目标的边界。
- 慢或 flaky 的 provider；但必须有单独 contract/integration 覆盖。

## 专业测试 skill 路由

- TEA 先给出现代测试架构判断；只有项目已有对应工具，或用户要求安装/使用时，才调用专业 skill。
- 需要写 Playwright E2E/API/component/visual/accessibility 测试、locator、fixture、auth、trace 调试时，使用 `playwright-core`。
- 需要终端优先的浏览器自动化、截图/视频/trace、生成测试代码、Electron `_electron.launch()` 证据时，使用 `playwright-cli`。
- 只有项目有 CI，或用户要求配置 CI/CD 时，才使用 `playwright-ci`；没有 CI 的项目不要为了 Playwright 强行引入 CI。
- 只有需要 consumer-driven contract testing 时，才使用 `pact`；契约定义仍以项目已有 contract 文件为准。
- TEA 只判断测试类型和边界；Playwright/Pact 的具体写法交给对应专业 skill。

## 上线风险测试

- Unit 可以 mock 外部依赖；integration/contract 应验证 mock 假设是否符合真实 API、event、provider 或 tool protocol。
- 对关键上线风险使用 backward compatibility、smoke、canary 或灰度验证；不要让 E2E 覆盖所有细节。
- static analysis、architecture check、lint/typecheck 是质量门禁，用来自动发现可规则化的问题。

## CI 质量门禁

使用仓库已有 gate；只补当前风险真正需要的缺口：

- lint
- typecheck
- unit
- integration
- contract
- critical E2E
- architecture boundary check
- smoke

## 禁止事项

- 不要追求无意义 coverage 数字。
- 不要写只验证 mock 被调用的测试。
- 不要让 E2E 覆盖所有细节。
- 不要把测试难写作为拆出浅模块的理由。
- 没有运行或说明验证命令时，不要声称完成。
