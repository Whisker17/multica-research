---
topic: "VOSA 系列标准深度分析（VOSA / VOSA-20 / VOSA-RWA）"
project_slug: "evm-privacy-research"
topic_slug: "vosa-standards"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/vosa-standards.md"
  draft: "evm-privacy-research/research-sections/vosa-standards/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/vosa-standards/final.md"

scope: |
  深度分析 VOSA（Virtual One-time Sub-Account）系列三草案——VOSA 原语、VOSA-20 隐私包装代币、
  VOSA-RWA 合规门控代币——评估其作为「轻量级 + 合规友好」方案对 Mantle 的适配性。
  VOSA 自称「UTXO without Merkle trees」：用 ERC-5564 stealth 派生一次性子账户 + Poseidon 承诺 +
  Groth16 证明，以 O(1) 可清理 SPENT_MARKER 替代 nullifier + Merkle，号称较 shielded pool 少约
  10x 约束、省约 97% 存储、纯应用层无协议改动。VOSA 与 ERC-7984/shielded-pool 属不同设计点：
  以「故意暴露转账图」换更低成本与更强可审计性。
  本分析须如实标注成熟度限制（论坛草案/单作者/未审计），不宜赋予天然高权重。

audience: "Mantle 工程团队、协议/基础设施负责人、企业金融/RWA/BD 团队、隐私方案评估决策者"

expected_output: |
  一份中文结构化研究 section，包含：
  - VOSA 原语机制深度拆解（三要素、状态机、bounded state 论证）
  - 隐私边界明确定义（exposed-graph 模型 + 与 Tornado/Railgun 对比）
  - VOSA-20 包装代币全流程分析（shield/unshield、Fat Token Mode、审计扩展）
  - VOSA-RWA 合规门控机制分析（双 Groth16、keyHash/KYC、vs ERC-3643）
  - 五轴 rubric 评分（对齐框架 issue 定义）
  - vs ERC-7984、vs Railgun/Privacy Pool 对照表
  - 成熟度风险明确标注

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23T02:30:00Z"

multica_issue_id: "83543f05-df46-41aa-87a1-c658928c89d9"
branch_name: "research/evm-privacy-research/vosa-standards"
base_commit: "5d6c94f6877227aadaf731852a08f46da1213c54"
language: "中文"
research_depth: "deep-analysis"
mode: "single-issue-lightweight"

primary_sources:
  - name: "VOSA 原语提案"
    url: "https://ethereum-magicians.org/t/vosa-virtual-one-time-sub-account-a-simplified-privacy-primitive-for-evm/27809"
    status: "讨论中"
    date: "2026-02-23"
    author: "louisliu2048"
    access_date: "2026-06-23"
  - name: "VOSA-20 草案"
    url: "https://ethereum-magicians.org/t/draft-erc-vosa-20-privacy-preserving-wrapped-erc-20-token-standard/27832"
    status: "Draft"
    date: "2026-02-26"
    access_date: "2026-06-23"
  - name: "VOSA-RWA 草案"
    url: "https://ethereum-magicians.org/t/draft-erc-vosa-rwa-compliance-gated-privacy-token-for-real-world-assets/27908"
    status: "Draft"
    date: "2026-03-06"
    access_date: "2026-06-23"

secondary_sources:
  - name: "pERC-20 (EIP-8287) 提案"
    url: "https://ethresear.ch/t/perc20-private-token-standard-draft/25200"
    usage: "pERC-20 与 VOSA-20 的关系确认、接口对比"
  - name: "ERC-5564 Stealth Addresses"
    url: "https://eips.ethereum.org/EIPS/eip-5564"
    usage: "VOSA stealth 派生机制的基础标准"
  - name: "ERC-7984 Confidential Fungible Token"
    url: "https://eips.ethereum.org/EIPS/eip-7984"
    usage: "对照分析：shielded pool 路线 vs VOSA exposed-graph 路线"
  - name: "EIP-8182 Private ETH and ERC-20 Transfers"
    url: "https://eips.ethereum.org/EIPS/eip-8182"
    usage: "Ethereum 原生隐私转账方案对比参考（Hegota 升级目标）"
  - name: "ERC-3643 T-REX 合规代币标准"
    url: "https://docs.erc3643.org/erc-3643"
    usage: "VOSA-RWA vs ERC-3643 合规路线对比"
  - name: "Railgun 文档"
    url: "https://docs.railgun.org/"
    usage: "完全匿名方案对比参照（shielded pool + Privacy Pool）"
  - name: "EEA Privacy Working Group Report"
    url: "https://entethalliance.github.io/wg-privacy/privacy-report.html"
    version: "Version 1, April 2026"
    usage: "框架 rubric 评分基线（引用自 privacy-landscape-framework section）"
  - name: "CryptoNews pERC-20 报道"
    url: "https://cryptonews.com/news/ethereum-perc20-private-token-standard/"
    usage: "VOSA 设计理念的第三方解读与技术细节补充"

