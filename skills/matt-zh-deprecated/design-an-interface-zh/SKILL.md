---
name: design-an-interface-zh
description: 为模块生成多个差异很大的接口设计，并使用并行 sub-agents。用于用户想设计 API、探索接口选项、比较模块形状或提到 design
  it twice 时。
---

# design-an-interface-zh

> 这是 Matt Pocock `design-an-interface` skill 的中文本地化版本。官方英文上游保留在 `skills/deprecated/design-an-interface`；本目录可按中文团队习惯继续调整。

## 本地化说明

- 优先用中文与用户沟通。
- 保留上游流程、检查点和文件约定。
- 如果本文件与上游英文版本冲突，以本中文版本为准；同步上游时先比较差异，再合并。

# 设计一个界面

基于《软件设计哲学》中的“两次设计”：你的第一个想法不太可能是最好的。生成多个完全不同的设计，然后进行比较。

## 工作流程

### 1. 收集需求

设计之前，先了解：

- [ ] 该模块解决什么问题？
- [ ] 来电者是谁？ （其他模块、外部用户、测试）
- [ ] 有哪些关键操作？
- [ ] 有什么限制吗？ （性能、兼容性、现有模式）
- [ ] 什么应该隐藏在里面，什么应该暴露？

问：“这个模块需要做什么？谁会使用它？”

### 2. 生成设计（并行子代理）

使用任务工具同时生成 3 个以上子代理。每个人都必须产生一种**完全不同的**方法。
```
Prompt template for each sub-agent:

Design an interface for: [module description]

Requirements: [gathered requirements]

Constraints for this design: [assign a different constraint to each agent]
- Agent 1: "Minimize method count - aim for 1-3 methods max"
- Agent 2: "Maximize flexibility - support many use cases"
- Agent 3: "Optimize for the most common case"
- Agent 4: "Take inspiration from [specific paradigm/library]"

Output format:
1. Interface signature (types/methods)
2. Usage example (how caller uses it)
3. What this design hides internally
4. Trade-offs of this approach
```
### 3. 展示设计

显示每个设计：

1. **接口签名** - 类型、方法、参数
2. **使用示例** - 调用者如何在实践中实际使用它
3. **它隐藏了什么** - 复杂性保持在内部

按顺序呈现设计，以便用户可以在比较之前吸收每种方法。

### 4. 比较设计

显示所有设计后，将它们进行比较：

- **接口简单**：方法更少，参数更简单
- **通用与专用**：灵活性与专注
- **实施效率**：形状是否允许高效的内部结构？
- **深度**：隐藏显着复杂性的小接口（好）与实施薄弱的大接口（坏）
- **正确使用的难易程度** vs **误用的难易程度**

用散文而不是表格来讨论权衡。突出显示设计差异最大的地方。

### 5. 综合

通常，最好的设计结合了多种选择的见解。问：

- “哪种设计最适合您的主要用例？”
- “其他设计中有哪些值得融入的元素？”

## 评价标准

摘自《软件设计哲学》：

**界面简单**：更少的方法，更简单的参数=更容易学习和正确使用。

**通用**：无需更改即可处理未来的用例。但要注意过度概括。

**实施效率**：接口形状是否允许高效实施？或者强迫尴尬的内部？

**深度**：隐藏显着复杂性的小接口=深度模块（好）。大接口与薄实现=浅模块（避免）。

## 反模式

- 不要让子代理产生相似的设计 - 强制执行根本差异
- 不要跳过比较——价值是对比
- 不要实现 - 这纯粹是关于界面形状
- 不要根据实施工作进行评估