---
topic: "机密计算协处理器/机密层方案分析（Zama / Inco / Fhenix）"
project_slug: "evm-privacy-research"
topic_slug: "confidential-coprocessor"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/confidential-coprocessor.md"
  draft: "evm-privacy-research/research-sections/confidential-coprocessor/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/confidential-coprocessor/final.md"

scope: |
  深度分析「机密计算协处理器/机密层」bolt-on 家族——Zama fhEVM 与 Inco（两个重点）、Fhenix CoFHE。
  说清各自集成形态、解密/访问控制模型、合规能力与成熟度。
  家族共性：普通 Solidity + 加密类型，链上仅存 ciphertext handle + ACL，重计算离线。
  区别于 token-only 方案，本家族可隐藏任意合约状态。
  按部署形态（bolt-on）归类而非底层密码学——故 Inco（当前 TEE-first、FHE-roadmap）虽用 TEE 仍归此家族，
  与独立机密链（如 Sapphire）区分。

audience: "Mantle 工程团队、协议/基础设施负责人、企业金融/RWA/BD 团队、隐私方案评估决策者"

expected_output: |
  一份中文结构化研究 section，包含：
  - Zama fhEVM 四组件架构（host contract / Coprocessor / Gateway / 门限 KMS）深度解析
  - Inco 双层架构（Lightning TEE 当前能力 + Atlas FHE roadmap）深度解析，明确「今天=TEE」
  - Fhenix CoFHE 差异分析（EigenLayer 经济安全、协处理器 vs 链）
  - 三方案对比表 + 框架 rubric 评分
  - 轻量级集成评估：在现有 EVM L2 接入各需什么
  - 合规-选择性披露分析（observer access、门限解密 quorum、viewing key）
  - 风险与活性依赖分析（KMS quorum、TEE 硬件信任、性能基准）
  - Zama/Inco 在 Mantle 集成路径草图

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23T03:40:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23T03:40:00Z"

multica_issue_id: "085bc80d-f094-4585-98df-692c43731af5"
branch_name: "research/evm-privacy-research/confidential-coprocessor"
base_commit: "5d6c94f6877227aadaf731852a08f46da1213c54"
language: "中文"
research_depth: "deep-analysis"
mode: "single-issue-lightweight"

primary_sources:
  - name: "Zama Protocol Documentation"
    url: "https://docs.zama.org/protocol/"
    access_date: "2026-06-23"
    key_sections: "Litepaper, Architecture Overview, ACL, Host Contracts, Gateway, KMS"
  - name: "Zama fhEVM Documentation"
    url: "https://docs.zama.ai/fhevm/"
    access_date: "2026-06-23"
    key_sections: "Architecture Overview, ACL, Smart Contract, Decryption"
  - name: "Zama fhEVM Coprocessor Announcement"
    url: "https://www.zama.org/post/fhevm-coprocessor"
    access_date: "2026-06-23"
  - name: "ERC-7984 Confidential Fungible Token (EIP)"
    url: "https://eips.ethereum.org/EIPS/eip-7984"
    access_date: "2026-06-23"
    status: "DRAFT (submitted July 2025)"
  - name: "ERC-7984 Explained (Zama Blog)"
    url: "https://www.zama.org/post/erc-7984-the-confidential-token-standard-explained"
    access_date: "2026-06-23"
  - name: "OpenZeppelin Confidential Contracts (ERC-7984)"
    url: "https://docs.openzeppelin.com/confidential-contracts/token"
    access_date: "2026-06-23"
  - name: "Inco Network Official Site"
    url: "https://www.inco.org/"
    access_date: "2026-06-23"
  - name: "Inco Lightning Launch (GlobeNewsWire)"
    url: "https://www.globenewswire.com/news-release/2025/04/24/3067707/0/en/Inco-Raises-5M-in-Strategic-Round-Led-by-a16z-CSX-to-Accelerate-Web3-Confidentiality-Launches-Inco-Lightning-on-Base-Sepolia.html"
    access_date: "2026-06-23"
  - name: "Circle × Inco Confidential ERC-20 Framework"
    url: "https://www.circle.com/blog/confidential-erc-20-framework-for-compliant-on-chain-privacy"
    access_date: "2026-06-23"
  - name: "Inco Joins ERC3643 Association"
    url: "https://www.inco.org/blog/inco-joins-erc3643-association"
    access_date: "2026-06-23"
  - name: "Fhenix Official Site"
    url: "https://www.fhenix.io/"
    access_date: "2026-06-23"
  - name: "Fhenix × EigenLayer FHE Coprocessor (EigenLayer Blog)"
    url: "https://www.blog.eigenlayer.xyz/fhenix/"
    access_date: "2026-06-23"
  - name: "Fhenix CoFHE Access Control (DEV Community)"
    url: "https://dev.to/fhenix_io/privacy-isnt-private-by-default-understanding-access-control-in-cofhe-38l0"
    access_date: "2026-06-23"
  - name: "Fhenix FHE Rollup Whitepaper (Medium)"
    url: "https://medium.com/@Fhenix/introducing-fhe-rollups-scaling-confidential-smart-contracts-on-ethereum-and-beyond-305a908e922a"
    access_date: "2026-06-23"
  - name: "Encrypted Compute Ranked Framework (Leosereinn)"
    url: "https://medium.com/@leosereinn/encrypted-compute-ranked-a-framework-for-evaluating-programmable-privacy-networks-d54bb9a0ebab"
    access_date: "2026-06-23"
  - name: "EEA Privacy Working Group Report"
    url: "https://entethalliance.github.io/wg-privacy/privacy-report.html"
    version: "Version 1, April 2026"
    usage: "框架 rubric 评分对齐 (cross-reference from privacy-landscape-framework)"

