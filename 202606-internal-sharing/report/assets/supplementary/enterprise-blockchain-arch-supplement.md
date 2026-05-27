---
topic: "企业级区块链架构补充调研（zkSync Prividium / Canton 设计原理）"
project_slug: "202606-internal-sharing"
topic_slug: "supplement-enterprise-arch"
github_repo: "Whisker17/multica-research"
round: 1
status: draft

artifact_paths:
  outline: "202606-internal-sharing/outlines/supplement-enterprise-arch.md"
  draft: "202606-internal-sharing/research-sections/supplement-enterprise-arch/drafts/round-1.md"
  final: "202606-internal-sharing/research-sections/supplement-enterprise-arch/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

draft_metadata:
  outline_commit: "3ee77ec"
  outline_approval: "Orchestrator combined dispatch (comment fdd9ebd3-a6b5-492b-953b-e420c6905268) explicitly instructs outline + deep draft in single pass"
  items_covered: [item-1, item-2, item-3, item-4, item-5, item-6]
  fields_investigated:
    - architecture_design
    - privacy_mechanism
    - trust_boundary
    - enterprise_adoption_evidence
    - mantle_transferability
    - design_tradeoff
  diagrams_produced: [diag-1, diag-2, diag-3, diag-4]
  source_requirement_coverage:
    src-1: full
    src-2: full
    src-3: full
    src-4: partial
    src-5: full
    src-6: full
  generated_at: "2026-05-27"
  language: "zh-CN"
---

# 企业级区块链架构补充调研：zkSync Prividium 与 Canton 设计原理

## 1. Executive Summary

本文是 Slides Outline Chapter 3 Section 3.3 机构金融方向的架构补充材料，深入对比 zkSync Prividium 和 Canton 两个最具代表性的企业级区块链方案的设计原理。

核心结论：**Prividium 和 Canton 代表了企业级区块链隐私的两种范式——"Prove-Not-Reveal"（证明但不泄露）和 "Need-to-Know"（按需可见），两者在信任假设、开发者生态和适用场景上有根本差异。**

Prividium 采用 Validium 架构，将整条链的交易数据私有化，仅向以太坊提交状态根和 STARK 证明。它保留了完整的 EVM 兼容性，开发者可以用 Solidity/Hardhat/Foundry 直接迁移，以太坊 L1 作为中立结算层。这使它成为希望在 EVM 生态内获得企业级隐私的机构的首选——截至 2026 年 5 月，35+ 金融机构参与了 Prividium 验证，包括 Cari Network 联合五家美国区域银行（合计存款 >$600B）构建代币化存款网络。

Canton 则从根本上重新设计了账本模型。它不是"把以太坊做成私有版"，而是构建了一个 **Virtual Global Ledger**，没有任何节点持有完整全局状态，每个 Participant 仅持有自身 Party 相关的合约投影。隐私不是后加的功能，而是架构的基线——Sequencer 只看到加密 blob，Mediator 只看到确认信号，Participant 只看到自己的子交易树。Broadridge DLR 在此架构上达到日均 $368B / 月近 $8T 的回购结算量，DTCC 计划 2026 上半年进入 controlled production MVP。

对 Mantle 的启示：Prividium 的 Proxy RPC + RBAC + Private DA 模式是 OP Stack 上最直接可复现的企业合规栈；Canton 的 Merkle DAG 投影、Observer 角色和 Sequencer/Mediator 职责分离提供了架构设计语言，但技术栈不可直接迁移。

## 2. Item Findings

### 2.1 item-1: zkSync Prividium Validium 核心架构

#### architecture_design

Prividium 的架构本质是一条**许可制 Validium 链**，运行在机构自有基础设施或云环境中，通过三层结算路径锚定到以太坊：

```
用户 → 认证(Okta/SIWE) → Proxy RPC(三步验证) → Sequencer(私有执行)
    → Prover(Airbender GPU, 生成 STARK 证明)
    → ZKsync Gateway(聚合多链证明)
    → Ethereum L1(链上验证, 仅见状态根+证明)

数据存储: PostgreSQL + Blob Store (私有子网, 无互联网暴露)
L1 可见: 仅状态根哈希 + STARK 验证结果 — 零交易数据
```

