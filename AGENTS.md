# AI Coding Agent 常驻规则

## 架构默认规则

- 优先低耦合、高内聚、清晰 seam、深模块。
- Module 是隐藏复杂性的单元；Interface 要小，Implementation 可以深。
- 修改架构相关代码前，先识别：Module、Interface、Implementation、Depth、Seam、Adapter、Leverage、Locality、test surface；需要总体规划时先查 `docs/architecture/`；用 C4 统一映射 Context/Container/Component/Code-Class，并按 Module/Boundary/Contract/Governance 四维检查；涉及边界、职责、契约、协作或治理变化时，先读取/更新对应 C4、类图或时序图，再按图判断代码划分是否合理，最后改代码。
- 业务/应用逻辑不要依赖 infrastructure、framework、transport、storage、provider、tool、event 的实现细节。
- UI/API/CLI 是入口层，不放核心业务规则。
- Adapter 只用于真实外部系统、协议、存储、工具、provider、模型或框架；不要为假想未来变化提前创建。
- 避免耦合泄漏：调用方不应被迫理解 provider、transport、schema、配置文件、工具事件或框架内部细节。

## 测试默认规则

- Interface as test surface：测试公开行为和契约，不测试私有实现细节。
- 优先围绕 seam、adapter、contract 写测试，让内部实现可替换。
- 不要为了测试方便把生产代码拆成很多浅函数。
- API、event、tool protocol、provider、service 边界应有 contract test。

## 依赖和抽象规则

- 不默认新增抽象：没有真实变化点，就不要新增 interface、factory、registry、plugin system、adapter、config 或 layer。
- 先删除或合并浅模块，再考虑加深模块，最后才新增抽象。
- 优先标准库、平台能力和已有依赖；新增依赖必须有明确收益。
- service/event/API 通信必须有显式契约：typed contract、schema、OpenAPI、AsyncAPI 或等价形式。
- 依赖方向应尽量可被 dependency-cruiser、ArchUnit 或类似工具验证。

## 验证规则

- 如果项目已有 lint、typecheck、test、contract、smoke、architecture check 命令，改动后运行相关命令。
- 如果无法运行验证命令，必须说明原因和替代验证方式。
- 没有当前验证证据，不要声称架构或测试已完成。
- 除非用户明确要求，不要生成 ADR、长篇架构文档、Design It Twice 或完整工程生命周期流程。

## Agent skills

### Issue tracker

GitHub issues；外部 PR 不作为 triage 请求入口。见 `docs/agents/issue-tracker.md`。

### Triage labels

使用 `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。见 `docs/agents/triage-labels.md`。

### Domain docs

单上下文：根目录 `CONTEXT.md`，ADR 按需放在 `docs/adr/`。见 `docs/agents/domain.md`。
