---
name: setup-pre-commit-zh
description: 在当前仓库设置 Husky pre-commit hooks，包括 lint-staged（Prettier）、类型检查和测试。用于用户想添加
  pre-commit hooks 或提交前格式化/类型检查/测试时。
---

# setup-pre-commit-zh

> 这是 Matt Pocock `setup-pre-commit` skill 的中文本地化版本。官方英文上游保留在 `upstream/mattpocock/skills/misc/setup-pre-commit`；本目录可按中文团队习惯继续调整。

## 本地化说明

- 优先用中文与用户沟通。
- 保留上游流程、检查点和文件约定。
- 如果本文件与上游英文版本冲突，以本中文版本为准；同步上游时先比较差异，再合并。

# 设置预提交挂钩

## 这设置了什么

- **Husky** 预提交挂钩
- **lint-staged** 在所有暂存文件上运行 Prettier
- **更漂亮**配置（如果丢失）
- 预提交挂钩中的 **typecheck** 和 **test** 脚本

## 步骤

### 1.检测包管理器

检查“package-lock.json”（npm）、“pnpm-lock.yaml”（pnpm）、“yarn.lock”（yarn）、“bun.lockb”（bun）。使用存在的任何一个。如果不清楚，默认为 npm。

### 2.安装依赖项

安装为 devDependency：
```
husky lint-staged prettier
```
### 3.初始化Husky
```bash
npx husky init
```
这将创建 `.husky/` 目录并将 `prepare: "husky"` 添加到 package.json。

### 4. 创建 `.husky/pre-commit`

编写此文件（Husky v9+ 不需要 shebang）：
```
npx lint-staged
npm run typecheck
npm run test
```
**适应**：用检测到的包管理器替换“npm”。如果 repo 在 package.json 中没有“typecheck”或“test”脚本，请忽略这些行并告诉用户。

### 5. 创建 `.lintstagedrc`
```json
{
  "*": "prettier --ignore-unknown --write"
}
```
### 6. 创建 `.prettierrc` （如果缺少）

仅当不存在 Prettier 配置时才创建。使用这些默认值：
```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```
### 7. 验证

- [ ] `.husky/pre-commit` 存在并且可执行
- [ ] `.lintstagedrc` 存在
- [ ] package.json 中的`prepare`脚本是`"husky"`
- [ ] `prettier` 配置存在
- [ ] 运行 `npx lint-staged` 来验证它是否有效

### 8. 承诺

暂存所有更改/创建的文件并提交消息：“添加预提交挂钩（husky + lint-staged + prettier）”

这将通过新的预提交挂钩运行——这是一个一切正常的良好烟雾测试。

## 注释

- Husky v9+ 不需要 hook 文件中的 shebangs
- `prettier --ignore-unknown` 跳过 Prettier 无法解析的文件（图像等）
- 预提交首先运行 lint-staged（快速，仅分阶段），然后进行完整的类型检查和测试