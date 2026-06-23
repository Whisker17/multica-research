---
topic: "ZK 隐私优先公链方案分析（Aztec / Noir）"
project_slug: "evm-privacy-research"
topic_slug: "zk-privacy-chain-aztec"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/zk-privacy-chain-aztec.md"
  draft: "evm-privacy-research/research-sections/zk-privacy-chain-aztec/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/zk-privacy-chain-aztec/final.md"

scope: |
  分析隐私优先 ZK 公链标杆 Aztec（原生私密合约、note/UTXO、客户端证明、多密钥披露），
  作为「隐私优先原生 VM」设计范式参考，明确其「重型/独立非 EVM、非 bolt-on」定位与可借鉴之处。
  覆盖六个维度：(1) 私密状态模型 note/UTXO + commitment + nullifier + Noir 合约语言，
  (2) PXE 客户端证明执行，(3) 多密钥选择性披露——当前协议活跃密钥（nullifier key、incoming-viewing key）
  与保留/未激活密钥（outgoing-viewing key、tagging key）须显式区分,
  (4) 成熟度与风险（Alpha 主网 + 已知严重漏洞 + v5 修复目标），(5) Mantle 可借鉴设计，
  (6) WHI-254 框架 rubric 评分。
  须显式标注 Aztec 为「独立非 EVM 链、非 bolt-on」，不可直接集成 Mantle，
  但其密码学级隐私设计（note 模型、客户端证明、多密钥披露）是隐私范式最高参考。

audience: "Mantle 工程团队、协议/基础设施负责人、企业金融/RWA/BD 团队、隐私方案评估决策者"

expected_output: |
  一份中文结构化研究 section，包含：
  - Aztec 私密状态模型全解析（note/UTXO、commitment + nullifier、note hash tree、nullifier tree、nullify-on-read、全局隐私集）
  - Noir 合约语言与私有/公共函数双执行模型
  - PXE 客户端证明执行机制（Client-IVC / CHONK proving system、浏览器/移动端证明）
  - 多密钥架构与选择性披露（当前活跃 2 种密钥对 + 保留 2 种密钥对，区分当前协议能力与提案/未来功能）
  - 成熟度与风险评估（Alpha v4 关键漏洞、v5 修复计划、审计状态、Beta 过渡条件）
  - Mantle 可借鉴设计提炼（note 模型启示、客户端证明模式、多密钥选择性披露架构）
  - WHI-254 五轴 rubric 评分 + 选择性披露 6 维向量填充
  - Aztec 机制表 + 与 EEA 7 方案对比定位

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23T03:15:00Z"
  round_2_changes: |
    [Major] item-3/item-5/item-6/diagram-3: Split current protocol keys (nullifier + incoming viewing)
    from reserved/not-currently-active keys (outgoing viewing + tagging). Reworked selective disclosure
    to reflect only current protocol; moved HackMD compliance workflow to clearly-labelled future/proposal
    subsection. Revised WHI-254 6-dim vector to current-protocol-only. Downgraded borrowability for
    tagging key and compliance proof rows in item-5.
    [Minor] item-1: Hedged Noir 1.0 maturity claim — pre-release/beta, not stable release.

multica_issue_id: "e7283682-53ae-4f3f-a33b-df6393c27d52"
branch_name: "research/evm-privacy-research/zk-privacy-chain-aztec"
base_commit: "5d6c94f6877227aadaf731852a08f46da1213c54"
language: "中文"
research_depth: "deep-analysis"
mode: "squad"

primary_sources:
  - name: "Aztec 官方文档"
    url: "https://docs.aztec.network"
    key_sections: "Concepts (Storage/Notes, Accounts/Keys), Foundational Topics (PXE, Transactions, Wallets), Protocol Specs (Addresses-and-Keys)"
    access_date: "2026-06-23"
  - name: "Aztec 官方博客"
    url: "https://aztec.network/blog"
    key_posts: "fully-confidential-ethereum-transactions, introducing-aztec-nr, critical-vulnerability-in-alpha-v4, alpha-network-security-what-to-expect, road-to-mainnet, the-best-of-both-worlds"
    access_date: "2026-06-23"
  - name: "WHI-254 隐私全景框架（privacy-landscape-framework）"
    url: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"
    usage: "引用五轴 rubric、8 需求体系、选择性披露 6 维向量模型、轻量级判定标准作为评分口径"