prerequisite_sections:
  - topic_slug: "privacy-landscape-framework"
    usage: "五轴评估 rubric、选择性披露 6 维 taxonomy、部署形态分类与轻量级判定标准"
---

# Research Outline: 机密计算协处理器/机密层方案分析（Zama / Inco / Fhenix）

## Research Questions

1. Zama fhEVM 的四组件架构（host contract / Coprocessor / Gateway / 门限 KMS）如何协同工作？symbolic execution + handle 模型的数据流是什么？ACL 如何在链上/链下（Gateway 聚合）两层执行权限控制？public-decrypt 与 user-decrypt（re-encryption）的适用场景与安全性差异？
2. ERC-7984 作为「confidential ERC-20」标准定义了什么接口（confidentialTransfer / confidentialBalanceOf / setOperator）？它与 ERC-20 的关系是什么（非兼容继承，而是全新接口设计）？OpenZeppelin Confidential Contracts 提供了哪些扩展（Wrapper / Freezable / ObserverAccess / Restricted / Votes）？
3. Inco Lightning（TEE-based）的当前架构是什么？Confidential Compute Nodes + Decryption Nodes Quorum + Callback Relayer 如何工作？其 TEE 信任假设（Intel TDX）与 Zama 的密码学信任假设有何本质区别？Atlas（FHE）roadmap 何时落地、信任模型如何变化？
4. Fhenix CoFHE 作为「FHE 协处理器 + EigenLayer 经济安全」与 Zama 的「FHE 协处理器 + 门限 KMS」有何架构差异？CoFHE 的 optimistic rollup 验证 + 经济质押模型的安全保证与 Zama threshold MPC 的安全保证各有什么权衡？
5. 在现有 EVM L2（如 Mantle）上集成这三个方案各需要什么？链改动范围（precompile / 合约部署 / 无修改）、开发者工具链（Solidity 库）、基础设施依赖（Coprocessor 节点 / TEE enclave / KMS 网络）如何评估？
6. 三方案在合规-选择性披露方面各提供什么能力？Zama 的 ACL + ObserverAccess、Inco 的 delegated viewing + ERC-3643 关联、Fhenix 的 permit-based sealing 如何对齐框架 issue 的 6 维向量模型？
7. 各方案的风险与活性依赖是什么？KMS quorum 去中心化程度（Zama 13 MPC nodes）、TEE 硬件信任链（Inco Intel TDX 侧信道风险）、EigenLayer 经济安全阈值（Fhenix restaked ETH）？厂商自报 benchmark（Zama 20 TPS→GPU 500-1000 TPS、Fhenix 50x faster decryption）是否有独立验证？

## Items

### item-1: Zama fhEVM 架构深度解析 — 四组件模型、handle/ACL、解密模式与 ERC-7984

**目标**：完整梳理 Zama fhEVM 的四组件架构及其数据流，解释 symbolic execution 与 handle 模型如何让 host chain 无需执行 FHE 运算，深入分析 ACL 权限系统（链上 ACL 合约 → Gateway 聚合 → KMS 鉴权）和两种解密模式（public-decrypt / re-encryption），以及 ERC-7984 标准接口与 OZ 扩展体系。

**调查维度**：

**1a. 四组件架构与数据流**
- **fhEVM Solidity Library**：开发者在普通 Solidity 中使用 encrypted types（euint8/16/32/64/128/256, ebool, eaddress, ebytes64/128/256）和 FHE 操作（加/减/乘/比较/条件选择）
- **Host Contracts (fhEVM Executor)**：部署在 host chain 的智能合约，不执行 FHE 运算，仅产生 symbolic pointer（handle）并 emit event 通知 Coprocessor；维护链上 ACL
- **Coprocessors**：去中心化节点网络，监听 host chain 事件，执行实际 FHE 运算（基于 TFHE-rs），返回加密结果；多个 Coprocessor 并行执行，majority agreement 确保正确性；Coprocessor 有质押要求
- **Gateway**：协议控制面——验证加密输入、聚合 ACL、跨链桥接 ciphertext、协调 Coprocessor 与 KMS 之间的通信
- **KMS（Key Management Service）**：门限 MPC 网络（13 个 MPC 节点），负责 FHE 密钥生成/轮换、CRS 生成、门限解密；底层实际是一条 L1 链（带 web API）
- 数据流：用户 encrypt → host chain symbolic execution → Coprocessor FHE computation → 结果 handle 回写 host chain → 解密请求经 ACL 验证 → Gateway 转发 KMS → 门限解密返回
- **关键架构优势**：host chain 不因 FHE 减速，非 FHE 交易正常速度执行；FHE 操作可并行（非顺序）；链上仅存 handle（pointer），不存实际 ciphertext