prerequisite_sections:
  - slug: "privacy-landscape-framework"
    issue_id: "51a89bf9-8955-4ae4-914e-cc6920ffea9a"
    role: "提供五轴 rubric、8 需求体系、选择性披露 6 维向量模型、轻量级判定标准"
---

# Research Outline: VOSA 系列标准深度分析（VOSA / VOSA-20 / VOSA-RWA）

## Research Questions

1. VOSA 原语的三要素（Virtual / One-time / Sub-Account）如何协同工作？ERC-5564 stealth 派生在 VOSA 中的具体角色是什么——是直接复用 ERC-5564 的 `generateStealthAddress` 接口，还是仅借用概念？
2. VOSA 的状态机（UNUSED → ACTIVE → SPENT → cleanup）与 SPENT_MARKER 机制如何实现 bounded state？与 Zcash/Tornado 的 nullifier + Merkle tree 方案相比，O(1) 可清理的具体实现路径和 tradeoff 是什么？
3. VOSA 的隐私边界（隐藏金额/余额/身份，暴露转账图）在框架的 exposed-graph 模型中如何定位？作者自述中与 Tornado Cash、Railgun 等完全匿名方案的差异表述是否准确和完整？
4. VOSA-20 的 shield/unshield 流程、Fat Token Mode 和 IVOSA20Auditing 审计扩展分别解决什么问题？约束数和 in-browser 证明时延是否支撑「轻量级」声称？
5. VOSA-RWA 的双 Groth16 证明架构如何实现合规门控（keyHash / 链下 KYC / replay 防护）？与 ERC-3643 的合规路线有何本质区别？freeze 功能的未解决状态对生产部署意味着什么？
6. 以框架 issue 的五轴 rubric 打分，VOSA 系列在密码学路线、被保护数据维度、信任模型、部署形态、合规-选择性披露各轴的评分如何？与 ERC-7984 和 Railgun/Privacy Pool 的横向对比结论是什么？

## Items

### item-1: VOSA 原语机制深度拆解 — 三要素、stealth 派生、Poseidon 承诺与状态机

深入分析 VOSA（Virtual One-time Sub-Account）原语的核心机制设计。VOSA 自称「UTXO without Merkle trees」，其核心创新在于用 SPENT_MARKER + epoch cleanup 替代传统 nullifier + Merkle tree，实现 O(1) 状态追踪和有界状态增长。

**三要素拆解**：
- **Virtual**：地址仅作为合约内 mapping 键存在，不是真实 EVM 账户（EOA），不占用全局状态树条目。这意味着 VOSA 地址无法接收 ETH 转账或被外部直接调用——所有交互通过包装合约进行。
- **One-time**：每个子账户地址仅使用一次（类似 UTXO note），花费后标记为 SPENT 并在 epoch 清理中回收。这消除了余额累积问题但引入了找零管理需求。
- **Sub-Account**：从主密钥（master key）通过 stealth 地址派生技术生成。接收者持有 spending key 和 viewing key，发送者使用接收者的 stealth meta-address 生成一次性子账户地址。

**ERC-5564 stealth 派生机制**：
VOSA 构建在 ERC-5564（Stealth Addresses）之上。ERC-5564 定义了标准化的非交互式 stealth 地址生成：发送者使用接收者的 stealth meta-address（包含 spending public key 和 viewing public key）非交互式生成一次性地址。须确认 VOSA 是否直接调用 ERC-5564 的 `generateStealthAddress` 接口，还是在概念层面借用 stealth 派生并自行实现（可能适配 Poseidon 哈希而非 ERC-5564 默认的 secp256k1）。

**Poseidon 承诺方案**：
VOSA 使用 Poseidon 哈希函数构建 note commitment。Poseidon 是专为 ZK 电路优化的哈希函数，在 Groth16 约束系统中的开销远低于 SHA-256 或 Keccak。note commitment 结构预期为 `commitment = Poseidon(value, owner_pubkey, salt/blinding)`，使得金额和归属在链上不可逆推。须从原帖确认具体 commitment 结构和字段。

