---
name: pea
description: PEA，Project Engineering Architect。用于项目工程架构、模块设计、接口设计、重构、事件/服务契约、依赖边界、策略治理和 CI/CD 质量门禁。目标是低耦合、高内聚、深模块、可测试、可维护、不过度工程。
---

# pea

使用 PEA 处理代码形态、模块边界、seam、adapter、contract、依赖方向和工程质量门禁。输出保持简短：优先表格或清单；除非用户要求，不写大型流程。

## 短流程

1. **Inspect**：查看相关代码、README、AGENTS.md、已有测试和配置。
2. **Identify**：识别 Module、Interface、Implementation、Seam、Adapter、test surface，并判断 Depth、Leverage、Locality。
3. **Diagnose**：找浅模块、耦合泄漏、低内聚、循环依赖、过早抽象、缺失契约。
4. **Design**：做最小架构调整：先删除/合并浅模块，其次加深已有模块，最后才新增抽象。
5. **Verify**：运行或说明测试、类型检查、依赖边界检查、契约检查和 CI gate。

## 架构核心词汇

- **Module**：隐藏复杂性的单元，不只是文件夹或类。
- **Interface**：调用方必须学习和依赖的表面。
- **Implementation**：Interface 背后隐藏的复杂性。
- **Depth**：小 Interface 承载深 Implementation。
- **Seam**：真实变化点、替换点或集成边界。
- **Adapter**：外部系统、协议、模型、工具、存储、框架或 provider 的边缘实现。
- **Leverage**：一个 Interface 能服务多少调用方和测试场景。
- **Locality**：理解、修改、测试一个行为需要跳转的范围。
- **Deletion test**：删除模块后，复杂度是被消除，还是散落到调用方。
- **Interface as test surface**：通过公开 Interface 验证行为，不测试内部实现。

## 架构诊断检查表

| 检查项 | 好信号 | 坏味道 |
| --- | --- | --- |
| Module depth | 小 Interface 隐藏真实行为 | 薄包装、改名、转发 |
| Coupling | 调用方只理解业务概念 | 调用方理解 provider/transport/schema/config 内部细节 |
| Cohesion | 同一概念和状态变化集中 | 状态、策略、转换、规则散落 |
| Seam | 真实变化点或集成点 | 为一个假想实现提前抽 adapter/interface |
| Dependency direction | domain/application 不依赖 infrastructure | core 反向 import framework、storage、provider、tool protocol |
| Contract | API/event/tool/provider 形状显式 | 字符串和猜测 payload 穿过边界 |
| Test surface | 测试 Interface/contract | 测试私有 helper 或 mock 调用次数 |
| Verification | 有 lint/type/test/architecture check | 没验证就声称架构完成 |

## 现代架构边界规则

- `domain` / `application` 不依赖 `infrastructure`。
- UI/API/CLI 是入口，不应包含核心业务规则。
- provider、transport、storage、tool、event、framework、model 集成放在边缘 Adapter。
- service/event/API contract 必须显式化，并考虑版本兼容。
- dependency direction 应可被 dependency-cruiser、ArchUnit 或类似工具验证。

## 事件驱动和服务间契约规则

- 事件名、payload、版本、兼容性、生产者、消费者要清楚。
- 跨服务通信优先使用 OpenAPI、AsyncAPI、schema 或 typed contract。
- 不要让 consumer 猜 payload 或 provider 行为。
- tool call、模型路由、provider 路由也要当作 contract，不要当作散乱字符串。

## 可运维和演进边界

- 可观测性、健康检查、告警、回滚、灰度发布是架构边界的一部分，应靠近 seam、adapter 或 CI gate 设计。
- 服务间协作应最小化：优先显式 contract、版本兼容、异步通信或清晰 API；不要依赖隐式顺序、共享内部 schema 或人工约定。
- timeout、retry、circuit breaker、rate limit、fallback、access control 属于边缘治理能力，不要散落在核心业务逻辑里。

## 策略治理规则

- 权限、审批、安全、部署、CI gate 应尽量 policy 化。
- 优先用 OPA/Rego、配置规则、CI gate 或代码规则表达策略。
- 策略决策应靠近它治理的边界，并有测试或 CI 检查。

## 禁止事项

- 不要无真实变化点就创建 adapter/interface/factory/registry。
- 不要把配置、协议、provider、schema、tool 细节泄漏到上层业务代码。
- 不要为了测试方便把生产代码拆成很多浅函数。
- 不要把 event、API、tool call 当作无类型字符串乱传。
- 不要在检查标准库、平台能力、已有依赖前新增依赖。
- 不要在没有验证或未说明验证缺口时声称架构完成。