**1b. Handle 模型（Symbolic Execution）**
- Handle = ciphertext 的链上指针，而非实际加密数据本身
- 实际 ciphertext 存储在 Coprocessor 网络中
- Symbolic execution：host chain 上的 FHE 操作不产生实际结果，只产生指向结果的 pointer；类似编程语言的 lazy evaluation
- Handle 可以被链式组合（chaining）——不需要等前一个 FHE 操作完成就可以发起下一个操作
- 全局 FHE 公钥用于加密所有输入和状态

**1c. ACL（Access Control List）权限系统**
- ACL 合约部署在每条 Host Chain 上，记录「谁可以解密什么」
- 两层 ACL：链上 ACL 合约（per Host Chain）+ Gateway 聚合 ACL（跨链统一视图，供 KMS 鉴权）
- ACL 事件机制：每次合约 allow 一个地址使用 ciphertext，emit event → Coprocessor relay → Gateway 聚合
- **持久权限**：`FHE.allow(ciphertext, address)` / `FHE.allowThis(ciphertext)` — 跨交易持久化
- **临时权限**：`TFHE.allowTransient(ciphertext, address)` — 单笔交易内有效，使用 transient storage 节省 gas
- **验证**：`FHE.isSenderAllowed(ciphertext)` — 检查调用方是否被授权
- **公开解密标记**：`FHE.makePubliclyDecryptable(ciphertext)` — 永久标记为可公开解密
- ACL 不仅用于解密控制，也用于计算权限控制（合约必须被 allow 才能对 ciphertext 执行 FHE 操作）

**1d. 解密模式**
- **Public Decrypt**：明文结果上链（例如用于合约需要检查的条件）；通过 Gateway → KMS 门限解密 → 明文返回链上合约
- **User Decrypt (Re-encryption)**：先用全局私钥门限解密，再用用户提供的公钥重新加密，返回给用户；只有用户自己能用自己的私钥解密最终结果；适用于用户查询自己的余额等场景
- 两种模式都需要 ACL 授权
- 可配置解密模式：threshold / centralized / KMS

**1e. ERC-7984 标准与 OZ 扩展**
- **ERC-7984 定义**：confidential fungible token 标准，所有金额用 confidential pointers（bytes32 handle）表示；非 ERC-20 兼容，是全新接口设计
- **核心接口**：`confidentialTotalSupply()` → encrypted bytes32；`confidentialBalanceOf(address)` → encrypted bytes32；`confidentialTransfer(address, bytes32)`；`confidentialTransferFrom(address, address, bytes32, bytes)`；`setOperator(address, uint48)` — 带时间限制的 operator 授权
- **作者**：Aryeh Greenberg, Ernesto García, Hadrien Croubois 等（Zama + OZ 团队）；2025 年 7 月提交，当前 DRAFT 状态
- **OZ Confidential Contracts 扩展**：
  - `ERC7984ERC20Wrapper`：将 ERC-20 包装为 confidential token，双向免费转换
  - `ERC7984Freezable`：freezer 角色可冻结/解冻 token
  - `ERC7984ObserverAccess`：每个账户可添加 observer（如审计员/监管方），observer 被授予查看余额和转账金额的权限
  - `ERC7984Restricted`：用户账户转账限制（合规控制）
  - `ERC7984Votes`：confidential vote tracking 和委托

**1f. Zama 平台成熟度**
- 2025 年 6 月成为全球首家 FHE 独角兽（估值 $1B，融资超 $150M）
- 2025 年 12 月底 Ethereum mainnet 上线
- $ZAMA token 拍卖 2026 年 1 月 12 日开始
- fhEVM v0.7（2025 年 7 月）引入 Gateway 核心组件
- 当前 CPU 吞吐量 ~20 TPS；GPU 路线图（2026 H2）目标 500-1000 TPS/chain
- ASIC 路线图目标 100,000+ TPS/chain（单服务器）
- Bootstrapping 延迟已降至 <1ms（NVIDIA H100 GPU），吞吐量 189,000 bootstraps/sec（8x H100）
- 开源（BSD-3-Clause-Clear），商业使用需许可证

- **Priority**: high
- **Dependencies**: none

### item-2: Inco 深度解析 — Lightning(TEE) 当前能力 + Atlas(FHE) Roadmap + RWA 合规定位

**目标**：完整梳理 Inco 的双层架构，明确区分「今天 = TEE（Lightning）」与「未来 = FHE（Atlas）」，深入分析其作为「机密层」的集成模式、TEE 信任假设、RWA/机构合规定位，以及与 Circle/ERC-3643 的合规生态布局。

