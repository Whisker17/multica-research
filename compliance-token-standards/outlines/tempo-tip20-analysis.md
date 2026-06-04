---
topic: "Tempo TIP-20 + TIP-403 深度分析"
project_slug: "compliance-token-standards"
topic_slug: "tempo-tip20-analysis"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "compliance-token-standards/outlines/tempo-tip20-analysis.md"
  draft: "compliance-token-standards/research-sections/tempo-tip20-analysis/drafts/round-{n}.md"
  final: "compliance-token-standards/research-sections/tempo-tip20-analysis/final.md"
  index: "compliance-token-standards/research-sections/_index.md"

scope: "深度分析 Tempo 的 TIP-20 token 标准及其配套的 TIP-403 Policy Registry，涵盖：(1) TIP-20 核心架构——Precompile suite 实现、TIP-20 Factory（createToken 接口）、确定性地址派生、与 ERC-20 的向后兼容性、memo/rewards 扩展字段、ERC-7572 contract URI 支持；(2) TIP-403 Policy Registry 合规机制——Whitelist Policy 与 Blacklist Policy、跨 token 共享 policy、token 与 policy 的绑定方式、TIP-1015 compound policies、Chainalysis 自动覆盖；(3) Transfer 流程与合规执行路径——transferAuthorized modifier、sender/receiver 双重检查、系统级函数（systemTransferFrom/transferFeePreTx/transferFeePostTx）；(4) RBAC 与发行方控制——ISSUER_ROLE（mint/burn）、PAUSE_ROLE/UNPAUSE_ROLE（紧急控制）、BURN_BLOCKED_ROLE（销毁被封锁地址 token）、Admin 权限管理；(5) 支付优化特性——Payment Lanes（独立 blockspace，55%/45% 分配）、Fee AMM（任意 TIP-20 token 支付交易费并自动兑换）、StablecoinDEX（端对端批量撮合）、Transfer Memos（标准 ERC-20 + 32-byte memo）、sub-millidollar 转账成本、TIP-1034 Channel Reserve Precompile；(6) Rewards 分发机制——Opt-in 奖励分发、reward recipient 设置、constant-time distribution、自动转发到指定接收地址；(7) 扩展 TIPs 生态——TIP-1004（permit）、TIP-1006（burnAt）、TIP-1015（compound policies）、TIP-1022（virtual address deposit forwarding）、TIP-1026（logoURI）、TIP-1034（channel reserve）、TIP-1035（implicit approval list）；(8) 生态合作——Chainalysis 覆盖、AllUnity/Bridge/LayerZero 集成、Currency identifier（'USD'/'EUR'）、KlarnaUSD、Tempo Zones（隐私执行环境）；(9) 合规能力 Taxonomy 映射——按 WHI-177 建立的 8 类合规能力框架评估 TIP-20，与 B20/ERC-3643 进行焦点对比。主要调研方法：TIP-20/TIP-403 文档 spec 为主，tempoxyz/tempo 源码交叉验证（pinned commit: 2b0bb3025ebc532cc1287e714230a8f9f5f82be4），tempoxyz/docs 辅助（pinned commit: 7035c72cdc4b66c4fa349b533a713a5a9491c2f6）。所有源码引用须注明 commit hash。"
audience: "区块链协议工程师、RWA/合规产品负责人、机构金融/BD 团队，以及 Research Review Agent。读者熟悉 EVM、precompile 架构、ERC-20 标准和基础合规概念，但需要一份从协议层合规实现细节出发的 TIP-20 技术深度分析。本文定位为 WHI-177 合规 Token 标准行业趋势研究的配套深度 section。"
expected_output: "compliance-token-standards/research-sections/tempo-tip20-analysis/final.md，深度技术分析文档，包含：TIP-20 precompile 完整架构分析（含地址派生、Factory 接口、ERC-20 兼容层）、TIP-403 Policy Registry 合规机制详解（含 compound policies、Chainalysis 集成）、Payment Lanes/Fee AMM/StablecoinDEX 支付基础设施分析、RBAC 权限矩阵、Rewards 分发机制、扩展 TIPs 技术分析、合规能力 Taxonomy 8 类映射表（与 B20/ERC-3643 焦点对比）"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-04T08:25:00Z"

multica_issue_id: "586341f0-3ee8-4a89-8aa1-3535dd847d90"
report_issue_id: "4c88c789-585a-4c50-965e-628d50cb8bde"
branch_name: "research/compliance-token-standards/tempo-tip20-analysis"
base_commit: "008e66bff9bfb866807c2a1f7f7131be9cba232b"
language: "中文"
research_depth: "deep"

