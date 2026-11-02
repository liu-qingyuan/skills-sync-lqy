---
{
  "paths": [
    "scripts/sync_installed_project_skills.py",
    "setup",
    "scripts/tests/test_skill_maintenance.py"
  ],
  "fingerprint": "sha256:19b03c709eebeea716f8620ba84f9044ecfdc2de383d02575fb4e5a1ccca5ac9"
}
---

# 已安装 skills 同步与初始化

## 当前行为

只更新已有同名 installable skills，整目录复制，支持 dry-run；项目事实、明确关闭决定和门禁资产在安装目录外保留；仅同步 skills 不会直接安装 hooks，首次默认启用由后续 setup 或实施交付处理，工具升级仍需 install。根 ./setup 仍仅复制架构 AGENTS，不同内容先备份，不安装 hooks、改标签或启动 Ralph。

## 限制与剩余

不合并已安装 skill 的本地定制、不新增未安装 skill、不自动更新项目工具或复核业务事实。
