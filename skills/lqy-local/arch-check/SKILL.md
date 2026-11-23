---
name: arch-check
description: 用 arch-check 只读分析当前或指定代码项目，交付可点击的架构图、模块职责、合约和有依据的问题；支持已有 Python 依赖规则和复杂度对照。
---

# 架构阅读与验证

目标默认是**调用者的项目**，不是工具仓库。遵守目标项目的 AGENTS.md 和授权范围，不执行目标项目、测试或安装脚本。此技能调用可信的独立 arch-check checkout（默认 `$HOME/work/arch-check`，其它位置设 `ARCH_CHECK_HOME`）；需要本机 Node 和工具支持的 GitNexus（当前 1.6.12），Python 检查另需 python3。缺依赖时说明缺哪一项，不下载、不改目标配置。

把 `AC` 设为**本技能目录**中的 [scripts/arch-check](scripts/arch-check) 的绝对路径。用本次全新的外部输出目录（位于目标源码树之外）保存 facts、报告和 view。以下是 Agent 的工作，不让用户填写 JSON：

1. 运行 `"$AC" guide` 阅读与工具版本配套的批处理流程和报告协议，然后 `"$AC" prepare "$TARGET" "$OUT/facts"`。按需筛选 agent-context.json 的文件、符号、关系和 unknowns，再按需读同一快照的源码与项目说明。预算超限或范围受限时说明缺口；不要用内置示例替代。
2. 用当前 Codex 会话解释项目用途、Module、Interface、Contract 和主要协作。按协议写 `$OUT/report.json`：绑定本次 input_id、真实符号、精确引文；观察到的调用与推断分开。等待/释放疑点可按协议写 source_concerns；说明触发条件、影响、验证方法和未覆盖范围，不把阅读当成复现。
3. 运行 `"$AC" publish "$OUT/facts" "$OUT/report.json" "$OUT/view"`。核对 **view/index.html** 打开的是这次的项目、能从图上选中模块、追到相应证据，而非工具默认页。返回可打开的绝对路径、重要发现与局限。
4. 用户要看问题时，复用已有可执行判据。项目提供了有效声明和规则才运行 `"$AC" lint "$TARGET" DECLARATIONS RULES`（后两项相对目标或为目标内绝对路径）；保留 JSON 及退出码，1 为已见违规，2 为覆盖不足，不能当作“无问题”。Python 复杂度用 `"$AC" compare "$BEFORE" "$AFTER"`；没有另一个版本时可两边传同一 Python 范围，读取 after 的函数指标，不声称发生回归。若要在图上显示 lint，使用阅读器现有的同项目收据导入并核对快照；没有绑定的项目不要沿用结果。将机器违规、度量信号、源码待复核和未验证明确分开；运行或模型证据缺失就写未验证，不打架构总分。
