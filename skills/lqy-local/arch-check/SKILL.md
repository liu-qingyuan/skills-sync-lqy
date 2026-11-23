---
name: arch-check
description: 只读分析当前或指定项目，生成可点击的架构图；用源码、依赖规则和复杂度指标定位问题。
---

# arch-check

默认分析调用者的项目，不是工具仓库。遵守目标项目约定，不执行其代码、测试或安装脚本。使用可信 checkout（默认 `$HOME/work/arch-check`，可设 `ARCH_CHECK_HOME`）；缺 Node、GitNexus 或所需 Python 3 时说明，不自动安装。

用本技能的 [scripts/arch-check](scripts/arch-check) 作为 `AC`，在源码树外新建 `OUT`：

1. `"$AC" guide` 读取报告协议；`"$AC" prepare "$TARGET" "$OUT/facts"` 采集事实。
2. 当前会话阅读本次快照，按协议写 `$OUT/report.json`。用真实符号和精确引文解释职责、Interface、Contract 和协作；推断与已观察事实分开，不让用户填 JSON。
3. `"$AC" publish "$OUT/facts" "$OUT/report.json" "$OUT/view"`。打开 `view/index.html`，核对项目、可选模块及证据，返回页面绝对路径、发现和未覆盖范围。

**按需检查：** 有声明和规则时用 `lint TARGET DECLARATIONS RULES`，保留收据和退出码（1 有违规，2 覆盖不足）；只把匹配快照的收据挂到图上。用 `compare BEFORE AFTER` 看 Python 复杂度，同一版本只报当前指标。区分机器违规、度量信号、源码疑点和运行复现，不打架构总分。