**Validium 与 ZK Rollup 的核心差异**在于数据可用性：

| 维度 | ZK Rollup (zkSync Era) | Validium (Prividium) |
|------|----------------------|---------------------|
| 交易数据存储 | 以太坊 L1 (链上 blobs/calldata) | 运营商私有数据库 |
| L1 可见内容 | Calldata + 证明 | 仅状态根 + 证明 |
| 状态转换有效性 | ZK 证明保证 | ZK 证明保证（相同） |
| 数据可用性保证 | 以太坊保证 | 运营商保证（降级） |
| 状态可重构性 | 任何人可重构 | 仅运营商可重构 |
| 隐私性 | 公开透明 | 完全私有 |
| 抗审查性 | L1 强制交易 | 受 TransactionFilterer 限制 |

#### privacy_mechanism

Prividium 的隐私是**整链级别的**，不是逐交易配置的。所有交易对外部/L1 观察者完全不可见，这是 Validium 模型的固有特性而非额外功能。ZK 证明保证了状态转换的正确性——任何人都可以在以太坊上独立验证 STARK 证明有效，无需信任运营商或 Matter Labs。

证明系统已从第一代 Boojum (FRI-based STARK) 升级到 **Airbender**：开源 RISC-V 证明系统，支持商用 GPU 运行，官方声称亚秒级区块证明和 ~$0.0001/tx 证明成本，目标 15,000+ TPS。

#### trust_boundary

关键信任边界：**Prividium 的隐私保证是"对外部/L1 观察者隐私"（密码学保证），而非"对运营商隐私"**。运营商（Sequencer + Prover + 数据库）对链内所有数据具有完全可见性。RBAC/Proxy RPC 的权限控制是组织治理层面的执行，而非 ZK proof 层面的密码学保证。

| 组件 | 信任类型 | 可见数据 | 被攻破时影响 |
|------|---------|---------|------------|
| Proxy RPC + Prividium API | 可信企业网关（非密码学） | 完整请求内容 | 权限绕过，但不影响 L1 结算正确性 |
| Sequencer | 可信运营商 | 全部交易+完整状态 | 排序操纵/审查，但无法伪造证明 |
| Prover (Airbender) | 可信运营商→密码学输出 | 执行轨迹 | 输出仍受 STARK 数学约束 |
| PostgreSQL/Blob | 可信运营商存储 | 全量状态 | DA 降级，用户无法独立重构状态 |
| ZKsync Gateway | 半可信聚合 | 仅状态根+证明 | 延迟提交，但无法篡改证明内容 |
| Ethereum L1 | 密码学+去中心化 | 仅状态根+验证结果 | 以太坊级安全保证 |

#### design_tradeoff

DA 降级在 DeFi 场景下不可接受（用户需要无许可逃生），但在机构场景下是**设计特性**——银行运营自己的 Prividium 链，数据可用性由自身 IT 基础设施保证，不存在"信任第三方"的问题。监管法规（GDPR、银行保密法）反而要求交易数据不得无限制公开。

### 2.2 item-2: Prividium 企业准入控制与合规栈

#### architecture_design

Prividium 实现了四层准入控制，从外到内：

**第一层：身份认证** — 支持 Okta OIDC（企业 SSO）、SIWE（加密原生钱包签名）和混合模式。一个用户可关联多个钱包，所有关联钱包继承相同的角色权限。

**第二层：Proxy RPC 网关** — 整个网络的唯一入口，执行三步验证：JWT 令牌验证 → 钱包地址匹配 → 合约函数级权限检查。未授权请求返回 401/403 并记录审计日志。标准 RPC 端点必须保持私有，仅公开暴露 Proxy RPC。

**第三层：RBAC 权限系统** — 通过 Admin Dashboard 管理用户、角色和权限。权限粒度到合约函数级别，可选限制函数参数。管理员无需修改代码即可配置策略。

**第四层：L1 TransactionFilterer** — 部署在以太坊 L1 的合约，过滤通过强制交易路径（绕过 Proxy RPC）提交的交易。白名单内地址允许不受限强制交易，其余仅允许 ETH/ERC-20 转账，禁止合约部署和任意函数调用。

#### enterprise_adoption_evidence

