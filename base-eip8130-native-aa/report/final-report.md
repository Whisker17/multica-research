# 从 Base 的 EIP-8130 入手探索 native AA 的方案 -- 最终调研报告

> **项目**: 从 Base 的 EIP-8130 入手探索 native AA 的方案
> **Project slug**: `base-eip8130-native-aa`
> **报告日期**: 2026-06-27
> **报告分支**: `research/base-eip8130-native-aa/final-report`
> **Sections index**: `base-eip8130-native-aa/research-sections/_index.md`
> **语言**: 中文（技术术语保留英文原名）

---

## 执行摘要

本报告回答项目所有者提出的四个核心问题：EIP-8130 与 ERC-4337/EIP-7702 的原理差异与优势、7702 之后的 native AA 版图与 Base 选型动因、Mantle 当前 AA 现状与效果评估、以及 Mantle 是否需要实现类似 native AA 方案的结论与建议。

**核心结论**：

1. **EIP-8130 与 4337/7702 的差异不是"谁更高级"，而是验证和支付进入协议路径的深度不同。** ERC-4337 是应用层 AA（UserOperation + Bundler + EntryPoint + Paymaster），不改共识；EIP-7702 是 EOA 增强（type `0x04` set-code delegation），保留原地址但不提供完整账户配置/payer/batch 生命周期；EIP-8130 是协议原生 native AA（AA typed tx + AccountConfiguration + canonical authenticator + payer + 2D nonce + phased calls），使 txpool/sequencer/execution 路径可直接识别验证、付款与执行结构。

2. **Base 选择 8130 的最强可辩护解释是 bounded validation + OP Stack 可控 rollout。** OP design-doc PR #378 公开评论将 8130 描述为 authenticator/verifier 对节点可见、更 performant、更 opinionated，而 EIP-8141 的验证方法不在 tx 顶层可知。Base 已合并覆盖 tx type、Cobalt gate、AccountConfiguration、actor auth、txpool/RPC/receipt/estimateGas/phased calls 等完整 pipeline 的 PR。但未发现公开完整 memo 正式逐项拒绝 RIP-7560 或 EIP-8141。

3. **Mantle 当前 4337/7702 的效果判定是"效果一般 / 部分指标偏弱，7702 聚合采用证据不足"，不是"效果不好/失败"。** Mantle 2026 YTD 有 11,479 个 UserOps、1,107 个 smart accounts、3 个 paymasters、98.28% sponsored；归一化后约 0.0821 UserOps / 100 tx，与 Base 的 0.0817 接近，但绝对量小使该比值脆弱。7702 有 op-geth plumbing 和 live type `0x04` 样例，但聚合采用数据未知。

4. **Mantle 不应现在直接工程化生产实现 EIP-8130；推荐「PoC 先行」，生产实现放入「暂缓观察」门槛。** EIP-8130 仍是 Draft，需要 client/fork/txpool/RPC/receipt/security/tooling 改造，钱包/provider 生态尚未证明可用。Mantle 应运行有界 devnet PoC 验证 client delta 和 native payer/account config 可行性，同时保持 4337/7702 现有路径并增强生态投入。

---

## 一、AA 方案三层 taxonomy 与 native AA 定义

### 1.1 三层分类

本研究将 AA 方案分为三层（来源：WHI-275 native-aa-framework）：

| 层级 | 方案 | 协议修改 | 特征 |
|---|---|---|---|
| 应用层 AA | ERC-4337 | 无共识修改 | UserOperation + Bundler + EntryPoint + Paymaster + alt mempool |
| EOA 增强 | EIP-7702 | Pectra Core；type `0x04` | EOA set-code delegation；保留原地址；不是完整 native AA |
| 协议原生 native AA | EIP-8130 / RIP-7560 / EIP-8141 | 新 tx type + 协议级验证/支付 | 交易有效性、验证、gas 支付或执行调度需要 client/协议规则识别并执行 |

### 1.2 Native AA 的严格定义