pinned_commits:
  tempoxyz_tempo: "2b0bb3025ebc532cc1287e714230a8f9f5f82be4"
  tempoxyz_docs: "7035c72cdc4b66c4fa349b533a713a5a9491c2f6"
---

# Research Outline: Tempo TIP-20 + TIP-403 深度分析

## Research Questions

1. TIP-20 作为协议层 precompile 级 token 标准，其核心架构设计（Precompile suite、Factory 确定性地址派生、ERC-20 向后兼容层、tempo_precompile! 宏）的完整技术细节是什么？与传统 Solidity ERC-20 实现的关键差异有哪些？
2. TIP-403 Policy Registry 如何实现 token 级别的合规访问控制？Whitelist/Blacklist/Compound（TIP-1015）三种 policy 类型的创建、管理和执行流程是什么？跨 token 共享 policy 的机制和限制？transferAuthorized modifier 在 transfer/mint/burn/reward 操作中如何统一执行？
3. TIP-20 的完整 transfer 流程是什么——从用户发起到最终执行/revert，经过哪些 policy 检查和状态验证？系统级函数（systemTransferFrom、transferFeePreTx、transferFeePostTx）的调用权限和执行语义？
4. TIP-20 的 RBAC 模型（ISSUER_ROLE/PAUSE_ROLE/UNPAUSE_ROLE/BURN_BLOCKED_ROLE/Admin）与 B20 的 7-role 模型和 ERC-3643 的 Agent role 模型相比，权限粒度和安全设计有何异同？
5. Payment Lanes（55%/45% blockspace 分配）、Fee AMM（固定汇率 stablecoin 兑换）和 StablecoinDEX（批量撮合端对端交易）三层支付基础设施如何协同工作？TIP-1034 Channel Reserve Precompile 的链上支付通道设计？
6. TIP-20 Rewards 分发机制的 opt-in 模型、constant-time distribution 算法、reward recipient 转发机制如何实现？与 DeFi 领域常见的 staking/merkle drop 方案相比有何架构优势？
7. 扩展 TIPs（1004/1006/1015/1022/1026/1034/1035）各自解决什么问题？它们如何扩展 TIP-20 的能力边界？
8. Tempo Zones 隐私执行环境如何与 TIP-20/TIP-403 集成？Zone 内的 confidential transfer 如何保留合规检查？
9. 按照 WHI-177 建立的 8 类合规能力 Taxonomy（Identity/KYC、Transfer Policy、Issuer Controls、Sanctions/Blacklist、Recovery、Legal Document/Metadata、Payment Reconciliation、Auditability/Privacy），TIP-20 在每一类的实现深度和设计取舍是什么？与 B20 和 ERC-3643 的关键差异？

## Source Access Constraints

> **C1 — 源码仓库未同步**：本次分析中 `tempoxyz/tempo`（pinned commit `2b0bb3025ebc`）和 `tempoxyz/docs`（pinned commit `7035c72cdc`）均未成功同步到工作环境。技术细节主要依据官方文档站（docs.tempo.xyz）、Tempo Rust API 文档（rustdocs.tempo.xyz）、公开源码（github.com/tempoxyz/tempo）和 Web 搜索结果。关键声明标注为 "docs-stated" 而非 "code-confirmed"。Deep draft 阶段应尝试再次同步仓库；若仍不可用，需在每个技术 claim 处标注证据等级。
>
> **C2 — 代码验证分级**：优先级顺序为 code-confirmed（pinned commit 源码直接验证）> docs-stated（官方文档站描述）> rustdocs-stated（Rust API 文档）> secondary-source（第三方分析文章）> inferred（架构推断）。B20 对比数据来自 WHI-177 landscape research（code-confirmed at base/base@8e8767281d）。

## Items

### item-1: TIP-20 核心架构——Precompile Suite 实现

深度分析 TIP-20 作为 Tempo 原生 precompile 级 token 标准的核心架构设计。

**Precompile 注册与宏系统**：TIP-20 tokens 作为 precompile 注册到 Tempo 的 PrecompilesMap（按地址前缀匹配）。`tempo_precompile!` 宏强制 direct-call-only（禁止 delegatecall）并设置 storage context。需分析 PrecompilesMap 完整注册列表（TIP-20 tokens、TIP20Factory、TIP403Registry、TipFeeManager、StablecoinDEX、NonceManager、ValidatorConfig、AccountKeychain、ValidatorConfigV2）及各自的地址空间。