Docker Compose 开发环境（`local-prividium` 仓库）的组件构成反映了企业级打包程度：

- Prividium API（控制/权限/Protected RPC）
- Keycloak（身份管理服务器）
- Admin Panel + User Panel（管理和用户界面）
- zkSync OS + Sequencer + Prover
- L1 Anvil（本地以太坊模拟）
- Block Explorer（私有浏览器）
- Prometheus + Grafana（监控）
- 可选 "institutional repo lending demo"

此外，`zksync-sso` 仓库提供 ERC-7579 模块化智能账户、Passkey、Sessions、Paymaster 和 Account Recovery，与 Prividium SDK 深度集成。

截至 2026-05，Cari Network（由第 27 任美国货币监理署署长创建）正在联合五家美国区域银行（合计存款 >$600B），目标 2026 Q3 试点；Deutsche Bank 确认了合作伙伴关系；BitGo 提供机构级托管整合。

**来源可信度**: 企业参与为 medium-high（基于官方公告和产品页面，部分为供应商声称）；`local-prividium` 代码证据为 high（GitHub 仓库可直接检验），但本地开发环境不等于生产部署证明。

### 2.3 item-3: Canton Participant-Synchronizer 架构与 need-to-know 隐私

#### architecture_design

Canton 的架构与传统区块链在根本假设上不同：**不存在全局共享状态**。

```
传统区块链:                          Canton:
┌────────────────┐              ┌──────────────────────────┐
│  Global State  │              │ Virtual Global Ledger    │
│ All Contracts  │              │ (逻辑联合, 无处存储)       │
│ All Balances   │              └──────┬──────┬──────┬─────┘
│ All History    │                     │      │      │
└───┬────┬───┬──┘                     ▼      ▼      ▼
    ▼    ▼   ▼                  ┌──────┐┌──────┐┌──────┐
  Full  Full  Full              │ P1   ││ P2   ││ P3   │
  Copy  Copy  Copy              │{A,B} ││{B,D} ││{C,E} │
                                └──────┘└──────┘└──────┘
每个节点: 完全相同的副本          每个 Participant: 独有的投影
```

核心组件职责分离：

| 组件 | 职责 | 可见数据 | 不可见数据 |
|------|------|---------|----------|
| **Participant** | 承载 Party，维护 ACS，构造/验证交易 | 本节点托管 Party 的投影 | 非托管 Party 的一切 |
| **Sequencer** | 排序和分发加密消息 | 加密 blob、收件人列表、大小、时间戳 | 交易内容、合约状态、业务逻辑 |
| **Mediator** | 2PC 协调，聚合确认，出具 verdict | 需确认的 Participant、确认/拒绝信号 | 交易内容、为什么确认/拒绝 |
| **Topology Manager** | 管理身份、权限、Package vetting | 拓扑交易（Party-Participant 映射） | 业务交易内容 |

#### privacy_mechanism

Canton 的隐私是 **sub-transaction projection + Merkle DAG blinding + encrypted view distribution**：

1. Requester Participant 运行 Daml Engine，生成交易树并按接收方加密各子树视图
2. Sequencer 排序分发加密消息（看不到内容）
3. 相关 Participants 解密自己的视图并独立验证
4. Mediator 聚合确认结果，出具 approve/reject verdict
5. 各 Participant 根据 verdict 更新本地 ACS

一笔 DvP 交易在不同参与方眼中呈现不同视图：Alice 看到自己的资产转移和对手方必要输出；Bank 只看到自己发行资产的 transfer；Regulator 仅看到被显式加入 observer 的合约。这比 Fabric channel 或常规链下隐私更精细——隐私粒度到子交易级别。

Daml 合约的 signatory/observer/controller 语义使多方授权、义务和可见性成为一等概念，而非依赖 Solidity 风格的任意 modifier 约定。

#### trust_boundary

Sequencer-Mediator 分离的设计意图是**最小化信息暴露面**：

- Sequencer 被攻破：只能影响消息排序（活性攻击），无法读取交易内容或伪造确认
- Mediator 被攻破：只能影响确认/拒绝决策，无法篡改消息顺序或读取内容
- 两者都看不到交易明文——这从架构上消除了排序器可见性带来的 MEV 风险

