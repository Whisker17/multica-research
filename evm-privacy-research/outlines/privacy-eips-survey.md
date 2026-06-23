---
topic: "Privacy 相关 EIP 全景梳理（含检索方法论）"
project_slug: "evm-privacy-research"
topic_slug: "privacy-eips-survey"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/privacy-eips-survey.md"
  draft: "evm-privacy-research/research-sections/privacy-eips-survey/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/privacy-eips-survey/final.md"

scope: |
  系统梳理 ERC-7984/ERC-7945、VOSA 之外所有与 privacy 相关的活跃/重要 EIP 与论坛草案，
  按隐私原语与层级分类，给出状态、能力边界与对 Mantle 相关性，补全标准层版图。
  检索方法论覆盖：eips.ethereum.org 关键词检索、Ethereum Magicians 论坛标签、
  ethereum/EIPs 与 ethereum/ERCs 仓库 open PR。
  排除标准：已 Withdrawn；明确非隐私目标（如 EIP-8105 单列「相关但非隐私」）。
  依赖 WHI-254（框架）已完成。

audience: "Mantle 工程团队、协议/基础设施负责人、企业金融/RWA/BD 团队、隐私方案评估决策者"

expected_output: |
  检索方法论 + 候选/排除清单（含截止日期）+ EIP 分类表（原语 × 层级 × 状态 × 相关性）+
  stealth 双密钥机制边界说明 + EIP-8182 协议层 shielded pool 定位 + 对 Mantle 相关性评级

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23T07:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23T08:00:00Z"
  round_2_changes: |
    - [Major] Fixed EIP-8141 misidentification: EIP-8141 is "Frame Transaction" (native AA), NOT "Privacy Pool Withdrawal Fees"
    - [Major] Fixed pERC-20 status: PR #1796 (EIP-8287) closed → PR #1817 (ERC-8302) open; status is "Open ERC PR" not "Draft"
    - [Minor] Strengthened search methodology with exact query strings, result counts, and ethresear.ch searches

multica_issue_id: "3f53d683-eefb-4af0-ae59-8ee77f02c537"
branch_name: "research/evm-privacy-research/privacy-eips-survey"
base_commit: "5d6c94f"
language: "中文"
research_depth: "survey"
mode: "squad"

dependencies:
  - project_slug: "evm-privacy-research"
    topic_slug: "privacy-landscape-framework"
    multica_issue_id: "51a89bf9-8955-4ae4-914e-cc6920ffea9a"
    status: "done"
    usage: "引用 WHI-254 框架的 8 需求体系、6 技术家族、5 轴 rubric、选择性披露 6 维向量模型、轻量级判定标准作为评估口径"

primary_sources:
  - name: "eips.ethereum.org — Ethereum Improvement Proposals"
    url: "https://eips.ethereum.org"
    access_date: "2026-06-23"
    usage: "每个 EIP 的规范文本、状态、作者、创建日期"
  - name: "ethereum/EIPs GitHub 仓库"
    url: "https://github.com/ethereum/EIPs"
    access_date: "2026-06-23"
    usage: "EIP YAML frontmatter 状态核验、open PR 检索"
  - name: "ethereum/ERCs GitHub 仓库"
    url: "https://github.com/ethereum/ERCs"
    access_date: "2026-06-23"
    usage: "ERC YAML frontmatter 状态核验、open PR 检索"
  - name: "Ethereum Magicians 论坛"
    url: "https://ethereum-magicians.org"
    access_date: "2026-06-23"
    usage: "提案讨论帖、非正式草案、社区反馈"
  - name: "ethresear.ch"
    url: "https://ethresear.ch"
    access_date: "2026-06-23"
    usage: "研究阶段提案（如 pERC-20）"
  - name: "WHI-254 隐私需求与技术全景框架（final.md）"
    path: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"
    usage: "评估框架依赖：8 需求、6 技术家族、5 轴 rubric、6 维选择性披露向量、轻量级判定标准"

prerequisite_sections:
  - topic_slug: "privacy-landscape-framework"
    status: "done"
---

# Research Outline: Privacy 相关 EIP 全景梳理（含检索方法论）

## Research Questions

1. 采用何种可复现的检索方法论，可以系统发现以太坊生态中所有与 privacy 相关的活跃/重要 EIP 和论坛草案？检索的截止日期、数据来源和排除标准如何定义？
2. 已发现的隐私相关 EIP 按隐私原语（值级/执行级/状态级/身份级）如何分类？每个 EIP 的 EIP 状态（Draft/Review/Final/Stagnant/Withdrawn）、核心密码学原语和能力边界是什么？
3. ERC-5564/6538 stealth address 的双密钥机制（spending key + viewing key）如何工作？其能力边界在哪里——为什么只提供收款方匿名而**不**提供余额/金额隐私？
4. EIP-8182 协议层 shielded pool 的定位是什么？其 UTXO 模型 + Groth16 BN254 架构如何实现统一匿名集？与应用层 ZK token wrapper（ERC-8065）和 privacy-native token（pERC-20）的定位分工是什么？
5. EIP-8105 encrypted mempool 的目标是什么？为何应分类为「相关但非隐私」而非隐私 EIP？
6. 各隐私相关 EIP 对 Mantle L2 的相关性如何评级（High/Medium/Low）？哪些可以作为 bolt-on 方案直接部署，哪些需要协议层变更？
7. 已发现的 EIP 如何映射到 WHI-254 框架的 8 需求体系（R1-R8）和 7 项被保护数据维度？

