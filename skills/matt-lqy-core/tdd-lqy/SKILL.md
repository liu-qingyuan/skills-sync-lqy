---
name: tdd-lqy
description: 测试驱动开发与测试策略。用于 test-first 功能或 bug、red-green-refactor，或需要决定测试层级、mock 边界和 contract 覆盖时。
---

# 测试驱动开发

## 合同

- 通过公开 Interface 验证可观察行为；Implementation 可以重写，测试不应因此变化。
- Feature 证明某个 abstraction 需要存在。在第一个 RED 前，确定满足当前需求的最小完整 Interface；每个 cycle 都通过该 Interface 增加行为，不要让单个测试长出 one-off public method、mode 或特殊分支。
- 按风险选择最低足够测试层级；层级、mock 或 contract 边界不明确时，读取 [TEST-STRATEGY.md](TEST-STRATEGY.md)。
- 读取项目 `CONTEXT.md` 和相关 ADR；优先从 spec、现有代码和测试确定合同，只有真实歧义才询问用户。
- Module、Interface、Seam 或知识归属需要改变时，在第一个 RED 前使用 `$codebase-design-lqy`。

测试示例见 [tests.md](tests.md)，mock 约束见 [mocking.md](mocking.md)。

## 循环

### 1. 选定行为

确认当前测试命令、公开 Interface 和最高优先级行为。Bug fix 先通过公开表面复现已观察回归。不要预先写完所有测试。

### 2. RED

只写一个测试，并确认它因为缺少目标行为而失败，而不是环境、fixture 或拼写问题。

### 3. GREEN

写满足当前合同的最小实现并运行聚焦测试。最小实现不等于 one-off patch；不得增加未来功能、推测性抽象或只服务当前测试的生产入口。

### 4. REFACTOR

只在绿色时重构。新代码出现具体设计证据时，按需使用 `$codebase-design-lqy` 的设计审查；一次只做一个最小结构改动，并立即重跑测试。不要按代码长度、重复外观或测试便利机械拆 helper、class 或 value object。

### 5. 重复

为下一个最重要行为重复 RED → GREEN → REFACTOR，直到当前验收完成。

## 反模式

不要先批量写测试再批量实现。这种 horizontal slice 会提前承诺 imagined behavior 和测试结构。使用 tracer bullet / vertical slice：一个行为、一个 RED/GREEN cycle、一次反馈。

## 停止条件

- 测试通过公开 Interface 保护当前行为或合同。
- 测试层级足以发现当前风险，没有扩大到所有边缘情况。
- 生产代码没有测试专用入口或 speculative feature。
- 聚焦测试与相关完整测试套件均已运行，或明确说明无法运行的原因。
