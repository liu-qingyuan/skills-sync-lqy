---
{
  "paths": [
    "scripts/sync_installed_project_skills.py",
    "setup",
    "scripts/tests/test_skill_maintenance.py"
  ],
  "fingerprint": "sha256:6600ba9efd0d07ef61b537d4e85f42bb7ca555fcbd9ef2f68f3ea70ad155a6c0"
}
---

# 已安装 skills 同步与初始化

## 当前行为

只更新已有同名 installable skills，整目录复制，支持 dry-run；项目事实和门禁资产在安装目录外保留，工具升级需显式 install。根 ./setup 仍仅复制架构 AGENTS，不同内容先备份，不安装 hooks、改标签或启动 Ralph。

## 限制与剩余

不合并已安装 skill 的本地定制、不新增未安装 skill、不自动更新项目工具或复核业务事实。
