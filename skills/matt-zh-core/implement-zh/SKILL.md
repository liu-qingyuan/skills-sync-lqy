---
name: implement-zh
description: 根据 PRD 或一组 issues 实现一项工作。
---

# implement-zh

> 这是 Matt Pocock `implement` skill 的中文本地化版本。官方英文上游保留在 `upstream/mattpocock/skills/engineering/implement`；本目录可按中文团队习惯继续调整。

## 本地化说明

- 优先用中文与用户沟通。
- 保留上游流程、检查点和文件约定。
- 如果本文件与上游英文版本冲突，以本中文版本为准；同步上游时先比较差异，再合并。

实施PRD中用户描述的工作或问题。

尽可能在预先商定的接缝处使用 /tdd-zh。

定期运行类型检查，定期运行单个测试文件，最后运行一次完整的测试套件。

完成后，使用 /review-zh 来检查工作。

将您的工作提交到当前分支。