secondary_sources:
  - name: "Aztec Default Keys Specification"
    url: "https://docs.aztec.network/protocol-specs/addresses-and-keys/keys"
    usage: "多密钥架构技术细节（nsk_m, ivsk_m, ovsk_m, tsk_m）"
  - name: "Compliance & Selective Disclosure in Aztec (HackMD)"
    url: "https://hackmd.io/bVRw0Rc4TNOFy2Kfcppe3A"
    usage: "合规证明工作流、Tagging Key Set Proof、选择性数据披露机制"
  - name: "Taurus private-CMTAT-aztec (GitHub)"
    url: "https://github.com/taurushq-io/private-CMTAT-aztec"
    usage: "企业级合规代币在 Aztec 上的参考实现"
  - name: "ChainSafe 2026 Guide to Blockchain Privacy"
    url: "https://blog.chainsafe.io/2026-guide-to-blockchain-privacy/"
    usage: "行业横向对比语境"
  - name: "Aztec Security: Audits of Bigfield"
    url: "https://aztec.network/blog/security-of-the-aztec-network-audits-of-bigfield"
    usage: "审计状态（ZKSecurity, Zellic, Spearbit）"
  - name: "NAVe: Formally Verifying Noir Zero Knowledge Programs (arXiv)"
    url: "https://arxiv.org/pdf/2601.09372"
    usage: "Noir 形式化验证工具生态"
  - name: "EEA Privacy Working Group Report"
    url: "https://entethalliance.github.io/wg-privacy/privacy-report.html"
    version: "Version 1, April 2026"
    usage: "Aztec 在 EEA 框架中的定位参照（Aztec 非 EEA 成员方案但在 §10 被引用为参考）"

prerequisite_sections:
  - topic_slug: "privacy-landscape-framework"
    dependency_type: "framework"
    usage: "引用 WHI-254 五轴 rubric、R1-R8 需求体系、选择性披露 6 维向量模型、轻量级判定标准进行评分"
---

# Research Outline: ZK 隐私优先公链方案分析（Aztec / Noir）

## Research Questions

1. Aztec 的私密状态模型（note/UTXO + commitment + nullifier + 全局隐私集 + nullify-on-read）如何实现密码学级别的交易隐私？与 EVM 账户模型的根本差异和设计取舍是什么？
2. PXE 客户端证明执行（Client-IVC / CHONK proving system）如何确保私有输入不出端？其浏览器/移动端证明性能和用户体验约束是什么？
3. Aztec 的多密钥架构中，当前协议活跃密钥（nullifier key、incoming-viewing key）与保留/未激活密钥（outgoing-viewing key、tagging key）分别承担何种角色？当前协议的选择性披露能力如何映射到 WHI-254 选择性披露 6 维向量模型？与 EEA 方案（COTI view-key、Paladin notary、Nightfall X.509）的披露机制有何本质区别？
4. Alpha 主网的成熟度如何评估？已知关键漏洞（Alpha v4 proving system 漏洞，2026-03-17 发现）的影响范围、v5 修复计划、以及从 Alpha 到 Beta 到 Mainnet 1.0 的过渡条件是什么？
5. Aztec 明确拒绝 EVM 兼容性（「no EVM, no Solidity, no account-based architecture」），其「独立非 EVM 链」定位对 Mantle 意味着什么？哪些设计可借鉴、哪些不可移植？
6. 在 WHI-254 五轴 rubric 框架下，Aztec 的各轴评分如何？其在 EEA 7 方案 + 补充方案中的定位是什么？

## Items

### item-1: 私密状态模型 — note/UTXO + commitment + nullifier + Noir 合约语言

深度分析 Aztec 的私密状态模型，这是其隐私架构的核心基础。

**1.1 Note（UTXO）模型**：
- Note 定义：加密数据片段，仅持有者可解密。每个 note 代表一个状态片段（如「Alice 有 50 tokens」）
- Note 与 Bitcoin UTXO 的类比和差异：Aztec note 承载任意私有状态（不仅限于 token balance），支持通用可编程逻辑
- Note 生命周期：创建 → 读取 → 消费/nullify → 新 note 创建
- 典型交易流程：Alice 转 $10 给 Bob → 消费 $100 note → 创建 $10 note (Bob) + $90 note (Alice) → 发布 nullifier

**1.2 Commitment + Nullifier 机制**：
- **Note Hash Tree**（Merkle tree）：存储 note commitments（note 的哈希值），append-only 结构
- **Nullifier Tree**（Merkle tree）：存储已消费 note 的 nullifier，防止双花
- Nullifier 设计关键：nullifier 不泄露其对应的 note（密码学 fingerprint），观察者无法判断哪个 note 被消费
- Nullifier 确定性派生：每个 note 的 nullifier 由 note 数据 + nullifier secret key 确定性生成
- **Nullify-on-read**：即使仅读取 note（不消费），也必须 nullify 并创建新 note，防止两笔读取同一 note 的交易被关联

**1.3 全局隐私集（Global Privacy Set）**：
- Aztec 维护一棵全局 note tree 和一棵全局 nullifier tree，所有合约共享
- 每个私有应用贡献并从同一隐私集中取用——无逐应用启动成本、无围墙花园
- 隐私集大小直接影响匿名性：支付、兑换、借贷、薪资、金库、身份证明均汇入同一 commitment set

**1.4 私有/公共混合状态**：
- **Private state**：UTXO 模型（note hash tree + nullifier tree）
- **Public state**：EVM 风格账户模型（public data tree）
- 私有 → 公共方向性流：私有函数可排队公共函数，公共函数**不能**调用私有函数
- 混合状态使 Aztec 能同时处理需要隐私的逻辑和需要公开验证的逻辑

