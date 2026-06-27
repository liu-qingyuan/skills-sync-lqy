---
name: migrate-to-shoehorn-zh
description: 把测试文件中的 `as` 类型断言迁移到 @total-typescript/shoehorn。用于用户提到 shoehorn、想替换测试里的
  as，或需要 partial test data 时。
---

# 迁移到 Shoehorn

## 为什么是鞋拔？

`shoehorn` 可以让你在测试中传递部分数据，同时保持 TypeScript 满意。它用类型安全的替代方案替换了“as”断言。

**仅测试代码。**切勿在生产代码中使用鞋拔子。

测试中“as”的问题：

- 受过训练不使用它
- 必须手动指定目标类型
- 对于故意错误的数据，双为（“与类型一样未知”）

## 安装
```bash
npm i @total-typescript/shoehorn
```
## 迁移模式

### 大型对象，所需属性很少

之前：
```ts
type Request = {
  body: { id: string };
  headers: Record<string, string>;
  cookies: Record<string, string>;
  // ...20 more properties
};

it("gets user by id", () => {
  // Only care about body.id but must fake entire Request
  getUser({
    body: { id: "123" },
    headers: {},
    cookies: {},
    // ...fake all 20 properties
  });
});
```
后：
```ts
import { fromPartial } from "@total-typescript/shoehorn";

it("gets user by id", () => {
  getUser(
    fromPartial({
      body: { id: "123" },
    }),
  );
});
```
### `as Type` → `fromPartial()`

之前：
```ts
getUser({ body: { id: "123" } } as Request);
```
后：
```ts
import { fromPartial } from "@total-typescript/shoehorn";

getUser(fromPartial({ body: { id: "123" } }));
```
### `与类型一样未知` → `fromAny()`

之前：
```ts
getUser({ body: { id: 123 } } as unknown as Request); // wrong type on purpose
```
后：
```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```
## 何时使用每个

|功能|使用案例|
| ---------------- | -------------------------------------------------- |
| `fromPartial()` |传递仍进行类型检查的部分数据 |
| `fromAny()` |故意传递错误的数据（保持自动完成）|
| `fromExact()` |强制完整对象（稍后与 fromPartial 交换）|

## 工作流程

1. **收集需求** - 询问用户：
   - 哪些测试文件具有导致问题的“as”断言？
   - 他们是否正在处理仅某些属性重要的大型对象？
   - 他们是否需要故意传递错误的数据进行错误测试？

2. **安装和迁移**：
   - [ ] 安装：`npm i @total-typescript/shoehorn`
   - [ ] 查找带有 `as` 断言的测试文件： `grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] 将 `as Type` 替换为 `fromPartial()`
   - [ ] 将 `asknown as Type` 替换为 `fromAny()`
   - [ ] 添加来自 `@total-typescript/shoehorn` 的导入
   - [ ] 运行类型检查来验证