---
{
  "status": "implemented",
  "paths": [
    "skills/matt-lqy-core/setup-matt-pocock-skills-lqy/**",
    ".feature-docs/**",
    "AGENTS.md",
    "docs/agents/feature-docs.md",
    "skills/matt-lqy-core/setup-matt-pocock-skills-lqy/tests/test_feature_docs.py",
    "scripts/tests/test_skill_maintenance.py"
  ],
  "reviewed_code": "sha256:19d56580d00e74970e25563ed96a2f65c136d23311b725c0bfa9bf4bf924ddbc"
}
---

# Feature 当前事实与本地门禁

## 当前行为

单个标准库工具提供 install/list/check/review；三字段记录兼容旧格式，源码和测试都绑定版本。pre-commit 查 index，pre-push 查实际 tip；缺失引用、未归属源码、过期基准阻止普通交付。安装只追加范围，保留项目事实，拒绝覆盖定制 hooks/资产。

## 限制与剩余

不判断散文真假、不跑业务测试或硬限制 issue 关闭；hooks 可绕过。clone 需恢复安装；只在 macOS 验证，本仓库只纳管索引列出的三组能力。