**TIP20Factory**：部署地址 `0x20Fc000000000000000000000000000000000000`。createToken 接口：token 创建时指定 name、symbol、decimals、currency（ISO 4217 三字母代码）、quoteToken（必须为已部署 TIP-20，USD currency 的 token 必须指定 USD quote token）、supplyCap。Factory 初始化默认值：`transferPolicyId = 1`（always-allow）、`supplyCap = type(uint128).max`、`paused = false`、`totalSupply = 0`。

**确定性地址派生**：`TIP20_PREFIX || lowerBytes`，TIP20_PREFIX = 12 字节 `20C000000000000000000000`，lowerBytes = `keccak256(msg.sender, salt)` 最高 64 位。前 1000 地址（lowerBytes < 1000）保留给协议。需验证地址碰撞概率和安全性分析。

**ERC-20 向后兼容**：TIP-20 暴露完整 ERC-20 接口（balanceOf、totalSupply、transfer、transferFrom、approve、allowance），扩展 memo 支持（transferWithMemo/mintWithMemo/burnWithMemo + 32-byte memo field）和 rewards distribution。

**ERC-7572 Contract URI / TIP-1026 logoURI**：TIP-20 支持 onchain 元数据——TIP-1026 添加可选 logoURI 字段，ERC-7572 contractURI() 支持需验证实现状态。

**Transfer 限制**：TIP-20 token 不能被发送到其他 TIP-20 token 合约地址。`validRecipient` 守卫拒绝零地址或 TIP-20 前缀地址。

- **Priority**: high
- **Dependencies**: none

### item-2: TIP-403 Policy Registry 合规机制

深度分析 TIP-403 Policy Registry 作为 TIP-20 合规基础设施的完整实现。

**Registry 架构**：TIP403Registry 部署地址 `0x403c000000000000000000000000000000000000`。全局单例 precompile，存储所有 policy。policyId 从 2 开始自增（0 和 1 为内置 policy）。

**内置 Policy**：`policyId = 0` always-reject（拒绝所有 token transfer）；`policyId = 1` always-allow（允许所有 token transfer，也是 Factory 创建 token 的默认值）。

**Policy 类型**：
- Whitelist：仅列表中地址可参与 transfer，其他所有地址被阻止
- Blacklist：列表中地址被阻止，其他所有地址允许
- Compound（TIP-1015 扩展）：为 sender/recipient/mint recipient 指定不同的简单策略。结构不可变（创建后不能修改引用），但被引用的简单策略本身可由各自 admin 修改

**Policy 管理接口**：create_policy(admin, policy_type)、update_allowlist/update_blocklist（修改成员）、stage_update_admin/finalize_update_admin（两阶段 admin 转移）、renounce_admin（永久放弃管理权）。

**跨 Token 共享**：一个 policy 可被多个 TIP-20 token 引用。当 policy 更新（如 whitelist 添加/移除地址），所有引用该 policy 的 token 立即生效。同一 policy 也在 StablecoinDEX 和 Rewards 系统中生效——不存在被 blocked 地址通过 DEX 或 reward 侧信道接收流动性的漏洞。

**Chainalysis 集成**：Chainalysis 自动 token 覆盖，包括 TIP-20 memo 解码进行 AML 监控。需分析 Chainalysis 如何与 TIP-403 policy 交互——是否自动维护 blacklist policy。

**Tempo Zones 集成**：TIP-403 policy 控制 Zone 参与资格。Whitelist policy 的 token 需要 issuer 显式 enable zone；Blacklist policy 的 token 需要 issuer 未 disable zone。Zone 内转账保留 TIP-403 policy 检查。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Transfer 流程与合规执行路径

完整追踪 TIP-20 的 transfer 路径，从用户调用到最终状态变更，标注每一步的检查内容和涉及 precompile。

**Standard Transfer 流程**：
1. 用户调用 `transfer(to, amount)` 或 `transferFrom(from, to, amount)`
2. `validRecipient` 守卫：检查 to != address(0) 且 to 不是 TIP-20 前缀地址
3. `transferAuthorized` modifier：调用 `TIP403_REGISTRY.isAuthorized(transferPolicyId, from)` 检查 sender + `TIP403_REGISTRY.isAuthorized(transferPolicyId, to)` 检查 receiver。两者必须都返回 true，否则 revert `PolicyForbids`
4. Pause 状态检查：token 暂停时 revert
5. 余额检查 + 状态变更（扣减 from，增加 to）
6. 发出 Transfer 事件