## Items

### item-1: 检索方法论与候选/排除清单

建立可复现的 EIP 检索方法论，明确数据来源、检索关键词、排除标准和截止日期，输出完整的候选清单和排除清单。

**检索数据来源**（按优先级排序）：

| # | 数据来源 | 检索方式 | 目的 |
|---|---------|---------|------|
| S1 | eips.ethereum.org | 关键词全文检索：`confidential`, `private`, `privacy`, `stealth`, `shielded`, `encrypt`, `zero-knowledge`, `zk`, `anonymous`, `obfuscate`, `hiding` | 主检索通道，覆盖已合并 EIP/ERC |
| S2 | ethereum/EIPs GitHub 仓库 | Open PR 搜索 + YAML frontmatter 扫描 | 发现尚未合并的 Draft 提案 |
| S3 | ethereum/ERCs GitHub 仓库 | Open PR 搜索 + YAML frontmatter 扫描 | 发现尚未合并的 ERC 草案 |
| S4 | Ethereum Magicians 论坛 | `privacy` / `ERC` / `confidential` 标签过滤 | 发现非正式草案和讨论阶段提案 |
| S5 | ethresear.ch | `private token` / `privacy EIP` / `shielded pool` 搜索 | 发现研究阶段提案（如 pERC-20） |
| S6 | EEA Privacy Working Group Report §06b | 报告引用的 EIP 列表 | 交叉验证，确保不遗漏 |

**检索执行记录**（截止日期 2026-06-23，GitHub Search API + Web Search）：

S2 — ethereum/EIPs GitHub open PR 搜索：

| 查询字符串 | 结果数 | 隐私相关命中 |
|-----------|--------|------------|
| `privacy repo:ethereum/EIPs is:open is:pr` | 5 | #11762 (Privacy-Native Fungible Tokens) |
| `shielded OR encrypt repo:ethereum/EIPs is:open is:pr` | 1 | #11518 (Counterfactual Transaction — 非隐私) |

S3 — ethereum/ERCs GitHub open PR 搜索：

| 查询字符串 | 结果数 | 隐私相关命中 |
|-----------|--------|------------|
| `privacy OR private repo:ethereum/ERCs is:open is:pr` | 21 | #1817 (Private Fungible Tokens / ERC-8302), #1373 (Privacy Address Format), #1680 (Encrypted Token), #1379 (Private ERC-20), #1681 (Cryptographic Amnesia) |
| `confidential repo:ethereum/ERCs is:open is:pr` | 3 | #1143 (Encrypted Data), #1361 (Encrypted Hashed Arguments) |
| `stealth repo:ethereum/ERCs is:open is:pr` | 0 | — |
| `zero-knowledge OR zk repo:ethereum/ERCs is:open is:pr` | 15 | #1747 (ZK Compliance Oracle), #1062 (Oracle-Permissioned ERC-20 with ZK Proofs), #1234 (MultiTrustCredential ZK Presentation), #1238 (ZK Proof Verification for Smart Accounts) |

S5 — ethresear.ch 搜索：

