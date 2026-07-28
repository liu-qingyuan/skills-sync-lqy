# 测试策略

仅在测试层级、mock 或 contract 边界不明确时读取。目标是用最低足够层级证明当前风险，而不是增加测试数量。

## 层级

- 纯计算和领域规则：unit。
- Module 内多个真实协作者：integration。
- API、event、CLI、tool、provider、storage 或 schema 边界：contract 或边界 integration。
- 关键用户链路：E2E；不要用 E2E 覆盖所有细节。

优先沿用仓库已有测试形态和命令。更高层测试只有在较低层无法证明当前风险时才增加。

## Mock 边界

不要 mock 当前要验证的公开行为、contract、Adapter 转换或关键集成边界。外部不稳定、高成本系统和难构造失败场景可以 fake/mock/stub，但关键假设应另有 contract 或 integration 证据。

外部依赖在 composition root 或 Module 构造时注入；不要为了测试让每个业务调用方传递 provider，也不要只为 mock 创建没有真实变化点的 Interface。

## Contract

优先复用 OpenAPI、AsyncAPI、JSON Schema、typed model、Protobuf 或项目已有格式。非 HTTP 边界同样包含 stdin/stdout、exit code、stderr、message、tool 和 provider protocol。

业务行为测试通常通过业务 Interface 断言；Adapter 或 storage integration test 可以直接检查真实边界状态，因为该边界本身就是测试表面。