**调查维度**：

**2a. Inco Lightning 架构（TEE-based，当前生产）**
- **定位**：不是新链，而是现有链的「机密层」（confidentiality layer），类比 TLS/SSL
- **底层技术**：TEE（Trusted Execution Environment），当前使用 Intel TDX（Trust Domain Extensions）——CPU 级安全隔区，即使节点运营方也无法看到 enclave 内部数据
- **四组件**：
  - Smart Contract Library：Solidity 工具包，扩展 EVM 以支持 encrypted types
  - Confidential Compute Nodes：TEE enclave 节点网络，链下执行加密计算
  - Decryption Nodes + Callback Relayer：基于 quorum 的 TEE 网络，处理解密请求，签名结果，通过验证的 callback 交易回写链上
  - Client-side JS Library：前端 SDK，本地加密输入、管理密钥/签名、解密输出
- **开发者体验**：import Solidity library → 获得 encrypted state，不需要新链或新钱包；标准 Solidity 开发

**2b. TEE 信任假设与风险**
- **本质**：信任 Intel 硬件（TDX）的安全隔离保证——与 Zama/Fhenix 的密码学信任假设有本质区别
- **Intel TDX 特性**：CPU 内存加密引擎硬件隔离，host OS / hypervisor 可管理 VM 生命周期但不能读取 VM 内存；远程证明（Remote Attestation）
- **侧信道风险**：继承 SGX/TDX 的侧信道攻击面（Spectre/Meltdown 类）；安全性依赖于 Intel 硬件无漏洞
- **运营方信任**：虽然 TEE 保护了计算，但 TEE 节点运营方仍控制可用性（活性风险）
- **与 Sapphire/Phala 同类型风险**：Inco Lightning 继承相同的 TEE 风险画像

**2c. Atlas（FHE roadmap）**
- 未来协议，利用 FHE 和 MPC 提供 trustless 的链上可编程机密性
- 计划用于替代/补充 Lightning 的 TEE 信任假设
- 上线时间：原计划「later this year」（2025 年说法），实际进度待验证
- 信任模型变化：从 Hardware-Anchored Trust (TEE) → Cryptographic Trust (FHE/MPC)

**2d. Confidential ERC-20 与 RWA 合规**
- **Circle × Inco 联合框架**：Confidential ERC-20 Framework——将标准 ERC-20 转换为隐藏余额和交易金额的 confidential 版本
- **核心设计选择**：confidentiality（隐藏金额/余额）而非 anonymity（隐藏地址）——地址公开，金额加密
- **访问控制与选择性披露**：
  - Delegated viewing：授权特定方（审计员/监管方）查看账户详情，无需分享私钥
  - 可编程解密规则：permissioned parties 可被授予访问权限
  - 智能合约级转账规则：AML、黑名单、交易限额、管辖权限制
- **ERC-3643 Association**：Inco 加入 ERC-3643（RWA 合规 token 标准）协会，贡献 confidentiality 能力
- **Confidential Token Association**：Inco 与 OpenZeppelin、Zama 共同创立（2025 年 4 月）

**2e. 平台成熟度**
- 总融资 $10M：$5M（2025 年 4 月，a16z CSX 领投）+ 前轮 $5M；投资方含 Coinbase Ventures、Circle Ventures、1kx
- Inco Lightning 在 Base Sepolia testnet 上线（2025 年 4 月）
- Base mainnet 集成状态：多源信息矛盾——有声明「live on Base mainnet」但也有「beta on Base Sepolia」，需核实
- 原来是 FHE-first pitch，2025 年 pivot 到 TEE-first（Lightning）以加快交付

**2f. Force-Exit 机制**
- 需调查：当 TEE/机密层不可用时，用户是否有逃生通道（force-exit / escape hatch）？
- 与独立链不同，Inco 作为 bolt-on 机密层，理论上 host chain 资产安全不依赖机密层活性——但需验证实际机制

- **Priority**: high
- **Dependencies**: none

### item-3: 轻量级集成评估 — 在现有 EVM L2 接入各需什么

**目标**：评估在现有 EVM L2（如 Mantle）上集成 Zama fhEVM、Inco Lightning、Fhenix CoFHE 各需要什么，包括链改动范围、开发者工具链、基础设施依赖，以及对合约逻辑/状态隐私的覆盖度。

**调查维度**：

**3a. Zama fhEVM 集成要求**

*路径 A — Coprocessor 模式（推荐，无链改动）*：
- 链改动：**无** — host chain 不需要修改，不需要 precompile
- 部署需求：在 host chain 上部署 fhEVM host contracts（ACL 合约 + Executor）
- 开发者工具：import fhEVM Solidity library，用 encrypted types 替换需要隐私的变量
- 基础设施依赖：Zama 运营的 Coprocessor 网络 + Gateway + KMS（或自建）
- 许可证：开发/研究免费（BSD-3-Clause-Clear），商业部署需 Zama 许可

