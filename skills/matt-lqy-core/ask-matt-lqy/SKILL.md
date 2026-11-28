---
name: ask-matt-lqy
description: "推荐 LQY 工作流：默认 Ralph、可选子 agent 并行、单 Ticket、规划、诊断、复盘和交接。只推荐，不自动启动。"
disable-model-invocation: true
---

# 选择工作流

推荐前先读取候选 skill 的实际 `SKILL.md`，不要仅凭名字描述能力，也不替用户执行 user-only 入口。

## 主流程

- 想法未明确：有项目时用 `grill-with-docs-lqy`，否则用 `grill-me-lqy`。
- 需要可运行的答案：按需 `prototype-lqy`，把验证出的决策带回讨论。
- 多 Ticket：`to-spec-lqy` 建立父 spec / Git 契约，`to-tickets-lqy` 发布有依赖的实施 Tickets。
- 批量实施：**Ralph 是默认入口**。用户明确启动 `ralph-plan-lqy` 后，按 branch / worktree 串行消费 ready-for-agent Tickets，交 `implement-lqy` 完成每项。
- 用户授权子 agent 并行实施：使用 `implement-spec-subagent-lqy`，复用同一 Spec/Tickets，按项目约定与风险选择共享工作区或独立 worktree；由单一整合者在稳定快照上验证交付，不在规划后自动启动。
- 单 Ticket：`implement-lqy`，公开 Seam 上 TDD、验证、bounded 双轴 review、受限 clean 和完成状态。
- 写 PR 正文：`pr-lqy`；不要求从直接 commit/push 改成 PR。
- 会话复盘：用户主动选择 `retro-lqy`；独立运行只提建议，已授权 chief 调用时遵循 chief 的最后一步替代规则。

Ralph 仍是默认实施入口；显式选择 chief 时，遵循其委派和过程调用，不把安装 chief 或软件工厂词汇当成已启动执行。

## 其它入口

- 需要持续委派工作、保留跨会话历史：显式使用 `chief-of-staff-lqy`，按其过程协调新上下文 subagents、调用复盘并维护约定位置的 wiki。
- 设计软件工厂：`software-factory-lqy`，用任务、运行和服务槽位组织设计，按需读取服务调研材料；它是设计语言，不是执行引擎。
- 已观察故障：`diagnosing-bugs-lqy`，先建立反馈循环。
- 外部 issue 请求：`triage-lqy`；已经由 Ticket publisher 准备的工作不重复 triage，PR 不作为请求入口。
- 多会话仍无法看清方向：`wayfinder-lqy`；决策 Ticket 不进 Ralph，路线清晰后再 `to-spec-lqy`。
- 当前有真实架构摩擦：`improve-codebase-architecture-lqy`，只调查相关热点。
- 教学：`teach-lqy`。编辑 agent 文档：`writing-for-agents-lqy`。
- 旧个人 skills 仍可显式使用，但不因上游删除就自动删掉或转移它们的数据。

## 上下文边界

依次判断：当前对话继续是否足够；下一阶段能否只从 Ticket 等一手材料重新开始；是否需要跨 harness / 目录的 portable handoff；有没有适合有限只读委派的独立问题；最后才考虑 compact。

`handoff-out` 输出可复制 prompt，`handoff-lqy` 写临时交接文件，二者不互相替代。不照搬某个模型的固定 Token 阈值，按实际上下文和完整证据判断。

缺少 tracker / domain 配置时，提示用户显式调用 `setup-matt-pocock-skills-lqy`。本工作流保持 GitHub Issues-only、单领域术语表与中文输出。
