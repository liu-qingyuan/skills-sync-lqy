---
{
  "title": "单 Ticket 实施与交付",
  "status": "implemented",
  "code": [
    "skills/matt-lqy-core/implement-lqy/**"
  ],
  "tests": [
    "scripts/tests/test_skill_maintenance.py"
  ],
  "reviewed_code": "sha256:fdd55c00282cc4641f046b0a45b8476f1c4e027926ed91738f5cb2350bf9663f"
}
---

## 当前行为

implement 只实施指定 Ticket 或已授权 Ralph worker 选定的任务，保留现有设计 gate、TDD 和预算化双轴 review。已启用记录的项目先读索引，按需复核相关能力；代码与事实一起暂存，index/commit 检查通过后交付。

完整交付仍 commit/push、评论 hash/验证/摘要并关闭 issue；绿色未完增量同步当前能力与剩余，保持 issue open。详细执行规则以 `implement-lqy/SKILL.md` 为准。

## 限制与剩余

这是 skill 的执行约定，不是强制调度器；Git 记录门禁不保证模型必然正确关闭 issue 或运行测试。未初始化记录的项目保持原流程并提示显式 setup，不自动安装 hooks；没有 upstream 时仍停止询问。
