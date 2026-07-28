# 测试判断

## 好的测试

- 通过当前公开 Interface 验证调用方可观察的行为或合同。
- 使用能证明风险的最低足够层级，并运行真实的目标代码路径。
- 在不改变行为时允许 Implementation、私有 helper 和内部协作完全重构。
- 名称表达业务行为或回归条件，而不是内部调用步骤。

## 糟糕的测试

- 测试私有方法、mock 调用次数、临时数据 shape 或内部执行顺序。
- 生产行为未变时，仅因内部重命名或重组而失败。
- 为 imagined behavior 批量承诺测试结构。

业务行为测试优先通过业务 Interface 观察结果。Adapter、contract 或 storage integration test 可以直接检查对应协议、schema 或真实存储状态；这不是绕过 Interface，因为该边界本身就是测试目标。
