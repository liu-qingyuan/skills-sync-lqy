---
name: implement-zh
disable-model-invocation: true
description: 根据 spec 或一组 Ticket 实现一项工作。
---

实现用户在 spec 或 Ticket 中描述的工作。

若用户提供 Ticket 引用，开始之前先从 Issue tracker 获取并说出它的标题。引用含糊时先询问。

条件允许时，在预先商定的接缝处调用 Skill 工具并指定 `tdd-zh`。

定期运行类型检查，定期运行单个测试文件，最后运行一次完整的测试套件。

完成后，调用 Skill 工具并指定 `code-review-zh` 来检查工作。

将你的工作提交到当前分支。