**1.5 Noir 合约语言**：
- Noir：开源、Rust 风格 ZK 编程语言，专为零知识证明电路设计
- Aztec.nr：Noir 的智能合约框架，为 Noir 添加合约功能和语法（类似 Solidity 开发体验）
- 私有函数 vs 公共函数：私有函数在 PXE 客户端执行并生成 ZK 证明；公共函数在 AVM 网络侧执行
- Noir 1.0 处于 pre-release / beta 阶段（截至 2026 年 6 月尚未发布 stable release），配套形式化验证工具 NAVe（arXiv:2601.09372）
- 与 Solidity 的根本差异：Noir 要求开发者在 ZK 电路范式下思考，学习曲线显著高于 Solidity

**关键要求**：
- 须绘制 note 生命周期图（创建 → commitment → 消费 → nullifier → 新 note）
- 须与 EEA 方案的状态模型进行结构对比（COTI GC encrypted state、Nightfall ZK commitments、Paladin ephemeral EVM）
- 须评估全局隐私集的匿名性优势 vs 独立合约隐私域（如 Paladin privacy domains）的隔离优势

- **Priority**: high
- **Dependencies**: none

### item-2: PXE 客户端证明执行 — 私有函数本地执行、私有输入不出端

深度分析 Aztec 的 PXE（Private eXecution Environment，发音 "pixie"）客户端证明模型。

**2.1 PXE 架构**：
- PXE 是客户端组件，负责：模拟私有交易、管理私有状态、提供 oracle 接口
- 私有函数执行完全在用户设备上（手机/PC/浏览器），ZK 证明本地生成
- 没有任何私有数据离开用户设备——输入、输出、账户信息、执行的函数均不泄露
- PXE 与 AVM（Aztec Virtual Machine）的双执行模型：PXE 处理私有函数，AVM 处理公共函数

**2.2 交易生命周期**：
- 用户在 PXE 中执行私有函数 → 生成 ZK 证明 + nullifiers + note commitments
- 证明连同公共调用栈提交到 Aztec 网络
- Sequencer 验证证明（不看数据），执行公共调用栈
- 交易打包入块 → L1 结算
- 关键约束：私有执行**先于**交易提交完成（提交时证明已生成），公共执行在提交后由网络执行

**2.3 客户端证明系统 — Client-IVC / CHONK**：
- Client-IVC（Interactive Verification of Computation）：Aztec 的客户端递归证明系统
- CHONK：针对低内存设备（手机、浏览器）极致优化的 ZK 证明系统
- 性能目标：浏览器和移动端高效递归证明生成
- 当前约束：Alpha 阶段 ~1 TPS、~6s 出块时间；目标 2026 年底压缩至 ~3-4s

**2.4 与其他方案的证明模型对比**：
- **Aztec PXE（客户端证明）** vs **COTI GC（服务端 GC 计算）**：Aztec 零信任（不信任任何服务端）；COTI 信任 GC 计算方
- **Aztec PXE** vs **Silent Data TEE（硬件隔区执行）**：Aztec 纯密码学信任；Silent Data 硬件信任
- **Aztec PXE** vs **Nightfall ZK rollup（服务端证明）**：Aztec 用户自证明；Nightfall 需 prover 基础设施
- 客户端证明的取舍：最强隐私保障（零泄露），但用户设备需承担证明计算负载，影响 UX

**关键要求**：
- 须绘制 PXE 交易生命周期图（用户设备 → PXE 执行+证明 → 提交 → Sequencer → L1 结算）
- 须评估客户端证明对企业场景的适用性（企业用户 vs 终端用户设备能力差异）
- 须标注当前性能瓶颈（1 TPS、慢出块）和 roadmap 目标

- **Priority**: high
- **Dependencies**: item-1

### item-3: 多密钥选择性披露 — 当前协议活跃密钥与保留密钥的区分

深度分析 Aztec 的多密钥架构，**显式区分当前协议活跃密钥与保留/未激活密钥**，评估当前协议实际具备的选择性披露能力及其合规映射。

**3.1 密钥架构概览（当前协议 vs 保留）**：

**3.1.1 当前协议活跃密钥**（协议层已集成，默认 note 发现和消费依赖这两种密钥）：

| 密钥对 | 全称 | 主密钥 | 当前协议角色 |
|--------|------|--------|-------------|
| **Nullifier Key** | nsk_m / Npk_m | master nullifier secret key / public key | note nullifier 计算（消费 note 的授权）——协议核心密钥 |
| **Incoming Viewing Key** | ivsk_m / Ivpk_m | master incoming viewing secret key / public key | 为接收方加密 note（接收方解密查看）；**默认 note 发现**依赖 incoming viewing key 的共享密钥派生（shared-secret derivation from Ivpk + address points），而非 tagging key |

**3.1.2 保留/未激活密钥**（协议规范中已定义但当前版本未激活使用）：