**Memo Transfer 变体**：`transferWithMemo(to, amount, memo)` / `transferFromWithMemo(from, to, amount, memo)` 额外接受 32-byte memo 参数并发出包含 memo 的事件。

**Mint/Burn 流程**：同样经过 transferAuthorized 检查。Mint 额外检查 supply cap。BurnBlocked 变体需要 BURN_BLOCKED_ROLE + 目标地址必须被 policy 阻止。

**Reward 操作**：distributeReward、setRewardRecipient、claimRewards 同样执行 TIP-403 authorization 检查。

**系统级函数**：
- `systemTransferFrom`：仅可由其他 Tempo 协议 precompile 调用
- `transferFeePreTx`：尊重暂停状态（暂停时 revert）
- `transferFeePostTx`：故意在暂停时仍可执行（确保暂停操作本身的交易能完成并获得 fee refund）

需产出完整的 transfer 执行流程图（含 policy 检查分支和 revert 路径）。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: RBAC 与发行方控制

深度分析 TIP-20 的角色权限模型及其与 B20/ERC-3643 的对比。

**TIP-20 角色模型**：

| 角色 | 功能 | 权限范围 |
|------|------|----------|
| Admin | grantRole/revokeRole/renounceRole/setRoleAdmin | 角色管理元权限 |
| ISSUER_ROLE | mint/burn/mintWithMemo/burnWithMemo | 供应量控制 |
| PAUSE_ROLE | pause token | 紧急暂停 |
| UNPAUSE_ROLE | unpause token | 恢复操作 |
| BURN_BLOCKED_ROLE | 销毁被 TIP-403 policy 阻止的地址余额 | 制裁执行 |

**与 B20 对比**（code-confirmed at base/base@8e8767281d）：B20 有 7 个角色——DefaultAdmin、Mint、Burn、BurnBlocked、Pause、Unpause、Metadata。关键差异：B20 额外有 Metadata role（updateName/updateSymbol）和 renounceLastAdmin 安全机制；B20 Asset 变体额外有 OPERATOR_ROLE 和 announcement 机制。

**与 ERC-3643 对比**：ERC-3643 使用 Agent role 模型，支持 freeze（地址级冻结）、forced transfer（强制转移 token 到指定地址）和 recovery（密钥丢失恢复）。TIP-20 和 B20 均不支持 forced transfer——只能 burn blocked 地址余额，不能将其转移到其他地址。这是协议层方案与应用层方案在 Recovery 能力上的关键差异。

**Pause 语义**：Pause 控制所有 transfer 操作和 reward 相关 flow。暂停时 administrative/configuration 函数仍然允许。transferFeePostTx 在暂停后仍可执行（fee refund 保证）。

- **Priority**: high
- **Dependencies**: item-1

### item-5: 支付优化——Payment Lanes、Fee AMM 与 StablecoinDEX

深度分析 TIP-20 支付基础设施的三层架构及其协同工作方式。这是 TIP-20 区别于 B20 和 ERC-3643 的最显著差异化特性。

**Payment Lanes**：
- 分类方法：`tx.to` 是否具有 TIP-20 前缀 `0x20c0`——纯交易数据分类，无需访问链上状态
- 非支付交易上限 45% 总 Gas 限制（225 MGas），支付交易保证至少 55% 区块空间
- Block 结构：block header 携带 general lane 和 payment lane 分别的 gas limit；block body 按 system tx -> general lane -> sub-blocks -> end-of-block system tx 顺序执行
- 设计目标：消除 "noisy neighbor" 问题，支付交易费用低且稳定（即使网络其他活动 spike）

**Fee AMM**：
- 定位：非通用 DEX，而是支付基础设施——仅在支付交易费时触发兑换
- Pool 构成：user token（用户持有的 stablecoin）+ validator token（验证器偏好的结算 token）
- 汇率模型：预先固定的汇率规则，不依赖外部市场价格
- 执行时机：end-of-block system transaction 阶段
- 无原生 Gas token：Tempo 不设原生 Gas token，所有交易费用 TIP-20 稳定币支付

**StablecoinDEX**：
- 定位：singleton orderbook precompile，专门用于同一底层资产的稳定币之间交易（不同 USD token、代币化存款、合成美元）
- 撮合模型：不连续撮合，新订单在 block 内积累，end-of-block system call 批量撮合（减少 MEV）
- 价格优先级：按 price tick 分组，price-time priority
- Flip orders：支持自动反向的订单类型（TIP-1030 允许同 tick flip）

