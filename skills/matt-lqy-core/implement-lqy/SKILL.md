---
name: implement-lqy
description: 根据 PRD 或一组 issues 实现一项工作。
---

实施PRD中用户描述的工作或问题。

尽可能在预先商定的接缝处使用 /tdd-lqy。

定期运行类型检查，定期运行单个测试文件，最后运行一次完整的测试套件。

完成后，使用 /review-lqy 来检查工作。

写 issue 评论、完成摘要或关闭说明前，遵守 `docs/agents/issue-tracker.md` 的语言约定；没有约定时，LQY 默认使用中文。

多行 `gh issue comment` 使用 heredoc 或 `--body-file`，避免 shell 展开 `$(...)`。

将您的工作提交到当前分支。