| 密钥对 | 全称 | 主密钥 | 当前状态 |
|--------|------|--------|---------|
| **Outgoing Viewing Key** | ovsk_m / Ovpk_m | master outgoing viewing secret key / public key | **保留**——设计用于发送方查看自己的发出记录，当前协议版本未激活（「not currently used」） |
| **Tagging Key** | tsk_m / Tpk_m | master tagging secret key / public key | **保留**——设计用于 note 发现方案中计算标签，当前协议版本未激活（「not currently used」），note 发现使用基于 incoming viewing key 的默认机制 |

**3.2 密钥管理与安全模型**：
- 协议密钥（nullifier + incoming viewing）：PXE 创建账户时自动生成，嵌入协议不可更改
- 如果协议密钥泄露，须部署新账户（无法原地轮换）
- 签名密钥（signing key）：由账户合约开发者抽象，允许完全灵活的认证方法
- **App-siloing**：nullifier key 按合约隔离——每个合约获得独立的 nullifier key 派生，限制密钥泄露的爆炸半径
- 保留密钥（Ovpk、Tpk）在账户创建时已派生，但协议层当前未读取/使用

**3.3 当前协议的选择性披露机制**：
- **核心原则**：用户选择向谁披露什么数据，以加密或解密形式
- **无合约级 read key**：解密使用 master incoming viewing key（解锁所有合约的数据），因此不能简单分发 read key
- **当前替代机制**：分享数据本身 + 证明明文与链上密文的对应关系（ZK proof that plaintext encrypts to on-chain ciphertext）
- **默认 note 发现**：基于 incoming viewing key 的共享密钥派生（recipient Ivpk + sender address points → trial decryption），所有接收方的 note 通过此机制发现——**不使用 tagging key**
- 当前协议的披露粒度：可选择性证明 note 属性（金额、身份等）而不泄露全部数据，但基于交互式数据分享 + ZK proof，无 tagging-based 分层发现能力

**3.4 未来/提案阶段的增强披露机制**（HackMD 探索性提案，非当前协议）：

> ⚠️ 以下内容来源于 HackMD 探索性文档（Compliance & Selective Disclosure in Aztec），描述的是**提案/未来设计**，非当前协议已实现功能。

- **Tagging Key 发现机制（提案）**：分享 app-specific tagging secret 给审计方 → 审计方可发现（discover）加密数据但不能解密 → 足以证明从加密数据推导出的属性（如税基、损益）
- **合规证明工作流（提案）**：
  - Tagging Key Set Proof → 验证方收集所有相关密文
  - 交互式挑战：验证方挑战证明方逐笔证明 note 的属性
  - 高保密模式：验证方创建所有待披露 note hash 的 Merkle tree，证明方递归验证整个交易历史摘要
- **状态标注**：此工作流依赖 tagging key 的协议激活，当前版本不可用；属于 Aztec 长期合规路线图的一部分

**3.5 映射到 WHI-254 选择性披露 6 维向量**（仅当前协议能力）：

| 维度 | 标签 | 依据 |
|------|------|------|
| a-Authority | `key-holder` | 用户自主决定向谁分享数据和证明 |
| b-Trigger | `data-share`（主动数据分享 + ZK proof） | 当前协议下披露通过交互式数据分享触发；tagging-based 发现触发为未来提案 |
| c-Payload | `amount`, `identity`, `logic`（可选择性披露子集） | 基于 ZK proof 可按需证明金额/身份/逻辑的特定属性而不泄露全部 |
| d-Scope | `per-tx`, `per-account` | 当前协议下披露粒度为交易级或账户级；app-siloed tagging 为未来提案 |
| e-Revocability | `one-time`（数据分享后不可撤回） | 当前机制下分享的数据/证明不可撤回；tagging secret 轮换为未来提案 |
| f-Leakage | `existence`（commitment 上链可见）, `timing`（交易时序可观察） | note commitments 在全局 note hash tree 中公开可见但内容加密 |

**3.6 与 EEA 方案的选择性披露对比**（基于当前协议能力）：
- **Aztec（ZK proof of plaintext-to-ciphertext）** vs **COTI（permissioned view-keys）**：Aztec 密码学级选择性披露（证明属性但不泄露数据）；COTI 基于密钥分发的全数据披露
- **Aztec** vs **Paladin（notary/observer）**：Aztec 无中间方（纯 P2P 密码学）；Paladin 依赖 notary 公证方
- **Aztec** vs **Prividium（RBAC + operator）**：Aztec 无 operator 可见性（operator 无法读取私有数据）；Prividium operator 可见全部
- 当前协议的独特优势：纯密码学 ZK proof 实现属性证明而不暴露明文——即使不含 tagging key，已超越 EEA 多数方案的披露精度
- 未来增强预期：tagging key 激活后将进一步实现「发现而不解密」的分层披露，是密码学级选择性披露的更高阶形态

**关键要求**：
- 须绘制 Aztec 多密钥架构图，**显式区分活跃密钥（实线）与保留密钥（虚线/灰色）**
- 须填充 WHI-254 选择性披露 6 维向量，**仅基于当前协议能力**，逐维度标注证据来源
- 须将 Aztec 向量与 EEA 方案向量（WHI-254 item-4 §4.4 汇总表）进行显式对比
- 须在「未来/提案」子节中评估合规证明工作流对 GDPR/MiCA/Travel Rule 的潜在满足度，标注为提案而非当前能力

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 成熟度与风险评估 — Alpha 主网、已知严重漏洞、v5 修复目标