Canton 的隐私不是 ZK 隐私：它依赖加密路由和协议投影，不提供"明文从未被任何参与方知道"的数学证明。metadata leakage（消息大小、频率、接收者流量模式）仍存在。

### 2.4 item-4: Canton 亚线性集成、分区架构与互操作性

#### architecture_design

Canton 的"亚线性数据集成"是指：**每个节点只处理与自身相关的数据子集，计算和存储开销与该节点参与的交易量成正比，而非与网络总交易量成正比**。这使得 Canton 可以水平扩展——增加 Synchronizer 不增加现有 Participant 的负担。

跨 Synchronizer 互操作通过 **reassignment**（unassignment + assignment）实现，关键约束：

- **非原子性**：合约在源 Synchronizer 上 unassign 后、在目标 Synchronizer 上 assign 前处于不可用状态
- **无跨 Synchronizer 全局排序**：不同 Synchronizer 事件可以以任意顺序出现
- Global Synchronizer 作为公共协调点，连接应用和资产网络，但不应被理解为全局原子结算层

#### enterprise_adoption_evidence

- **Broadridge DLR**: 2026-04 日均 $368B、月近 $8T 的 repo 结算（A 级证据：机构官方生产量）
- **DTCC**: 2025-12-17 公告与 Digital Asset/Canton 合作，目标 2026H1 controlled production MVP，DTC 托管 U.S. Treasury 代币化（B 级证据）
- **J.P. Morgan Kinexys**: 2026-01-07 公告 phased integration throughout 2026（B/D 级：intention 而非生产部署）
- **GS DAP / HSBC Orion**: Digital Asset 客户案例，发行/结算从 T+5 到 <60s（A/B 级）

采用指标需保留口径差异：Global Synchronizer 声称 $2T+/month RWA tokenization、Digital Asset 声称 $1.5T+ real-world securities、$6T assets onchain / 600+ institutions——均为 vendor-reported，未独立审计。

### 2.5 item-5: 两者架构对比与适用场景边界

#### privacy_mechanism

```
┌──────────────────┬────────────────────────────┬──────────────────────────────┐
│ 维度              │ Prividium                  │ Canton                       │
├──────────────────┼────────────────────────────┼──────────────────────────────┤
│ 隐私范式          │ Prove-Not-Reveal           │ Need-to-Know                 │
│                  │ 整链对外不可见              │ 子交易级选择性投影             │
│ 隐私粒度          │ 链级（全有或全无）          │ 子交易级（每方看不同子树）     │
│ 隐私保证方式      │ ZK 证明 + 链下 DA          │ 加密路由 + Merkle DAG 投影    │
│ 对运营商隐私      │ 无（运营商可见全部）        │ 部分（Seq/Med 看不到明文）     │
│ 数据可用性        │ 运营商保证                  │ 各 Participant 本地持有投影    │
│ 结算验证          │ 以太坊 L1 STARK 验证       │ 2PC + Synchronizer 协调       │
│ 开发者生态        │ EVM/Solidity/Foundry       │ Daml/Scala/JVM               │
│ 合约语义          │ EVM 标准                    │ signatory/observer/controller │
│ GDPR 合规        │ 强（数据不上 L1，可删除）    │ 强（各方本地控制数据）         │
│ 适用场景          │ 机构 EVM L2 企业链          │ 多机构协作金融网络             │
│ 不适用场景        │ 需要子交易级多方隐私        │ 需要 EVM 生态/DeFi 组合性     │
└──────────────────┴────────────────────────────┴──────────────────────────────┘
```

#### design_tradeoff

**Prividium 的核心权衡**：用数据可用性降级换取隐私。这在"运营商 = 用户自身"的机构场景中是合理的，但排除了无许可 DeFi 和需要全局状态可组合性的应用。优势是开发者迁移成本极低——任何 Solidity dApp 可直接部署。

**Canton 的核心权衡**：用全局状态缺失换取子交易级隐私。没有全局查询和全局可组合性，但使得一笔多方交易中不同参与方只看到与己相关的部分。优势是金融合约语义最强——Daml 的 signatory/observer/controller 天然映射金融合同的签署方/观察方/控制方。劣势是开发者池小、非 EVM、缺少 DeFi 可组合性。

