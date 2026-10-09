---
name: setup-ts-deep-modules-zh
description: 将 dependency-cruiser 接入 TypeScript 仓库，让每个 package 成为深模块：实现隐藏在子文件夹中，只能通过入口文件从外部访问。由用户手动调用。
disable-model-invocation: true
---

# 配置 TS 深模块

让仓库中的每个 package 都成为**深模块**：小接口背后承载大量行为。package 的公共表面是它的**入口点**（package 根目录的文件），其子文件夹中的内容都对外隐藏。本 Skill 安装 [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) 和确保只能通过入口点访问的规则，并证明规则确实有效。

关于深模块、接口、接缝和深度的术语，请通过 Skill 工具调用 `codebase-design-zh` 并在整个流程使用其语言。

## 强制执行的结构

```
src/packages/
  <name>/
    index.ts        ← 入口点（公开）；外部从这里导入
    client.ts       ← 另一个入口点；一个 package 可以有多个入口点
    lib/            ← 实现：对外隐藏，内部文件可以互相导入
    tests/          ← 就近放置的测试与 fixture（子文件夹，因此为私有）
```

公共表面是 package 的**所有根目录文件**，而非指定的唯一 `index.ts`。按照约定，实现在 `lib/`，测试在 `tests/`，使所有 package 采用相同的双子文件夹结构。不过规则是通用的：*任何*子文件夹的内容都属于私有，因此无需为新增文件夹修改配置。

四条规则，均为 `error`：

1. **入口点边界**：package 外部的代码（应用或其他 package）只能导入其根目录入口点，不得导入其子文件夹。
2. **package 内部自由**：同一个 package 的内部文件可以自由互相导入。
3. **测试经由入口点**：`<pkg>/tests/` 下的文件可以导入任何 package 的入口点及其自己的 `tests/` fixture，但不可导入任何 package 的子文件夹内部文件（包括自己的 package）。跨 package 集成测试可以进行，深层导入不行。
4. **没有循环依赖**。

**入口点，而不是 barrel。**因为每个根目录文件都是公共表面，一个 package 可以暴露多个小入口点（`index.ts`、`client.ts`、`server.ts`），而不是把所有内容都塞进一个巨大 `index.ts`。不鼓励用 barrel 文件重导出整棵子树；保持入口点小巧，把实现藏进子文件夹。

分层（哪些 package 可依赖哪些）是*另一项*关注点，在配置中保留注释占位，留给此仓库填写。

## 步骤

### 1. 识别环境

- **包管理器**：`pnpm-lock.yaml` → pnpm；`yarn.lock` → yarn；`bun.lockb` → bun；否则 npm。以下每条命令都用对应工具（`pnpm`/`yarn`/`npm run`/`bunx`）。
- **package 根目录**：若存在 `src/`，用 `src/packages`；否则用 `packages`。若仓库已有其他明显约定，先与用户确认。
- **已有配置**：查找 `.dependency-cruiser.*`。若已有配置，**不要覆盖**：将四条规则和选项合并进去，并告诉用户新增了什么。

**完成条件：**包管理器、package 根目录和现有配置状态均已明确。

### 2. 安装 dependency-cruiser

用检测到的包管理器将 `dependency-cruiser` 安装为 devDependency。

**完成条件：**`dependency-cruiser` 出现在 `devDependencies` 中。

### 3. 编写配置

将 [`dependency-cruiser.config.cjs`](./dependency-cruiser.config.cjs) 复制到仓库根目录，命名为 `.dependency-cruiser.cjs`。根据步骤 1 将 `PACKAGES_ROOT` 设为所选根目录。规则基于路径深度，且与扩展名无关，所以无需调整其他内容。

**完成条件：**`.dependency-cruiser.cjs` 存在，`PACKAGES_ROOT` 正确，包含四条禁止规则。

### 4. 接入检查

- 添加 `lint:boundaries` 脚本：`depcruise <packages-root>`（或 `depcruise src`）。
- 将其纳入现有运行 typecheck 的总检查命令（如 `check` / `ci` / `validate`）。**不要**改动 `tsconfig` 或添加路径别名。
- 若不存在总检查脚本，添加 `lint:boundaries` 并告诉用户需将其纳入 CI。

**完成条件：**`lint:boundaries` 存在，并与 typecheck 一起执行。

### 5. 搭建示例 package

在 `<packages-root>/example/` 创建提交到版本库、可供复制的模板：

- `index.ts` 是入口点，导出一个委托给内部文件的函数（使 package 明显是*深*模块，而不是透传包装）。
- `lib/impl.ts` 是位于**子文件夹**的内部文件，由 `index.ts` 导入，不可从外部访问。
- `tests/example.test.ts` **只**导入 `../index`（入口点），并通过公共函数断言。

告诉用户这是可复制或删除的起始模板。

**完成条件：**示例 package 已存在，通过根目录入口点暴露行为，并将 `impl` 隐藏在子文件夹中。

### 6. 证明规则生效

这是整个 Skill 的完成标准：不能在违规时失败的配置没有价值。

1. 运行 `lint:boundaries`；干净示例必须**通过**。
2. 暂时向 `tests/example.test.ts` 添加深层导入（如 `import { thing } from "../lib/impl"`），重新运行 `lint:boundaries`；必须以 `tests-through-entrypoints` **失败**。
3. 撤销深层导入，再次运行；必须**通过**。

**完成条件：**已观察到通过 → 因深层导入失败 → 再次通过。若步骤 2 没有失败，规则未正确接入，先修复再完成。

### 7. 记录约定

在 package 根目录、与受约束 package 并列的位置，写 `README.md`（`<packages-root>/README.md`），说明 `src/packages/<name>/` 布局（根目录入口点、`lib/` 实现、`tests/` 测试），“只能通过 package 的入口点（根目录文件）导入”，以及如何运行 `lint:boundaries`。明确**不鼓励 barrel 文件**：使用多个小入口点，而不是让一个 index 重导出整棵子树。内容控制在可复制模板和各一段的四条规则。

然后在仓库 Agent 指令文件（优先已有的 `CLAUDE.md`，否则 `AGENTS.md`，若两者都没有则新建 `AGENTS.md`）中添加一条指向该文件的**上下文指针**。一行足够，如：`Package 是深模块：新建或导入前参见 [src/packages/README.md](./src/packages/README.md)。` 这使 Agent 能主动发现边界规则，而非违规后才察觉。

**完成条件：**`<packages-root>/README.md` 已存在且不鼓励 barrel，仓库 `CLAUDE.md`/`AGENTS.md` 包含其链接。

## 备注

- 配置的 `$1` 反向引用（dependency-cruiser 的分组匹配）允许 package 访问自己的内部文件、禁止外部访问。不要将其展开为逐 package 的独立规则。
- 公开与私有由**深度**决定：根目录文件是入口点，子文件夹中的内容是私有的。惯例是 `lib/`（实现）和 `tests/`，但规则不写死文件夹名，新增文件夹无需改配置。新增入口点也只需增加一个根目录文件（不需要 barrel）。
- Package 采用**扁平**布局：根目录下一级子目录各为一个 package。内部文件可以任意嵌套，但不能在一个 package 中再嵌套另一个 package。
- 使用 `.cjs`（不是 `.js`），以便即使仓库设置了 `"type": "module"`，配置中的 `module.exports` 仍可使用。
