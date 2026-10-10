---
{
  "title": "已安装 skills 同步与初始化",
  "status": "implemented",
  "code": [
    "scripts/sync_installed_project_skills.py",
    "setup"
  ],
  "tests": [
    "scripts/tests/test_skill_maintenance.py"
  ],
  "reviewed_code": "sha256:299066220100fe709b4feed0c7252e4ffa02c3243f72810ec0af19edd0ff6321"
}
---

## 当前行为

同步脚本只更新目标 `.agents/skills/` 中已存在的同名 installable skills，从 `skills/` 整目录复制，支持 dry-run；新的 Feature 工具、模板与约定随 setup skill 一起分发。项目自有 `docs/features/` 与 `.feature-docs/` 位于安装目录外，不随同步删除；工具升级仍需显式执行 install。

根 `./setup` 仍只复制本仓库的架构 `AGENTS.md`，不同内容先备份；不因此安装 Feature hooks、修改 GitHub labels 或启动 Ralph。

## 限制与剩余

同步会替换已安装 skill 的整个目录，不合并本地定制、不自动新增未安装 skill；定制内容应先保留。本文不代替具体安装命令及 README，不承诺自动更新项目工具或自动复核业务事实。
