---
name: improve-codebase-architecture-lqy
description: "围绕实际变化热点调查深模块加深机会，用 HTML 展示候选，再由用户选择是否继续设计。"
disable-model-invocation: true
---

# 改进代码库架构

只调查实际架构摩擦，不自动实施重构。先读取 `codebase-design-lqy` 的 `SKILL.md`，使用 Module、Interface、Depth、Seam、Adapter、Leverage、Locality 等共享词汇；领域名称来自项目指定的术语表（新项目默认 `GLOSSARY.md`）。

## 探索

用户指定方向时只调查该模块、子系统或痛点；否则从近期 Git 变更识别持续编辑的热点，没有明显热点再扩大。不要为从未改动的角落制造重构任务。

读取相关 ADR，尊重现有取舍。有只读 agent 能力且调查独立时可委派，没有时直接查；不假设 Claude Explore agent，也不新建执行平台。

按实际摩擦判断：是否为一个概念来回跳转多个浅模块；调用方是否掌握内部策略；同一知识是否散落；实际故障是否缺少公开测试表面。用删除测试判断复杂性会消失还是回到调用方，不按代码行数或文件数量提出重构。

## 呈现候选

按 [HTML-REPORT.md](HTML-REPORT.md) 写自包含 HTML 到 OS 临时目录，告知绝对路径并在环境支持时打开。每项只展示：相关文件、具体摩擦、最小变化、Locality / Leverage / 测试收益、当前 / 目标图和推荐强度。用最清楚的图形，不为展示同时生成所有图。

与 ADR 冲突时仅在有真实证据支持重审时提出并明确标注。不给未选候选提前设计完整 Interface。报告后问用户想继续哪一项。

## 用户选择后

读取并执行 `grilling-lqy` 的 `SKILL.md`，澄清约束、依赖、Seam 和保留的测试。主动澄清术语时才读取并执行 `domain-modeling-lqy`；普通阅读词汇不启动建模。

确认的概念写入项目指定的同一份术语表，不自动迁移旧文档或双写。难以逆转且真实的取舍才建议 ADR。用户明确要比较多个 Interface 时才使用 codebase-design 的 Design It Twice；无并行能力就串行比较，不把设计调查变成多 agent 实施。

下一步由用户选择：形成 spec、单 Ticket 或保留调查。不自动启动 Ralph，也不直接整改项目环境。