| 查询字符串 | 主要命中 |
|-----------|---------|
| `private token` / `privacy EIP` / `shielded pool` | pERC20 草案帖 (https://ethresear.ch/t/perc20-private-token-standard-draft/25200), EIP-8287 原始帖 (https://ethresear.ch/t/eip8287-privacy-native-fungible-token-standard-draft/25089), EIP-7503 RFC (https://ethresear.ch/t/rfc-eip7503-private-transfers/18664), Universal Encrypted Mempool 讨论 (https://ethresear.ch/t/universal-enshrined-encrypted-mempool-eip/23685), Ethereum Privacy Roadmap (https://ethresear.ch/t/ethereum-privacy-the-road-to-self-sovereignty/22115) |

**排除标准**：

| 排除规则 | 说明 |
|---------|------|
| EX-1: 已 Withdrawn | 状态为 Withdrawn 的 EIP/ERC 排除 |
| EX-2: 明确非隐私目标 | 主要目标非用户/交易隐私（如 EIP-8105 目标为抗 MEV/抗审查），单列「相关但非隐私」 |
| EX-3: 范围内其他 issue 已覆盖 | ERC-7984（Confidential Fungible Token）、ERC-7945（Confidential Transactions）、VOSA 由独立 issue 覆盖 |
| EX-4: 纯消费者隐私/混币器 | Tornado Cash 等无合规准入的纯混币器方案 |
| EX-5: 非 EVM 生态 | 与 EVM 生态无交互的纯非 EVM 隐私方案（Monero/Zcash 主链本身） |

**截止日期**：2026-06-23（UTC）。所有检索结果基于此日期的快照。后续更新须标注新截止日期。

**输出**：

- 候选清单：通过所有排除规则的 EIP/ERC/论坛草案，附编号、标题、状态、创建日期、分类标签
- 排除清单：被排除的 EIP/ERC，附排除原因和适用的排除规则编号
- 检索日志：每个数据来源的检索关键词、结果数量、筛选过程

**不可核验提案处理**：对于 GitHub 仓库中找不到 YAML frontmatter 或官方页面不可访问的提案，标注「状态不可核验」及尝试的核验方式（如 GitHub 仓库搜索、eips.ethereum.org 搜索、curl 直接获取 raw markdown 等）。

- **Priority**: high
- **Dependencies**: none

### item-2: EIP 分类表 — 隐私原语 × 层级 × 状态 × Mantle 相关性

基于 item-1 的候选清单，构建系统分类表，按隐私原语、部署层级、EIP 状态和 Mantle 相关性四个维度对每个 EIP 进行分类。

**分类维度**：

**维度 A — 隐私原语分类**（对齐 WHI-254 框架 7 项被保护数据维度）：

| 原语类别 | 对齐 WHI-254 | 代表 EIP |
|---------|-------------|---------|
| 收款方匿名（Recipient Anonymity） | R3 对手方身份隐私 | ERC-5564, ERC-6538 |
| 转账金额/余额隐藏（Value/Balance Confidentiality） | R1 金额隐私, R2 余额隐私 | EIP-8182, ERC-8065 |
| 交易图解耦（Transaction Graph Unlinkability） | R5 资金流隐私 | EIP-7503, EIP-8182 |
| 合规门控隐私（Compliance-Gated Privacy） | R6 合规可审计, R7 选择性披露 | Privacy Pools |
| 隐私赋能基础设施（Privacy-Enabling Infrastructure） | R5 交易图, 间接 R3 | EIP-8250（keyed nonces，AA 基础设施但有隐私赋能效果） |
| 相关但非隐私（Related Non-Privacy） | — | EIP-8105（encrypted mempool, 抗 MEV）, EIP-8141（Frame Transaction, 原生 AA — paymaster 间接赋能隐私池 gas 支付但非隐私提案本身） |

**维度 B — 部署层级**：

| 层级 | 说明 | 判定标准 |
|------|------|---------|
| 协议层（Core/Protocol） | 需要以太坊硬分叉或共识层变更 | EIP category = Core |
| 应用层（ERC/Application） | 可在现有 EVM 上以智能合约形式部署 | EIP category = ERC |
| 论坛/研究阶段 | 尚未提交正式 EIP，仅有 ethresear.ch 帖子或 Magicians 讨论 | 无正式 EIP 编号或仅有 Draft PR |

**维度 C — EIP 状态**（以太坊 EIP 标准流程）：

`Draft → Review → Last Call → Final`；另有 `Stagnant`（超过 6 个月无活动）、`Withdrawn`（作者撤回）

**维度 D — Mantle 相关性**：

| 评级 | 判定标准 | 示例 |
|------|---------|------|
| **High** | 可直接在 Mantle L2 上部署或集成，无需协议层修改；或 Mantle 已有相关技术基础 | ERC-5564（合约部署）、ERC-8065（ZK wrapper） |
| **Medium** | 需要适配修改或仅作为参考架构；或依赖 Mantle 尚不支持的 precompile | EIP-8182（需 Mantle 自行实现 shielded pool）、ERC-8302/pERC-20（Open ERC PR） |
| **Low** | 仅适用于以太坊 L1 硬分叉或与 Mantle 架构不兼容 | EIP-7503（依赖 L1 burn-and-mint）、EIP-8250（L1 keyed nonces for Frame TX）、EIP-8141（L1 Frame Transaction AA）、EIP-8105（L1 encrypted mempool） |

**分类表结构**（每行一个 EIP）：

| EIP 编号 | 标题 | 状态 | 类别 | 隐私原语 | 部署层级 | WHI-254 需求映射 | Mantle 相关性 | 能力边界摘要 |
|---------|------|------|------|---------|---------|----------------|-------------|-------------|

**关键标注要求**：

1. **ERC-5564/6538 能力边界**：须显式标注「stealth addresses 仅提供收款方匿名（R3），**不**提供余额/金额隐私（R1/R2）」
2. **EIP-8105 分类**：须显式标注「相关但非隐私——目标为抗 MEV/抗审查（R8），非用户隐私」
3. **EIP-8182 定位**：须说明其协议层 shielded pool 统一匿名集的独特定位，与应用层方案的区别
4. **每个结论附验证 URL + 访问日期**

- **Priority**: high
- **Dependencies**: item-1

### item-3: Stealth Address 双密钥机制深度解析与能力边界

深度解析 ERC-5564 + ERC-6538 的 stealth address 双密钥机制（SECP256k1 ECDH），明确其能力边界和不能力范围。

**核心机制**：

- **双密钥结构**：每个接收者持有 spending key（花费密钥）和 viewing key（查看密钥）
- **Stealth Meta-Address**：由两个公钥编码（spending public key + viewing public key），通过 ERC-6538 registry 发布
- **地址生成流程**：发送方使用接收方的 stealth meta-address + 临时密钥，通过 ECDH 派生出一次性 stealth address
- **单例合约**：ERC-5564 部署在 `0x5564...5564`，ERC-6538 部署在 `0x6538...6538`

**能力边界（CRITICAL）**：

| 维度 | 是否保护 | 说明 |
|------|---------|------|
| 收款方身份（R3） | ✅ 保护 | 每笔交易生成新的 stealth address，外部观察者无法将多笔交易关联到同一收款方 |
| 转账金额（R1） | ❌ **不保护** | 转账金额在链上完全公开可见 |
| 账户余额（R2） | ❌ **不保护** | 虽然余额分散在多个 stealth address，但每个地址余额公开 |
| 发送方身份 | ❌ **不保护** | 发送方地址完全公开 |
| 交易图（R5） | ⚠️ 部分 | 观察者无法确认收款方身份，但交易流向（from → stealth address）可见 |

**与 WHI-254 框架映射**：

- 技术家族：ZKP（viewing key 分离依赖椭圆曲线 ECDH，非 ZK proof，但属于密码学隐私原语）
- 选择性披露：viewing key 持有者可解密收款方身份 → disclosure_vector = (key-holder, viewing-key-share, identity, per-tx, revocable, graph+existence)
- 轻量级判定：纯合约部署，无额外基础设施 → bolt-on，满足轻量级标准

**Mantle 相关性：High**——可直接在 Mantle L2 部署 ERC-5564/6538 合约（已有以太坊主网单例地址范式），零协议层修改。

**调查要点**：

- 验证 Umbra Protocol（ERC-5564 主要实现）在 L2 上的部署状态
- 检查 viewing key 扫描的性能影响（接收者需扫描所有 Announcement 事件）
- 与 VOSA（本 issue 范围外）的关系说明：ERC-5564/6538 提供基础 stealth address 原语，VOSA 在此之上添加 verifiable obfuscation

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: EIP-8182 协议层 Shielded Pool 定位与架构分析

深度分析 EIP-8182（Private ETH and ERC-20 Transfers）的协议层定位、技术架构和与应用层方案的分工。

**核心定位**：

EIP-8182 是以太坊协议层（Core EIP）的 shielded pool 提案，通过硬分叉引入系统合约，为 ETH 和 ERC-20 提供原生隐私转账。与应用层方案（ERC-8065, pERC-20 等）的核心区别在于：协议层统一匿名集（所有用户共享同一 shielded pool），而非应用层碎片化匿名集。

**技术架构**：

| 架构要素 | EIP-8182 设计 |
|---------|-------------|
| 模型 | UTXO（note-based，非 account-based） |
| 证明系统 | Groth16 on BN254 |
| 部署方式 | 系统合约（system contract），硬分叉激活 |
| 管理密钥 | 无 admin key，无 proxy，不可升级 |
| 目标升级 | Hegota 硬分叉（计划 H2 2026） |
| 支持资产 | ETH + 任意 ERC-20 |
| 作者 | Tom Lehman (@RogerPodacter, Facet) |

**隐私能力映射（WHI-254 维度）**：

| WHI-254 维度 | 保护级别 | 说明 |
|-------------|---------|------|
| R1 金额隐私 | ✅ 完全保护 | Pedersen commitment 隐藏金额 |
| R2 余额隐私 | ✅ 完全保护 | UTXO 模型，余额分散在加密 notes 中 |
| R3 对手方身份 | ✅ 完全保护 | 统一匿名集，接收者不可识别 |
| R5 交易图 | ✅ 完全保护 | Nullifier 机制防止 double-spend 同时保持不可链接性 |
| R4 业务逻辑 | ❌ 不保护 | 仅值级隐私，不支持通用合约隐私执行 |
| R6 合规 | ⚠️ 待定 | 提案中提及 Privacy Pools 兼容性，具体合规机制待确认 |

**隐私赋能基础设施提案**：

以下 EIP 并非 EIP-8182 的专属配套提案，但其功能对隐私池的实用性有间接赋能效果：

- **EIP-8141: Frame Transaction**（Draft, Core）——Vitalik Buterin 等提出的原生账户抽象（Native AA）提案，引入 frame-based 交易执行模型（VERIFY + EXECUTE frames）和 paymaster 机制。**非隐私提案**，但 paymaster 功能可间接赋能隐私池场景：第三方 paymaster 可代付 gas，使用户无需从公开地址充值 gas 即可使用 shielded pool（打破 funding link）。此功能是 EIP-8141 的通用 AA 能力的一个应用场景，而非其设计目标。[verified: github.com/ethereum/EIPs/blob/master/EIPS/eip-8141.md, 2026-06-23; eips.ethereum.org/EIPS/eip-8141, 2026-06-23]
- **EIP-8250: Keyed Nonces for Frame Transactions**（Draft, Core）——Thomas Thiery, Toni Wahrstätter, Lightclient, Vitalik Buterin 提出。将 EIP-8141 frame transaction 的单一 sender nonce 替换为 (nonce_key, nonce_seq) 双部分系统。**隐私赋能效果**：不同 key 下的交易相互独立，观察者无法通过连续递增 nonce 关联同一发送方的多笔交易，对 privacy pool 共享 sender 场景尤其重要。Vitalik 确认为 2026 隐私路线图优先事项之一。[verified: github.com/ethereum/EIPs/blob/master/EIPS/eip-8250.md, 2026-06-23]

**注意**：部分二手媒体报道（如 Blockonomi 2026-05 文章）将 EIP-8141 描述为「privacy pool withdrawal fee」提案。经核验 EIP-8141 GitHub 源文件和 eips.ethereum.org 官方页面，EIP-8141 的正式标题为 "Frame Transaction"，核心内容为原生账户抽象，不包含 privacy pool 专属的 withdrawal fee 机制。「withdrawal fee from pool」是 EIP-8141 paymaster 功能的一个潜在应用场景，非 EIP 本身的设计目标。[source_confidence: GitHub YAML 核验优先于二手媒体报道]

**与应用层方案对比**：

| 维度 | EIP-8182（协议层） | ERC-8065（应用层 wrapper） | ERC-8302/pERC-20（应用层 native, Open ERC PR） |
|------|-------------------|-------------------------|------------------------|
| 匿名集 | 全以太坊统一 | 每个 wrapper 合约独立 | 每个 pERC-20 token 独立 |
| 部署条件 | 以太坊硬分叉 | 合约部署即可 | 合约部署即可 |
| 支持资产 | ETH + 任意 ERC-20 | ERC-20/721/1155/6909 | 仅 fungible token（替代 ERC-20） |
| 隐私层级 | 值级（R1+R2+R3+R5） | 值级 | 值级 |
| 合规机制 | Privacy Pools 兼容（待确认） | 继承底层 token 合规 | 内置 blacklist，总供应量公开 |

**Mantle 相关性：Medium**——EIP-8182 设计目标为以太坊 L1 硬分叉，Mantle L2 无法直接受益。但其 UTXO + Groth16 架构可作为 Mantle 自建 shielded pool 的参考设计。

**调查要点**：

- 验证 Hegota 硬分叉时间线和 EIP-8182 inclusion 状态
- 分析 Groth16 BN254 证明的 gas 成本和 prover 时间
- 检查 Privacy Pools 合规层的具体设计

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: 应用层隐私 Token 标准 — ERC-8065, ERC-8302/pERC-20 及其他

分析应用层（无需硬分叉）的隐私 token 标准，重点覆盖 ERC-8065（ZK Token Wrapper）和 ERC-8302/pERC-20（Private Fungible Tokens, Open ERC PR #1817）。

**ERC-8065: Zero Knowledge Token Wrapper**

| 属性 | 值 |
|------|------|
| 状态 | Draft |
| 类别 | ERC（应用层） |
| 创建日期 | 2025-10-18 |
| 作者 | Jiahui Cui (@doublespending), 0xZPL |
| 核心机制 | EIP-7503 风格 burn-and-remint，ZK proof 证明 burn 有效性后 remint 等值 token |
| 支持资产 | ERC-20, ERC-721, ERC-1155, ERC-6909 |
| 隐私能力 | 打破链上可追踪性（R5 交易图解耦），金额可隐藏（R1），收款方匿名取决于实现 |
| 合规机制 | 继承底层 token 的合规逻辑 |

**pERC-20 / ERC-8302: Private Fungible Tokens**

| 属性 | 值 |
|------|------|
| 状态 | **Open ERC PR**（非已合并 Draft）——ethereum/ERCs PR #1817, 文件 `ERCS/erc-8302.md` |
| 类别 | ERC（应用层） |
| 创建日期 | 2026-06-09（ethresear.ch 原始帖）|
| 作者 | Cyimon (@Cyimon) |
| PR 历史 | PR #1796 (`erc-8287.md`, "Privacy-Native Fungible Tokens") → **已关闭**；PR #1817 (`erc-8302.md`, "Private Fungible Tokens") → **当前活跃** |
| 发布渠道 | ethresear.ch 原始草案 (https://ethresear.ch/t/eip8287-privacy-native-fungible-token-standard-draft/25089) → 扩展版含 approve 功能 (https://ethresear.ch/t/perc20-private-token-standard-draft/25200) → GitHub ERCs PR #1817 |
| 核心机制 | UTXO/note-based 模型 + Groth16 + Poseidon hash commitments，完全替代 ERC-20 接口（无 balanceOf/approve/allowance），扩展版新增 ZIP-32 subaccount-based approve/allowance/transferFrom |
| 隐私能力 | R1 金额 + R2 余额 + R5 交易图 |
| 合规机制 | 内置 blacklist，总供应量公开可见 |
| 特殊说明 | 不是 ERC-20 wrapper，而是全新接口标准——token 从创建起即具有隐私属性。与 ERC-20 capability-complete 但 ABI 不兼容 |
| source_confidence | GitHub PR #1817 直接核验 (https://github.com/ethereum/ERCs/pull/1817, 2026-06-23)；PR #1796 关闭确认 (https://github.com/ethereum/ERCs/pull/1796, 2026-06-23) |

**其他候选**（基于 item-1 检索结果补充）：

- **EIP-7503**: Zero-Knowledge Wormholes——Stagnant 状态（Core），burn-and-mint 与 ZK proof 的原始提案。ERC-8065 引用其设计模式。Mantle 相关性 Low（Core EIP，依赖 L1 burn 语义）
- **Privacy Pools (0xBow)**：非正式 EIP，应用层方案。使用 Association Sets 实现合规门控隐私。$4.6M 交易量。Vitalik 背书。Mantle 相关性 High（纯合约部署）
- **ERC-3643 (T-REX)**：非隐私 EIP，但通过 KYC/合规准入控制提供隐私相关功能。已在多链部署。Mantle 相关性 High
- **ERC-7573 (DvP)**：Delivery-Versus-Payment 结算，使用 shielded pool commitments。隐私相邻。

**应用层方案对比与定位分工**：

| 方案 | 设计哲学 | 适用场景 | Mantle 相关性 |
|------|---------|---------|-------------|
| ERC-8065 | Wrapper——为现有 token 添加隐私 | 已有 ERC-20/721 需要隐私增强 | High |
| ERC-8302/pERC-20 | Native——token 从创建起即隐私（Open ERC PR, 非已合并标准） | 新发 privacy-first token | Medium |
| Privacy Pools | Compliance——合规门控隐私池 | 需要 AML/合规证明的场景 | High |

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-6: 隐私赋能基础设施提案（EIP-8141, EIP-8250）及 EIP-8105 定性

分析与隐私生态间接相关的协议层基础设施提案，以及 EIP-8105（encrypted mempool）的「相关但非隐私」定性。

**关键修正说明**：Round 1 outline 将 EIP-8141 误标为 "Privacy Pool Withdrawal Fees"（EIP-8182 配套提案）。经 GitHub 源文件核验（https://github.com/ethereum/EIPs/blob/master/EIPS/eip-8141.md, 2026-06-23），EIP-8141 实际为 "Frame Transaction"——Vitalik Buterin 等提出的原生账户抽象提案。部分二手媒体（Blockonomi 等）将 EIP-8141 paymaster 功能在隐私池场景的应用误报为 EIP 本身的目标。本 round 予以纠正。目前**不存在**编号为 "EIP-8141" 的 privacy pool withdrawal fee 专属提案；该概念仅作为 EIP-8141 paymaster 的潜在应用场景被讨论。

**EIP-8141: Frame Transaction（原生账户抽象）**

| 属性 | 值 |
|------|------|
| 状态 | Draft |
| 类别 | Core |
| 创建日期 | 2026-01-29 |
| 作者 | Vitalik Buterin 等 |
| 核心功能 | 引入新交易类型 0x06，将交易拆分为 VERIFY + EXECUTE frames；新增 APPROVE opcode；支持 paymaster 代付 gas |
| **分类** | **相关但非隐私**——核心目标为原生账户抽象（Native AA），非隐私提案 |
| 隐私间接赋能 | Paymaster 机制允许第三方代付 gas，privacy pool 用户可通过 paymaster 从提款中扣除 gas，避免从公开地址充值（打破 funding link）。此为 AA 通用能力的一个应用场景 |
| WHI-254 映射 | 不直接满足 R1-R8 任何一项；paymaster 功能间接赋能 R5（交易图解耦，消除 gas 充值关联） |
| Mantle 相关性 | Low——L1 协议层 AA 变更，Mantle L2 有独立的 AA 实现路径 |
| 核验 | [verified: github.com/ethereum/EIPs/blob/master/EIPS/eip-8141.md, 2026-06-23] [verified: eips.ethereum.org/EIPS/eip-8141, 2026-06-23] |

**EIP-8250: Keyed Nonces for Frame Transactions**

| 属性 | 值 |
|------|------|
| 状态 | Draft |
| 类别 | Core |
| 作者 | Thomas Thiery, Toni Wahrstätter, Lightclient, Vitalik Buterin |
| 核心功能 | 将 EIP-8141 frame transaction 的单一 sender nonce 替换为 (nonce_key, nonce_seq) 双部分系统 |
| **分类** | **隐私赋能基础设施**——EIP-8141 的配套提案（非 EIP-8182 配套），有显著隐私赋能效果 |
| 隐私赋能机制 | 不同 key 下的交易 replay-independent，观察者无法通过连续递增 nonce 关联同一发送方的多笔交易；对 privacy pool 共享 sender 地址场景尤其重要。Vitalik 将 keyed nonces 纳入 2026 隐私路线图三大优先事项之一（AA+FOCIL, Keyed Nonces, Kohaku） |
| WHI-254 映射 | 间接赋能 R5（交易图解耦），间接赋能 R3（发送方侧身份不可关联） |
| Mantle 相关性 | Low——依赖 EIP-8141 Frame Transaction（L1 协议层变更），Mantle L2 有独立 nonce 管理 |
| 核验 | [verified: Ethereum Magicians discussion, 2026-06-23] |

**EIP-8105: Universal Enshrined Encrypted Mempool — 定性分析**

| 属性 | 值 |
|------|------|
| 状态 | Draft |
| 类别 | Core |
| 创建日期 | 2025-12-17 |
| 作者 | Jannik Luhn (@jannikluhn), Shutter Network |
| 核心功能 | 方案无关的加密 mempool——交易在被打包进区块前保持加密状态 |
| 支持的解密方案 | 阈值加密、MPC 委员会、TEE、延迟加密、FHE |
| 新增交易类型 | Type 0x05（加密交易）、Type 0x06（解密密钥）|
| 依赖 | EIP-7732 (ePBS) |

**为何分类为「相关但非隐私」**：

1. **作者明确声明**（引用 EIP-8105 Motivation 段）：「The goal is not to improve user privacy (e.g., transaction confidentiality) as transactions are publicly revealed eventually.」
2. **临时加密而非永久隐私**：交易仅在 pre-confirmation 阶段加密，一旦被打包进区块即公开解密，交易内容（金额、参与方、逻辑）对公众完全可见
3. **目标是 R8 而非 R1-R5**：保护的是执行策略（防 MEV/front-running/sandwich），对齐 WHI-254 R8（执行策略保护/反 MEV），而非交易数据的持久隐私
4. **后续发展**：EIP-8105 目前支持 LUCID 方案而非寻求 Hegota 硬分叉 inclusion

**WHI-254 映射**：R8（执行策略保护）。不满足 R1-R5 任何一项。

**Mantle 相关性：Low**——需要以太坊 L1 共识层变更（依赖 ePBS）。Mantle L2 的 sequencer 架构不同于 L1 公共 mempool，MEV 保护需要不同的解决方案（如 private sequencing）。

- **Priority**: high
- **Dependencies**: item-2, item-4

### item-7: WHI-254 框架映射总表与 Mantle 相关性综合评估

将 item-1 到 item-6 的所有 EIP 分析结果汇总，构建 WHI-254 框架映射总表和 Mantle 综合相关性评估。

**WHI-254 8 需求映射矩阵**：

构建每个 EIP × R1-R8 的覆盖矩阵（✅完全覆盖 / ⚠️部分覆盖 / ❌不覆盖），标注每个 ✅/⚠️ 的具体机制。

| EIP | R1 金额 | R2 余额 | R3 身份 | R4 逻辑 | R5 图 | R6 合规 | R7 披露 | R8 MEV |
|-----|---------|---------|---------|---------|-------|---------|---------|--------|
| ERC-5564 | ❌ | ❌ | ✅ | ❌ | ⚠️ | ❌ | ⚠️ viewing-key | ❌ |
| EIP-8182 | ✅ | ✅ | ✅ | ❌ | ✅ | ⚠️ | ⚠️ | ❌ |
| ERC-8065 | ✅ | ⚠️ | ⚠️ | ❌ | ✅ | ❌ | ❌ | ❌ |
| EIP-8105 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**5 轴 Rubric 预填充**（对齐 WHI-254 diagram-2 雷达图模板）：

为每个 EIP 填充 5 轴评估向量：
- 轴 1 — 密码学路线：每个 EIP 使用的核心密码学原语
- 轴 2 — 数据维度覆盖：7 维保护级别
- 轴 3 — 信任模型：密码学/硬件/组织信任假设
- 轴 4 — 部署形态：bolt-on / 合约套件 / 协议层变更
- 轴 5 — 合规披露：选择性披露能力（如有）

**Mantle 相关性综合评估**：

| 相关性 | EIP 列表 | 部署路径 | 预期工作量 |
|--------|---------|---------|-----------|
| **High** | ERC-5564, ERC-6538, ERC-8065, Privacy Pools, ERC-3643 | 合约部署，无协议层修改 | 低 |
| **Medium** | EIP-8182（参考架构）, ERC-8302/pERC-20（Open ERC PR） | 需要 Mantle 侧适配或自研 | 中 |
| **Low** | EIP-7503, EIP-8250, EIP-8141（Frame TX AA）, EIP-8105 | L1 硬分叉专属或架构不兼容 | 高或不适用 |

**空白区域分析**：基于 WHI-254 框架，识别当前 EIP 生态中的隐私能力空白：
- R4（业务逻辑/合约状态隐私）：无现有 EIP 覆盖，依赖 Aztec/TEE 等非标准方案
- R6+R7 的标准化合规框架：缺乏统一的 EIP 级合规-隐私桥接标准

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| eip_number | EIP/ERC 编号（如 EIP-8182, ERC-5564），论坛草案标注「非正式」 | all |
| eip_status | EIP 状态（Draft/Review/Last Call/Final/Stagnant/Withdrawn），附 GitHub YAML frontmatter 核验 URL 和访问日期 | all |
| privacy_primitive | 隐私原语分类标签：recipient-anonymity / value-confidentiality / graph-unlinkability / compliance-gated / protocol-infra / related-non-privacy | item-2, item-7 |
| deployment_layer | 部署层级：protocol-core / application-erc / forum-research | item-2, item-7 |
| whi254_requirement_map | 对齐 WHI-254 8 需求的覆盖向量（R1-R8，每项标注 ✅/⚠️/❌ 及具体机制） | item-2, item-3, item-4, item-5, item-6, item-7 |
| capability_boundary | 能力边界：该 EIP 明确**不**提供的隐私能力，标注原因（如 ERC-5564 不提供金额隐私因为 ECDH 仅混淆地址） | item-2, item-3, item-4, item-5, item-6 |
| mantle_relevance | Mantle 相关性评级（High/Medium/Low）及判定理由 | all |
| crypto_primitive | 核心密码学原语（ECDH/Groth16-BN254/Pedersen-commitment/nullifier/burn-and-remint/threshold-encryption 等） | item-3, item-4, item-5, item-6 |
| verification_url | 状态核验 URL（GitHub raw markdown permalink 或 eips.ethereum.org 页面）+ 访问日期 | all |
| source_confidence | 证据等级：GitHub YAML 核验 / eips.ethereum.org 页面 / 论坛帖子 / 二手资料推断 / 不可核验（附尝试方式） | all |
| companion_eips | 配套/依赖/赋能 EIP 列表及关系类型（如 EIP-8250 是 EIP-8141 配套, EIP-8141 paymaster 间接赋能 EIP-8182 privacy pool 场景） | item-4, item-6 |

## Diagrams

### diagram-1: 隐私相关 EIP 全景分类图

按隐私原语（横轴）× 部署层级（纵轴）的二维矩阵图。每个 EIP 以卡片形式放置在对应格中，卡片颜色编码 EIP 状态（Final=绿, Review=蓝, Draft=黄, Stagnant=灰）。排除范围内的 EIP（ERC-7984, ERC-7945, VOSA）用虚线框标注「独立 issue 覆盖」。EIP-8105 单独列在「相关但非隐私」区域。

- **Type**: matrix / classification map
- **Applies to**: item-2
- **Purpose**: 一眼看清隐私 EIP 的全景分布，识别空白区域和聚集区域

### diagram-2: 隐私 EIP 生态关系图

以 EIP-8182 shielded pool 为中心的关系图，展示三层关系：(1) 同层隐私提案（ERC-8065, ERC-8302/pERC-20, Privacy Pools）标注关系类型 alternative / complements；(2) 隐私赋能基础设施（EIP-8141 Frame TX → paymaster 间接赋能, EIP-8250 keyed nonces → anti-correlation 赋能）标注 enables / indirect-benefit，并明确标注这些是 AA 提案而非隐私提案；(3) 相关非隐私（EIP-8105 encrypted mempool）标注 related-non-privacy。EIP-8250 → EIP-8141 标注 companion（EIP-8250 是 EIP-8141 的配套，非 EIP-8182 的配套）。

- **Type**: dependency / relationship graph
- **Applies to**: item-4, item-6
- **Purpose**: 展示隐私 EIP 生态结构，区分直接隐私提案、隐私赋能基础设施和相关非隐私提案

### diagram-3: Stealth Address 双密钥 ECDH 流程图

展示 ERC-5564 stealth address 生成的端到端流程：发送方获取 stealth meta-address → ECDH 派生 → 生成一次性 stealth address → 转账 → 接收方扫描 Announcement → viewing key 解密识别 → spending key 花费。明确标注哪些信息对外部观察者可见（转账金额、发送方地址）vs 不可见（收款方身份）。

- **Type**: sequence / flow diagram
- **Applies to**: item-3
- **Purpose**: 直观展示 stealth address 的能力边界——为何保护身份但不保护金额

### diagram-4: WHI-254 需求覆盖热力图

R1-R8（行）× 各 EIP（列）的热力图，单元格颜色编码覆盖程度（✅绿/⚠️黄/❌红）。右侧汇总列标注每项需求的 EIP 覆盖数量，底部汇总行标注每个 EIP 的需求覆盖广度。空白区域（如 R4 无 EIP 覆盖）高亮标注。

- **Type**: heatmap
- **Applies to**: item-7
- **Purpose**: 识别 EIP 生态的隐私能力空白和覆盖冗余

### diagram-5: Mantle 相关性评级与部署路径决策树

决策树图：从「Mantle 是否需要此隐私能力？」出发，经「是否需要协议层修改？」→「是否可作为 bolt-on 部署？」→ 最终落入 High/Medium/Low 相关性评级。每个叶节点列出对应的 EIP。

- **Type**: decision tree
- **Applies to**: item-7
- **Purpose**: 为 Mantle 团队提供 EIP 选择决策参考

## Source Requirements

### Primary Sources — EIP 规范文本

每个 EIP 的分析须基于以下优先级的来源：

1. **GitHub YAML frontmatter**（最高优先级）：`https://raw.githubusercontent.com/ethereum/EIPs/master/EIPS/eip-{number}.md` 或 `https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-{number}.md`。用于核验 EIP 状态、类别、作者、创建日期。
2. **eips.ethereum.org 渲染页面**：`https://eips.ethereum.org/EIPS/eip-{number}`。用于阅读完整规范文本。
3. **Ethereum Magicians 讨论帖**：每个 EIP 的 `discussions-to` 字段指向的论坛帖子。用于了解社区反馈和争议点。

### Secondary Sources

- **ethresear.ch**：研究阶段提案（如 pERC-20）
- **WHI-254 框架文档**：`evm-privacy-research/research-sections/privacy-landscape-framework/final.md`
- **EEA Privacy Working Group Report** (Version 1, April 2026)：用于交叉验证 EIP 的技术分类

### 引用规范

- 每个 EIP 状态结论附 GitHub raw markdown URL + 访问日期（格式：`[verified: github.com/ethereum/EIPs, 2026-06-23]`）
- EIP 内容引用标注 section（如 `[EIP-8182 §Abstract]`）
- 论坛草案标注发布日期和 URL
- 不可核验的状态标注 `[unverified: attempted via {method}]`
- WHI-254 框架引用标注 `[WHI-254 §{section}]`
