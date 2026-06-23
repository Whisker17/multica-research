---
topic: "ERC-7984 机密代币标准深度分析（含 ERC-7945 对比）"
project_slug: "evm-privacy-research"
topic_slug: "erc7984-confidential-token"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/erc7984-confidential-token.md"
  draft: "evm-privacy-research/research-sections/erc7984-confidential-token/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/erc7984-confidential-token/final.md"
  index: "evm-privacy-research/research-sections/_index.md"

scope: |
  深度分析 ERC-7984（Confidential Fungible Token）接口设计、技术中立性与选择性披露机制；
  Step 1: 拆解 ERC-7984 接口（confidentialBalanceOf、confidentialTransfer(From)、operator 模型、AmountDisclosed、receiver callback、interface id）；
  Step 2: 技术中立性——bytes32 指针如何让 FHE/ZK/TEE 后端可替换，与 OZ 参考实现关系；
  Step 3: 选择性披露扩展（ObserverAccess/Freezable/Restricted）评估；
  Step 4: ERC-7984 vs ERC-7945 head-to-head（接口/allowance/成熟度/生态）；
  Step 5: 按框架 rubric 打分

audience: "Mantle 工程团队、协议/基础设施负责人、企业金融/RWA/BD 团队、隐私方案评估决策者"

expected_output: |
  一份中文结构化研究 section，包含：
  - 完整列出 ERC-7984 核心接口与披露扩展
  - 技术中立+可替换后端论证（标注不覆盖合约逻辑隐私）
  - ERC-7984 vs ERC-7945 对比表（接口/allowance/成熟度/生态）
  - 按 WHI-254 框架 rubric 打分
  - 外部结论标注访问日期+URL+commit SHA

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23"

multica_issue_id: "f0035b6e-4f0d-4a98-80ad-2f68d46c40be"
branch_name: "research/evm-privacy-research/erc7984-confidential-token"
base_commit: "5d6c94f6877227aadaf731852a08f46da1213c54"
language: "中文"
research_depth: "deep-analysis"
mode: "single-issue"

primary_sources:
  - name: "ERC-7984 EIP Specification"
    url: "https://eips.ethereum.org/EIPS/eip-7984"
    status: "Draft"
    created: "2025-07-03"
    access_date: "2026-06-23"
    authors: "Aryeh Greenberg, Ernesto García, Hadrien Croubois, Ghazi Ben Amor, Clement Danjou, Joseph Andre Turk, Silas Davis, Nicolas Pasquier (Zama/OpenZeppelin)"
  - name: "ERC-7945 EIP Specification"
    url: "https://eips.ethereum.org/EIPS/eip-7945"
    status: "Review"
    created: "2025-05-09"
    access_date: "2026-06-23"
    authors: "Siyuan Zheng, Zhe Han, Xiaoyu Liu et al. (Ant Group/Ant International)"
  - name: "OpenZeppelin Confidential Contracts (IERC7984.sol + extensions)"
    url: "https://github.com/OpenZeppelin/openzeppelin-confidential-contracts"
    access_date: "2026-06-23"
  - name: "WHI-254 隐私全景框架 (rubric + disclosure taxonomy)"
    path: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"
    commit: "5d6c94f6877227aadaf731852a08f46da1213c54"

prerequisite_sections:
  - topic_slug: "privacy-landscape-framework"
    multica_issue_id: "51a89bf9-8955-4ae4-914e-cc6920ffea9a"
    usage: "五轴 rubric、6 维选择性披露向量模型、轻量级判定标准、隐私层级区分"
---

# Research Outline: ERC-7984 机密代币标准深度分析（含 ERC-7945 对比）

## Research Questions

1. ERC-7984 的核心接口设计（IERC7984）相较于 ERC-20 做了哪些根本性变更？operator 模型替代 allowance 模型的设计理由和 DeFi 可组合性影响是什么？
2. `bytes32` 指针机制如何实现技术中立性——使 FHE、ZK、TEE 后端可替换？OZ 参考实现（fhEVM）与 EIP 规范之间的耦合度如何？「技术中立」的边界在哪里（覆盖值级隐私但不覆盖合约逻辑隐私）？
3. ERC-7984 的选择性披露扩展生态（ObserverAccess、Freezable、Restricted、Rwa、Hooked）在 WHI-254 的 6 维披露向量模型中如何定位？其合规能力覆盖范围和缺口是什么？
4. ERC-7984 与 ERC-7945（Ant Group）在接口设计哲学（最大功能 vs 最小互操作）、授权模型（operator vs allowance）、ERC-20 兼容性、生态成熟度上有哪些实质差异？
5. 按 WHI-254 五轴 rubric 评估 ERC-7984 和 ERC-7945，两者在密码学路线、数据维度、信任模型、部署形态和合规-选择性披露上的评分差异是什么？

