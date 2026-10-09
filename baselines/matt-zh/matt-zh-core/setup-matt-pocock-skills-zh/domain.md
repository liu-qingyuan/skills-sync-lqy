# 领域文档

工程 Skill 在探索代码库时如何使用仓库的领域文档。

## 探索前阅读

- 根目录的 **`GLOSSARY.md`**；或
- 若根目录存在 **`GLOSSARY-MAP.md`**，它指向各上下文自己的 `GLOSSARY.md`。阅读与主题相关的每份术语表。
- **`docs/adr/`**：阅读涉及即将修改区域的 ADR。多上下文仓库还需检查 `src/<context>/docs/adr/` 中的上下文级决策。

文件不存在时**直接继续**，不要将缺失报告为问题，也不要建议预先创建。`/domain-modeling-zh`（经由 `/grill-with-docs-zh` 或 `/improve-codebase-architecture-zh` 触发）会在术语或决策真正确定时按需创建。

## 文件布局

单上下文（多数仓库）：

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多上下文（根目录有 `GLOSSARY-MAP.md`）：

```
/
├── GLOSSARY-MAP.md
├── docs/adr/                          ← 系统级决策
└── src/
    ├── ordering/
    │   ├── GLOSSARY.md
    │   └── docs/adr/                  ← 上下文级决策
    └── billing/
        ├── GLOSSARY.md
        └── docs/adr/
```

## 使用术语表的语言

当产物中命名领域概念（Issue 标题、重构建议、假设、测试名称）时，使用 `GLOSSARY.md` 定义的术语，避免使用它明确不推荐的同义词。

若所需概念尚未收入术语表，则需判断：是你在发明项目从未使用的语言（重新考虑），还是术语表确实有缺口（记录并交给 `/domain-modeling-zh`）。

## 标记 ADR 冲突

若产物与现有 ADR 冲突，应明确指出，不要默默覆盖：

> *与 ADR-0007（事件溯源订单）冲突，但值得重新讨论，因为……*
