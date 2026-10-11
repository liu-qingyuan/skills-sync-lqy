---
{
  "paths": [
    "skills/matt-lqy-core/implement-lqy/**",
    "skills/matt-lqy-core/implement-spec-subagent-lqy/**",
    "skills/matt-lqy-core/code-review-lqy/**",
    "skills/matt-lqy-core/to-spec-lqy/**",
    "skills/matt-lqy-core/to-tickets-lqy/**",
    "skills/matt-lqy-core/ask-matt-lqy/**",
    "docs/architecture/spec-implementation.md",
    "scripts/tests/test_skill_maintenance.py"
  ],
  "fingerprint": "sha256:7c3ee88ccc608c05edadd1a0ec00b71f7bdb9cfd438ddcaa62348c73ea699843"
}
---

# Ticket 实施与交付

## 当前行为

每个 worker 只实施指定或已授权派发的一个 Ticket，沿用设计 gate、TDD、双轴 review。规划保留真实依赖并指出合理并行与资源冲突，发布后停止；Ralph 默认串行，可显式选择 implement-spec-subagent-lqy。新入口可由承接授权的主流程派发，安全独立的小任务可共享 worktree，独立提交/滚动整合优先独立 worktree。worker 可在本票内做只读辅助；共享 worker 不操作 Git/index，独立 worker 可本地 commit。共享写入全部交回或暂停后，单一整合者对明确授权的单票/交付批次做有限双轴 review、完整验证及 Git/issue 收口后释放依赖；独立工作区可逐票滚动交付。

## 限制与剩余

这是执行约定，不是强制调度器或锁服务。实际文件、共享资源和稳定快照仍需核查，不按模块名推定独立；只读辅助不扩大范围、不绕过 review 预算，不与其它流程消费同一批票。未初始化记录的项目沿用原流程；集成分支无 upstream、冲突或门禁失败时停止，保留现场。文件合同/加载测试不等于真实实施的端到端验收。