## Items

### item-1: ERC-7984 核心接口拆解 — IERC7984 完整接口分析

完整分析 ERC-7984 的接口设计，覆盖 EIP 规范（eip-7984.md）定义的所有 methods、events、errors 和 constants。重点拆解以下方面：

**核心函数族**：
- `confidentialBalanceOf(address) → bytes32`：加密余额查询，返回 bytes32 指针
- `confidentialTotalSupply() → bytes32`：加密总供应量
- `confidentialTransfer(address, bytes32)` / `confidentialTransfer(address, bytes32, bytes)`：基础转账（含可选 data 参数用于密码学证明）
- `confidentialTransferFrom(address, address, bytes32)` / `confidentialTransferFrom(address, address, bytes32, bytes)`：委托转账
- `confidentialTransferAndCall` / `confidentialTransferFromAndCall`（各 2 个重载）：带回调的转账

**Operator 模型**：
- `setOperator(address, uint48 until)`：时间限制的 operator 授权，替代 ERC-20 的 approve/allowance
- `isOperator(address holder, address spender) → bool`：查询 operator 状态
- 设计理由：移除加密 allowance 跟踪的复杂性、自然过期、多 operator 并行

**Events**：
- `ConfidentialTransfer(address indexed from, address indexed to, bytes32 indexed amount)`
- `OperatorSet(address indexed holder, address indexed operator, uint48 until)`
- `AmountDisclosed(bytes32 indexed handle, uint256 amount)`：选择性披露事件

**Receiver Callback**：
- `IERC7984Receiver.onConfidentialTransferReceived(address operator, address from, bytes32 amount, bytes data) → bytes32 success`
- 回调失败时的 token 退回机制（类似 ERC-721 safeTransfer 模式）

**Interface ID**：`0x4958f2a4`（ERC-165 支持）

- **Priority**: high
- **Dependencies**: none

### item-2: 技术中立性 — bytes32 指针与可替换后端架构

分析 ERC-7984 如何通过 `bytes32` 指针机制实现技术中立性，使不同隐私后端可替换。

**bytes32 指针机制**：
- 所有金额以 `bytes32` 指针表示（EIP 规范层面）
- 指针的解析（resolution）、操作（manipulation）和存储位置（onchain/offchain）均为实现特定（implementation specific）
- `data` 参数（`bytes calldata`）承载实现特定的密码学证明、访问权限或其他信息

**可替换后端论证**：
- FHE 后端：加密 handle 指向 FHE 密文，运算由 coprocessor 异步执行（Zama fhEVM 参考实现）
- ZK 后端：指针指向 commitment/nullifier，data 参数承载 ZK proof
- TEE 后端：指针指向 enclave 内加密状态，data 参数承载远程证明
- MPC 后端：指针指向分片密文，data 参数承载参与方协议信息

**OZ 参考实现与 EIP 规范的关系**：
- OZ `IERC7984.sol` 使用 Zama fhEVM 类型（`euint64`, `externalEuint64`, `ebool`）而非通用 `bytes32`
- EIP 规范使用通用 `bytes32`，OZ 实现是 FHE 特定的具象化
- 差异：OZ 接口有 `inputProof` 参数（FHE 特定）；EIP 规范使用通用 `data` 参数
- 评估 OZ 实现是否构成事实标准，以及其他后端实现 ERC-7984 的实际可行性

**技术中立性边界**：
- **覆盖**：值级隐私（R1 金额、R2 余额）——ERC-7984 保护 token 转账金额和余额
- **不覆盖**：合约逻辑隐私（R4）——ERC-7984 本身不隐藏智能合约执行逻辑或状态变量。合约逻辑隐私需要执行层方案（如 fhEVM 全栈、TEE 执行环境、Aztec private functions）
- 对齐 WHI-254 隐私层级区分：ERC-7984 = 值级隐私标准，不等同于执行级或状态级隐私

- **Priority**: high
- **Dependencies**: item-1

### item-3: 选择性披露扩展生态评估

评估 ERC-7984 的选择性披露扩展套件，对齐 WHI-254 的 6 维披露向量模型。

**核心扩展分析**：