*路径 B — Native 模式（深度集成）*：
- 使用 fhEVM-go library 修改 go-ethereum（或 geth fork）
- 需要添加 FHE precompile（默认地址 0x93）
- 修改 PrecompiledContract 接口
- 依赖 tfhe-rs 本地编译（Go 不支持此类构建）
- 适用于想要原生支持 FHE 的链

**3b. Inco Lightning 集成要求**
- 链改动：**无** — bolt-on 机密层，host chain 无需修改
- 部署需求：在 host chain 上部署 Inco 合约套件
- 开发者工具：import Inco Solidity library，使用 encrypted types
- 基础设施依赖：Inco 运营的 TEE Confidential Compute Nodes + Decryption Quorum Nodes + Callback Relayer
- 当前限制：仅支持 Base（testnet/mainnet 待确认）

**3c. Fhenix CoFHE 集成要求**
- 链改动：**无** — 协处理器模式
- 部署需求：在 host chain 上部署 Fhenix relay contract
- 开发者工具：import Fhenix FHE Solidity library，使用 encrypted integer types
- 基础设施依赖：Fhenix CoFHE Coprocessor 网络 + Threshold Decryption Network + EigenLayer operators
- 当前支持：Ethereum Sepolia、Base（2026 年 2 月）、Arbitrum Sepolia

**3d. 对比评估维度**

| 维度 | Zama (Coprocessor) | Inco Lightning | Fhenix CoFHE |
|------|-------------------|----------------|--------------|
| 链改动 | 无 | 无 | 无 |
| 部署方式 | 合约 + 外部 Coprocessor | 合约 + TEE 节点 | 合约 + FHE Coprocessor |
| 底层密码学 | TFHE (FHE) | TEE (Intel TDX) | BFV/TFHE (FHE) |
| 安全模型 | 门限 MPC + FHE 数学保证 | 硬件信任 (Intel) | EigenLayer 经济安全 + FHE |
| 信任假设 | ≥ KMS quorum 诚实 | Intel TDX 无漏洞 | ≥ EigenLayer stake 诚实 |
| 开发者体验 | Solidity + encrypted types | Solidity + encrypted types | Solidity + encrypted types |
| 合约状态隐私覆盖 | 任意合约状态 | 任意合约状态 | 任意合约状态 |

**3e. 合约逻辑/状态隐私覆盖度**
- 三方案均超越 token-only 隐私，可隐藏任意合约状态
- 覆盖范围：余额、转账金额、合约变量、比较结果、条件分支结果（通过 cmux/select）
- 限制：地址/身份不隐藏（与 ZK 方案如 Aztec 的区别）；交易图/资金流可见

**3f. 对齐框架部署形态判定**
- 对齐 privacy-landscape-framework 的一票否决条件和轻量级判定标准
- 三方案均为 bolt-on Coprocessor 模式，不需要新链/新桥/全节点运维/硬分叉
- 初步判定：均可归类为「轻量级 bolt-on」——但需验证具体细节

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Fhenix CoFHE 差异分析 — 经济安全、协处理器 vs 链

**目标**：深入分析 Fhenix CoFHE 与 Zama fhEVM 的架构差异，特别是 EigenLayer 经济安全模型 vs 门限 KMS 模型的安全权衡，以及 Fhenix 从「FHE L2」到「FHE Coprocessor」的演进。

**调查维度**：

**4a. CoFHE 架构详解**
- **Pipeline 架构**：validation → computation → publishing → decryption 四阶段分离
- **Relay Contract**：部署在 host chain，监听 FHE 计算事件
- **Relay Node**：监听 Relay Contract 事件，桥接调用到 Fhenix rollup
- **FHE Rollup**：无状态 FHE 计算层，执行加密计算
- **Threshold Decryption Network**：授权解密网络，仅向被授权方揭示明文
- 架构设计理念：「encrypted memory 的权限系统」而非传统黑盒计算

**4b. EigenLayer 经济安全模型**
- Fhenix CoFHE 通过 EigenLayer restaking 获得经济安全保证
- EigenLayer operators 证明计算有效性（attestation）
- 恶意 operator 的 stake 被 slash
- 与 Zama 的门限 MPC 对比：
  - Zama：密码学保证（≥ threshold 节点诚实则安全）+ 质押激励
  - Fhenix：经济安全保证（攻击成本 > restaked ETH）+ optimistic rollup 验证
- 安全性权衡：密码学保证 vs 经济博弈论保证

**4c. 从 FHE L2 到 FHE Coprocessor 的演进**
- Fhenix 原为「首个 FHE-powered L2 区块链」
- 演进为 confidential DeFi infrastructure company，核心产品 CoFHE
- FHE Rollup Whitepaper（2026 年 3 月）：所有状态加密，CoFHE 处理计算，validity proofs 提交到 base layer
- 与 Zama 的关系：Fhenix 使用 Zama 的 TFHE-rs 库（Zama 无论哪个 FHE 链赢都收许可费）

