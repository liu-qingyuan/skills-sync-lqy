---
name: grill-with-docs-lqy
disable-model-invocation: true
description: 通过连续追问打磨计划或设计，并在过程中创建或更新 ADR、术语表等文档。
---

按 skills 列表的实际路径分别读取并执行 `grilling-lqy` 与 `domain-modeling-lqy` 的 `SKILL.md`；使用项目指定的同一份术语表，新项目默认 `GLOSSARY.md`，旧 CONTEXT 不自动迁移。达成共识后，只提醒用户下一步调用 `$to-spec-lqy` 整理并发布 spec；不要直接实施或自动启动后续 skill。