系统评估 Aztec 的成熟度和风险状况，使用 WHI-254 EEA Readiness Matrix 三阶段模型作为参照。

**4.1 网络里程碑时间线**：
- 2025-05：公共测试网上线（v2.0.3 升级后达到功能完备）
- 2025-11：Ignition Chain 上线（去中心化 L2 协调层，185+ 运营商，3,400+ sequencer）
- 2026-01：社区治理提案通过 TGE（AZTEC token 交易和 sequencer staking）
- 2026-Q1：Alpha 网络上线（首个私有智能合约执行环境 L2）
- 2026-03-17：发现 Alpha v4 关键漏洞
- 2026-07（计划）：v5 发布修复关键漏洞
- Beta 过渡条件：90 天无关键问题 + 99% uptime
- Mainnet 1.0：Beta 成功运行足够时间后

**4.2 Alpha v4 关键漏洞**：
- 发现日期：2026-03-17
- 影响范围：**proving system 整体**，不受 validator re-execution committee 的 Training Wheel 缓解
- 潜在后果：严重协议中断 + 用户资金被盗
- 修复计划：打包进 v5 版本，计划 2026-07 发布
- 漏洞详情和补丁在 v5 发布前不公开
- 官方警告：应用和 portal 应提醒用户 Alpha 安全保障有限，不要存入不能承受损失的资金

**4.3 审计状态**：
- Pre-Alpha 审计演练：ZKSecurity + Zellic + Spearbit 对 Bigfield 原语（circuit standard library 中最复杂组件之一）进行审计
- AVM（Aztec Virtual Machine）：内部和外部审计**尚未完成**（有意为之——AVM 执行为公共，受 Training Wheel 保护）
- 审计策略：持续进行中，预期会在各组件中发现更多漏洞
- 总融资：>$178M（包括 a16z 领投的 $100M Series B）

**4.4 EEA Readiness Matrix 评估**：

| 阶段 | EEA 判定标准 | Aztec 状况 | 判定 |
|------|-------------|-----------|------|
| Pilot | 有可演示系统；有命名参与方 | ✓ Alpha 网络运行中；3,400+ sequencer | 超出 Pilot |
| Early Production | ≥1 命名客户生产上线；≥3 月运营；≥1 次第三方审计 | ✗ 无命名企业客户生产流量；有 Bigfield 审计但非全面；有关键未修复漏洞 | **未达到** |
| General Availability | ≥3 客户跨 ≥2 机构类别；≥12 月运营；≥2 次审计 | ✗ 远未达到 | **未达到** |

**Aztec 成熟度判定**：**Pilot → Early Pilot（Alpha）**。超出基本 Pilot 定义（有运行网络和大量参与者），但因 (a) 无命名企业客户生产流量、(b) 存在已知未修复的关键漏洞、(c) 全面审计仍在进行中，无法达到 Early Production。

**4.5 风险评估摘要**：
- **关键风险**：proving system 级别漏洞未修复（v5 前），用户资金理论上可被盗
- **中等风险**：AVM 审计未完成；Alpha 阶段无状态迁移（每次部署独立）
- **低风险**：Noir 语言生态尚早期；开发者工具链不成熟
- **缓解因素**：Training Wheel（validator re-execution）对公共执行有效；持续审计由顶级审计公司执行
- **明确定位**：Aztec 官方明确标注「Alpha — 不要存入不能承受损失的资金」

**关键要求**：
- 须绘制 Aztec 网络里程碑时间线图
- 须将 Aztec 成熟度与 EEA 7 方案的 Readiness Matrix 评估进行显式对比（COTI-L2 GA vs Aztec Pilot-Alpha）
- 须逐项列出已知漏洞、审计状态、修复计划
- 须标注「独立链、非 bolt-on」定位——与 EEA 方案中被一票否决的独立链（Silent Data, Linea Enterprise, Prividium, Polygon CDK）同属一类

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

### item-5: Mantle 可借鉴设计 — 从 Aztec 范式中提炼设计启示

提炼 Aztec 隐私架构中对 Mantle 有参考价值的设计元素，同时明确不可直接移植的部分。

**5.1 明确「非 bolt-on」定位**：
- Aztec 明确拒绝 EVM/账户模型/Solidity：「no EVM, no Solidity, no account-based blockchain architecture — all of which are privacy-leaking」
- Aztec 是**独立非 EVM 隐私 L2**，不是 Mantle 可以 bolt-on 集成的方案
- 在 WHI-254 部署形态分类中，Aztec 属于 **C 类（独立链或 VM）**
- 触发一票否决条件 V1（需要部署独立 VM/链）和 V2（需要资产桥）

**5.2 可借鉴设计元素**：