本文将 native AA 限定为：交易有效性、账户验证、gas 支付或执行调度需要客户端/协议规则识别并执行，而不只是合约和链下服务自愿配合。按此边界，ERC-4337 不是 native AA；EIP-7702 是协议级 EOA 增强但不是完整 native AA；EIP-8130/RIP-7560/EIP-8141 是完整 native AA 候选。

---

## 二、EIP-8130 原理深度解析

### 2.1 核心机制

EIP-8130（Draft）引入 EIP-2718 AA typed transaction（Base 当前 `0x7B`），把以下语义从应用层提升到协议交易和执行层：

| 原生字段/概念 | 语义 | 与 4337/7702 的差异 |
|---|---|---|
| `sender` / `sender_auth` | EOA 时为 65-byte ECDSA recovery；configured account 时为 authenticator + data | 4337 在 EntryPoint validateUserOp 中做；7702 仍靠 EOA ECDSA |
| `payer` / `payer_auth` | 原生 payer field + payer signature hash（绑定 resolved sender） | 4337 用 Paymaster 合约；7702 无原生 payer lifecycle |
| AccountConfiguration / actor / scope | 配置账户 owner/actor set + scope bits（SENDER/PAYER/CONFIG/SIGNATURE/UNRESTRICTED） | 4337/7702 不提供协议级账户配置管理 |
| 2D nonce + nonce-free | `nonce_key + nonce_sequence` 支持并行 channel；nonce-free 用 10s 短窗口 + replay id | 4337 用 EntryPoint nonce lane；7702 用 EOA nonce |
| `account_changes` | Create/ConfigChange/Delegation 三类账户配置写入 | 无等价物 |
| `calls: Vec<Vec<Call>>` | 按 phase 分组的批量调用；phase 内 atomic，失败后跳过后续 phase | 4337 靠 account calldata；7702 靠 delegate code |
| AA receipt/RPC | `phaseStatuses` 暴露 per-phase outcome | 普通 receipt 不区分内部 call 结果 |

### 2.2 Base 实现路径

Base 从 2026 年 5 月起连续合并 EIP-8130 PR，覆盖完整 pipeline：

- **Types/RPC gate** (5月): #2863/#2866/#2868/#2926/#3008
- **Cobalt 激活/precompile/registry** (6月初): #3119/#3121/#3170/#3440
- **Authenticator/AccountConfiguration/scope** (6月中): #3467/#3534/#3535/#3540/#3557
- **2D nonce/gas/validation** (6月中): #3010/#3585/#3586/#3589/#3595
- **Account changes/EVM/phased calls** (6月下): #3651/#3653/#3680/#3696
- **RPC/receipt/txpool/devnet** (6月下): #3720/#3722/#3723/#3748/#3749/#3753/#3754/#3755/#3763/#3766
- **Open/in-flight** (截至 6月27日): #3698/#3752/#3775

### 2.3 Spec drift 注意事项

EIP-8130 仍是 Draft。Base 已将 tx type 从 local baseline 的 `0x7D` 改为 current main 的 `0x7B`，payer type 从 `0xFA` 改为 `0x7C`。术语也从 owner/verifier 迁移到 actor/authenticator。报告中的常量以核验时实际值为准，不能写成最终规范值。

---

## 三、ERC-4337 与 EIP-7702 的机制与局限

### 3.1 ERC-4337：成熟但有结构性代价

ERC-4337 是当前最成熟的应用层 AA 方案（Final ERC），不需要共识修改。其结构性代价包括：

- **Gas overhead**：外层 EntryPoint 调用、UserOp calldata、validation/execution 双阶段、preVerificationGas、事件日志和 bundle 结算的累加开销
- **基础设施依赖**：bundler、alt-mempool、paymaster 的部署和运维
- **EOA 迁移摩擦**：通常需要新 smart account 地址；v0.8 增加 7702 support 缓解
- **版本碎片化**：v0.6/v0.7/v0.8 字段和接口差异

### 3.2 EIP-7702：EOA 增强，不是完整 native AA

