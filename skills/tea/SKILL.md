---
name: tea
description: TEA，Testing Engineering Architect。用于测试工程架构、测试分层、contract test、E2E 边界、architecture check、回归保护、bugfix 验证和 CI 质量门禁。重点是通过公开行为、Interface、Seam、Adapter、Contract 测试，避免脆弱的实现细节耦合。
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

## 4 类测试

| 类型 | 适用场景 | 不负责 |
| --- | --- | --- |
| Unit 单元测试 | 纯领域逻辑、稳定小 Interface、无外部依赖的规则。 | 不验证数据库、网络、provider、真实协议。 |
| Integration 集成测试 | 模块协作、真实配置、真实依赖或接近真实的 fake，验证 Adapter 转换边界。 | 不覆盖所有用户路径。 |
| Contract 契约测试 | API、event、tool protocol、provider、schema、service contract；Pact/PactFlow 属于这一层。 | 不验证内部实现和 UI 流程。 |
| E2E 端到端测试 | 关键用户路径或端到端业务链路。 | 不覆盖所有细节，不替代 unit/integration/contract。 |

Architecture check、static analysis、smoke、canary 是质量门禁/上线验证，不是第 5 类测试。

## 测试应该服务架构

- 业务测试不应理解 provider、transport、storage、framework 或 tool 内部细节。
- Adapter 测试应证明外部 contract 与内部模型之间的转换。
- Contract test 应保护 payload 形状、版本、兼容性和错误行为；Pact/PactFlow 可用于 consumer/provider contract。
- 需要生成 Pact consumer test、provider verification、Pact Broker/PactFlow、can-i-deploy 配置或诊断时，使用 `pactflow` skill；TEA 只负责判断这里需要 Contract Test。
- 架构检查应在技术栈支持时强制依赖方向。
- 回归测试应先能复现已观察到的 bug，再通过真实公开表面验证修复。

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
