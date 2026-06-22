---
name: pea
description: PEA，Project Engineering Architect。用于项目工程架构、模块设计、接口设计、重构、C4 宏观到微观架构规划、Mermaid 类图和时序图实现视图、事件模型、领域模型、契约模型、依赖边界、策略治理和 CI/CD 质量门禁。按 Module、Boundary、Contract、Governance 四类架构职责判断，目标是低耦合、高内聚、深模块、可测试、可维护、不过度工程。
---

# pea

使用 PEA 处理代码形态、模块边界、seam、adapter、contract、依赖方向和工程质量门禁。输出保持简短：优先表格或清单；除非用户要求，不写大型流程。

## 短流程

1. **Inspect**：查看相关代码、README、AGENTS.md、`docs/architecture/`、已有测试和配置。
2. **Identify**：识别 Module、Interface、Implementation、Seam、Adapter、Contract、test surface。
3. **Diagnose**：按 4 类架构职责找浅模块、耦合泄漏、低内聚、循环依赖、过早抽象、缺失契约。
4. **Design**：做最小架构调整：先删除/合并浅模块，其次加深已有模块，最后才新增抽象；涉及架构变更时先选 C4 层级，用 PEA 四维检查，再更新必要的类图/时序图，最后改代码。
5. **Verify**：运行或说明测试、类型检查、依赖边界检查、契约检查、架构图/类图/时序图一致性检查和 CI gate。


## C4 主线 + PEA 检查维度

- 总体系统架构规划优先调用 `c4-architecture` skill；补充类图、时序图优先调用 `mermaid-visualizer` skill。
- 先读取项目已有 `docs/architecture/` 作为当前标准；不要凭空覆盖已有架构约定。
- C4 是观察尺度：Context → Container → Component → Code/Class，从宏观到微观。
- PEA 四类职责不是四张图，而是每个 C4 层级上的检查维度：Module、Boundary、Contract、Governance。
- Code 层实现细节优先用类图表达；复杂调用顺序、事件流、tool/provider/API 交互用时序图表达。
- Deployment/Dynamic/Sequence 是支持图：Deployment 偏 Governance，Dynamic/Sequence 偏 Boundary + Contract。
- 架构修改顺序：先选需要的 C4 层级，用 PEA 四维检查，再更新必要的类图/时序图，最后改代码并验证图、代码、测试一致。
- 默认路径：C4 图放 `docs/architecture/c4-*.md`；类图放 `docs/architecture/class-{module-or-feature}.md`；时序图放 `docs/architecture/sequence-{flow}.md`。
- 不要为了画图而画图；只有边界、职责、契约、调用顺序或实现关系会影响修改时才补图。

## PEA 的 4 类架构职责

| PEA 分类 | 中文 | 负责什么 |
| --- | --- | --- |
| **Module Architecture** | 模块架构 | deep module、small interface、high cohesion、low coupling、locality、deletion test。 |
| **Boundary Architecture** | 边界架构 | domain/application/infrastructure 分层，seam、adapter、provider、transport、storage、tool/event 边界。 |
| **Contract Architecture** | 契约架构 | API contract、event contract、tool protocol、provider contract、OpenAPI、AsyncAPI、schema、typed contract。 |
| **Governance Architecture** | 治理架构 | dependency direction、cycle detection、architecture rule、policy-as-code、CI/CD quality gate、dependency-cruiser、ArchUnit、OPA。 |

## C4 × PEA 矩阵

| C4 层级 | Module | Boundary | Contract | Governance |
| --- | --- | --- | --- | --- |
| Context | 系统职责是否单一清楚 | 系统边界、外部 actor、外部系统 | 外部 API/event/service 契约 | 外部依赖、权限、合规、安全边界 |
| Container | app/service/db/queue 职责是否高内聚 | domain/application/infrastructure、adapter、部署单元边界 | 服务间 API/event/tool/provider contract | 依赖方向、CI gate、运行时策略 |
| Component | 组件是否 deep module | seam、adapter、组件依赖方向 | 组件接口、schema、provider contract | architecture check、cycle check |
| Code/Class | interface 是否小、implementation 是否深 | class/type 依赖是否泄漏 | typed interface、schema、错误模型 | lint、typecheck、unit/contract/boundary check |

## 三个核心模型

| 模型 | PEA 负责什么 |
| --- | --- |
| 领域模型 DDD | 聚合、实体、值对象、领域服务、用例边界和业务规则归属。 |
| 事件模型 | 事件名、payload、版本、生产者/消费者、顺序、幂等和兼容性。 |
| 契约模型 | API/event/tool/provider/CLI 的输入输出、错误、schema/type 和版本。 |

## 架构核心词汇