EIP-7702（Final，Pectra 已上线 2025-05-07）让 EOA 通过 type `0x04` 交易写入 delegation indicator，保留原地址并执行 delegate code。它的价值是 EOA 原地址迁移和钱包 UX bridge，但：

- Root authority 仍是 ECDSA EOA
- 不定义 native payer lifecycle、AccountConfiguration、多 owner 生命周期、2D nonce 或 canonical authenticator
- Delegation 持久化但不随 execution revert 回滚

### 3.3 关键校正：7702 与 8130 的关系

EIP-8130 与 7702 的关系是 **composition via AccountChange::Delegation, not replacement**。8130 可通过 `AccountChange::Delegation` 设置/清除 EIP-7702-style delegation indicator，但主授权模型使用 `sender_auth`/`payer_auth`、AccountConfiguration 和 authenticator/verifier，不是复用 7702 的 `authorization_list`/`SignedAuthorization`。

---

## 四、7702 之后的 native AA 版图与 Base 选型动因

### 4.1 主要候选对比

| 方案 | 验证模型 | DoS/mempool 控制 | 成熟度 |
|---|---|---|---|
| EIP-8130 | 显式 authenticator；canonical set 可过滤 | 低-中：authenticator 身份显式 | Draft；Base 大规模实现中 |
| RIP-7560 | 账户/paymaster validation frame | 中-高：需 validation frame 规则和模拟 | Draft RIP；未发现 Base 实现信号 |
| EIP-8141 | VERIFY prefix frame；任意 EVM validation | 中-高：需 prefix 模拟和 gas/opcode 限制 | Draft；Hegota CFI，不是 Scheduled |

EIP-7701（Withdrawn，superseded by EIP-8141）、EIP-2938（Withdrawn）、EIP-3074（Withdrawn，superseded by 7702）均为历史参照。

### 4.2 Base 为什么选择 8130

按证据标签分级：

| 结论 | 证据标签 |
|---|---|
| 8130 的 top-level authenticator 使验证方法对节点可见；8141 需运行 tx 才知道规则违反 | 明确陈述（OP design-doc PR #378 comment） |
| OP Stack 8130 adoption proposal 和 FMA 存在 | design-doc-signal |
| Base 已合并完整 8130 pipeline PR | code-pr-signal |
| Base 倾向 bounded admission + OP Stack 可控 rollout | 合理推断（inference） |
| Base 正式拒绝 RIP-7560 / EIP-8141 | 未发现明确理由（unknown） |

**重要声明**：不能把推断升级为 Base 官方动因。Base 选择 8130 的可证明事实是工程投入和 PR 轨迹，以及 OP #378 公开评论，不是公开选型备忘录。

---

## 五、Mantle AA 现状与效果评估

### 5.1 节点能力

Mantle op-geth（commit `3c1c571e`）已具备 EIP-7702 所需的 execution-client plumbing：`SetCodeTxType = 0x04`、`authorizationList` RPC 字段、Prague/Isthmus/Skadi hardfork wiring。Live RPC 能返回 type `0x04` 交易。

### 5.2 ERC-4337 采用

Mantle 2026 YTD（Dune 快照 2026-01-01 至 2026-06-26）：

| 指标 | Mantle | Base | Arbitrum |
|---|---|---|---|
| UserOps | 11,479 | 1,388,890 | 698,614 |
| Smart accounts | 1,107 | -- | -- |
| Bundle senders | 66 | 272 | 199 |
| Paymasters | 3 | -- | -- |
| Sponsored % | 98.28% | -- | -- |
| UserOps / 100 tx | ~0.0821 | ~0.0817 | ~0.0613 |

归一化比值看似接近，但 Mantle 绝对量极小，该比值对单一应用/bot 流量高度敏感，不能等同于生态健康度相当。

### 5.3 效果判定

按 WHI-275 四类代理指标（链上采用度、开发者体验、基础设施成本/中心化、钱包/SDK 生态），Mantle AA 的准确判定是 **"效果一般 / 部分指标偏弱，7702 聚合采用证据不足"**，不是"效果不好/失败"。差距来源更像生态和可观测性（paymaster diversity、wallet/SDK 覆盖、应用需求、7702 analytics），不像节点能力或合约缺失。

