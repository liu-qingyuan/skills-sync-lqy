---
name: code-review-lqy
description: 从固定点（commit、branch、tag 或 merge-base）开始沿两个轴审查变更：Standards 和 Spec。用于用户想审查 branch、PR、WIP 变更或“review since X”时。
---

# Code Review

审查 `git diff <fixed-point>...HEAD`：

- **Standards**：是否符合仓库规则和 Fowler smell baseline。
- **Spec**：是否忠实实现来源 issue / PRD / spec。

有 spec 时，两个轴由两个 `general-purpose` sub-agents 并行检查并分别报告，避免上下文和结论互相污染。

issue tracker 配置见 `docs/agents/issue-tracker.md`；缺失时运行 `$setup-matt-pocock-skills-lqy`。默认使用中文，保留 labels、命令、路径、代码标识符、配置键和错误原文。

## 1. 固定范围

用户必须提供 fixed point；没有就询问。只解析和记录一次：

```bash
git rev-parse <fixed-point>
git diff <fixed-point>...HEAD
git log <fixed-point>..HEAD --oneline
```

引用无效或 diff 为空时停止，不启动 sub-agent。

## 2. 收集依据

按顺序查找 spec：commit message 中的 issue 引用、用户提供的路径、`docs/` / `specs/` / `.scratch/` 中匹配 branch 或 feature 的文件。仍未找到时询问用户；确认没有 spec 后跳过 Spec 轴并报告 `no spec available`。

Standards 来源包括仓库的 `CODING_STANDARDS.md`、`CONTRIBUTING.md` 等规则，以及 [Fowler smell baseline](references/fowler-smells.md)。审查前完整读取 baseline；仓库规则优先，smell 只是 judgment call，并跳过工具已强制执行的内容。

## 3. 并行审查

有 spec 时在一条消息中启动两个 agents；无 spec 时只启动 Standards：

- **Standards**：提供 diff 命令、提交列表、standards 文件和 baseline 的绝对路径。要求逐 file/hunk 报告规则违反或 possible smell，引用规则与 hunk，区分硬性违反和 heuristic；中文，最多 400 字。
- **Spec**：提供 diff 命令、提交列表和 spec。要求报告缺失/部分实现、scope creep、看似实现但行为错误的要求，并引用 spec；中文，最多 400 字。

若环境没有 sub-agent，当前 agent 分开执行两轴，仍不得合并发现。

## 4. 输出

分别输出 `## Standards` 和 `## Spec`，不跨轴合并或重排 findings。最后一行汇总每轴 finding 数量及该轴最严重问题；不要选跨轴 winner。