**与 OP Stack 适配性对比**：

| 维度 | Prividium 模式 | Canton 模式 |
|------|--------------|-----------|
| 与 OP Stack 兼容性 | 高 — Validium 是 ZK Stack 变体，架构思路可映射到 OP Stack L3 | 低 — 完全不同的执行模型和账本结构 |
| 可复现成本 | 中 — 需构建 Proxy RPC、RBAC、Private DA，但不改变 EVM 执行 | 高 — 需重建投影/2PC/Daml 等价能力 |
| 企业客户理解成本 | 低 — "你熟悉的 EVM，但是私有的" | 高 — 需要理解 Daml 和 Virtual Global Ledger |
| 开发者迁移成本 | 低 — Solidity/Foundry 直接可用 | 高 — 需学习 Daml |

### 2.6 item-6: 对 Mantle 的启示与最小可行合规技术栈

#### mantle_transferability

**从 Prividium 可直接借鉴的组件**（OP Stack 可复现）：

1. **Proxy RPC + 合规网关**: 在现有 Mantle RPC 前加认证/权限代理层，支持 Okta/SIWE，实现合约函数级 RBAC
2. **Private DA / Validium Zone**: 企业 L3 Zone 采用 Validium 模式，交易数据留在运营商私有存储，L2/L1 仅见状态根+证明
3. **TransactionFilterer 等价物**: L1/L2 bridge 合约中加入白名单/交易类型过滤，限制非授权强制交易
4. **私有 Block Explorer + 审计 API**: 仅授权用户可查看链上数据，支持 Selective Disclosure
5. **Admin Dashboard**: 用户/角色/权限管理界面，运营商无需写代码即可配置策略

**从 Canton 应借鉴的设计思想**（概念可借鉴，技术栈不可直接迁移）：

1. **Regulatory Observer 角色**: 合约级 observer role，监管方获得可审计视图而非完整明文
2. **Sequencer/Mediator 职责分离**: 可引入独立 compliance/verdict service 对企业 Zone 交易做 pre-execution policy verdict
3. **ACS Commitment 等价物**: 对企业 L3 / Private DA 维护可验证状态摘要，供多方 reconciliation
4. **Merkle view blinding**: 为隐私交易设计子动作承诺树，向不同角色分发加密 view

**不应直接迁移的部分**：

- Daml Runtime / Daml-LF — 与 EVM 兼容目标冲突
- Scala/JVM Canton monorepo — 运维成本过高
- Canton 2PC 作为共识 — 与 Rollup 安全模型冲突

#### Mantle 最小可行合规技术栈路线

```
Phase 1 (0-3 月): 准入与审计 MVP
┌──────────────────────────────────────────┐
│  Compliance RPC Gateway (认证+RBAC)      │
│  Identity / KYC Registry (合约级)        │
│  Sequencer Policy Engine (策略执行)      │
│  Audit Log Exporter (可导出审计日志)     │
│  L1 Bridge Filter (限制未授权强制交易)   │
└──────────────────────────────────────────┘

Phase 2 (3-9 月): 私有数据层
┌──────────────────────────────────────────┐
│  Private DA / Encrypted Archive          │
│  Selective Disclosure API                │
│  zkKYC / Compliance Proof PoC            │
│  Regulatory Observer API                 │
└──────────────────────────────────────────┘

Phase 3 (9-18 月): 企业 L3 / Validium Zone
┌──────────────────────────────────────────┐
│  Per-tenant L3 Zone (Validium 模式)      │
│  Zone Sequencer + Private DA             │
│  ZonePortal Settlement to Mantle L2      │
│  Admin Dashboard (无代码策略配置)         │
└──────────────────────────────────────────┘
```

**技术差距矩阵更新（对应 Slide 18）**：