- **Module**：隐藏复杂性的单元，不只是文件夹或类。
- **Interface**：调用方必须学习和依赖的表面。
- **Implementation**：Interface 背后隐藏的复杂性。
- **Depth**：小 Interface 承载深 Implementation。
- **Seam**：真实变化点、替换点或集成边界。
- **Adapter**：外部系统、协议、模型、工具、存储、框架或 provider 的边缘实现。
- **Contract**：跨模块、服务、事件、工具或 provider 的显式约定。
- **Leverage**：一个 Interface 能服务多少调用方和测试场景。
- **Locality**：理解、修改、测试一个行为需要跳转的范围。
- **Deletion test**：删除模块后，复杂度是被消除，还是散落到调用方。
- **Interface as test surface**：通过公开 Interface 验证行为，不测试内部实现。

## Module Architecture：模块架构

- 优先 deep module：small Interface + deep Implementation。
- 保持高内聚：同一业务概念、领域规则、状态变化、协议转换、策略判断尽量集中。
- 保持低耦合：调用方依赖 Interface，不依赖 Implementation 细节。
- 用 Locality 判断好坏：理解、修改、测试一个行为不应到处跳转。
- 用 Deletion test 判断浅模块：删除后复杂度如果只是散落到调用方，就说明它可能有价值；如果复杂度消失，优先删除。
- 不要把一个行为拆成很多只转发、改名、薄包装的一两行 helper。

## Boundary Architecture：边界架构

- `domain` / `application` 不依赖 `infrastructure`。
- UI/API/CLI 是入口，不应包含核心业务规则。
- provider、transport、storage、tool、event、framework、model 集成放在边缘 Adapter。
- Seam 必须是真实变化点、替换点或集成点；不要为了假想未来提前抽 seam。
- 一个实现通常不抽 Adapter；两个以上真实外部系统、协议、provider、存储或模型时，Adapter 才更合理。
- 避免耦合泄漏：业务代码不应知道 provider、transport、schema、配置文件、工具事件或框架内部细节。
- 可观测性、健康检查、告警、回滚、灰度发布是架构边界的一部分，应靠近 seam、adapter 或 CI gate 设计。
- timeout、retry、circuit breaker、rate limit、fallback、access control 属于边缘治理能力，不要散落在核心业务逻辑里。

## Contract Architecture：契约架构

- service/event/API/tool/provider contract 必须显式化，并考虑版本兼容。
- 事件模型要清楚：事件名、payload、版本、兼容性、生产者、消费者、顺序和幂等。
- 跨服务通信优先使用 OpenAPI、AsyncAPI、JSON Schema、Zod schema、Protobuf 或 typed contract。
- 不要让 consumer 猜 payload 或 provider 行为。
- tool call、模型路由、provider 路由也要当作 contract，不要当作散乱字符串。
- PEA 定义 contract；TEA 用 Contract Test 验证 contract。

## Governance Architecture：治理架构

- dependency direction 应可被 dependency-cruiser、ArchUnit 或类似工具验证。
- 用 architecture boundary check 防止 domain 依赖 infrastructure、application 依赖 UI、adapter 反向依赖 core。
- 用 cycle detection 防止循环依赖。
- 权限、审批、安全、部署、CI gate 应尽量 policy 化。
- 优先用 OPA/Rego、配置规则、CI gate 或代码规则表达策略。
- 服务间协作应最小化：优先显式 contract、版本兼容、异步通信或清晰 API；不要依赖隐式顺序、共享内部 schema 或人工约定。

## 架构诊断检查表

| 检查项 | 好信号 | 坏味道 |
| --- | --- | --- |
| Module | 小 Interface 隐藏真实行为 | 薄包装、改名、转发 |
| Boundary | domain/application 不依赖 infrastructure | core 反向 import framework、storage、provider、tool protocol |
| Contract | API/event/tool/provider 形状显式 | 字符串和猜测 payload 穿过边界 |
| Governance | 有依赖方向、循环依赖、policy、CI gate 检查 | 靠人工记忆防止架构漂移 |
| Architecture docs | C4 层级、PEA 四维、类图、时序图、代码、测试一致 | 图过期或代码绕过图上的边界 |
| Verification | 有 lint/type/test/architecture check | 没验证就声称架构完成 |

## 禁止事项

- 不要无真实变化点就创建 adapter/interface/factory/registry。
- 不要把配置、协议、provider、schema、tool 细节泄漏到上层业务代码。
- 不要为了测试方便把生产代码拆成很多浅函数。
- 不要把 event、API、tool call 当作无类型字符串乱传。
- 不要在检查标准库、平台能力、已有依赖前新增依赖。
- 不要在没有验证或未说明验证缺口时声称架构完成。
- 不要在 C4 层级、PEA 四维、类图或时序图未同步时声称架构修改完成。
