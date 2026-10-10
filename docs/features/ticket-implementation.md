---
{
  "status": "implemented",
  "paths": [
    "skills/matt-lqy-core/implement-lqy/**",
    "scripts/tests/test_skill_maintenance.py"
  ],
  "reviewed_code": "sha256:96bc6d8649687cac4e819206aa17af5635850fb711a5e7ad7108293423ed141e"
}
---

# 单 Ticket 实施与交付

## 当前行为

只实施指定或已授权 worker 选定的一个 Ticket，沿用设计 gate、TDD、双轴 review。启用记录的项目同步当前事实并检查 index/commit；完整交付关闭 issue，绿色未完增量保留剩余并保持 open。规则以 implement skill 为准。

## 限制与剩余

这是执行约定，不是强制调度器。未初始化记录的项目沿用原流程，提示显式 setup；无 upstream 时停止询问。