| 能力 | Prividium 已有 | Canton 已有 | Mantle 现状 | 差距等级 |
|------|-------------|-----------|-----------|---------|
| 合规 RPC 网关 | Proxy RPC + 3-step auth | N/A (不同架构) | 无 | 高 — 首要建设 |
| RBAC 权限 | 合约函数级 RBAC | Daml signatory/observer | 无 | 高 |
| 私有 DA | Validium (运营商 DB) | Participant 本地 ACS | EigenDA (公共) | 高 — 需 Validium Zone |
| 身份注册 | Okta/SIWE + Keycloak | Party/Participant topology | 无原生方案 | 高 |
| ZK 结算证明 | STARK (Airbender) | N/A (2PC 协议) | SP1 validity (规划中) | 中 |
| 审计/Selective Disclosure | Private Explorer + SD | Observer + 审计日志 | 无 | 高 |
| 企业 L3/Zone | ZK Stack Validium 变体 | Multi-Synchronizer | 无 | 高 — 中期重点 |
| 开发者工具 | Solidity/Foundry 兼容 | Daml (小众) | Solidity/Foundry | 低 — 已具备 |

## 3. Diagrams

### diag-1: Prividium 端到端交易流程与三层结算

```text
Prividium 三层结算路径

[用户/DApp] ──HTTPS──> [IdP: Okta/SIWE] ──JWT──> [Proxy RPC]
                                                     │
                                    三步验证: JWT + 钱包 + 函数权限
                                                     │
                                                     ▼
                                              [Sequencer RPC]
                                              (私有执行, 全量可见)
                                                     │
                                          ┌──────────┼──────────┐
                                          ▼                      ▼
                                   [PostgreSQL]          [Prover Farm]
                                   (完整 L2 状态)        (Airbender GPU)
                                   (私有子网)            (STARK 证明)
                                                              │
                          ═══════════════════════════════════════════
                          │  仅状态根 + STARK 证明离开私有边界   │
                          ═══════════════════════════════════════════
                                                              │
                                                              ▼
                                                     [ZKsync Gateway]
                                                     (聚合多链证明)
                                                              │
                                                              ▼
                                                     [Ethereum L1]
                                                     (链上验证, 不可篡改)
                                                     (可见: 状态根 + 验证结果)

信任边界总结:
  密码学保证: Prover → Gateway → Ethereum (STARK 证明链)
  组织治理:   IdP → Proxy RPC → Sequencer → PostgreSQL (运营商控制)
```

### diag-2: Canton Participant-Synchronizer 架构

```text
Canton 交易提交与 2PC 确认流程

[Enterprise App]
      │ Submit Daml command
      ▼
[Requester Participant]
      │ 1. 解释 Daml, 构建交易树
      │ 2. Merkle DAG 盲化, 按接收方加密视图
      │
      ▼ 签名加密请求
[Sequencer] ─────────────────────────> [Confirming Participants]
  │ 排序分发加密消息                      │ 解密可见视图
  │ (看不到内容)                         │ 验证一致性/授权
  │                                      │
  ▼                                      ▼ Approve/Reject
[Mediator] <──── 聚合确认信号 ──────────────
  │ (看不到内容, 只看信号)
  │ 出具 Verdict
  │
  ▼ Distribute Verdict
[All Participants] ──> 更新本地 ACS (if approved)

可见性矩阵:
  Sequencer:   加密 blob + 收件人 + 时间戳 (无明文)
  Mediator:    确认方列表 + 信号 + 截止时间 (无明文)
  Participant: 仅自身 Party 的子交易投影
  Regulator:   仅被显式加入 observer 的合约
```

### diag-3: Prividium vs Canton 对比

```text
┌─────────────────────┬──────────────────────┬──────────────────────┐
│                     │ Prividium            │ Canton               │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ 隐私范式            │ Prove-Not-Reveal     │ Need-to-Know         │
│ 隐私粒度            │ 整链级               │ 子交易级             │
│ 对 L1/公众          │ 完全不可见 (ZK)      │ N/A (非 L1 结算)     │
│ 对运营商            │ 完全可见             │ 分职责部分可见        │
│ 对其他参与方        │ N/A (单运营商)       │ 按 Daml 角色投影      │
│ 数据可用性          │ 运营商 DB            │ 各方本地 ACS          │
│ 结算信任            │ 以太坊 ZK 验证       │ 2PC + Synchronizer    │
│ 开发语言            │ Solidity             │ Daml                 │
│ GDPR 合规           │ 强                   │ 强                   │
│ OP Stack 适配       │ 高                   │ 低                   │
│ 最佳场景            │ 机构 EVM 企业链      │ 多机构协作网络        │
└─────────────────────┴──────────────────────┴──────────────────────┘
```