---

## 六、D1-D13 横向对比

以下为五个主要方案的 D1-D13 rubric 评分概要（1=弱/低，5=强/高；D12 高分表示适配成本高）：

| 维度 | ERC-4337 | EIP-7702 | EIP-8130 | RIP-7560 | EIP-8141 |
|---|---|---|---|---|---|
| D1 抽象层级 | 应用层 AA | EOA 增强 | 协议原生 AA | 协议原生 AA | 协议原生 frame |
| D2 协议改动范围 | 无 | Pectra type 0x04 | 新 AA tx + 全 pipeline | 新 AA tx + frames | 新 frame tx + opcodes |
| D3 基础设施依赖 | 高(bundler/EP/PM) | 低-中 | 中(client/authenticator) | 中-高(sandbox) | 中-高(prefix/trace) |
| D4 所有权与密钥 | 合约定义 | ECDSA root | Actor/authenticator/scope | 合约验证 | Frame validation |
| D5 Gas 代付 | Paymaster 成熟 | 无原生 payer | 原生 payer | 原生 paymaster | Frame payer |
| D6 批量原子性 | Account calldata | Delegate batch | Phased calls | Execution frame | Atomic frames |
| D7 Nonce/replay | EP nonce lane | EOA nonce | 2D nonce+nonce-free | 2D nonceKey | Sender nonce |
| D8 EOA 兼容 | 新地址(v0.8+7702) | 强(原地址) | EOA path+delegation | 需 smart account | 需 delegation |
| D9 签名/PQ | 任意合约签名 | ECDSA root | Canonical set 可扩展 | 任意验证 | Signature list |
| D10 成熟度 | Final/成熟 | Final/Pectra | Draft/Base 实现中 | Draft RIP | Draft/CFI |
| D11 安全攻击面 | Bundler/PM/EP | Delegation/storage | Auth/payer/scope/client | Validation/PM/sandbox | Prefix/frame/payment |
| D12 Mantle 适配成本 | 低-中 | 低-中 | 高 | 高 | 高-极高 |
| D13 目标场景 | Gasless/企业/SDK | EOA bridge/DeFi | Native payer/scope/batch | 4337 native 化 | L1 通用 AA/PQ |

---

## 七、Mantle native AA 策略建议

### 7.1 三档建议

| 选项 | 判断 | 依据 |
|---|---|---|
| **现在实现** | 不建议作为主路径 | EIP-8130 Draft；需 client/fork/txpool/RPC/receipt/security/tooling 改造；钱包/provider 生态未证明 |
| **暂缓观察** | 作为生产实现门槛 | 生产实现应等待 spec 稳定、Base public rollout、audit/DoS 经验、wallet/provider 示例和 PoC 数据 |
| **PoC 先行** | **主推荐** | Base 的 PR catalog 提供低成本学习入口；PoC 可验证 diff sizing、native payer/account config 可行性、coexistence 经验 |

### 7.2 PoC 路线图

| 阶段 | 目标 | 退出标准 |
|---|---|---|
| Phase 0: 决策准备 | 锁定目标场景和 EIP/Base commit 参考 | PoC charter |
| Phase 1: Client diff sizing | 估算 Base-to-Mantle 复用度 | reuse/adapt/rewrite/unknown diff table |
| Phase 2: 最小 devnet PoC | 证明一条 AA tx 路径 | 本地/devnet demo + test vectors |
| Phase 3: 失败模式测试 | 验证安全边界 | 失败测试可观测可约束 |
| Phase 4: 生态 demo | 测试可用性 | SDK/wallet 脚本 + 4337/7702 共存文档 |
| Phase 5: 生产决策 gate | 决定扩展/暂停/放弃 | 书面 go/no-go memo |

### 7.3 PoC 约束

- 不得修改 Mantle 主网
- 不意味着 4337 或 7702 将被废弃
- 不得在证明 client 可行性之前构建完整钱包生态
- 不得将 Draft EIP-8130 常量或 Base 特定选择视为稳定标准

