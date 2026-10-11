---
{
  "paths": [
    "skills/matt-lqy-core/setup-matt-pocock-skills-lqy/**",
    ".feature-docs/**",
    "AGENTS.md",
    "docs/agents/feature-docs.md",
    "skills/matt-lqy-core/setup-matt-pocock-skills-lqy/tests/test_feature_docs.py",
    "scripts/tests/test_skill_maintenance.py"
  ],
  "fingerprint": "sha256:a5cbef558c654bc02ccc0e65330b26689cb613093f5c33fbcd6b1e6983c12abc"
}
---

# Feature 当前事实与本地门禁

## 当前行为

单个标准库工具提供 install/list/check/review；paths/fingerprint 绑定当前事实，旧格式兼容。review 只解析指定页，不被其他未完成页阻断；独立文件与页面可并行复核，整合者串行交付。pre-commit 查完整 index，pre-push 查实际 tip，缺失／未归属／过期阻断交付。安装只追加范围，保留事实并拒绝覆盖定制 hooks/资产。

## 限制与剩余

不判断散文真假、不跑业务测试或硬限制 issue 关闭；不提供写锁，同文件和共享 Git/build 不能并发写。hooks 可绕过。clone 需恢复安装；只在 macOS 验证，只纳管索引列出的能力。
