---
name: finish-remaining-stories
description: 顺序推进 BMAD sprint 剩余 stories，逐条闭环到通过。
---

# Finish Remaining Stories

## Goal

在已有 BMAD 规划产物的项目中，按 `sprint-status.yaml` 的真实顺序，一次只推进一条 story；只要没有真实 blocker，就持续循环直到 backlog 清空。

## Use when

仅在以下条件满足时使用：
- 已有 `_bmad-output/planning-artifacts/epics.md`
- 已有或可生成 `_bmad-output/implementation-artifacts/sprint-status.yaml`
- 用户要持续清理 sprint 剩余 stories，而不是只做单条 story

如果只是实现一条 story，优先用 `$bmad-dev-story` 或 `$bmad-create-story`。

## Non-negotiables

- 一次只处理一条 story
- leader 只编排，默认不吃回 dev / review / verify 工作
- 不跳过当前应处理的 story
- 不越权接管 `sprint-status.yaml` 的主状态所有权
- 测试或 review 不通过时，留在当前 story 继续修复
- 没有验证证据，不算完成

额外边界：
- Epic 1 / Epic 4 的 continuity 边界不能混写
- Epic 2 不拥有 model / validation 语义
- renderer 不得重新推导 verdict / primary action

## Long-loop contract

这是一个长循环 skill，不是“做完一条 story 就停”的 skill。

执行者必须遵守：
- 完成一条 story **不等于** 完成这次 skill invocation
- 当前 story 收尾后，必须立刻再次运行 `scripts/next_story.py`
- 只要 `found=true` 且没有真实 blocker，就继续当前长循环

只有以下情况才允许给用户最终停止式总结：
1. `found=false`，说明所有 stories 已清空
2. 当前 story / epic 被判定为 `blocked`，必须转 `$bmad-correct-course`
3. OMX / BMAD runtime 不可用，且无法恢复当前编排

## Inputs

优先使用：
- `{project-root}/_bmad-output/planning-artifacts/epics.md`
- `{project-root}/_bmad-output/planning-artifacts/architecture.md`
- `{project-root}/_bmad-output/implementation-artifacts/sprint-status.yaml`
- 当前 story 文件（若存在）
- `project-context.md`（若存在）

先运行：
- `python3 scripts/resolve_project.py`

然后使用返回的 `project_root`。若缺少 `sprint-status.yaml`，先运行 `$bmad-sprint-planning`。

## Story selection

运行：
- `python3 scripts/next_story.py "{status-file}"`

选择优先级固定为：
1. `in-progress`
2. `review`
3. `ready-for-dev`
4. `backlog`

若 `found=false`，说明剩余 stories 已清空；输出总结并停止。

## Story preparation

按当前状态处理：
- `backlog`：运行 `$bmad-create-story`
- `ready-for-dev`：自动跑 Validate Story
- `in-progress`：恢复当前 story
- `review`：先吸收 review 结果，再回到当前 story 修复

如果 story 文件缺失但状态不是 `backlog`，先修正 story 文件与状态一致性，再继续。

## Plan before execution

先对当前 story 做一次**轻量** `$deep-interview`，只澄清：
- 是否存在真实歧义
- 是否有跨 epic 越界风险
- acceptance criteria / test shape 是否缺口明显

若 OMX runtime 存在，澄清后先清理 deep-interview 状态：
- `omx state clear --input '{"mode":"deep-interview","all_sessions":true}' --json`

然后运行 `$ralplan`，只为**当前 story**产出：
- 目标与成功标准
- 需要触达的文件 / 模块
- 预期测试证据
- 禁止项与明确边界

## Team execution

默认执行面是 `$team`，不是 leader 直接接管整条 story。

leader 负责：
- 选择当前 story
- 产出当前 story 的澄清 / 计划 / 禁止项
- 启动并监控 `$team`
- 根据结果决定回环、收尾或转 `$bmad-correct-course`

worker 负责：
- `bmad-dev-story`
- 测试 / 复测
- `bmad-code-review`
- 回传验证证据

默认 team staffing：
- `2 lanes`
- `$team 2:executor`
- `worker-1 / dev lane`：实现与测试修复
- `worker-2 / review+verify lane`：review、AC 复核、验证证据确认

leader 监控：
- `omx team status <team-name>`

team verdict 处理：
- `changes-requested`：留在当前 story，再起下一轮 `$team`
- `blocked`：转 `$bmad-correct-course`
- `approved + tests passing`：进入 story 收尾

## Story and epic closeout

当前 story 收尾前必须确认：
- 实现已落地
- 必需测试已通过
- review lane 已给出 `approved` 或等价无阻塞结论
- `sprint-status.yaml` 与 story 文档一致

某个 epic 的 stories 全部完成后：
- 运行 `$bmad-sprint-status`
- 自动运行 `$bmad-retrospective`
- 将 retrospective 结论带入下一 epic

## Output discipline

长循环过程中：
- 中间进展优先写回 story 工件、retrospective、`sprint-status.yaml` 等项目产物
- 不要把“完成了一条 story”当作本次 skill 完成
- 如果当前只是做完一条并准备好下一条，正确动作是继续，不是停下来汇报

## Helpers and references

优先使用确定性脚本，不要手写 ad hoc 状态逻辑：
- `scripts/resolve_project.py`
- `scripts/next_story.py`
- `scripts/update_status.py`（仅用于异常修复 / 补同步 / epic roll-up）

这些脚本依赖 `scripts/status_lib.py`。

按需读取：
- `references/status-ownership.md`
- `references/headless-adapters.md`
- `references/guardrails.md`
- `references/team-orchestration.md`

## Verification

宣称当前 story 完成前，至少确认：
- 代码已实现
- 对应测试已运行
- 当前 story 的 review 已通过，或已被下一轮 team 回合吸收修复
- `sprint-status.yaml` 与实际结果一致

任一条件不满足，就继续留在当前 story。