**TIP-1034 Channel Reserve Precompile**（T5 hardfork）：
- 将 channel reserve 内嵌为原生 precompile，声称比 legacy MPP 合约节省最高 72% Gas
- 支付通道功能：channel open、settle、top-up、close、request-close、withdraw
- Payment-lane 资格：MPP 迁移到 protocol-native channel reserve 路径以获得 payment-lane 资格

**子-millidollar 成本**：目标 < $0.001/transfer；T5 性能达 18K TPS，平均 block time 500ms。

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-6: Transfer Memos 与 Payment Reconciliation

深度分析 TIP-20 memo 机制及其在支付对账场景中的应用。

**32-byte Memo 字段**：
- 支持的函数：`transferWithMemo(to, amount, memo)`、`transferFromWithMemo(from, to, amount, memo)`、`mintWithMemo(to, amount, memo)`、`burnWithMemo(from, amount, memo)`
- Memo 通过事件发出，不存储在链上状态中
- 用例：支付引用 ID、发票号、客户 ID、跨系统对账标识

**ISO 4217 Currency Identifier**：
- `currency()` 返回三字母代码（"USD"/"EUR"/"GBP"）
- 创建时设定不可更改
- `currency == "USD"` 的 token 可用于支付交易费
- 在 StablecoinDEX 中用于路由同一底层资产的不同 token

**Chainalysis Memo 解码**：Chainalysis 原生集成 TIP-20 memo 解码进行 AML 监控。使得传统支付系统的 reference ID 在链上可追溯、可审计。

**与传统支付系统对接**：
- 存款场景：exchange 使用单一 master hot wallet + customer ID memo，按 memo 事件解析进行入账
- TIP-1022 Virtual Address 替代方案：为每个客户生成虚拟存款地址，自动转发到 master wallet，消除 sweep 交易

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-7: Rewards 分发机制

深度分析 TIP-20 原生 rewards distribution system。

**Opt-in 模型**：
- 用户通过 `setRewardRecipient(address)` 设置 reward recipient 来 opt-in
- Recipient 可以是用户自身地址或指定的转发地址
- 未 opt-in 的用户不参与 reward 分配

**Distribution 机制**：
- `distributeReward(amount)` 由任何人调用，向所有 opted-in 持有者按比例分配
- Constant-time 更新：不管 token 持有者数量多少，分配操作的 Gas 恒定
- 算法设计：需分析具体实现——推测使用 cumulative reward-per-token 记账模型（类似 Synthetix StakingRewards 但内嵌于 precompile）

**Claim 机制**：
- `claimRewards()` 由 opted-in 持有者调用，领取累积的 reward
- Claim 操作同样经过 TIP-403 transferAuthorized 检查——被 blocked 的地址无法 claim reward

**合规整合**：
- distributeReward、setRewardRecipient、claimRewards 均执行 TIP-403 policy 检查
- 不存在通过 reward 侧信道绕过 policy 的漏洞
- Pause 控制覆盖 reward 操作

**与传统方案对比**：
- 无需单独的 staking 合约
- 无需 merkle drop 的链下证明生成和链上验证
- 直接集成在 token precompile 中，所有 TIP-20 token 标准化支持
- 用例：利息型稳定币发行（如 KlarnaUSD 向持有者分发收益）

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-8: 扩展 TIPs 技术分析

逐一分析主要扩展 TIPs 的技术设计和解决的问题。

| TIP | 名称 | 解决的问题 | 关键技术细节 |
|-----|------|-----------|-------------|
| TIP-1004 | EIP-2612 Permit | Gasless 授权 | Off-chain 签名 permit，避免单独 approve 交易 |
| TIP-1006 | burnAt | 授权 burn | 授权管理员从任意地址 burn token，扩展 ISSUER_ROLE 能力 |
| TIP-1015 | Compound Policies | sender/recipient 不同规则 | 一个 compound policy 引用三个简单策略（sender/recipient/mint recipient）；结构不可变但被引用策略可修改 |
| TIP-1022 | Virtual Address Forwarding | 消除 sweep 交易 | Precompile-native 虚拟地址，deposit 自动转发到 master wallet；消除 per-address 状态创建和 state bloat |
| TIP-1026 | Token Logo URI | 链上元数据 | 可选 onchain logoURI，替代链下 token registry |
| TIP-1034 | Channel Reserve Precompile | 支付通道 Gas 优化 | 原生 precompile 支付通道（open/settle/top-up/close/withdraw）；声称 72% Gas 节省；payment-lane 资格 |
| TIP-1035 | Implicit Approval List | 简化协议交互 | 协议 precompile 白名单免 approve；保留 normal TIP-20 allowance semantics |