**4d. 技术创新**
- **Decomposable BFV**（2026 年 2 月）：将大明文值分解为小 ciphertext 片段再加密，允许并行处理，显著提升 exact FHE schemes 的吞吐量
- 性能声称：解密速度比竞品快 50x（未独立验证）；门限解密延迟改善 37x，吞吐量提升 20,000x（对比早期方案）

**4e. 访问控制与 Permit 模型**
- Permit-based access：用户通过 permit 证明身份，授权 unsealing of sealed outputs
- Sealed output：FHE 计算结果的 sealed 形式，需要 permit 才能 unseal
- Cofhe.js SDK：前端加密输入、管理 access control permits、unseal 加密输出

**4f. 平台成熟度**
- 融资 $22M
- CoFHE testnet：Ethereum Sepolia、Base（2026 年 2 月）、Arbitrum Sepolia
- 合作伙伴：EigenLayer（经济安全）、Offchain Labs（Arbitrum 生态）
- 日本投资（BIPROGY、TransLink Capital）——亚洲隐私稳定币方向
- 尚未 mainnet

- **Priority**: medium
- **Dependencies**: item-1

### item-5: 合规-选择性披露 — observer access、门限解密 quorum、viewing key

**目标**：分析三方案在合规-选择性披露方面的能力，对齐 privacy-landscape-framework 定义的 6 维向量模型，评估各方案在机构/RWA 合规场景下的选择性披露完备性。

**调查维度**：

**5a. Zama 合规-选择性披露**

对齐 6 维向量模型：
- **维度 a（披露授权方）**：`key-holder`（ACL allow）+ `smart-contract`（合约逻辑自动授权）+ `regulator`（ObserverAccess 扩展）
- **维度 b（触发方式）**：`viewing-key-share`（re-encryption 机制——用户提供公钥）+ `on-chain-request`（public decrypt）+ `automatic`（ObserverAccess observer 持续可见）
- **维度 c（披露载荷）**：`amount`（confidentialBalanceOf）+ `amount+identity`（根据合约设计）+ `all`（如果合约允许）；支持粒度控制
- **维度 d（范围/粒度）**：`per-tx`（单笔 allowTransient）+ `per-account`（persistent allow）+ `per-contract`（allowThis）
- **维度 e（可撤销性）**：`permanent`（persistent allow 一旦设定无法自行撤销——需调查是否有 revoke 机制）+ `auditable-log`（所有 ACL 事件 on-chain emit + Gateway 聚合）
- **维度 f（残余泄露）**：`existence`（交易存在可见）+ `timing`（交易时序可观察）；地址公开

OZ 扩展如何服务合规：
- `ERC7984ObserverAccess`：监管方/审计员作为 observer 查看余额和转账
- `ERC7984Restricted`：转账限制（KYC/AML 准入）
- `ERC7984Freezable`：合规冻结能力
- `ERC7984Votes`：保密治理投票

**5b. Inco 合规-选择性披露**

对齐 6 维向量模型：
- **维度 a**：`key-holder` + `smart-contract`（可编程解密规则）+ `regulator`（delegated viewing）
- **维度 b**：`compliance-gate`（智能合约级 AML/KYC/黑名单/交易限额规则）+ `viewing-key-share`（delegated viewing 不需分享私钥）+ `automatic`（ERC-3643 合规引擎）
- **维度 c**：`amount`（余额/转账金额隐藏，地址公开）；可编程载荷控制
- **维度 d**：`per-tx` + `per-account`（delegated viewing 可选粒度）
- **维度 e**：需调查 revocability 支持；`auditable-log`（链上可验证）
- **维度 f**：`existence` + `timing`；地址公开

合规生态定位：
- Circle × Inco Confidential ERC-20 Framework 专为合规隐私设计
- ERC-3643 Association 成员——RWA 合规 token 标准 confidentiality 贡献
- Confidential Token Association 共同创立方
- 核心叙事：confidentiality ≠ anonymity，面向机构合规需求

**5c. Fhenix 合规-选择性披露**

对齐 6 维向量模型：
- **维度 a**：`key-holder`（permit holder）+ `smart-contract`（合约定义的 access rules）
- **维度 b**：`viewing-key-share`（permit-based unsealing）+ `on-chain-request`（threshold decryption request）
- **维度 c**：需调查载荷粒度
- **维度 d**：需调查范围粒度
- **维度 e**：需调查 revocability
- **维度 f**：`existence` + `timing`；地址公开

Fhenix 在合规叙事上弱于 Zama 和 Inco——未见明确的 compliance/RWA 合作或框架

**5d. 合规-选择性披露对比表**

| 能力 | Zama | Inco | Fhenix |
|------|------|------|--------|
| Observer/审计员访问 | OZ ObserverAccess 扩展 | Delegated viewing | Permit-based（较基础） |
| 合规转账限制 | OZ Restricted 扩展 | 智能合约级规则 + ERC-3643 | 需调查 |
| 冻结能力 | OZ Freezable 扩展 | 需调查 | 需调查 |
| 合规生态伙伴 | OZ、Confidential Token Association | Circle、OZ、ERC-3643 Association | 有限 |
| 机构/RWA 定位 | 中（通用隐私平台） | 强（RWA + 合规显式叙事） | 弱（DeFi 优先） |

