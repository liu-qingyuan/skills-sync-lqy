---
{
  "title": "Feature 当前事实与本地门禁",
  "status": "implemented",
  "code": [
    "skills/matt-lqy-core/setup-matt-pocock-skills-lqy/**",
    ".feature-docs/**",
    "AGENTS.md",
    "docs/agents/feature-docs.md"
  ],
  "tests": [
    "skills/matt-lqy-core/setup-matt-pocock-skills-lqy/tests/test_feature_docs.py",
    "scripts/tests/test_skill_maintenance.py"
  ],
  "reviewed_code": "sha256:dc189b816374e87f001acd9c27e7fc51d6205ef58f9b24835f0d798116593926"
}
---

## 当前行为

setup skill 携带一个 Python 标准库工具：显式安装、自动索引、只读快照检查和指定能力复核。项目统一入口为 `.feature-docs/run`；范围只显式追加，升级保留事实与原范围，既有 hooks/定制资产冲突则拒绝覆盖。

源码、模板和公开测试可使用任意真实仓库目录的 globs。pre-commit 查 index，pre-push 查实际 tip；缺失引用、未归属源码或过期基准阻止普通交付。复核不自动暂存。项目记录放 `docs/features/`，不会被已安装 skills 整目录同步删除。

## 限制与剩余

仅检查声明范围和版本绑定，不判断散文真假、不执行业务测试或阻止 issue 关闭；有 Shell 权限者能绕过 hooks。clone 后需执行 `./.feature-docs/run install`。当前只在 macOS 验证，不宣称 Windows/Linux 已通过；本仓库仅先纳管索引列出的三组能力。
