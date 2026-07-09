---
name: claude-handoff-zh
description: 把当前对话交接给一个新的后台 agent，让它立即接手继续工作。
---

为当前对话写一份 handoff summary，让新的 agent 可以继续这项工作。不要保存文件，而是用这份 summary 作为 prompt 启动后台 agent：`claude --bg --name "<descriptive name>" "<handoff summary>"`。它从当前工作目录启动并立即返回；用户通过 `claude agents` 管理它。

始终传入带描述性的 `-n`/`--name`（例如 `--name "Fix login bug"`）。这个名称会显示在 job list、session picker 和 terminal title 中。

在 summary 中包含一个 `suggested skills` section，建议该 agent 应该调用哪些 skills。

不要重复已经被其他 artifacts 捕获的内容（PRDs、plans、ADRs、issues、commits、diffs）。用 path 或 URL 引用它们。

删去任何敏感信息，例如 API keys、passwords 或 personally identifiable information；summary 会成为 agent 的 prompt。

如果用户传了参数，把它们视为下一会话关注点的描述，并据此定制 summary。
