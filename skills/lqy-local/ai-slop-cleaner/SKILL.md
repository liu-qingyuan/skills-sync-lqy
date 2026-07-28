---
name: ai-slop-cleaner
description: "[OMX] 执行清除低质内容的 cleanup/refactor/deslop 工作流"
---

# AI Slop Cleaner Skill

采用回归测试优先、逐项处理异味的清理工作流，减少 AI 生成的低质内容，在保持行为不变的同时提升信息质量。

## 何时使用

在以下情况使用此 skill：
- 某条代码路径可以正常工作，但显得臃肿、杂乱、重复或抽象过度
- 用户要求对 AI 生成的输出执行 “cleanup”、“refactor” 或 “deslop”
- 后续实现留下了重复代码、死代码、薄弱边界、缺失的测试、类回退代码或不必要的包装层
- 需要在不进行大范围重写的前提下采用规范的清理工作流

## 与 GPT-5.5 指南对齐

- 除非存在风险或用户要求更多细节，否则输出应简洁且证据充分。
- 将较新的用户指令视为对局部工作流的更新，同时保留先前不冲突的约束。
- 持续检查、测试、诊断和验证，直到清理工作有充分依据。
- 自动推进明确且可逆的清理步骤；只有某项选择会实质性改变范围或行为时才询问。

## 文件列表范围与 Ralph 工作流

- 此 skill 可以使用 **文件列表范围**，而非整个功能区域。
- 当调用方提供变更文件列表时（例如 Ralph 会话负责的编辑），清理必须严格限制在这些文件内。
- 在 **Ralph 工作流** 中，强制 deslop 阶段应仅针对 Ralph 修改的文件运行此 skill；除非调用方明确要求其他模式，否则使用标准模式。

## 流程

1. **先用回归测试锁定行为**
   - 识别不得改变的行为
   - 编辑清理候选项前，添加或运行针对性的回归测试
   - 如果当前行为未经测试，先建立所需的最小范围测试覆盖
   - 对于类回退代码，在清理前覆盖主路径，以及要保留的任何兼容性/故障安全回退

2. **编码前制定清理计划**
   - 列出要消除的具体异味
   - 将本轮清理限制在指定的文件或范围内
   - 如果提供了文件列表范围，本轮清理必须限制在该变更文件列表内
   - 在计划中列出回退相关发现、分类和上报状态
   - 按从最安全、信号最明确到风险最高的顺序安排修复
   - 清理计划明确前不要开始编码

3. **编辑前清点类回退代码**
   - 在指定范围内搜索类回退检测信号：quick hacks、temporary workaround、temporary fallback、just bypass、just skip、fallback if it fails、swallowed errors、silent defaults、broad compatibility shims 和 duplicate alternate execution paths
   - 修改前对每项发现进行分类：
     - **Masking fallback slop** — 隐藏错误或证据、绕过主要契约、抑制测试或验证、吞掉失败、静默使用默认值，或添加未经测试的替代路径
     - **Grounded compatibility/fail-safe fallback** — 范围限定在外部系统、版本或故障安全边界内，记录了理由，保留失败证据，并且主路径和回退行为都有回归测试
   - 在保留回退路径前，优先修复根因、删除相关代码、修复边界或采用显式失败行为
   - 对范围广泛、含义不明、跨层或涉及架构的类回退代码，在编辑前调用 `$ralplan` 取得一致意见
   - 递归保护：如果已处于 ralplan、ralph、team 或其他 OMX 工作流中，不要再启动嵌套的 `$ralplan`；应记录该发现，并将其附加到当前 ralplan、leader 或 plan handoff 中