- **Priority**: high
- **Dependencies**: item-1, item-2, item-4

### item-6: 风险与活性依赖 — KMS quorum、TEE 硬件信任、性能基准

**目标**：分析三方案的安全风险、活性依赖和性能基准，特别标注厂商自报 benchmark 的独立验证状态。

**调查维度**：

**6a. Zama — KMS quorum 去中心化与活性**
- KMS 13 MPC 节点——quorum 阈值是多少？（须查文档确认 t-of-13）
- KMS 节点运营方是否足够去中心化？（初期可能 Zama 自营为主）
- KMS 底层是一条 L1 链——该链的共识安全性如何？
- 活性依赖：如果 KMS quorum 不可用，所有解密操作暂停（计算可继续，但无法获取结果）
- Coprocessor 网络去中心化程度？（质押 + majority agreement）

**6b. Inco — TEE 硬件信任链**
- Intel TDX 侧信道攻击面：历史上 SGX 多次被 side-channel 攻破（Spectre/Meltdown/Plundervolt/ÆPIC Leak/Downfall）
- TDX 是 SGX 的继任者，安全性更强但仍存在理论攻击面
- 远程证明（Remote Attestation）依赖 Intel 证明服务——单点信任
- TEE 节点运营方控制可用性——如果 TEE 节点集群下线，机密层不可用
- 「今天 = TEE」的风险定性：Hardware-Anchored Trust，不是 Cryptographic Trust

**6c. Fhenix — EigenLayer 经济安全阈值**
- 经济安全依赖 restaked ETH 的规模——如果质押不足，攻击成本可能低于攻击收益
- Optimistic rollup 验证有挑战窗口——在窗口内是否有足够激励进行 fraud proof？
- EigenLayer operator 集中度风险
- Threshold Decryption Network 的去中心化程度

**6d. 性能基准（厂商自报，标注「未独立验证」）**

| 指标 | Zama（自报） | Inco（自报） | Fhenix（自报） |
|------|-------------|-------------|---------------|
| 当前吞吐量 | ~20 TPS (CPU) | 未公开 | 未公开 |
| 路线图吞吐量 | 500-1000 TPS (GPU, 2026 H2) | 未公开 | 未公开 |
| 远期目标 | 100,000+ TPS (ASIC) | 未公开 | 未公开 |
| Bootstrapping 延迟 | <1ms (H100 GPU) | N/A (TEE, 无 bootstrapping) | 未公开 |
| 解密速度 | 门限解密（延迟未公开） | TEE 解密（低延迟） | 「50x faster than competitors」 |
| FHE overhead | ~100-1000x vs 明文 | N/A (TEE overhead 远小于 FHE) | 37x 延迟改善 / 20,000x 吞吐量提升 vs 早期 |

**所有性能数据标注「未独立验证」**——均为厂商自报或厂商赞助文章引用，未见独立第三方 benchmark。

**6e. 共同风险**
- 三方案均处于早期阶段（Zama 刚 mainnet、Inco/Fhenix 仍 testnet）
- FHE 密钥管理的长期安全性——密钥泄露意味着所有历史 ciphertext 可解密
- 量子计算威胁：FHE 本身是 post-quantum（基于格密码），但 TEE（Inco）不具备 post-quantum 特性
- 监管不确定性：全链加密可能被某些管辖权视为 non-compliant

- **Priority**: high
- **Dependencies**: item-1, item-2, item-4

### item-7: 框架 Rubric 评分、三方案对比表与 Mantle 集成路径草图

**目标**：按 privacy-landscape-framework 定义的五轴 rubric 对三方案评分，生成结构化对比表，并为 Zama/Inco 绘制在 Mantle 上的初步集成路径草图。

**调查维度**：

**7a. 五轴 Rubric 评分**

对齐 privacy-landscape-framework item-3 五轴评估 rubric：

| 评估轴 | Zama fhEVM | Inco Lightning | Fhenix CoFHE |
|--------|-----------|----------------|--------------|
| **轴 1 — 密码学路线** | FHE (TFHE) + MPC (KMS) | TEE (Intel TDX) [当前]; FHE/MPC [roadmap] | FHE (BFV/TFHE) + EigenLayer |
| **轴 2 — 数据维度** | 金额✓ 余额✓ 身份✗ 图✗ 逻辑✓ 状态✓ 订单流✗ | 同 Zama | 同 Zama |
| **轴 3 — 信任模型** | Cryptographic (FHE) + Organizational (KMS) | Hardware-Anchored (TEE) | Cryptographic (FHE) + Economic (EigenLayer) |
| **轴 4 — 部署形态** | Bolt-on 协处理器 | Bolt-on 机密层 | Bolt-on 协处理器 |
| **轴 5 — 合规披露** | 多维度（ObserverAccess / Restricted / Freezable） | 多维度（Delegated Viewing / ERC-3643） | 基础（Permit-based） |