| 设计元素 | Aztec 实现 | Mantle 借鉴方向 | 可行性评估 |
|---------|-----------|---------------|-----------|
| **Note/UTXO 隐私模型** | 全局 note hash tree + nullifier tree | 可参考 commitment + nullifier 方案用于 token 级隐私（如 ERC-7984 + nullifier 扩展） | 中等——需要 UTXO 层但可在 EVM 合约层模拟 |
| **Nullify-on-read** | 防止两笔读取同一 note 的交易被关联 | 值得在隐私交易设计中纳入防关联考量 | 概念可借鉴，实现需适配 EVM |
| **全局隐私集** | 所有合约共享一个 commitment set | 启示：避免逐应用隐私池（如 Paladin 域隔离），追求跨应用匿名性 | 概念可借鉴，但 EVM 上实现需额外设计 |
| **多密钥分层披露（概念层面）** | 协议定义 4 种密钥对（当前活跃 2 种：nullifier + incoming viewing；保留 2 种：outgoing viewing + tagging） | **概念可借鉴**：多密钥分层架构（spend key + view key + audit key）的设计理念不依赖 UTXO 模型 | 中等——概念可借鉴，但 Aztec 当前仅 2 种密钥活跃，完整分层披露尚未在协议层验证 |
| **Tagging Key（发现而不解密）** | **当前未激活**——协议规范定义但标注「not currently used」；note 发现使用 incoming viewing key 的共享密钥派生 | 概念值得关注：未来若 Aztec 激活 tagging key 并验证合规效果，可参考其机制 | 低（当前）——该功能尚未在协议层激活和验证，不可作为已验证设计引用 |
| **客户端证明** | PXE 本地执行 + 证明 | 启示方向，但企业场景中服务端证明（如 COTI GC、TEE）更实际 | 低——Mantle 企业用户不一定有客户端证明能力 |
| **合规证明工作流（提案）** | HackMD 探索性提案：Tagging Key Set Proof → 交互式挑战 → 递归验证 | 概念层面可关注，但**非当前协议功能**——依赖 tagging key 激活，属于 Aztec 长期合规路线图 | 低（当前）——提案阶段，未经协议验证 |

**5.3 不可移植的设计**：
- **非 EVM 执行环境**：Noir + AVM 无法 bolt-on 到 Mantle
- **UTXO 状态模型**：Mantle 使用 EVM 账户模型，不可能切换到 UTXO
- **客户端证明依赖**：Mantle 企业场景中客户端证明的 UX 成本过高
- **全重新设计的合约语言**：要求开发者放弃 Solidity 转向 Noir，不符合 Mantle EVM 生态

**5.4 对 Mantle 隐私方案选型的启示**：
- Aztec 证明了**密码学级隐私是技术上可行的**，但代价是完全放弃 EVM 兼容性
- Mantle 的「轻量级 bolt-on」约束意味着只能借鉴 Aztec 的**概念和密码学原语**，而非直接采用其架构
- **优先借鉴**：多密钥分层架构概念 + ZK proof of plaintext-to-ciphertext 选择性披露 + commitment/nullifier 隐私模型
- **明确排除**：直接集成 Aztec 或采用类 Aztec 的非 EVM 架构

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4

### item-6: WHI-254 框架 Rubric 评分 — 五轴评估 + 选择性披露向量

使用 WHI-254 五轴统一评估 rubric 对 Aztec 进行完整评分，填充选择性披露 6 维向量，并定位 Aztec 在全景方案中的位置。

**6.1 轴 1 — 密码学路线**：

| 维度 | 评分 |
|------|------|
| 主技术家族 | ZKP（ZK-SNARK，UltraHonk/PLONK 系） |
| Trusted Setup | 需要——Aztec CRS（最大规模 MPC setup 已完成） |
| 后量子叙事 | ZK-SNARK 体系受量子威胁（非后量子安全） |
| 路线组合 | 纯 ZKP（客户端 Client-IVC + 网络 rollup proof） |

**6.2 轴 2 — 被保护数据维度**：

| 维度 | 评分 | 依据 |
|------|------|------|
| 金额 (R1) | ● 完全保护 | note commitments 加密金额 |
| 余额 (R2) | ● 完全保护 | UTXO 模型下余额以加密 note 集合表示 |
| 身份 (R3) | ● 完全保护 | 私有函数在 PXE 执行，链上无身份信息 |
| 图结构 (R5) | ● 完全保护 | nullifier 不泄露对应 note；全局隐私集消除交易关联 |
| 业务逻辑 (R4) | ● 完全保护 | Noir private functions 全执行隐私 |
| 合约状态 (R4) | ● 完全保护 | 私有状态以加密 note 存储，公有状态可选择性公开 |
| 订单流 (R8) | ◐ 部分保护 | PXE 客户端执行保护交易意图；但提交后 sequencer 可见公共调用栈 |

**6.3 轴 3 — 信任模型**：

| 维度 | 评分 |
|------|------|
| 主信任模型 | **Cryptographic Trust**（纯密码学） |
| 信任假设 | ZK-SNARK 密码学假设（离散对数/配对）；CRS trusted setup（MPC 仪式）；sequencer 活性假设 |
| 硬件信任 | 无（纯软件密码学） |
| 运营方信任 | 最小——sequencer 不可见私有数据，仅验证证明 |