4. **编辑前对问题分类**
   - **类回退代码** — 掩盖问题的回退、变通分支、旁路、被吞掉的错误、静默默认值、宽泛的 shim、替代执行路径
   - **重复** — 重复逻辑、复制粘贴的分支、多余的辅助代码
   - **死代码** — 未使用的代码、无法到达的分支、过时的标志、遗留的调试代码
   - **不必要的抽象** — 纯转发包装器、臆测性间接层、仅使用一次的辅助层
   - **边界违规** — 隐藏耦合、职责泄漏、错误层级的导入或副作用
   - **UI/设计低质模式** — 将视觉输出视为依赖上下文的信号，而非绝对禁令；理由明确时，保留有意为之的品牌、设计系统、无障碍或产品上下文例外
     - 韩文正文过小：应质疑 11-12px 的正文；除非密集型系统明确支持较小字号且满足无障碍要求，否则韩文正文通常需要至少 14px
     - 无必要的层次感：当层级或可操作性不需要时，避免给每个 logo、表面、卡片、图标、背景和步骤块添加阴影
     - 重复的内容脚手架：精简重复的眉题 + 标题 + 描述 + 段落堆叠、填充式说明文字，以及没有增加含义的通用 emoji 徽章
     - 默认 AI 配色：缺少品牌、语义或系统依据时，应质疑 #3B82F6 等默认蓝色或紫色
     - 过度规整的网格：如果产品上下文更适合节奏变化、不对称、轮播切片、便当式构图或不同强调层级，应避免下意识采用统一的 3 列或 4 列卡片网格
     - 极端渐变：除非品牌或营销活动有意要求这种强度，否则应减弱 "AI demo" 渐变
   - **缺失的测试** — 行为未锁定、回归覆盖薄弱、边界情况存在缺口

5. **每轮只处理一种异味**
   - **类回退代码处置门禁** — 继续前，应移除掩盖问题的回退低质代码、修复根因，或上报含义不明的案例
   - **第 1 轮：删除死代码**
   - **第 2 轮：消除重复**
   - **第 3 轮：清理命名和错误处理**
   - **第 4 轮：加强测试**
   - 每轮结束后重新运行针对性验证
   - 避免将无关重构并入同一组编辑

6. **运行质量门禁**
   - 回归测试保持通过
   - Lint 通过
   - Typecheck 通过
   - 相关单元测试和集成测试通过
   - 如果有静态扫描或安全扫描，则应通过
   - diff 保持最小且不超出范围
   - 除非明确要求，否则不新增抽象或依赖

7. **最后提供证据充分的报告**
   - 变更的文件
   - 完成的简化
   - 回退相关发现、分类和上报状态
   - 已运行的测试、诊断和构建检查
   - 范围包含视觉或 UI 文件时，列出 UI/设计审查清单中的发现
   - 剩余风险
   - 后续事项或有意推迟的清理

## 输出格式

```text
AI SLOP CLEANUP REPORT
======================

Scope: [files or feature area]
Behavior Lock: [targeted regression tests added/run]
Cleanup Plan: [bounded smells and order]
Fallback Findings: [none, or finding -> masking fallback slop / grounded compatibility/fail-safe fallback -> escalation status]
UI/Design Findings: [none/N/A, or signal -> action taken/deferred -> intentional exception rationale]

Passes Completed:
- Fallback-like code resolution gate - [root-cause repair, explicit failure behavior, preserved grounded fallback, or ralplan handoff]
1. Pass 1: Dead code deletion - [concise fix]
2. Pass 2: Duplicate removal - [concise fix]
3. Pass 3: Naming/error handling cleanup - [concise fix]
4. Pass 4: Test reinforcement - [concise fix]

Quality Gates:
- Regression tests: PASS/FAIL
- Lint: PASS/FAIL
- Typecheck: PASS/FAIL
- Tests: PASS/FAIL
- Static/security scan: PASS/FAIL or N/A

Changed Files:
- [path] - [simplification]

Fallback Review:
- Findings: [fallback-like findings detected]
- Classification: [masking fallback slop | grounded fallback]
- Escalation Status: [none | raised to leader/ralplan | no escalation]

Remaining Risks:
- [none or short deferred item]
```

## 场景示例

**正确：** 测试已锁定行为且下一轮异味处理已经明确后，用户说 `continue`。继续执行下一轮范围明确的清理。

**正确：** 用户在规划后将范围缩小到某个文件。继续遵循回归测试优先的工作流，但只在新范围内执行。

**错误：** 在通过测试保护行为之前就开始重写架构。

**错误：** 将多个异味类别合并为一次大型重构，且不进行中间验证。

**错误：** 保留一个 `fallback if it fails` 分支，在吞掉错误后静默使用默认值，而不是修复根因或明确暴露失败。

**正确：** 针对特定版本的兼容 shim 范围明确、有文档记录、保留错误证据，主路径和回退路径都有回归测试，并作为 grounded compatibility/fail-safe fallback 报告。
