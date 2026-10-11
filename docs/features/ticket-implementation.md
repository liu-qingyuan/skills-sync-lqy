---
{
  "paths": [
    "skills/matt-lqy-core/implement-lqy/**",
    "scripts/tests/test_skill_maintenance.py"
  ],
  "fingerprint": "sha256:d7b61fa5d3b788d9e42243e3e26498242ff7f0b1b5d4a4edbd239022677539dd"
}
---

# 单 Ticket 实施与交付

## 当前行为

每个 worker 只实施指定或已授权选定的一个 Ticket，沿用设计 gate、TDD、双轴 review。同 worktree 的独立文件可并行，worker 交回范围与证据，由单一整合者检查 index/commit 并交付；完整交付关闭 issue，绿色未完增量保持 open。规则以 implement skill 为准。

## 限制与剩余

这是执行约定，不是强制调度器。未初始化记录的项目沿用原流程，提示显式 setup；无 upstream 时停止询问。
