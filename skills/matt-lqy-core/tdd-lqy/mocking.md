# Mock 边界

仅在 [TEST-STRATEGY.md](TEST-STRATEGY.md) 判断需要 test double 后使用。

- Mock/fake/stub 真实外部边界或难构造失败场景，不 mock 当前要验证的行为和合同。
- 在 composition root 或 Module 构造时替换外部依赖；不要把 provider 参数泄漏到每次业务调用。
- Test double 应满足同一 typed contract；优先断言可观察结果，不断言内部调用次数和顺序。
- 不要仅为测试创建生产 Interface；Seam 必须对应真实外部系统、协议、存储、provider 或变化点。
