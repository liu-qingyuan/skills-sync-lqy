---
name: scaffold-exercises-lqy
description: 创建练习目录结构，包括 sections、problems、solutions 和 explainers，并确保通过 lint。用于用户想
  scaffold exercises、创建练习 stub 或设置新课程章节时。
---

# 脚手架练习

创建通过“pnpm ai-hero-cli 内部 lint”的练习目录结构，然后使用“git commit”提交。

## 目录命名

- **部分**：`练习/`内的`XX-部分名称/`（例如，`01-retrieval-skill-building`）
- **练习**：节内的“XX.YY-exercise-name/”（例如，“01.03-retrieval-with-bm25”）
- 章节编号 = `XX`，练习编号 = `XX.YY`
- 名称为破折号（小写、连字符）

## 练习变体

每个练习至少需要以下子文件夹之一：

- `问题/` - 带有 TODO 的学生工作区
- `solution/` - 参考实现
- `explainer/` - 讲解材料，无 TODO

存根时，默认为“explainer/”，除非计划另有指定。

## 所需文件

每个子文件夹（`problem/`、`solution/`、`explainer/`）都需要一个 `readme.md`：

- **不为空**（必须有真实内容，即使是单个标题行也可以）
- 没有损坏的链接

存根时，创建一个带有标题和描述的最小自述文件：
```md
# Exercise Title

Description here
```
如果子文件夹有代码，它还需要一个 `main.ts` （>1 行）。但对于存根来说，仅自述文件练习就可以了。

## 工作流

1. **解析计划** - 提取部分名称、练习名称和变体类型
2. **创建目录** - 为每个路径`mkdir -p`
3. **创建存根自述文件** - 每个变体文件夹一个带有标题的“readme.md”
4. **运行 lint** - `pnpm ai-hero-cli 内部 lint` 进行验证
5. **修复任何错误** - 迭代直到 lint 通过

## Lint 规则总结

linter（`pnpm ai-hero-cli 内部 lint`）检查：

- 每个练习都有子文件夹（`problem/`、`solution/`、`explainer/`）
- 至少存在“problem/”、“explainer/”或“explainer.1/”之一
- `readme.md` 在主子文件夹中存在且非空
- 没有`.gitkeep`文件
- 没有 `speaker-notes.md` 文件
- 自述文件中没有损坏的链接
- 自述文件中没有“pnpm runexercise”命令
- 每个子文件夹都需要`main.ts`，除非它是只读的

## 移动/重命名练习

重新编号或移动练习时：

1. 使用 `git mv` （不是 `mv`）重命名目录 - 保留 git 历史记录
2.更新数字前缀以维持顺序
3. 移动后重新运行 lint

示例：
```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```
## 示例：从计划中存根

给定一个像这样的计划：
```
Section 05: Memory Skill Building
- 05.01 Introduction to Memory
- 05.02 Short-term Memory (explainer + problem + solution)
- 05.03 Long-term Memory
```
创造：
```bash
mkdir -p exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer
mkdir -p exercises/05-memory-skill-building/05.02-short-term-memory/{explainer,problem,solution}
mkdir -p exercises/05-memory-skill-building/05.03-long-term-memory/explainer
```
然后创建自述文件存根：
```
exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer/readme.md -> "# Introduction to Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/explainer/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/problem/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/solution/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.03-long-term-memory/explainer/readme.md -> "# Long-term Memory"
```
