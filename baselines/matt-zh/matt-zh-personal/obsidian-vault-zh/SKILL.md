---
name: obsidian-vault-zh
description: 在 Obsidian vault 中搜索、创建和管理带 wikilinks 与索引笔记的 notes。用于用户想查找、创建或整理 Obsidian
  笔记时。
---

# 黑曜石宝库

## 金库位置

`/mnt/d/黑曜石宝库/AI 研究/`

根部大多平坦。

## 命名约定

- **索引注释**：汇总相关主题（例如，`Ralph Wiggum Index.md`、`Skills Index.md`、`RAG Index.md`）
- **标题大小写**适用于所有音符名称
- 没有用于组织的文件夹 - 使用链接和索引注释代替

## 链接

- 使用黑曜石 `[[wikilinks]]` 语法：`[[注释标题]]`
- 注释链接到底部的依赖项/相关注释
- 索引注释只是“[[wikilinks]]”的列表

## 工作流

### 搜索笔记
```bash
# Search by filename
find "/mnt/d/Obsidian Vault/AI Research/" -name "*.md" | grep -i "keyword"

# Search by content
grep -rl "keyword" "/mnt/d/Obsidian Vault/AI Research/" --include="*.md"
```
或者直接在保管库路径上使用 Grep/Glob 工具。

### 创建一个新笔记

1. 使用**标题大小写**作为文件名
2. 将内容作为学习单元编写（根据 Vault 规则）
3. 在底部相关注释中添加`[[wikilinks]]`
4. 如果是编号序列的一部分，请使用分层编号方案

###查找相关注释

在保管库中搜索“[[Note Title]]”以查找反向链接：
```bash
grep -rl "\\[\\[Note Title\\]\\]" "/mnt/d/Obsidian Vault/AI Research/"
```
### 查找索引注释
```bash
find "/mnt/d/Obsidian Vault/AI Research/" -name "*Index*"
```

