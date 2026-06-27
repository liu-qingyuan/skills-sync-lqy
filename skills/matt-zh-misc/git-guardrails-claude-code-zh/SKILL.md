---
name: git-guardrails-claude-code-zh
description: 设置 Claude Code hooks，阻止危险 git 命令（push、reset --hard、clean、branch -D 等）。用于用户想防止破坏性
  git 操作、添加 git 安全 hook 或阻止 git push/reset 时。
---

# 设置 Git Guardrails

设置一个 PreToolUse 挂钩，在 Claude 执行危险的 git 命令之前拦截并阻止它们。

## 什么被阻止

- `git push`（所有变体，包括`--force`）
-`git重置--硬`
- `git clean -f` / `git clean -fd`
-`git分支-D`
- `git checkout .` / `git Restore .`

当被阻止时，克劳德看到一条消息，告诉它没有访问这些命令的权限。

## 步骤

### 1.询问范围

询问用户：仅针对**此项目**（`.claude/settings.json`）安装还是**所有项目**（`~/.claude/settings.json`）？

### 2.复制钩子脚本

捆绑的脚本位于：[scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

根据范围将其复制到目标位置：

- **项目**：`.claude/hooks/block-dangerous-git.sh`
- **全局**：`~/.claude/hooks/block-dangerous-git.sh`

使用“chmod +x”使其可执行。

### 3. 在设置中添加钩子

添加到适当的设置文件：

**项目**（`.claude/settings.json`）：
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```
**全局**（`~/.claude/settings.json`）：
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```
如果设置文件已存在，请将挂钩合并到现有的 `hooks.PreToolUse` 数组中 - 不要覆盖其他设置。

### 4.询问定制

询问用户是否要在阻止列表中添加或删除任何模式。相应地编辑复制的脚本。

### 5. 验证

运行快速测试：
```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```
应该以代码 2 退出并向 stderr 打印一条 BLOCKED 消息。