| 扩展 | 功能 | 合规维度 |
|------|------|---------|
| `ERC7984ObserverAccess` | 账户级 observer 指定，被授权方可解密余额和转账金额 | 选择性披露（R7）、审计（R6） |
| `ERC7984Freezable` | 加密冻结金额，冻结部分不可转账 | 合规执行（R6）、制裁 |
| `ERC7984Restricted` | 账户级转账限制（blocklist/allowlist 模式） | KYC/AML 准入（R6） |
| `ERC7984Rwa` | RWA 合规套件：admin/agent 角色、canTransact、冻结、强制转账、地址恢复 | 全合规（R6、R7） |
| `ERC7984Hooked` | pre/post transfer hooks（IERC7984HookModule） | 可编程合规 |
| `ERC7984ERC20Wrapper` | 明文 ERC-20 ↔ 加密 ERC-7984 双向转换 | 互操作 |
| `ERC7984Omnibus` | 综合账户（omnibus）转账事件，含加密子账户地址 | 机构结算 |
| `ERC7984Votes` | 加密投票权委托和追踪 | 治理 |

**6 维向量映射**：
- Authority: `key-holder`（ObserverAccess 中用户自主设置 observer）
- Trigger: `viewing-key-share`（observer 被授予 ACL 解密权限）
- Payload: `amount`（ObserverAccess 授权观察余额和转账金额）
- Scope: `per-account`（observer 按账户设置）
- Revocability: 待评估——ObserverAccess 支持更换 observer（`setObserver`），但旧 observer 是否仍能访问历史 handle 需要分析
- Leakage: `existence`, `timing`（转账事件公开可见，交易时序可观察；转账金额为加密 handle 不泄露）

**合规能力覆盖与缺口分析**：
- 对照 WHI-254 合规映射表（GDPR、MiCA/Travel Rule、AML/CFT、金融审计）
- 评估 ERC-7984 扩展组合能否满足各合规要求
- 识别缺口：例如 `regulator` authority 是否需要额外扩展？审计日志机制是否完整？

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: ERC-7984 vs ERC-7945 Head-to-Head 对比

对 ERC-7984（Zama/OpenZeppelin）和 ERC-7945（Ant Group）进行系统性 head-to-head 对比，覆盖接口设计、授权模型、ERC-20 兼容性、成熟度和生态。

**接口设计哲学**：
- ERC-7984：最大功能（maximal functionality），从 ERC-20/721/1155/6909 汲取教训，提供完整接口集（8 种 transfer 变体 + callback + operator）
- ERC-7945：最小互操作面（minimum interoperable surface），仅标准化核心操作（balance、transfer、transferFrom、approve、allowance），允许不同证明系统和密文编码共存

**数据类型选择**：
- ERC-7984：`bytes32` 固定长度指针——pointer resolution 为实现特定
- ERC-7945：`bytes memory` 动态长度——直接承载密文/commitment，无需间接指针

**授权模型**：
- ERC-7984：Operator 模型（`setOperator(address, uint48 until)`）——无 allowance 金额，时间限制，多 operator 并行
- ERC-7945：传统 Allowance 模型（`confidentialApprove`/`confidentialAllowance`）——从调用者余额分割 allowance 部分，维持加密 allowance 跟踪。设计与 ERC-20 approve 显著不同：调用 approve 会从余额中拆分出 allowance 部分

**ERC-20 兼容性**：
- ERC-7984：明确不兼容 ERC-20，通过 ERC7984ERC20Wrapper 扩展提供桥接
- ERC-7945：可选的 "Fat Token" 模式——同一合约同时实现 IERC7945 和 IERC20，账户持有明文和加密双重余额

**成熟度对比**：

| 维度 | ERC-7984 | ERC-7945 |
|------|----------|----------|
| EIP 状态 | Draft (2025-07) | Review (2025-05) |
| 提出时间 | 2025-07-03 | 2025-05-09 |
| 发起方 | Zama + OpenZeppelin | Ant Group (Ant International) |
| 参考实现 | OpenZeppelin Confidential Contracts (v0.5.0+, 已审计) | EIP 内嵌 Zether 风格示例，无独立参考实现库 |
| 生态采纳 | Confidential Token Association、Blockscout 集成、GSR OTC 交易 | 无公开生态采纳报告 |
| 审计 | OpenZeppelin 自审计 + BatcherConfidential diff audit | 无公开审计报告 |

**totalSupply 处理**：
- ERC-7984：`confidentialTotalSupply()` 为必须实现的方法
- ERC-7945：`confidentialTotalSupply()` 为可选——因为所有用户可解密 totalSupply 时，mint/burn 金额可通过前后差值推断

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

### item-5: WHI-254 五轴 Rubric 评分 — ERC-7984 与 ERC-7945

按 WHI-254 框架的五轴统一 rubric 对 ERC-7984 和 ERC-7945 进行结构化评分，产出可与 EEA 7 方案横向比较的评分。

**轴 1 — 密码学路线**：
- ERC-7984：技术中立（bytes32 指针），参考实现为 FHE (Zama TFHE)，支持组合其他路线
- ERC-7945：技术中立（bytes memory），无特定后端偏好，但缺乏参考实现验证