### diag-4: Mantle 最小可行合规技术栈

```text
Mantle 企业合规技术栈分阶段建设路线

Phase 1                    Phase 2                   Phase 3
(准入与审计 MVP)            (私有数据层)               (企业 L3 Zone)
                                                      
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────┐
│ Compliance RPC  │   │ Private DA /    │   │ Per-tenant L3 Zone  │
│ Gateway         │──>│ Encrypted       │──>│ (Validium 模式)     │
│                 │   │ Archive         │   │                     │
│ Identity/KYC    │   │                 │   │ Zone Sequencer      │
│ Registry        │   │ Selective       │   │ + Private DA        │
│                 │   │ Disclosure API  │   │                     │
│ Sequencer       │   │                 │   │ ZonePortal          │
│ Policy Engine   │   │ zkKYC PoC      │   │ Settlement → L2     │
│                 │   │                 │   │                     │
│ Audit Log       │   │ Regulatory      │   │ Admin Dashboard     │
│ Exporter        │   │ Observer API    │   │ (无代码配置)        │
│                 │   │                 │   │                     │
│ L1 Bridge       │   │                 │   │                     │
│ Filter          │   │                 │   │                     │
└─────────────────┘   └─────────────────┘   └─────────────────────┘

借鉴来源:
  Prividium → Proxy RPC, RBAC, Private DA, TransactionFilterer, Explorer
  Canton   → Observer 角色, 职责分离, ACS Commitment, 审计设计语言
```

## 4. Source Coverage

| 来源要求 | 覆盖度 | 证据 |
|---------|--------|------|
| src-1 internal_research | full | 复用 WHI-334/335/336/337/338/343/348，enterprise-canton/final.md，enterprise-privacy/final.md，competitor-zksync/final.md |
| src-2 official_docs (Prividium) | full | zkSync Prividium Architecture、Overview、Features 官方文档 |
| src-3 official_docs (Canton) | full | Canton architecture、privacy、multi-synchronizer、topology 官方文档 |
| src-4 code_analysis | partial | local-prividium Docker Compose 组件通过 GitHub 仓库 README 和 PR 分析确认；Canton 本地代码库不可用 |
| src-5 enterprise_case_sources | full | Broadridge DLR 2026-04 release、DTCC 2025-12-17 公告、Cari Network / Deutsche Bank 公开声明 |
| src-6 comparative_sources | full | enterprise-canton 和 enterprise-privacy 研究提供完整对比基线 |

## 5. Gap Analysis

1. **Canton 本地代码库不可用**: dispatch 指定的 `/Users/whisker/Work/src/networks/canton` 路径不存在。本文复用了既有 WHI-335/336 的代码分析结论（覆盖 Participant、Synchronizer、Mediator、MerkleTree、TransactionView、Daml Engine 等核心模块），未做新的源码级审查。
2. **zkSync Prividium 本地代码库缺失**: `/Users/whisker/Work/src/networks/` 下无 Prividium 专用代码库。分析基于 `local-prividium` 和 `zksync-sso` GitHub 仓库的 README/PR 以及官方文档。
3. **Prividium 生产部署证据有限**: Cari Network、Deutsche Bank 等合作为公开声明，非独立验证的生产部署数据。local-prividium 是开发环境，不等于主网采用。
4. **Canton 采用指标口径差异**: $2T+/month、$1.5T+/month、$6T onchain 等数据均为 vendor-reported，未独立审计。
5. **Mantle 技术栈路线未经产品验证**: 三阶段合规技术栈路线基于架构判断，需通过 RWA issuer、payment、机构钱包等客户发现验证优先级。

## 6. Revision Log

| Round | Change | Notes |
|-------|--------|-------|
| 1 | Initial deep draft | Produced from outline commit `3ee77ec` under Orchestrator combined outline+draft dispatch. Covered all 6 items, 6 investigation fields, 4 diagrams. Key constraints: Canton local codebase unavailable — reused WHI-335/336 code analysis; Prividium analysis based on official docs + local-prividium GitHub repo. |