重点分析：
- TIP-1015 + TIP-403 如何协同实现细粒度合规控制（sender 允许所有持有者 + receiver 需要 KYC whitelist 的典型场景）
- TIP-1022 对支付处理商的实际价值（对比传统 sweep 模式的 Gas 成本和运维复杂度）
- TIP-1034 对 channel-based 支付应用（如 Machine Payments Protocol）的支撑

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-5

### item-9: 生态合作与集成

分析 TIP-20 的生态系统建设和外部集成。

**Chainalysis 集成**：
- 自动 token 覆盖：TIP-20 token 自动纳入 Chainalysis 监控范围
- Memo 解码：Chainalysis 解码 TIP-20 memo 进行 AML 监控
- 来源：Chainalysis 2026 年 3 月博客公告

**跨链基础设施**：
- AllUnity 集成：需调研具体角色（发行基础设施 / stablecoin 发行方）
- Bridge 支持：跨链桥接 TIP-20 token
- LayerZero 集成：跨链消息传递和 token 桥接

**Currency Identifier 生态应用**：
- `currency()` ISO 4217 三字母代码在 StablecoinDEX 路由中的作用
- 在 Fee AMM 中确定 user token / validator token 配对
- 跨 token 的同一底层资产识别

**KlarnaUSD**：首个银行发行 TIP-20 token（2025 年 12 月测试网）。验证 TIP-20 对传统金融机构发行合规稳定币的可行性。

**Tempo Zones**（隐私）：
- 定位：平行区块链形式的隐私执行环境
- 运营者模型：受信任实体管理 Zone，可监控活动和控制访问但不控制资产
- 资产互操作：Zone 内资产与 Mainnet、其他 Zone、onramp、流动性池完全互操作
- TIP-403 Policy 适用：Zone 参与受 token 的 TIP-403 policy 控制
- 合规设计："Privacy, not secrecy"——授权实体（监管者、内部审计）可获得特殊访问密钥
- 用例：payroll、treasury management、confidential supply chain finance

**设计合作伙伴**：Anthropic、DoorDash、Mastercard、Nubank、OpenAI、Ramp、Revolut、Shopify、Standard Chartered、Visa。

**性能数据**：T5 18K TPS、500ms block time、0.5s deterministic finality、< $0.001/transfer target。

- **Priority**: medium
- **Dependencies**: item-2, item-5, item-6

### item-10: 合规能力 Taxonomy 映射与焦点对比

按 WHI-177 建立的 8 类合规能力 Taxonomy，系统评估 TIP-20 在每一类的实现深度，并与 B20（code-confirmed）和 ERC-3643 进行焦点对比。此 item 是本研究的核心总结产出。

**评估方法**：每类能力按「TIP-20 实现方式 -> 设计取舍 -> 与 B20/ERC-3643 差异」的结构展开。证据等级标注（docs-stated / code-confirmed / secondary / inferred）。

**8 类能力评估框架**：

