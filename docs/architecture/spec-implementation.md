# Spec 实施入口

Ralph 默认不变；子 agent 入口复用 Spec/Tickets，根据项目约定与实际风险选择共享工作区或独立 worktree。单一整合者收口，共享写入暂停后验证同一快照。不新增调度平台、配置模式或 Git 字段。

C4：用户/GitHub 为 Context，Git 仓库/AI 会话为 Container，规划/实施/review 为 Component；类图描述文档合同。Module 是实施入口，Interface 是已授权 Spec 和项目规则；Implementation 隐藏派发、协调与交付。Depth 来自复用既有 gate/TDD/review，Seam 是 Ticket 与 worker 证据，Adapter 是已有子 agent 能力；合同集中提供 Leverage/Locality。test surface 为文件合同、加载与 Git/publisher 回归，不宣称模型执行或运行时锁已验证。

## 架构 / 调用

当前：
```mermaid
flowchart LR
    User["用户选择入口"] --> Plan["Spec 与 Tickets"]
    Plan --> Ralph["默认 Ralph"] --> Single["单 Ticket 实施"]
    Plan --> C["子 agent 整合者"] --> W["仅独立 worktrees"]
    W --> C --> D["逐票合并 review 与交付"]
```

目标：
```mermaid
flowchart LR
    User["用户实施授权"] --> Plan["同一 Spec 与 Tickets"]
    Plan --> Ralph["默认 Ralph"]
    Plan --> C["承接授权的整合者"]
    C --> Shared["不相交的小任务共享工作区"]
    C --> Isolated["独立提交或滚动整合用 worktrees"]
    Shared --> Quiet["全部写入结束或协调暂停"]
    Isolated --> Merge["串行合并"]
    Quiet --> Review["限定交付范围 review 与验证"]
    Merge --> Review --> Delivery["整合者提交 push 与关闭"]
```

## 时序

当前：
```mermaid
sequenceDiagram
    participant C as 整合者
    participant A as 独立 Worker A
    participant B as 独立 Worker B
    C->>A: Ticket 分支与起点 SHA
    C->>B: Ticket 分支与起点 SHA
    A-->>C: commit 与证据
    C->>C: 合并 review 验证并交付 A
    Note over C,B: B 继续独立写入
```

目标：
```mermaid
sequenceDiagram
    participant C as 整合者
    participant A as 共享 Worker A
    participant B as 共享 Worker B
    participant H as 只读辅助
    C->>A: Ticket 与不相交写入文件
    C->>B: Ticket 与不相交写入文件
    A->>H: 本票查证 不扩大范围
    H-->>A: 证据
    A-->>C: 文件与验证结果
    C->>B: 协调暂停或等待写入结束
    B-->>C: 已暂停或已交回结果
    C->>C: 固定授权批次快照 review 验证与交付
    C->>C: 刷新前沿后继续派发
```

## 状态

当前：
```mermaid
stateDiagram-v2
    [*] --> Eligible
    Eligible --> Running
    Running --> Candidate: 本地 commit
    Candidate --> Integrated: 串行合并
    Integrated --> Delivered: review 验证 push 与关闭
    Delivered --> [*]
```

目标：
```mermaid
stateDiagram-v2
    [*] --> Eligible
    Eligible --> Running: 可安全独立实施
    Running --> Candidate: 文件或 commit 与证据
    Candidate --> Snapshot: 共享写入结束或暂停
    Candidate --> Snapshot: 独立提交串行合并
    Snapshot --> Delivered: 有限 review 验证与交付
    Snapshot --> Stopped: 范围不明 冲突或门禁失败
    Running --> Stopped: 失败或过大
    Delivered --> [*]
    Stopped --> [*]: 保留未完成状态与现场
```

## 文档合同

当前：
```mermaid
classDiagram
    class Ticket
    class GitContract
    class WorkerResult {
        ticket
        worktree_branch
        start_sha
        commit_sha
        tests_and_status
    }
    Ticket --> GitContract : frozen_target
    Ticket --> WorkerResult : isolated_execution
```

目标：
```mermaid
classDiagram
    class Ticket
    class GitContract
    class WorkerResult {
        ticket
        workspace_and_files
        commit_if_isolated
        tests_and_status
    }
    class DeliveryBatch {
        authorized_tickets
        actual_files
        fixed_point
    }
    Ticket --> GitContract : target_unchanged
    Ticket --> WorkerResult : delegated_execution
    WorkerResult --> DeliveryBatch : one_integrator
```

Boundary/Contract/Governance：授权可由主流程传递，规划确认仍不等于实施授权。worker 可在范围内做只读辅助委派，不再拆派实施或绕过 review 预算。共享 worker 不操作 Git/index，整合者在写入全部交回或协调暂停后，对明确授权的文件/批次做有限 review、完整验证和交付；其它工作不混入。独立 worktree 可本地 commit，支持逐票滚动整合；项目禁止新工作区时不自行绕过。最终 Git/blocker 合同与 publication gate 不变，不与其它实施流程消费同一批任务。review 是单票或明确批次的既有双轴纪律，不按 worker 数增加预算。