**状态机分析**：

```
UNUSED → ACTIVE → SPENT → cleanup(epoch)
```

- **UNUSED**：子账户地址已派生但尚未收到资金（commitment 未在链上注册）
- **ACTIVE**：commitment 已注册到链上 mapping，资金可用于转账
- **SPENT**：所有者提交 ZK 证明花费此 note，合约设置 SPENT_MARKER
- **cleanup**：epoch 到期后，SPENT 状态的 mapping 条目可被任何人清理（删除），释放存储

**SPENT_MARKER vs nullifier 对比**：
传统隐私方案（Zcash、Tornado、Railgun）使用 nullifier（note 唯一标识的哈希）+ Merkle tree（所有 note 的累积集）。花费时公布 nullifier 并证明 note 在 Merkle tree 中。VOSA 的 SPENT_MARKER 直接在 mapping 中标记，无需维护全局 Merkle tree。这带来：
- **优势**：O(1) 查找和标记（vs Merkle tree 的 O(log n)）；无需 Merkle 路径证明约束（减少约束数）；可清理旧条目（bounded state）
- **代价**：SPENT_MARKER 暴露了哪个具体地址被花费（vs nullifier 仅暴露「某个 note 被花费」而不暴露具体是哪个），这是转账图暴露的根本原因

**bounded state 论证**：
VOSA 声称实现有界状态增长。其机制为：SPENT 状态的 note 在 epoch 到期后可被链上清理（mapping entry 删除，EVM SSTORE 从非零变为零可获得 gas 退还）。假设 epoch 长度为 E blocks，则链上活跃状态条目数上界为 [当前 epoch 的 ACTIVE notes] + [上一 epoch 尚未清理的 SPENT notes]。须验证：(a) 清理激励是否充足（gas 退还是否覆盖清理调用成本），(b) 极端情况下（大量 notes 同时到期未清理）是否存在状态膨胀风险。

须从原帖逐项核实以上机制描述的准确性，特别是 commitment 结构、ERC-5564 的复用程度、epoch cleanup 的具体实现。

- **Priority**: critical
- **Dependencies**: none

### item-2: 隐私边界与 Exposed-Graph 模型 — 隐藏什么、暴露什么、与完全匿名方案对比

明确 VOSA 系列的隐私边界定义，将其归入框架（privacy-landscape-framework）的评估体系，并对照完全匿名方案（Tornado Cash、Railgun/Privacy Pool）分析作者的自述声称。

**VOSA 隐私边界**（对齐框架 8 需求体系 R1-R8）：

| 框架需求 | VOSA 保护状态 | 机制 | 备注 |
|---------|-------------|------|------|
| R1 交易金额隐私 | ● 完全保护 | Poseidon commitment 隐藏金额 + Groth16 证明金额守恒 | 链上仅可见 commitment 值 |
| R2 账户余额隐私 | ● 完全保护 | 无 `balanceOf`，余额分散在多个 ACTIVE notes 中 | 需 viewing key 才能重建余额 |
| R3 对手方身份隐私 | ◐ 部分保护 | stealth 地址隐藏接收者真实身份；但发送者 EOA 与 VOSA 合约的交互可见 | 发送者身份取决于前端混淆（如 relayer） |
| R4 业务逻辑/合约状态隐私 | ✗ 不保护 | VOSA 为值级隐私原语，不隐藏合约执行逻辑 | 纯 token ledger 隐私 |
| R5 交易图/资金流隐私 | ✗ 不保护（exposed-graph） | SPENT_MARKER 暴露哪个 VOSA 地址被花费；新 VOSA 地址的创建在同一 tx 中可见 | 这是 VOSA 与 shielded pool 路线的根本分歧 |
| R6 合规可审计性 | ● 支持 | viewing key 允许授权方重建完整交易历史 | VOSA-RWA 增加 KYC 门控层 |
| R7 选择性披露 | ◐ 部分支持 | viewing key 分享机制 | VOSA-20 的 IVOSA20Auditing 扩展 |
| R8 执行策略保护（反 MEV） | ✗ 不保护 | 标准公开 mempool | 除非结合 encrypted mempool 等外部方案 |

**Exposed-Graph 模型定位**：
VOSA 的 exposed-graph 属于框架 item-4 选择性披露 6 维向量中的「残余公开泄露（维度 f）= graph」。这不是披露机制，而是隐私方案的固有副作用。链上观察者可以看到：
- 哪个地址向 VOSA 合约 shield 了资金
- 哪些 VOSA 子账户在同一交易中被创建（output notes）
- 哪些 VOSA 子账户被花费（SPENT_MARKER）
- 交互时序和频率模式

