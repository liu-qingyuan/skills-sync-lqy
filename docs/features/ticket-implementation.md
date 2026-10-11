---
{
  "paths": [
    "skills/matt-lqy-core/implement-lqy/**",
    "skills/matt-lqy-core/implement-spec-subagent-lqy/**",
    "skills/matt-lqy-core/to-spec-lqy/**",
    "skills/matt-lqy-core/to-tickets-lqy/**",
    "skills/matt-lqy-core/ask-matt-lqy/**",
    "docs/architecture/spec-implementation.md",
    "scripts/tests/test_skill_maintenance.py"
  ],
  "fingerprint": "sha256:27aad73ea0571040f05613ba8394fcff605500c81cba88a68591bafebff3b282"
}
---

# Ticket 实施与交付

## 当前行为

每个 worker 只实施指定或已授权派发的一个 Ticket，沿用设计 gate、TDD、双轴 review。规划保留真实依赖并指出合理并行与资源冲突，发布后停止；Ralph 默认串行，可显式选择 implement-spec-subagent-lqy。新入口并行派发安全独立的 Tickets，各自使用独立 worktree；worker 仅本地 commit，单一整合者在集成分支串行 review、验证、push/关闭后释放依赖，不等待整批。同 worktree 的原有独立文件并行约定不变。

## 限制与剩余

这是执行约定，不是强制调度器或锁服务。实际工作区与共享资源仍需核查；不与 Ralph 消费同一批票，不要求 worker 再派发 reviewers。未初始化记录的项目沿用原流程；集成分支无 upstream、冲突或门禁失败时停止，保留现场。文件合同/加载测试不等于真实实施的端到端验收。