| 能力类别 | TIP-20 核心实现 | 关键评估问题 |
|---------|----------------|-------------|
| Identity / KYC | 无原生身份层，wallet-level TIP-403 policy + Chainalysis 间接监控 | 与 ERC-3643 ONCHAINID 的根本差异？对 institutional KYC 需求的满足程度？ |
| Transfer Policy | TIP-403 registry + TIP-1015 compound + 跨 token 共享 | 与 B20 4-slot policy 的粒度差异？compound policy 的灵活性 vs B20 executor slot？ |
| Issuer Controls | 4-role RBAC（ISSUER/PAUSE/UNPAUSE/BURN_BLOCKED）+ Admin | 无 forced transfer/clawback（与 ERC-3643/ERC-1644 差异）；与 B20 7-role 的粒度差异 |
| Sanctions / Blacklist | BURN_BLOCKED + blacklist policy + Chainalysis 原生覆盖 | Chainalysis 集成深度——自动 blacklist 维护还是仅监控？ |
| Recovery | burnBlocked + TIP-1022 recovery authority（待验证） | 无 forced transfer = 无法将 token 恢复给合法所有者？与 ERC-3643 recovery 差距 |
| Legal Document / Metadata | ISO 4217 currency、TIP-1026 logoURI、ERC-7572 contractURI（待验证） | 无等价 ERC-1643 文档管理；metadata 能力偏向支付场景而非证券场景 |
| Payment Reconciliation | 32-byte memo + ISO 4217 + Payment Lanes + Channel Reserve + Virtual Address | **TIP-20 最强差异化领域**；B20/ERC-3643 无等价功能 |
| Auditability / Privacy | 全链上审计 + memo 审计追踪 + Tempo Zones 隐私层 | Zones 的 "privacy not secrecy" 模型 vs Circle Arc 的 precompile privacy |

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8, item-9

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| precompile_architecture | Precompile 地址（部署地址/前缀格式）、注册方式（PrecompilesMap）、宏系统（tempo_precompile!）、storage context 设置 | item-1, item-2, item-5 |
| factory_interface | createToken 参数（name/symbol/decimals/currency/quoteToken/salt/supplyCap）、初始化默认值、地址派生算法 | item-1 |
| policy_mechanism | Policy 类型（whitelist/blacklist/compound）、policyId 分配、admin 管理（两阶段转移/renounce）、跨 token 共享语义 | item-2, item-3, item-10 |
| transfer_flow | 从用户调用到状态变更的完整路径，每一步检查（validRecipient/transferAuthorized/pause/balance）和涉及 precompile | item-3 |
| rbac_model | 角色名称、功能、权限边界、Admin 元权限、与 B20/ERC-3643 角色模型对比 | item-4, item-10 |
| payment_infrastructure | Payment Lanes 分类方法和 blockspace 分配、Fee AMM pool/汇率/执行时机、StablecoinDEX 撮合模型、block 执行顺序 | item-5, item-6 |
| memo_and_reconciliation | 32-byte memo 传递方式和事件格式、ISO 4217 currency 设定和约束、与传统支付系统对接模式 | item-6, item-9 |
| rewards_mechanism | Opt-in 流程、distributeReward 执行语义、constant-time 算法、claimRewards 流程、compliance 整合 | item-7 |
| extension_tip_analysis | 每个扩展 TIP 的问题定义、技术方案、与核心 TIP-20 的接口点 | item-8 |
| ecosystem_integration | Chainalysis 集成深度、跨链桥接、Zones 架构、设计合作伙伴、性能数据 | item-9 |
| compliance_capability | 在 8 类 Taxonomy 中的具体实现方式、能力强弱评级、与 B20/ERC-3643 焦点对比、证据等级标注 | item-10 |
| evidence_classification | 每个关键 claim 的证据类型：docs-stated / rustdocs-stated / code-confirmed / secondary-source / inferred | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | TIP-20 Precompile 架构图：PrecompilesMap 全景（TIP20Factory、TIP-20 tokens 地址空间、TIP403Registry、TipFeeManager、StablecoinDEX、Channel Reserve），展示组件间的依赖和调用关系 | mermaid | item-1 |
| diag-2 | flow | TIP-403 Policy 执行流程图：从 transferAuthorized modifier 出发，展示 whitelist/blacklist/compound 三种 policy 类型的检查分支，标注 always-allow/always-reject 内置策略和 PolicyForbids revert | mermaid | item-2, item-3 |
| diag-3 | flow | TIP-20 完整 Transfer 流程图：用户发起 -> validRecipient -> transferAuthorized -> pause check -> balance check -> state change -> event emit，含 memo 变体和 system function 分支 | mermaid | item-3 |
| diag-4 | comparison | RBAC 权限矩阵：TIP-20 4-role vs B20 7-role vs ERC-3643 Agent role 对比表，标注每种方案支持的控制操作（mint/burn/pause/freeze/forced transfer/recovery/metadata） | mermaid/table | item-4, item-10 |
| diag-5 | architecture | 支付基础设施三层架构图：Payment Lanes（blockspace 分配 55/45）-> Fee AMM（user token -> validator token 汇率转换）-> StablecoinDEX（end-of-block 批量撮合），展示 block 执行顺序和资金流向 | mermaid | item-5 |
| diag-6 | flow | Fee AMM 资金流向图：用户持有 stablecoin A -> 发起交易 -> Fee AMM 将 A 按固定汇率转换为 validator 偏好的 stablecoin B -> validator 收到 B，展示 end-of-block settlement 机制 | mermaid | item-5 |
| diag-7 | flow | Rewards 分发流程图：issuer distributeReward -> constant-time accounting -> opted-in holder claimRewards -> TIP-403 check -> payout，标注 opt-in/out 状态和 recipient forwarding | mermaid | item-7 |
| diag-8 | taxonomy | 合规能力 Taxonomy 映射图：8 类能力 x TIP-20 实现深度评级（强/中/有限/无），与 B20/ERC-3643 并列，可视化 TIP-20 的差异化优势和能力缺口 | mermaid/table | item-10 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | TIP-20 规范（docs.tempo.xyz/protocol/tip20/spec）、TIP-20 概述（overview）、TIP-20 Rewards 规范（tip20-rewards/overview）、tempo-std Solidity 接口（ITIP20.sol/ITIP20Factory.sol/ITIP20RolesAuth.sol） | 4 |
| src-2 | official_docs | TIP-403 规范（docs.tempo.xyz/protocol/tip403/spec）、TIP-403 概述 | 2 |
| src-3 | official_docs | 扩展 TIPs 规范和概述：TIP-1004、TIP-1006、TIP-1015、TIP-1022、TIP-1026、TIP-1034、TIP-1035（docs.tempo.xyz/protocol/tips） | 3 |
| src-4 | official_docs | Tempo 支付基础设施文档：Payment Lanes 规范、Fee AMM 规范（docs.tempo.xyz/protocol/fees/spec-fee-amm）、StablecoinDEX 文档、Managing Fee Liquidity（guide） | 3 |
| src-5 | code_analysis | tempoxyz/tempo 源码（pinned commit 2b0bb3025ebc）：crates/precompiles/src/tip20/、tip20_factory/、tip403_registry/、tip_fee_manager/、stablecoin_dex/；若不可用，标注 C1 约束并降级为 docs-stated | 3 |
| src-6 | code_analysis | Rust API 文档（rustdocs.tempo.xyz/tempo_precompiles/）和 tempo-std Solidity 接口（github.com/tempoxyz/tempo-std）——用于交叉验证文档声明 | 2 |
| src-7 | comparison_baseline | WHI-177 landscape research final section（compliance-token-standards/research-sections/compliance-token-landscape/final.md）中的 B20 代码分析（base/base@8e8767281d code-confirmed）和 ERC-3643 分析——作为合规能力 Taxonomy 映射的对比基准 | 1 |
| src-8 | industry_analysis | 第三方技术分析：Sentora/Jesus Rodriguez Tempo 技术观察、Seungmin Jeon Tempo 架构分析系列、Chainstack Tempo 开发指南、Datawallet Tempo 介绍 | 3 |
| src-9 | ecosystem_evidence | Chainalysis Tempo 覆盖公告（2026 年 3 月博客）、KlarnaUSD 公告、Tempo Zones 公告（tempo.xyz/blog/introducing-tempo-zones/、tempo.xyz/blog/privacy-on-tempo） | 3 |