**与完全匿名方案对比**（基于作者自述 + 研究者分析）：

| 维度 | VOSA | Tornado Cash | Railgun / Privacy Pool |
|------|------|-------------|----------------------|
| 匿名集来源 | 无匿名集（exposed graph） | 固定面额存款池 | 全池 UTXO 集（Privacy Pool 加 association set） |
| Merkle tree | 无 | 全局 Merkle tree | 全局 Merkle tree |
| 状态增长 | O(1) 可清理（bounded） | O(n) 不可清理 | O(n) 不可清理（需要定期 merkle tree 迁移或截断） |
| 约束数 | 声称约 10x fewer | ~30k 约束（per deposit/withdraw） | ~100k-500k 约束 |
| 转账图隐私 | 暴露 | 隐藏（匿名集内不可区分） | 隐藏（Privacy Pool 可部分披露） |
| 合规友好 | 原生（viewing key + audit） | 不友好（Tornado 已被 OFAC 制裁） | Privacy Pool 的 association set 提供部分合规路径 |

须从原帖核实作者关于「约 10x fewer constraints」和「约 97% storage savings」的具体数值和比较基线。

- **Priority**: critical
- **Dependencies**: item-1

### item-3: VOSA-20 — 隐私包装 ERC-20 代币标准全流程分析

分析 VOSA-20 草案（Draft ERC）的完整技术设计。VOSA-20 将 VOSA 原语包装为 ERC-20 兼容的隐私代币标准，定义了 shield/unshield 流程、标准接口和扩展点。

**Shield/Unshield 流程**：
- **Shield（入金/遮蔽）**：用户将标准 ERC-20 token 存入 VOSA-20 包装合约。合约锁定 ERC-20 token，生成对应金额的 Poseidon commitment，将 commitment 注册到链上 mapping。此过程对外可见（哪个地址 shield 了多少金额——这是 exposed-graph 的入口泄露点）。
- **Private Transfer（隐私转账）**：花费一个或多个 ACTIVE VOSA note，创建新的 VOSA note 给接收方，附 Groth16 证明确保 input_sum == output_sum。旧 note 标记为 SPENT，新 note 注册为 ACTIVE。
- **Unshield（出金/解遮蔽）**：花费 VOSA note，销毁 commitment，解锁对应的 ERC-20 token 回到用户指定地址。此过程同样对外可见（出口泄露点）。

**Fat Token Mode**：
Fat Token Mode 是 VOSA-20 的一种扩展模式。基于 web 搜索信息和上下文推断，Fat Token Mode 可能指：将更多元数据（如 token ID、过期时间、合规标签）编码进 commitment 字段，使单个 VOSA note 承载超出纯金额的信息。须从原帖确认 Fat Token Mode 的确切定义、使用场景和对约束数的影响。

**IVOSA20Auditing 审计扩展接口**：
VOSA-20 定义了 IVOSA20Auditing 接口作为可选审计扩展。预期该接口允许授权审计方通过 viewing key 或专用 ZK 证明验证特定账户/交易的合规性，而无需接触所有交易明文。须从原帖确认：
- 接口的具体方法签名和参数
- 审计方的授权机制（on-chain registration 还是 off-chain 密钥分享）
- 审计粒度（per-tx / per-account / 全量）
- 审计证明是否需要额外的 ZK 电路

**约束数与 in-browser 证明时延**：
VOSA 声称较 shielded pool 方案约束数少约 10 倍。须确认：
- VOSA-20 transfer 电路的具体约束数（预期量级：~3k-10k 约束 vs Tornado ~30k 或 Railgun ~100k+）
- 约束减少的主要来源：无 Merkle 路径验证 + 简化的 nullifier 逻辑
- In-browser 证明生成时延：是否满足用户交互级响应时间（<5s 在标准浏览器上）
- Groth16 trusted setup 要求：是否使用通用 Powers of Tau ceremony 还是需方案专属 setup

**pERC-20 / EIP-8287 关系**：
须澄清 VOSA-20 与 pERC-20（EIP-8287，作者 Cyimon，2026-06-09）之间的关系。两者都声称是 EVM 上的隐私代币标准，都使用 Poseidon + Groth16 + 类 UTXO 模型。可能的关系：(a) VOSA-20 是 pERC-20 的前身/灵感来源，(b) 两者是同一作者的迭代版本，(c) 独立提案有相似设计。须从 ethereum-magicians 和 ethresear.ch 交叉对比确认。

