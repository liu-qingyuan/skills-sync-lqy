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
  "fingerprint": "sha256:21b845881241e55619d3d8a465cb5e36110053d2fbfa72b9c67194e10b8451fe"
}
---

# Ticket 实施与交付

## 当前行为

Spec 与 Tickets 以最小充分为准，不按篇幅、故事数或技术层扩写拆票。Spec 记录关键业务假设、验证输入的代表性及验证/拟上线配置差异；Ticket 引用相关约束，只覆盖目标涉及的层和真正需要的 prefactor，并在既有正文与验收中限定结论。技术验证通过不等于业务验收或可上线，未验证项明确保留；不强制每票真实采样或上线，不新增 section 或 publisher 字段。

每个 worker 只实施指定或已授权派发的一个 Ticket，沿用设计 gate、TDD、双轴 review。规划保留真实依赖并指出合理并行与资源冲突，发布后停止；Ralph 默认串行，可显式选择 implement-spec-subagent-lqy。新入口可由承接授权的主流程派发，安全独立的小任务可共享 worktree，独立提交/滚动整合优先独立 worktree。worker 可在本票内做只读辅助；共享 worker 不操作 Git/index，独立 worker 可本地 commit。共享写入全部交回或暂停后，单一整合者对明确授权的单票/交付批次做有限双轴 review、完整验证及 Git/issue 收口后释放依赖；独立工作区可逐票滚动交付。记录门禁默认开启，尚未安装且未明确关闭时，在真实能力通过测试后由交付者在 review 前首次启用，新增记录与资产纳入同次交付；worker 仅交回就绪证据，不要求项目预先写授权标记。

## 限制与剩余

这是执行约定，不是强制调度器或锁服务。实际文件、共享资源和稳定快照仍需核查，不按模块名推定独立；只读辅助不扩大范围、不绕过 review 预算，不与其它流程消费同一批票。明确关闭的项目沿用原决定，尚无真实能力或业务测试未通过时暂缓首次安装；集成分支无 upstream、冲突或门禁失败时停止，保留现场。文件合同/加载与 publisher 回归不等于模型会遵循规划规则、真实业务代表性或上线验收，也不等于真实实施的端到端验收。