## Required Output Tables

### 合规能力 Taxonomy 映射表（TIP-20 深度评估）

Deep draft 必须包含以下 8 类 Taxonomy 映射表。与 WHI-177 的全景版不同，本表对 TIP-20 每一类能力进行深度拆解（具体实现方式、函数/precompile 引用、设计取舍），B20 和 ERC-3643 列作为焦点对比参考。

| 能力类别 | TIP-20 实现方式 | TIP-20 设计取舍 | B20 对比 (code-confirmed) | ERC-3643 对比 | 证据等级 |
|---------|----------------|----------------|-------------------------|--------------|---------|
| Identity / KYC | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Transfer Policy | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Issuer Controls | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Sanctions / Blacklist | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Recovery | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Legal Document / Metadata | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Payment Reconciliation | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Auditability / Privacy | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |

### RBAC 角色对比矩阵

| 控制操作 | TIP-20 | B20 (code-confirmed) | ERC-3643 | 备注 |
|---------|--------|---------------------|----------|------|
| Mint | 待填充 | 待填充 | 待填充 | 待填充 |
| Burn | 待填充 | 待填充 | 待填充 | 待填充 |
| Burn Blocked | 待填充 | 待填充 | 待填充 | 待填充 |
| Pause | 待填充 | 待填充 | 待填充 | 待填充 |
| Unpause | 待填充 | 待填充 | 待填充 | 待填充 |
| Freeze (address-level) | 待填充 | 待填充 | 待填充 | 待填充 |
| Forced Transfer | 待填充 | 待填充 | 待填充 | 待填充 |
| Recovery | 待填充 | 待填充 | 待填充 | 待填充 |
| Metadata Update | 待填充 | 待填充 | 待填充 | 待填充 |
| Supply Cap | 待填充 | 待填充 | 待填充 | 待填充 |

### 扩展 TIPs 能力矩阵

| TIP | 类别 | 对应合规能力 | TIP-20 独有? | B20 等价机制 | 状态 |
|-----|------|-------------|-------------|-------------|------|
| TIP-1004 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| TIP-1006 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| TIP-1015 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| TIP-1022 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| TIP-1026 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| TIP-1034 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| TIP-1035 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