- **Priority**: high
- **Dependencies**: item-1

### item-4: VOSA-RWA — 合规门控隐私代币机制与 ERC-3643 对比

分析 VOSA-RWA 草案的合规门控机制设计，重点关注双 Groth16 证明架构、链下 KYC 机制、replay 防护，以及与 ERC-3643（T-REX）的路线对比。

**双 Groth16 证明架构**：
VOSA-RWA 在 VOSA-20 的基础 transfer 证明之上，增加第二个独立的 Groth16 证明用于合规验证。每次状态变更操作（transfer/mint/burn）须同时提交两个 ZK 证明：
- **Proof 1（Transfer Proof）**：继承自 VOSA-20，证明 input_sum == output_sum、发送者拥有 note、note 未被花费
- **Proof 2（Compliance Proof）**：证明操作满足链下合规要求——发送者和接收者都在 KYC 白名单中、未被制裁、满足转账金额限制等——而不向链上披露任何 PII

**keyHash 与链下 KYC 机制**：
VOSA-RWA 使用 keyHash 作为链上身份锚点。预期机制：
- 用户在链下完成 KYC/AML 验证（通过合规提供商）
- KYC 提供商签发 credential，包含用户 public key 的哈希（keyHash）
- keyHash 注册到链上合规合约（不含 PII）
- Compliance Proof 证明交易参与方的 key 对应已注册的 keyHash，且 KYC credential 有效且未过期
- 链上合约仅验证 ZK proof，不接触任何明文身份信息

**Replay 防护**：
须分析 VOSA-RWA 如何防止：
- 同一 compliance proof 被重放到不同交易
- 过期 KYC credential 的使用（时间戳绑定）
- 跨链/跨合约的 proof 重放（合约地址绑定）
预期使用 nonce + domain separator（EIP-712）+ 时间窗口的组合方案。

**vs ERC-3643（T-REX）对比**：

| 维度 | VOSA-RWA | ERC-3643 (T-REX) |
|------|---------|-----------------|
| 身份存储 | 链下 KYC + 链上 keyHash | 链上 ONCHAINID 身份注册表 |
| 隐私保护 | ZK 证明，链上无 PII | 无隐私，身份和持仓公开可见 |
| 合规验证 | 双 ZK proof，gas 成本高 | 合约调用 Identity Registry，gas 成本低 |
| 冻结功能 | 开放问题（open question） | 原生支持（`freeze`/`unfreeze`） |
| 强制转移 | 不明确 | 原生支持（`forcedTransfer`） |
| 标准成熟度 | 论坛草案（2026-03） | 生产使用标准（多年部署历史） |
| Transfer 限制 | ZK 电路内嵌规则 | Identity Registry + Compliance Contract |
| 投资者资格验证 | ZK 证明白名单成员资格 | 链上调用 ONCHAINID claim 验证 |

**Open Questions 记录**：
须如实记录 VOSA-RWA 草案中明确标注为未解决的问题：
- freeze 功能：如何在隐私 UTXO 模型中冻结特定用户资产？UTXO 模型不像账户模型那样有可直接冻结的 balance slot
- 强制转移：监管要求下如何在不知道用户 spending key 的情况下转移资产
- KYC 凭证过期/撤销的链上同步延迟
- 合规规则升级时旧电路 trusted setup 是否需要重做

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-5: 轻量级与生产就绪评估 — 部署形态、信任假设与成熟度风险

评估 VOSA 系列作为「轻量级 bolt-on」方案的适配性，使用框架 issue（privacy-landscape-framework）定义的轻量级判定标准，并明确标注成熟度风险。

**部署形态分析**：
VOSA 系列声称纯应用层方案，可部署在任意 EVM 链上，无需协议改动。对齐框架部署形态三级分类：
- VOSA 属于「B. 链上合约套件」——在现有 EVM 链上部署隐私合约集
- 无 L2/L3 依赖、无 sequencer、无独立 DA 层
- 无需硬分叉或共识层修改
- 可能需要 sidecar 服务（relayer 用于 meta-transaction 以隐藏发送者地址）

**框架一票否决条件检查**：