**6.4 轴 4 — 部署形态**：

| 维度 | 评分 |
|------|------|
| 部署形态 | **C. 独立链或 VM**（独立非 EVM 隐私 L2） |
| 轻量级判定 | **一票否决** — V1（独立 VM/链）+ V2（需要资产桥到 Ethereum L1） |
| 对 Mantle 集成 | **不可 bolt-on** — 需要部署完整 Aztec 网络 + 资产桥 |

**6.5 轴 5 — 合规-选择性披露**：
引用 item-3 §3.5 的 6 维向量填充结果（仅基于当前协议能力，不含 tagging key 和 HackMD 合规提案）。

**6.6 Aztec 在全景方案中的定位**：

| 定位维度 | Aztec | 对比 |
|---------|-------|------|
| 隐私级别 | **最高**（密码学级全执行隐私） | 超越所有 EEA 7 方案 |
| 部署重量 | **最重**（完全独立非 EVM 链） | 与 Silent Data/Linea Enterprise/Prividium/Polygon CDK 同属 C 类 |
| 成熟度 | **最低**（Pilot-Alpha，有未修复关键漏洞） | 远低于 COTI-L2 (GA)、Silent Data (Early Production) |
| EVM 兼容性 | **零**（明确拒绝 EVM） | 所有 EEA 7 方案均为 EVM 兼容/目标 |
| 可借鉴价值 | **高**（概念和密码学原语层面） | 多密钥架构概念、ZK proof of plaintext-to-ciphertext、commitment/nullifier 模型（tagging key 和合规证明工作流为提案/未来功能） |

**「隐私账本」二义判定**（引用 WHI-254 item-6）：
- Aztec 属于 **B（Business-State Ledger / 状态级账本）**，且是最完整的 B 类方案
- Aztec 同时覆盖 A（Token Ledger）——加密 note 可代表 token 值
- 判定：**A + B 兼备**，且 B 类能力来自密码学级全执行隐私（非准入控制）

**关键要求**：
- 须完整填充五轴 rubric 表（逐轴逐维度）
- 须与 EEA 7 方案的 rubric 评分进行显式对比（WHI-254 item-3 §3.2）
- 须填充选择性披露 6 维向量并与 WHI-254 向量汇总表（item-4 §4.4）对比
- 须标注 Aztec 的极端定位：「隐私最高 + 部署最重 + 成熟度最低 + EVM 兼容性零」

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| aztec_component_ref | 该结论对应的 Aztec 架构组件（note hash tree / nullifier tree / PXE / AVM / Noir / Client-IVC / CHONK / key-type），附文档 URL 和访问日期 | all |
| data_dimension | 被保护数据维度（金额/余额/身份/图/逻辑/状态/订单流），及保护级别（完全/部分/不保护），对齐 WHI-254 轴 2 | item-1, item-6 |
| trust_model | 信任模型分类（Cryptographic/Hardware-Anchored/Organizational/混合）及具体信任假设，对齐 WHI-254 轴 3 | item-2, item-6 |
| deployment_pattern | 部署形态分类（bolt-on/合约套件/独立链）及轻量级判定结果，对齐 WHI-254 轴 4 | item-5, item-6 |
| disclosure_vector | 选择性披露 6 维多标签向量：authority × trigger × payload × scope × revocability × leakage，对齐 WHI-254 轴 5 | item-3, item-6 |
| maturity_assessment | EEA Readiness Matrix 三阶段评估（Pilot/Early Production/GA）+ 风险评级 + 已知漏洞状态 | item-4 |
| mantle_relevance | 对 Mantle 轻量级机构隐私方案的具体启示、约束或设计借鉴 | item-5, item-6 |
| eea_comparison | 与 EEA 7 方案的显式对比（维度级、机制级或定位级），引用 WHI-254 对应评分 | item-1, item-2, item-3, item-6 |
| source_confidence | 证据等级：Aztec 官方文档直接引用 / Aztec 博客引用 / WHI-254 框架引用 / 行业分析推断；标注不确定性 | all |

## Diagrams

### diagram-1: Aztec 私密状态模型 — Note 生命周期与 Commitment/Nullifier 机制

展示 note 从创建到消费的完整生命周期：
- 创建 note → 计算 commitment (hash) → 写入 Note Hash Tree
- 消费 note → 计算 nullifier (deterministic, key-bound) → 写入 Nullifier Tree → 创建新 note(s)
- 标注全局隐私集（global note tree + global nullifier tree，所有合约共享）
- 对比 EVM 账户模型（State Trie）的结构差异

- **Type**: flow diagram / architecture
- **Applies to**: item-1
- **Purpose**: 直观展示 Aztec UTXO 隐私模型的核心机制，帮助理解为什么这种模型能实现密码学级隐私

### diagram-2: PXE 双执行模型 — 交易生命周期

