---
name: claude-handoff-zh
disable-model-invocation: true
argument-hint: 下一个会话将用于什么？
description: 把当前对话交接给一个新的后台 agent，让它立即接手继续工作。
---

为当前对话撰写交接摘要，让新的 Agent 接续工作。先保存到用户操作系统的临时目录，再用文件内容作为提示词启动后台 Agent：`claude --bg --name "<descriptive name>" -- "$(cat <summary file>)"`。从文件传递内容可避免 shell 执行摘要中的反引号或展开 `$`。它从当前工作目录启动并立即返回；用户通过 `claude agents` 管理。

始终传入带描述性的 `-n`/`--name`（例如 `--name "Fix login bug"`）。这个名称会显示在 job list、session picker 和 terminal title 中。

在摘要中包含 `suggested skills` 一节，明确指出下一位 Agent 应调用 Skill 工具指定哪些 `-zh` Skill。

不要重复已经由其他产物记录的内容（spec、计划、ADR、Issue、commit、diff）。用 path 或 URL 引用它们。

删去任何敏感信息，例如 API keys、passwords 或 personally identifiable information；summary 会成为 agent 的 prompt。

如果用户传了参数，把它们视为下一会话关注点的描述，并据此定制 summary。