| 否决条件 | VOSA 状态 | 判定 |
|---------|----------|------|
| V1: 需要部署新 L1/L2/L3/sidechain | 否，纯合约部署 | ✓ 通过 |
| V2: 需要新的资产桥 | 否，shield/unshield 在同链完成 | ✓ 通过 |
| V3: 须运维 sequencer/prover/DA 全节点 | 否，Groth16 证明在客户端生成 | ✓ 通过 |
| V4: 需要基础链硬分叉或共识层修改 | 否，纯 EVM 合约 | ✓ 通过 |

**通用成本指标评估**：

| 判定维度 | VOSA 评估 | 判定 |
|---------|----------|------|
| 链上存储增长 | commitment mapping + SPENT_MARKER，可 epoch 清理 | 轻量级 |
| 运维复杂度 | 可能需 1 个 relayer 服务（可选） | 轻量级~中量级 |
| 基础链侵入性 | 无修改，纯合约部署 | 轻量级 |
| 部署时间线 | 依赖 trusted setup + 审计（但方案本身部署简单） | 待评估 |

**ZK 路线专属成本指标**：

| 判定维度 | VOSA 评估 | 判定 |
|---------|----------|------|
| 约束数 | 声称 <10^4（待确认） | 轻量级 |
| Trusted Setup | Groth16 需要 trusted setup（Powers of Tau 或方案专属） | 中量级 |
| Prover 硬件需求 | 声称 in-browser 可证明 | 轻量级 |

**信任假设**：
- Groth16 soundness: BN254 q-DLOG / pairing 假设
- Trusted setup: Powers of Tau ceremony 或方案专属 ceremony（需确认）
- Poseidon 哈希的抗碰撞/抗原像性
- VOSA-RWA: KYC 提供商诚实签发 credential 的假设

**成熟度风险评估**（必须如实标注，不可高估）：

| 风险维度 | 状态 | 严重程度 |
|---------|------|---------|
| 标准状态 | 以太坊论坛讨论草案，非正式 EIP/ERC | 高 |
| 作者 | 单作者（louisliu2048），无已知机构支持 | 高 |
| 代码审计 | 未审计 | 高 |
| 实际部署 | 无已知主网部署 | 高 |
| 社区审查 | 论坛讨论有限，无核心开发者背书 | 高 |
| 参考实现 | 须确认是否有开源参考实现 | 待查 |
| 同行评议 | 无学术论文或形式化验证 | 高 |

**与 EEA Readiness Matrix 对标**：VOSA 系列处于 EEA 定义的 Pilot 之前阶段（Pre-pilot / Concept），远未达 Early Production 或 GA。

- **Priority**: critical
- **Dependencies**: item-1, item-2, item-3, item-4

### item-6: 五轴 Rubric 评分与横向对比 — vs ERC-7984 / vs Railgun-Privacy Pool

使用框架 issue（privacy-landscape-framework, WHI-254）定义的五轴统一评估 rubric 对 VOSA 系列打分，并与 ERC-7984（Confidential Fungible Token / shielded pool 路线）和 Railgun/Privacy Pool 进行横向对比。

**轴 1 — 密码学路线**：
- VOSA: ZKP（Groth16 + Poseidon），纯 ZK 路线
- 需 trusted setup（Groth16 固有要求）
- 后量子安全性：Groth16 基于 pairing，不抗量子（与 ERC-7984/Railgun 同）

**轴 2 — 被保护数据维度**（7 项）：

| 数据维度 | VOSA 系列 | ERC-7984 | Railgun/PP |
|---------|----------|---------|-----------|
| ① 金额 | ● 完全 | ● 完全 | ● 完全 |
| ② 余额 | ● 完全 | ● 完全 | ● 完全 |
| ③ 对手方身份 | ◐ 部分 | ● 完全（stealth） | ● 完全（stealth） |
| ④ 业务逻辑 | ✗ | ✗ | ✗ |
| ⑤ 转账图 | ✗（exposed-graph） | ● 完全（匿名集） | ● 完全（Privacy Pool） |
| ⑥ 合约状态 | ✗ | ✗ | ✗ |
| ⑦ 订单流/mempool | ✗ | ✗ | ✗ |

**轴 3 — 信任模型**：
- VOSA: Cryptographic Trust (ZK)
- 信任假设：BN254 安全、Poseidon 抗碰撞、trusted setup 诚实（1-of-N）
- VOSA-RWA 额外假设：KYC 提供商诚实
- 与 ERC-7984 同类型（都是 ZKP cryptographic trust）
- 与 Railgun 同类型

**轴 4 — 部署形态**：
- VOSA: 链上合约套件（B 类），通过一票否决，初步判定为轻量级
- ERC-7984: 待评估（取决于具体实现，可能为协议层或合约层）
- Railgun: 链上合约套件（B 类），已有多链部署