展示一笔交易从用户设备到 L1 结算的完整路径：
- 用户设备 → PXE（私有函数执行 + ZK 证明生成）→ 交易提交
- → Sequencer（验证证明 + 执行公共调用栈）→ 打包入块
- → L1 结算（ZK rollup proof on Ethereum）
- 标注数据边界：哪些数据留在客户端、哪些上链、哪些被 sequencer 看到

- **Type**: sequence / flow diagram
- **Applies to**: item-2
- **Purpose**: 展示客户端证明的隐私保障边界——私有数据何时何地是安全的

### diagram-3: Aztec 多密钥架构与选择性披露数据流（当前协议 vs 保留/提案）

展示密钥架构，**显式区分当前协议活跃密钥与保留密钥**：

**当前协议活跃（实线）**：
- Nullifier Key → 消费 note（app-siloed）——协议核心
- Incoming Viewing Key → 接收方解密 note + **默认 note 发现**（shared-secret derivation from Ivpk + address points）
- 当前选择性披露路径：数据分享 + ZK proof of plaintext-to-ciphertext

**保留/未激活（虚线/灰色）**：
- Outgoing Viewing Key → 发送方查看发出记录（协议已定义但当前未激活）
- Tagging Key → 审计方发现（不解密）加密数据（协议已定义但当前未激活）
- 合规证明路径（HackMD 提案）：Tagging Key Set Proof → 交互式挑战 → 属性证明（依赖 tagging key 激活）

- **Type**: architecture / data flow
- **Applies to**: item-3
- **Purpose**: 展示 Aztec 多密钥架构中当前已验证的选择性披露能力与未来提案增强的清晰边界

### diagram-4: Aztec 全景定位 — 隐私级别 vs 部署重量 vs 成熟度

在三维空间中定位 Aztec 相对于 EEA 7 方案 + 补充方案：
- X 轴：隐私级别（值级 → 执行级 → 全密码学级）
- Y 轴：部署重量（bolt-on → 合约套件 → 独立链）
- Z 轴或颜色：成熟度（Pilot → Early Production → GA）
- Aztec 位于极端角落：「隐私最高 + 部署最重 + 成熟度最低」

- **Type**: scatter plot / positioning map
- **Applies to**: item-6
- **Purpose**: 一图展示 Aztec 的独特定位——最先进的隐私技术但最远离 Mantle 的轻量级偏好

## Source Requirements

### Primary Sources

- **Aztec 官方文档** (https://docs.aztec.network)
  - 访问日期: 2026-06-23
  - 关键 section: Concepts/Storage/Notes, Foundational Topics/PXE, Foundational Topics/Accounts/Keys, Protocol Specs/Addresses-and-Keys/Keys
  - 使用方式: note 模型、PXE 架构、多密钥架构的技术细节
  - 引用要求: 标注文档路径

- **Aztec 官方博客** (https://aztec.network/blog)
  - 访问日期: 2026-06-23
  - 关键文章:
    - "Fully Confidential Ethereum Transactions: Aztec Network's Privacy Architecture"
    - "The Best of Both Worlds: How Aztec Blends Private and Public State"
    - "Introducing Aztec.nr: Aztec's Private Smart Contract Framework"
    - "Critical Vulnerability in Alpha v4"
    - "Alpha Network Security: What to Expect"
    - "Road to Mainnet"
    - "Security of the Aztec Network: Audits of Bigfield"
  - 使用方式: 架构设计意图、安全状态、roadmap
  - 引用要求: 标注博客标题和发布日期

- **WHI-254 隐私全景框架** (evm-privacy-research/research-sections/privacy-landscape-framework/final.md)
  - 使用方式: 五轴 rubric、R1-R8 需求体系、选择性披露 6 维向量模型、轻量级判定标准、EEA Readiness Matrix 对齐
  - 引用要求: 标注 item/section 编号

### Secondary Sources

- **Compliance & Selective Disclosure in Aztec** (HackMD)
  - URL: https://hackmd.io/bVRw0Rc4TNOFy2Kfcppe3A
  - 使用方式: 合规证明工作流、Tagging Key Set Proof
- **Taurus private-CMTAT-aztec** (GitHub)
  - URL: https://github.com/taurushq-io/private-CMTAT-aztec
  - 使用方式: 企业级合规代币参考实现
- **EEA Privacy Working Group Report** (Version 1, April 2026)
  - URL: https://entethalliance.github.io/wg-privacy/privacy-report.html
  - 使用方式: Aztec 在 EEA 框架中的定位参照
- **ChainSafe 2026 Guide to Blockchain Privacy**
  - URL: https://blog.chainsafe.io/2026-guide-to-blockchain-privacy/
  - 使用方式: 行业横向对比

### 引用规范

- 每个结论附 `[Aztec Docs: <path>]` 或 `[Aztec Blog: <title>]` 标签
- WHI-254 框架引用附 `[WHI-254 item-N §M.K]` 标签
- 推论性结论标注 `[推论]`
- 外部补充来源标注访问日期
- 所有成熟度和安全评估须标注评估时间点（截至 2026-06-23）