### 7.4 触发条件

| 触发 | 对建议的影响 |
|---|---|
| EIP-8130 spec 稳定 + Base 锁定生产常量 | 从小 PoC 转向实现规划 |
| Base 发布 public native-AA path + wallet/provider 示例 | 提升 OP Stack 复用和生态信心 |
| Mantle 产品团队选定 native payer/session key/phased-call 为战略优先 | 优先 PoC 和 partner demo |
| Mantle 4337/7702 生态显著改善 | 降低 native AA 生产紧迫性 |
| 安全审计发现不可接受的 payer/authenticator/txpool 风险 | 暂停或放弃 native AA |

---

## 八、面向工程团队的科普

### 一句话总结

- **ERC-4337**: 把 AA 做在协议上方，用 UserOperation、Bundler、EntryPoint、Paymaster 和 smart account 合约协调账户验证与代付。
- **EIP-7702**: 让既有 EOA 原地址通过 type `0x04` set-code delegation 执行 wallet code，但 root authority 和很多账户生命周期仍在 EOA/delegate code 层。
- **EIP-8130**: 把 sender/payer auth、AccountConfiguration、actor/scope、2D nonce、account changes、phased calls 和 AA receipt/RPC 变成 typed transaction 与 client pipeline 可见的协议语义。

### 对 Mantle 意味着什么

EIP-8130 对 Mantle 的价值不是"替代 4337/7702"，而是作为一个 **native account/payer semantics PoC**：验证 Mantle 是否真的需要把 AA admission、payer、account configuration 和 observability 下沉到协议层。如果 Mantle 的短期目标只是 gasless onboarding 和既有钱包 UX，应优先增强 4337/7702 文档、provider/paymaster 多样性、7702 analytics、SDK examples 和 app demand。

---

## 九、Cross-Cutting Analysis

### 9.1 共识点

所有 8 个 research sections 在以下结论上一致：

- EIP-8130 的核心创新是把账户验证、支付和执行语义下沉到协议交易路径
- ERC-4337 不是失败方案，而是有结构性代价的成熟方案
- EIP-7702 是短中期 EOA bridge，不是完整 native AA
- Base 对 8130 的工程投入是强信号，但不等于生态成熟
- Mantle 当前 AA 效果不能简单判定为"失败"

### 9.2 冲突与处理

| 冲突点 | 处理方式 |
|---|---|
| D12 评分各 section 不完全一致 | 以 WHI-275 框架的 checklist 为准：execution client、hardfork、infra、Base 复用、security audit |
| 7702/8130 关系措辞 | 以 WHI-277 校正为准：composition via AccountChange::Delegation, not replacement |
| Mantle AA 效果判定 | 以 WHI-280 为准："效果一般 / 部分指标偏弱"，不升级为"失败" |

### 9.3 Open Questions