**轴 5 — 合规-选择性披露 6 维向量**：

| 维度 | VOSA-20 | VOSA-RWA | ERC-7984 | Railgun/PP |
|------|--------|---------|---------|-----------|
| a. Authority | key-holder | key-holder, smart-contract | 待评估 | key-holder |
| b. Trigger | viewing-key-share | compliance-gate, viewing-key-share | 待评估 | viewing-key-share |
| c. Payload | amount+identity | amount+identity | 待评估 | amount+identity |
| d. Scope | per-tx, per-account | per-tx, per-account | 待评估 | per-tx |
| e. Revocability | 待确认 | 待确认 | 待评估 | one-time |
| f. Leakage | graph, existence, timing | graph, existence, timing | existence | existence |

**横向对比总结表**（核心差异点）：

| 维度 | VOSA | ERC-7984 / Shielded Pool | Railgun / Privacy Pool |
|------|------|--------------------------|----------------------|
| 设计哲学 | 暴露图换轻量 | 全隐藏（匿名集） | 全隐藏 + 可选合规 |
| 状态模型 | SPENT_MARKER（bounded） | Merkle + nullifier（unbounded） | Merkle + nullifier（unbounded） |
| 约束数量级 | ~10^3-10^4（声称） | ~10^4-10^5 | ~10^5-10^6 |
| 合规路线 | 原生 viewing key + RWA 扩展 | 待定义 | Privacy Pool association set |
| 成熟度 | 论坛草案 / 未审计 | EIP Draft / 有参考实现 | 主网运行多年 |
| Mantle 适配 | 轻量级 bolt-on（但不成熟） | 待评估 | 合约部署可行（但非企业定位） |

须确保每个评分结论附源 URL + 访问日期；推论性判断标注 `[推论]`；从原帖核实的声称标注 `[原帖验证]`。

- **Priority**: critical
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| mechanism_detail | VOSA 原语的具体机制实现细节：commitment 结构、状态转换条件、ZK 电路约束 | item-1, item-3, item-4 |
| privacy_boundary | 对齐框架 8 需求的保护状态（●完全/◐部分/✗不保护），附机制说明 | item-2, item-6 |
| data_dimension | 7 项被保护数据维度各自保护级别，对齐框架 item-2 映射 | item-2, item-6 |
| trust_model | 信任模型分类（Cryptographic/Hardware-Anchored/Organizational/混合）及具体假设 | item-5, item-6 |
| deployment_pattern | 部署形态分类（bolt-on/合约套件/独立链）+ 轻量级判定结果 | item-5, item-6 |
| disclosure_vector | 选择性披露 6 维多标签向量：authority×trigger×payload×scope×revocability×leakage | item-2, item-6 |
| compliance_mapping | 合规标准映射（GDPR/MiCA/Travel Rule/AML-CFT/KYC-KYB）及满足程度 | item-4, item-6 |
| maturity_risk | 成熟度风险等级（草案状态/审计状态/部署历史/社区审查/参考实现） | item-5 |
| source_confidence | 证据等级：原帖直接引用 / 原帖推论 / 二手报道 / 研究者推断 | all |
| vs_comparison | 与对照方案（ERC-7984 / Railgun / ERC-3643）的差异点，附具体维度标注 | item-2, item-4, item-6 |
| open_question | 草案中明确标注为未解决或研究者发现的未覆盖问题 | item-1, item-3, item-4, item-5 |
| mantle_relevance | 该结论对 Mantle 轻量级机构隐私方案的具体启示或约束 | item-5, item-6 |

## Diagrams

### diagram-1: VOSA 原语状态机与生命周期流程图

VOSA note 从生成到清理的完整生命周期流程图。展示 UNUSED → ACTIVE → SPENT → cleanup(epoch) 的状态转换，标注每个转换的触发条件（shield/transfer/spend + ZK proof / epoch 到期 + 任何人调用 cleanup）。对比传统 nullifier + Merkle 路径的流程差异。

- **Type**: flowchart / state machine
- **Applies to**: item-1
- **Purpose**: 一眼理解 VOSA 与传统 UTXO 隐私方案的核心架构差异

### diagram-2: VOSA-20 Shield/Transfer/Unshield 全流程时序图

展示三种核心操作（shield、private transfer、unshield）的完整交互时序：用户 → 客户端 ZK prover → VOSA-20 合约 → ERC-20 底层合约。标注每步的隐私状态变化（哪些信息对公众可见、哪些被 commitment 隐藏）。