**7b. 三方案全面对比表**

设计综合对比表，覆盖：
- 架构模型（组件数、数据流）
- 底层密码学/信任基础
- 安全模型（密码学 / 硬件 / 经济）
- 链集成要求（链改动 / 部署 / 基础设施）
- 合规-选择性披露能力
- 成熟度（融资 / 部署状态 / 生态伙伴）
- 性能（标注「未独立验证」）
- 许可证/商业模型
- Post-quantum 特性

**7c. Zama 在 Mantle 集成路径草图**

前提：Mantle 是 Optimistic Rollup L2，基于 OP Stack（geth fork），使用 MNT 作为 gas token。

集成路径（Coprocessor 模式，最轻量）：
1. 部署 fhEVM host contracts（ACL + Executor）到 Mantle
2. 配置 Gateway 连接（指向 Zama 或 self-hosted Gateway）
3. 开发者 import fhEVM Solidity library 编写 confidential contracts
4. 无需 Mantle 协议层修改
5. 考虑因素：Zama 商业许可证谈判、KMS 信任模型对 Mantle 治理的影响、性能对 Mantle 用户体验的影响

**7d. Inco 在 Mantle 集成路径草图**

集成路径：
1. Inco 目前仅支持 Base——Mantle 集成需 Inco 团队扩展支持
2. 若支持：部署 Inco 合约套件到 Mantle + Inco 运营 TEE 节点连接 Mantle
3. 无需 Mantle 协议层修改
4. 考虑因素：Inco TEE 信任模型（Intel 硬件依赖）对 Mantle 安全叙事的影响、Inco 团队扩展意愿/时间线、TEE 节点地理分布与延迟

**7e. Fhenix CoFHE 在 Mantle 路径备注**
- Fhenix 当前支持 Ethereum Sepolia / Arbitrum Sepolia / Base
- 作为 chain-agnostic 协处理器，理论上可扩展到 Mantle
- 但 EigenLayer 经济安全模型的成熟度不如 Zama KMS
- 合规能力弱于 Zama/Inco——机构用例支撑力不足

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

## Diagram Expectations

### diagram-1: 机密计算协处理器家族架构对比图
- 类型：并排三栏架构图
- 内容：Zama（Host Contract → Coprocessor → Gateway → KMS）、Inco（Host Contract → TEE Compute Nodes → Decryption Quorum）、Fhenix（Host Contract → Relay → CoFHE Rollup → Threshold Decryption + EigenLayer）
- 用途：直观对比三方案的组件差异和数据流

### diagram-2: Zama fhEVM 数据流时序图
- 类型：Sequence diagram
- 内容：User → Host Chain (symbolic execution) → Coprocessor (FHE computation) → Gateway (ACL check) → KMS (threshold decryption) → User (re-encrypted result)
- 用途：展示 handle 模型的完整生命周期

### diagram-3: 信任模型对比图
- 类型：矩阵图或 Venn 图
- 内容：Cryptographic Trust (Zama FHE, Fhenix FHE) vs Hardware-Anchored Trust (Inco TEE) vs Economic Trust (Fhenix EigenLayer) vs Organizational Trust (KMS operators)
- 用途：可视化三方案的信任假设差异

### diagram-4: Mantle 集成路径草图
- 类型：系统集成图
- 内容：Mantle L2 + Zama Coprocessor 路径 vs Inco 机密层路径，标注需要部署/配置的组件
- 用途：支撑集成评估结论

## Source Requirements

### 一手源（必须）
- Zama Protocol 官方文档（docs.zama.org）— 架构、ACL、KMS、解密模式
- Zama fhEVM 文档（docs.zama.ai/fhevm）— Solidity 库、smart contract 开发
- ERC-7984 EIP 正式文本（eips.ethereum.org）
- OpenZeppelin Confidential Contracts 文档
- Inco 官网及博客（inco.org）— Lightning/Atlas 架构、RWA 合规
- Fhenix 官网及文档（fhenix.io, cofhe-docs.fhenix.zone）— CoFHE 架构、Access Control
- Fhenix × EigenLayer 公告（EigenLayer Blog）
- Circle × Inco Confidential ERC-20 Framework
- Zama Protocol Litepaper

### 二手源（交叉验证）
- Figment: "Inside Zama" 深度分析
- Blockworks / U.Today: Fhenix × EigenLayer 报道
- GlobeNewsWire: Inco Lightning 发布公告
- Medium (Leosereinn): "Encrypted Compute, Ranked" 框架评估
- KuCoin Research: "FHE 2026" 综合报告

### 前置 section 交叉引用
- privacy-landscape-framework: 五轴 rubric、6 维选择性披露 taxonomy、部署形态轻量级判定标准

### 引用要求
- 每个结论附 URL + 访问日期（2026-06-23）
- 厂商自报性能数据标注「未独立验证」
- 区分一手源（官方文档/白皮书）和二手源（媒体报道/分析文章）
