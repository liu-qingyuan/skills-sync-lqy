---
name: tdd-zh
description: 测试驱动开发。用于用户想以 test-first 方式构建功能或修复 bug，提到 red-green-refactor，或需要集成测试时。
---

# 测试驱动开发

TDD 是 red → green 循环。这个 skill 是让该循环产出值得保留的测试的参考：什么是好测试、测试应该放在哪里、反模式，以及循环规则。每个 section 都适用于每一轮 cycle；在循环前和循环中查阅，而不是结束后才看。

探索代码库时，读取 `CONTEXT.md`（如果存在），让测试名称和 interface 词汇匹配项目领域语言，并尊重你触及区域的 ADR。

## 什么是好测试

测试通过 public interface 验证行为，而不是实现细节。代码可以完全改变；测试不应该。好的测试读起来像 specification：`user can checkout with valid cart` 清楚说明存在什么能力。它能在重构中存活，因为它不关心内部结构。

示例见 [tests.md](tests.md)，mocking guideline 见 [mocking.md](mocking.md)。

## Seams — 测试放在哪里

**seam** 是你测试的 public boundary：你在这个 interface 上观察行为，而不是伸进内部。测试存在于 seam 上，永远不要测试 internals。

**只在预先商定的 seams 上测试。** 写任何测试前，先写下要测试的 seams，并和用户确认。未经确认的 seam 上不写测试。你无法测试一切；预先同意 seams 是为了把测试工作放在 critical paths 和 complex logic 上，而不是每个 edge case。

问：“public interface 是什么？哪些 seams 应该测试？”

## 反模式

- **Implementation-coupled** — mock 内部 collaborators、测试 private methods，或通过 side channel 验证（例如绕过 interface 直接查数据库）。信号是：重构时测试坏了，但行为没变。
- **Tautological** — assertion 用与代码相同的方式重新计算 expected value（`expect(add(a, b)).toBe(a + b)`、用同样方式手算 snapshot、常量等于自身），所以它按构造必然通过，永远无法和代码产生分歧。Expected values 必须来自独立 source of truth：known-good literal、worked example 或 spec。
- **Horizontal slicing** — 先写完所有测试，再写所有实现。批量测试验证的是_想象中的行为_：你测试的是东西的 _shape_，而不是 user-facing behavior；测试对真实变化不敏感，而且你会在理解实现之前承诺测试结构。改用 **vertical slices**：一个测试 → 一个实现 → 重复。每个测试都是 **tracer bullet**，回应上一轮 cycle 学到的东西。

## 循环规则

- **Red before green.** 先写 failing test，再只写足够让它通过的代码。不要预判未来测试，也不要加 speculative features。
- **One slice at a time.** 每个 cycle 只处理一个 seam、一个 test、一个 minimal implementation。
- **Refactoring is not part of the loop.** 它属于 review stage（见 `code-review-zh` skill），不属于 red → green implementation cycle。