- **Type**: sequence diagram
- **Applies to**: item-3
- **Purpose**: 理解 exposed-graph 泄露发生在哪些具体步骤

### diagram-3: VOSA-RWA 双 Groth16 合规门控架构图

展示 VOSA-RWA 的双证明架构：Transfer Proof + Compliance Proof 并行验证流程。标注链下 KYC 签发 → keyHash 注册 → compliance proof 生成 → 链上双重验证的完整数据流。与 ERC-3643 的 ONCHAINID + Compliance Contract 路线对比。

- **Type**: architecture diagram / data flow
- **Applies to**: item-4
- **Purpose**: 对比 ZK 合规 vs 链上身份注册 两种路线的架构差异

### diagram-4: 五轴 Rubric 雷达图 — VOSA vs ERC-7984 vs Railgun

使用框架定义的五轴雷达图模板，填充 VOSA 系列、ERC-7984、Railgun/Privacy Pool 三个方案的评分，可视化对比。突出 VOSA 在「转账图隐私」轴上的明显短板和在「部署轻量级」轴上的优势。

- **Type**: radar chart (comparative)
- **Applies to**: item-6
- **Purpose**: 一张图呈现三种路线的 tradeoff 差异

### diagram-5: 隐私方案成熟度谱 — VOSA 在行业中的位置

线性谱图，左端为「概念/草案」，右端为「主网 GA」。标注 VOSA、ERC-7984、EIP-8182、Railgun、Tornado Cash（已制裁）、ERC-3643 等方案的位置。清晰展示 VOSA 处于极早期阶段。

- **Type**: spectrum / scale
- **Applies to**: item-5
- **Purpose**: 防止读者高估 VOSA 成熟度，直观对比行业现状

## Source Requirements

### Primary Sources
- **VOSA 原语提案** (ethereum-magicians, 2026-02-23)
  - URL: https://ethereum-magicians.org/t/vosa-virtual-one-time-sub-account-a-simplified-privacy-primitive-for-evm/27809
  - 访问日期: 2026-06-23
  - 使用方式: item-1, item-2 的核心论据来源。须逐项核实三要素定义、状态机转换、SPENT_MARKER 机制、bounded state 论证、与完全匿名方案的自述对比
  - 引用要求: 每个机制结论须标注原帖具体段落位置或引文

- **VOSA-20 草案** (ethereum-magicians, 2026-02-26)
  - URL: https://ethereum-magicians.org/t/draft-erc-vosa-20-privacy-preserving-wrapped-erc-20-token-standard/27832
  - 访问日期: 2026-06-23
  - 使用方式: item-3 的核心来源。须确认 shield/unshield 接口、Fat Token Mode 定义、IVOSA20Auditing 接口、约束数

- **VOSA-RWA 草案** (ethereum-magicians, 2026-03-06)
  - URL: https://ethereum-magicians.org/t/draft-erc-vosa-rwa-compliance-gated-privacy-token-for-real-world-assets/27908
  - 访问日期: 2026-06-23
  - 使用方式: item-4 的核心来源。须确认双 Groth16 架构、keyHash 机制、replay 防护、freeze open question

### Secondary Sources
- **ERC-5564 Stealth Addresses** — VOSA stealth 派生基础标准交叉验证
- **ERC-7984 Confidential Fungible Token** — shielded pool 路线对照
- **EIP-8182 Private ETH and ERC-20 Transfers** — Ethereum 原生隐私方案对照
- **ERC-3643 T-REX** — VOSA-RWA 合规路线对照
- **Railgun 文档** — 完全匿名方案对照
- **pERC-20 (EIP-8287, ethresear.ch)** — VOSA-20 与 pERC-20 关系厘清
- **EEA Privacy Working Group Report (V1, April 2026)** — rubric 评分框架基线
- **CryptoNews pERC-20 报道** — 第三方技术解读补充

### 引用规范
- 原帖直接引用标注 `[VOSA 原语帖, §段落描述, 访问 2026-06-23]`
- 原帖推论标注 `[推论, 基于 VOSA-20 草案 §段落, 访问 2026-06-23]`
- 二手报道标注来源和日期
- 研究者独立分析标注 `[研究者分析]`
- 与框架 rubric 对齐的评分标注 `[对齐 privacy-landscape-framework, §item-N]`
- 不确定性须显式标注：「须从原帖确认」「声称但未验证」「推断」
