# Spec 实施入口

Ralph 保持默认；显式 `implement-spec-subagent-lqy` 复用同一份 Spec/Tickets，独立 worktree 实现，单一整合者交付。不新增调度平台、配置模式或 Git 契约字段。

C4：用户与 GitHub 为 Context；目标 Git 仓库与 AI 会话为 Container；规划、实施、review 为 Component；类图仅描述已有文档合同。Module 为新实施 skill，Interface 为 Spec 引用和明确启动；Implementation 隐藏派发、隔离与整合。Seam 是 Ticket/Git 合同和 worker 结果，Adapter 是宿主已有子 agent 工具；复用既有验证与单票纪律获得 Leverage/Locality。test surface 为 skill 文件合同、skill 加载及既有 Git/publisher 回归；指令不等于运行时锁或端到端保证。

## 架构 / 调用

当前：
```mermaid
flowchart LR
    User["用户"] --> Plan["Spec 与 Tickets"]
    Plan --> Ralph["显式 Ralph"] --> Implement["单 Ticket 实施"]
    Implement --> GitHub["验证后推送与关闭"]
```

目标：
```mermaid
flowchart LR
    User["用户选择入口"] --> Plan["同一 Spec 与 Tickets"]
    Plan --> Ralph["默认 Ralph"] --> Implement["单 Ticket 纪律"]
    Plan --> Coordinator["显式子 agent 整合者"]
    Coordinator --> Workers["独立 worktrees"] --> Implement
    Workers --> Coordinator --> Delivery["串行 review 验证与交付"]
```

## 时序

当前：
```mermaid
sequenceDiagram
    participant R as Ralph
    participant I as Implement
    R->>I: 一个 eligible Ticket
    I->>I: TDD 验证与 review
    I-->>R: 推送并关闭后领取下一票
```

目标：
```mermaid
sequenceDiagram
    participant C as 整合者
    participant A as Worker A
    participant B as Worker B
    par 独立前沿
        C->>A: Ticket 路径分支与起点 SHA
    and
        C->>B: Ticket 路径分支与起点 SHA
    end
    A-->>C: 本地 commit 与验证证据
    C->>C: 串行合并 review 验证并交付 A
    Note over C,B: 立即补位新前沿 不等待整批
    B-->>C: 本地 commit 与验证证据
```

## 状态

当前：
```mermaid
stateDiagram-v2
    [*] --> Eligible
    Eligible --> Implementing
    Implementing --> Verified
    Verified --> Delivered
    Delivered --> [*]
```

目标：
```mermaid
stateDiagram-v2
    [*] --> Eligible
    Eligible --> Running: 未派发且可独立实施
    Running --> Candidate: commit 与证据
    Candidate --> Integrated: 串行合并
    Integrated --> Delivered: review 测试 push 与关闭
    Running --> Stopped: 失败或过大
    Integrated --> Stopped: 冲突或门禁失败
    Delivered --> [*]
    Stopped --> [*]: 保留未交付状态与 worktree
```

## 文档合同

当前：
```mermaid
classDiagram
    class Spec
    class Ticket
    class GitContract
    Spec --> Ticket : blocking_graph
    Ticket --> GitContract : frozen_target
```

目标：
```mermaid
classDiagram
    class Spec
    class Ticket
    class GitContract
    class WorkerResult {
        ticket
        worktree_branch
        start_sha
        commit_sha
        tests_and_status
    }
    Spec --> Ticket : same_blocking_graph
    Ticket --> GitContract : integration_target_unchanged
    Ticket --> WorkerResult : temporary_execution
```

Boundary/Contract/Governance：规划只生成依赖与并行风险，不实施。新入口只处理用户授权 Spec 的 eligible Tickets，整合者在集成 worktree 复用现有 gate；私有工作分支不是 Ticket 新目标。worker 不 push/关闭 issue，不嵌套调度；review 留在主线程，避免依赖子 agent 的再次派发能力。无法并行或隔离则报告阻塞，不静默切换执行入口。与 Ralph/其它整合者的互斥是执行前提，不宣称文档提供 OS 锁；失败保留现场，合入且验证通过后才释放依赖。
