---
name: domain-modeling-zh
description: 构建并打磨项目领域模型。在讨论代码库术语、编写或修改 GLOSSARY.md、记录或修改 ADR 时使用。
---

# 领域建模

在设计过程中主动构建并打磨项目的领域模型：质疑术语、设计边界场景，并在术语和决策刚明确时写入术语表及决策记录。仅仅读取 `GLOSSARY.md` 以获取词汇不算使用此 Skill；那只是任何 Skill 都可遵循的一条习惯。本 Skill 用于改变领域模型，而不是只消费它。

## 文件结构

大多数仓库只有一个领域上下文：

```text
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

若仓库根目录存在 `GLOSSARY-MAP.md`，则有多个领域上下文；该 map 指向各上下文位置：

```text
/
├── GLOSSARY-MAP.md
├── docs/
│   └── adr/                          ← 系统级决策
├── src/
│   ├── ordering/
│   │   ├── GLOSSARY.md
│   │   └── docs/adr/                 ← 特定上下文的决策
│   └── billing/
│       ├── GLOSSARY.md
│       └── docs/adr/
```

按需创建文件：只有真正有内容可写时才创建。第一个术语确定时创建缺失的 `GLOSSARY.md`；需要第一份 ADR 时创建缺失的 `docs/adr/`。

## 会话中怎么做

### 对照术语表提出质疑

用户用词与 `GLOSSARY.md` 的现有语言冲突时立即指出：“术语表将 cancellation 定义为 X，你似乎在说 Y。你想表达哪一个？”

### 收紧模糊语言

用户使用模糊或多义词时提出精确的规范术语：“你说的 account 是 Customer 还是 User？二者并不相同。”

### 讨论具体场景

讨论领域关系时，用具体场景压力测试。主动构造边界场景，明确概念边界。

### 和代码交叉核对

用户描述某件事的运行方式时，检查代码是否一致。若有矛盾，指出：“代码现在会取消整张订单，但你说可以部分取消。哪个才是正确规则？”

### 及时更新 GLOSSARY.md

术语一旦明确，立刻更新 `GLOSSARY.md`，不要攒到最后。格式见 [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md)。

`GLOSSARY.md` 应完全不包含实现细节。不要将它当作 spec、草稿本或实现决策记录；它只是术语表。

### 谨慎提出 ADR

仅当以下三个条件**全部**满足时才建议创建 ADR：

1. **难以逆转**：以后改变决定的成本不低。
2. **没有背景会显得意外**：未来读者会疑惑“为什么这样做？”
3. **来自真实权衡**：确实存在替代方案，当前方案因具体理由被选中。

缺少任意一条就跳过 ADR。格式见 [ADR-FORMAT.md](./ADR-FORMAT.md)。