**轴 2 — 被保护数据维度**：
- 两者均覆盖：金额 (R1) ● + 余额 (R2) ●
- 两者均不覆盖：身份 (R3) ○、图结构 (R5) ○、业务逻辑 (R4) ○、合约状态 (R4) ○、订单流 (R8) ○
- ERC-7984 和 ERC-7945 均为值级隐私标准，对比 WHI-254 的 Token Ledger (A) 分类

**轴 3 — 信任模型**：
- 两者均为标准层接口，信任模型取决于底层实现
- ERC-7984 参考实现（fhEVM）：Cryptographic Trust (FHE) + Organizational (threshold KMS, coprocessor operator)
- ERC-7945 无参考实现，信任模型完全由实现者决定

**轴 4 — 部署形态**：
- 两者均为合约级标准，部署形态取决于底层链
- ERC-7984 参考实现：fhEVM coprocessor 模式 = bolt-on
- 评估轻量级判定：ERC-7984 作为合约标准本身不触发任何一票否决条件（V1-V4），但底层隐私计算层可能触发

**轴 5 — 合规-选择性披露**：
- ERC-7984：通过扩展套件（ObserverAccess + Freezable + Restricted + Rwa + Hooked）提供丰富的合规-选择性披露能力
- ERC-7945：仅定义核心接口，合规能力完全由实现者自行构建；在 Rationale 中讨论了 audit 支持（审计方冗余加密），但未标准化

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| interface_specification | EIP 规范中定义的函数签名、参数类型、返回值、事件——对照 EIP 原文逐一列出 | item-1, item-4 |
| design_rationale | 设计选择的理由——为什么选择此方案而非替代方案，EIP Rationale section 引用 | item-1, item-2, item-4 |
| technical_neutrality | 与底层密码学/隐私后端的耦合程度评估——接口层 vs 实现层的分离边界 | item-2, item-4 |
| privacy_coverage | 对照 WHI-254 7 项隐私数据维度评估保护范围——覆盖/部分覆盖/不覆盖 | all |
| compliance_vector | 对照 WHI-254 6 维选择性披露向量填充评分——每个维度的标签和证据 | item-3, item-5 |
| ecosystem_maturity | 参考实现状态、审计报告、生态采纳（项目/工具集成）、社区活跃度 | item-4 |
| erc20_compatibility | 与 ERC-20 的兼容性策略——原生兼容/wrapper 桥接/fat token 双余额 | item-1, item-4 |
| rubric_score | WHI-254 五轴 rubric 每轴评分和依据——可与 EEA 7 方案横向比较 | item-5 |
| source_confidence | 结论的证据来源和置信等级——EIP 原文直接引用 / 参考实现代码分析 / 官方文档补充 / 研究者推论 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | ERC-7984 bytes32 指针架构图：展示 EIP 接口层（bytes32）→ 实现层（FHE euint64 / ZK commitment / TEE encrypted state）的分层关系，标注 data 参数在各后端的不同解释 | ascii | item-2 |
| diag-2 | comparison | ERC-7984 vs ERC-7945 接口对比表：覆盖函数名称、参数类型、授权模型、事件、ERC-20 兼容策略、totalSupply 处理——并排列出差异 | ascii | item-4 |
| diag-3 | comparison | ERC-7984 vs ERC-7945 五轴 rubric 评分对比雷达图/表：与 WHI-254 EEA 7 方案评分同口径 | ascii | item-5 |
| diag-4 | hierarchy | ERC-7984 扩展生态层级图：核心接口 IERC7984 → 扩展层（ObserverAccess / Freezable / Restricted / Rwa / Hooked）→ 工具层（ERC20Wrapper / Omnibus / Votes），标注每个扩展对应的合规维度 | ascii | item-3 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | EIP 规范原文（eip-7984.md, eip-7945.md）——所有接口结论须直接引用 EIP 原文 | 2 |
| src-2 | code_analysis | OpenZeppelin Confidential Contracts 源码分析（IERC7984.sol + extensions）——验证 OZ 实现与 EIP 规范的差异 | 3 |
| src-3 | official_docs | Zama/OpenZeppelin 官方文档和博客（技术架构、生态更新）| 2 |
| src-4 | official_docs | Ant Group/Ethereum Magicians ERC-7945 讨论帖和官方说明 | 1 |
| src-5 | internal_research | WHI-254 隐私全景框架（rubric + 披露 taxonomy + 隐私层级区分）——框架引用须包含 commit SHA | 1 |
| src-6 | industry_reports | Confidential Token Association / Blockscout / GSR 等生态采纳证据 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
