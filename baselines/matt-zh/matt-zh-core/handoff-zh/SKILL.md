---
name: handoff-zh
disable-model-invocation: true
argument-hint: 下一个会话将用于什么？
description: 把当前对话压缩成交接文档，方便另一个 agent 继续。
---

编写一份总结当前对话的交接文档，以便新的 agent 可以继续工作。保存到用户操作系统的临时目录（`$TMPDIR`，否则 `/tmp`；Windows 使用 `%TEMP%`），而不是当前工作区。

在文档中包含“建议的 Skill”章节，明确指出下一位 Agent 应调用 Skill 工具指定哪些 `-zh` Skill。

不要复制其他 artifacts（specs、plans、ADRs、issues、commits、diffs）中已捕获的内容。请改为通过路径或 URL 引用它们。

脱敏任何机密信息，例如 API 密钥、密码或个人身份信息。

如果用户传递了参数，请将它们视为下一个会话将重点关注的内容的描述，并相应地调整文档。