1. EIP-8130 仍是 Draft，spec drift 持续发生（tx type bytes、术语、caps 均有变化）
2. Base open PRs (#3698/#3752/#3775) 表明 e2e 测试、pending-state admission 和 auto-delegation 仍在收敛
3. Mantle 具体 client diff sizing 需要 Phase 1 PoC 产出，不在本报告范围
4. Base 是否正式评审并拒绝 RIP-7560/EIP-8141 无公开证据
5. Mantle 7702 全链采用量、unique authorizers、delegate target 分布均未知

---

## 附录 A：Input Research Sections

| Order | Topic slug | Multica issue ID | Main integration commit | Source ID |
|---|---|---|---|---|
| 1 | native-aa-framework | `8e4aa1e2-2554-48e2-847f-54f9f27a4084` | `aa0d69ba` | S1-framework |
| 2 | eip7702-mechanism-limits | `14e24b1d-5f0d-475b-b100-defce4c76216` | `927e7470` | S2-7702 |
| 3 | eip8130-deep-dive | `80d86900-2587-4726-a6af-c102dc5febab` | `c4a6deb2` | S3-8130 |
| 4 | erc4337-mechanism-limits | `5807f01c-922f-4969-bdbf-937f0740b6c8` | `6bf3e8a3` | S4-4337 |
| 5 | mantle-aa-status | `456057db-ab81-4dfb-a6ff-a7ed666477c6` | `e507dffc` | S5-mantle |
| 6 | post7702-native-aa-landscape | `c1205b12-9d26-4200-a547-9e034a901dc9` | `60e395a5` | S6-landscape |
| 7 | native-aa-cross-comparison | `97c9c1e3-020f-48c6-a6aa-9f7b7b13801c` | `b78d2b2d` | S7-comparison |
| 8 | mantle-native-aa-strategy | `605b8c4f-1fdf-4e5c-9f04-f2b5e2d1d348` | `12b51544` | S8-strategy |

## 附录 B：可追溯矩阵

| 报告结论 | 源 Section | 源路径 | Commit SHA |
|---|---|---|---|
| 三层 taxonomy: 应用层/EOA 增强/协议原生 | native-aa-framework (S1) | `base-eip8130-native-aa/research-sections/native-aa-framework/final.md` | `aa0d69ba` |
| EIP-8130 Transaction anatomy 与 12 字段语义 | eip8130-deep-dive (S3) | `base-eip8130-native-aa/research-sections/eip8130-deep-dive/final.md` | `c4a6deb2` |
| Scope bits 与 UNRESTRICTED enforcement | eip8130-deep-dive (S3) | 同上，Section 3.1 | `c4a6deb2` |
| 5 类 AccountChange 写语义 | eip8130-deep-dive (S3) | 同上，Section 3.3 | `c4a6deb2` |
| 2D nonce + nonce-free 10s 窗口 | eip8130-deep-dive (S3) | 同上，Section 5 | `c4a6deb2` |
| Base PR timeline（#2863 到 #3775） | eip8130-deep-dive (S3) | 同上，Section 7.1 | `c4a6deb2` |
| Phased calls execution semantics | eip8130-deep-dive (S3) | 同上，Section 6.2 | `c4a6deb2` |
| EIP-8130 D1-D13 rubric scores | eip8130-deep-dive (S3) | 同上，Section 9 | `c4a6deb2` |
| ERC-4337 UserOperation lifecycle (v0.7) | erc4337-mechanism-limits (S4) | `base-eip8130-native-aa/research-sections/erc4337-mechanism-limits/final.md` | `6bf3e8a3` |
| 4337 gas overhead 结构性来源 | erc4337-mechanism-limits (S4) | 同上，item-2 | `6bf3e8a3` |
| Mantle/Base/Arbitrum UserOps Dune 快照 | erc4337-mechanism-limits (S4) | 同上，item-7 | `6bf3e8a3` |
| EIP-7702 set-code delegation 机制 | eip7702-mechanism-limits (S2) | `base-eip8130-native-aa/research-sections/eip7702-mechanism-limits/final.md` | `927e7470` |
| 7702/8130 composition 校正 | eip7702-mechanism-limits (S2) | 同上，Executive Summary | `927e7470` |
| Mantle op-geth 7702 plumbing 核验 | mantle-aa-status (S5) | `base-eip8130-native-aa/research-sections/mantle-aa-status/final.md` | `e507dffc` |
| Mantle AA "效果一般" 判定 | mantle-aa-status (S5) | 同上，Executive Summary | `e507dffc` |
| 7702 后 native AA 候选全景 | post7702-native-aa-landscape (S6) | `base-eip8130-native-aa/research-sections/post7702-native-aa-landscape/final.md` | `60e395a5` |
| OP #378 评论 8130 vs 8141 | post7702-native-aa-landscape (S6) | 同上，Section 3.2 | `60e395a5` |
| Base 选型证据标签分级 | post7702-native-aa-landscape (S6) | 同上，Section 0 | `60e395a5` |
| D1-D13 横向对比矩阵 | native-aa-cross-comparison (S7) | `base-eip8130-native-aa/research-sections/native-aa-cross-comparison/final.md` | `b78d2b2d` |
| Inter-section tensions 处理 | native-aa-cross-comparison (S7) | 同上，item-1 Known inter-section tensions | `b78d2b2d` |
| PoC 先行主推荐 | mantle-native-aa-strategy (S8) | `base-eip8130-native-aa/research-sections/mantle-native-aa-strategy/final.md` | `12b51544` |
| PoC 路线图 Phase 0-5 | mantle-native-aa-strategy (S8) | 同上，item-5 | `12b51544` |
| 风险登记表与触发条件 | mantle-native-aa-strategy (S8) | 同上，item-6 | `12b51544` |
| 三层 AA 架构图 | mantle-native-aa-strategy (S8) | `base-eip8130-native-aa/research-sections/mantle-native-aa-strategy/assets/three-layer-aa.svg` | `12b51544` |
| 8130 为什么是 native 图 | mantle-native-aa-strategy (S8) | `base-eip8130-native-aa/research-sections/mantle-native-aa-strategy/assets/why-8130-native.svg` | `12b51544` |

## 附录 C：Sections Index Reference

```
base-eip8130-native-aa/research-sections/_index.md
```

8 sections, all status `done`, order 1-8.

## 附录 D：Diagram Assets

### 来自 research sections 的图表

| 图表 | 来源 | 类型 | 资产路径 |
|---|---|---|---|
| 交易结构图 | eip8130-deep-dive (S3) Section 2.4 | Mermaid | 内联 |
| 验证/执行管线图 | eip8130-deep-dive (S3) Section 4.6 | Mermaid | 内联 |
| Base 实现时间线 | eip8130-deep-dive (S3) Section 7.1 | Mermaid timeline | 内联 |
| EIP-7702 机制图 | eip7702-mechanism-limits (S2) Section 1.4 | Mermaid sequence | 内联 |
| 候选范围与矩阵覆盖 | native-aa-cross-comparison (S7) diag-1 | Mermaid flowchart | 内联 |
| Validation/admission 路径对比 | native-aa-cross-comparison (S7) diag-2 | Mermaid flowchart | 内联 |
| 三层 AA 架构对照 | mantle-native-aa-strategy (S8) diag-1 | SVG+PNG | `research-sections/mantle-native-aa-strategy/assets/three-layer-aa.{svg,png}` |
| 8130 为什么是 native | mantle-native-aa-strategy (S8) diag-2 | SVG+PNG | `research-sections/mantle-native-aa-strategy/assets/why-8130-native.{svg,png}` |

本报告未新增图表；所有图表来自上游 research sections。

## 附录 E：方法论说明

### 证据分级

本报告沿用上游 sections 的证据分级体系：

- `local-baseline-verified`: Base 本地 checkout commit 中直接可见
- `remote-pr-diff`: fetched origin/main 或 GitHub PR 显示已实现
- `spec-cited`: 官方 EIP/ERC/RIP 规范文本
- `code-pr-signal`: PR/commit 显示实际投入
- `design-doc-signal`: OP/Base design-doc 存在
- `explicit-public-statement`: 公开材料直接陈述
- `inference`: 合理推断
- `unknown`: 未发现足够证据
- `data-cited`: Dune/RPC/explorer 数据

### 引用的外部结论状态标注

| 外部结论 | 状态 | 核验日期 |
|---|---|---|
| EIP-8130 | Draft | 2026-06-27 |
| EIP-7702 | Final (Pectra) | 2026-06-27 |
| ERC-4337 | Final ERC | 2026-06-27 |
| RIP-7560 | Draft RIP | 2026-06-27 |
| EIP-8141 | Draft; Hegota CFI | 2026-06-27 |
| EIP-7701 | Withdrawn | 2026-06-27 |
| EIP-3074 | Withdrawn | 2026-06-27 |

### TW 推断声明

本报告未引入新调研。所有结论可回溯到上游 final sections。报告中无 `[TW inference]` 标记的结论，因为本次综合未产生超出上游 sections 的推断。

---

*报告生成于 2026-06-27，分支 `research/base-eip8130-native-aa/final-report`。*
