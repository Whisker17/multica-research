---
topic: "ERC-7984 机密代币标准深度分析（含 ERC-7945 对比）"
project_slug: "evm-privacy-research"
topic_slug: "erc7984-confidential-token"
github_repo: "Whisker17/multica-research"
round: 1
status: draft

artifact_paths:
  outline: "evm-privacy-research/outlines/erc7984-confidential-token.md"
  draft: "evm-privacy-research/research-sections/erc7984-confidential-token/drafts/round-1.md"
  final: "evm-privacy-research/research-sections/erc7984-confidential-token/final.md"
  index: "evm-privacy-research/research-sections/_index.md"

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23"
  outline_round: 1
  outline_commit: "2e55c62f353d61046aaad08b6f313e38bfc0369d"
  outline_approval_state: "outline-approved by Orchestrator dispatch; outline file frontmatter still says candidate"
  items_covered: ["item-1", "item-2", "item-3", "item-4", "item-5"]
  fields_investigated: ["interface_specification", "design_rationale", "technical_neutrality", "privacy_coverage", "compliance_vector", "ecosystem_maturity", "erc20_compatibility", "rubric_score", "source_confidence"]
  diagrams_produced: ["diag-1", "diag-2", "diag-3", "diag-4"]
  source_requirement_coverage: "EIP-7984/EIP-7945 primary text, OpenZeppelin Confidential Contracts source and audit PDFs, Zama/OpenZeppelin docs, WHI-254 final section covered; public adoption evidence remains partial and is downgraded to reported/unverified where not primary."

multica_issue_id: "f0035b6e-4f0d-4a98-80ad-2f68d46c40be"
branch_name: "research/evm-privacy-research/erc7984-confidential-token"
language: "中文"
mode: "single-issue-composable"
---

# ERC-7984 机密代币标准深度分析（含 ERC-7945 对比）

> 本 section 基于 ERC-7984 / ERC-7945 EIP 原文、OpenZeppelin Confidential Contracts 源码与官方文档、Zama 协议文档，以及 WHI-254 隐私全景框架。访问日期统一为 2026-06-23。外部源码快照：ethereum/ercs `56c2308c8d69e75e417bc2d2d551ff6f463ec18d`；OpenZeppelin/openzeppelin-confidential-contracts `41fe10be35dbcb512d63a334f11bd9ec73a360cf`。

## Executive Summary

ERC-7984 是一个面向「账户模型机密同质化代币」的接口标准：它把所有金额和余额表示为 `bytes32` confidential pointer，因此标准层只约定“金额是一个不透明指针”，而不把指针解析、密文存放、证明系统、KMS 或 coprocessor 绑定到某一种实现。EIP 原文明确说 pointer 的 resolution、operation、location 都是 implementation specific；`data` 参数则给实现方承载 cryptographic proofs、access permissions 或其他后端信息的空间。[source_confidence: EIP-7984 原文直接引用]

这使 ERC-7984 在接口层具备较强技术中立性：FHE 可以把 `bytes32` 解释为密文 handle，ZK 可以把它解释为 commitment/nullifier 或 commitment handle，TEE/MPC 可以把它解释为外部加密状态索引。但这种中立性不是已验证的多后端生态成熟度。当前最具体、最完整的参考实现来自 OpenZeppelin Confidential Contracts，且实现类型是 Zama fhEVM 的 `euint64` / `externalEuint64`，不是 EIP 规范中的裸 `bytes32`。因此结论应写成：**ERC-7984 规范技术中立；主参考实现是 FHE/fhEVM 特定具象化；非 FHE 后端可实现但缺少公开生产级参考实现证据**。[source_confidence: EIP 原文 + OZ 代码分析]

ERC-7984 相对 ERC-20 的关键设计变化是 operator 模型替代 allowance 模型。`setOperator(address,uint48)` 授予 operator 在到期前转出 holder 任意金额的能力，避免对加密 allowance 数量做持续跟踪。它降低了外部隐私计算系统需要维护的授权状态复杂度，但把风险转移为“时间受限的无限授权”。OpenZeppelin 文档也明确警告：operator 在授权期内可能拿走全部 token；且 operator 并不自动拥有余额 handle 的重加密/解密权限，所以不能可靠地“转走全部余额”，只能提交已知金额或已获 ACL 的 handle。[source_confidence: EIP-7984 + OZ docs]

选择性披露方面，ERC-7984 本体只有 `AmountDisclosed(bytes32,uint256)` 事件，披露触发和解密流程由实现决定；真正的合规能力来自 OpenZeppelin 扩展族：`ObserverAccess`、`Freezable`、`Restricted`、`Rwa`、`Hooked`、`ERC20Wrapper`、`Omnibus`、`Votes` 等。这里必须非常谨慎：`ERC7984ObserverAccess` 明确给 observer **permanent ACL access**，它能访问账户余额与转账金额 handle；`setObserver(..., address(0))` 只是把后续 observer 字段清空，并不构成历史 handle 访问权可撤销的证明。`ERC7984Hooked` 更强：代码注释明确把 hook module 视为 trusted contract，且模块授予自身或第三方的 ACL allowance 在 uninstall 后仍可持续。因此 WHI-254 披露向量中的 revocability 应标为 **constrained / historical revocation unverified**，不能写成普通可撤销披露。[source_confidence: OZ 代码直接引用]

与 ERC-7945 head-to-head，ERC-7984 是“更完整的 token 标准接口”：含 metadata、ERC-165、totalSupply、operator、8 个 transfer/callback 变体和 `AmountDisclosed`。ERC-7945 是“最小互操作面”：只要求 `confidentialBalanceOf`、`confidentialTransfer`、`confidentialTransferFrom`、`confidentialApprove`、`confidentialAllowance` 与两个事件；metadata 可选，`confidentialTotalSupply` 可选。ERC-7945 保留类似 ERC-20 的 allowance 语义，但其 `confidentialApprove` 并不是 ERC-20 `approve` 的隐私版，而是把 owner 的 confidential balance 分割成 allowance part 与 left part，之后 spender 从 allowance part 中扣减。[source_confidence: EIP-7945 原文直接引用]

按 WHI-254 五轴 rubric，两者都属于 **Token Ledger / Value-Level Privacy**：强覆盖金额隐私 R1 与余额隐私 R2，不覆盖身份 R3、业务逻辑/合约状态 R4、交易图 R5、订单流 R8。ERC-7984 在合规扩展与工程参考实现上明显更具体，但引入永久 ACL、trusted hooks、fhEVM coprocessor/KMS 运维信任等约束。ERC-7945 接口更小、更接近 ERC-20 互操作习惯，但参考实现、扩展生态和成熟度证据更弱。

---

## Item Findings

## item-1: ERC-7984 核心接口拆解 - IERC7984 完整接口分析

### 1.1 标准定位

ERC-7984 的 abstract 明确把 confidential fungible token 定义为 pointer-based token：所有 amount 都是 confidential pointer；balances 和 transfer amounts 因此保持机密；pointer 指向 onchain 或 offchain 的其他数据，解析和操作方式由实现决定。它不是 ERC-20 的兼容扩展，而是一个从 ERC-20/721/1155/6909 等 token 经验中重做的 confidential token 接口。[source_confidence: EIP-7984 原文]

OpenZeppelin 文档对此的工程表达是：ERC-7984 “similar to ERC-20, but built from the ground up with confidentiality in mind”，所有 balance 和 transfer amount 都是 ciphertext handle，且标准不兼容 ERC-20，而是提供 maximal functionality。[source_confidence: OZ docs]

### 1.2 必需 metadata / ERC-165

ERC-7984 compliant token MUST implement ERC-165，且 `supportsInterface(0x4958f2a4)` 必须返回 true。接口还包含明文 metadata：

| 方法 | 返回 | 隐私含义 |
|---|---:|---|
| `name()` | `string` | 明文 token 名称 |
| `symbol()` | `string` | 明文 symbol |
| `decimals()` | `uint8` | 明文 decimals；OZ 实现默认 6 |
| `contractURI()` | `string` | 合约 metadata URI，建议遵循 ERC-7572 |

这四个 metadata 方法不承载隐私目标；它们提升钱包/浏览器可用性，但会暴露 token 标识与元数据。[source_confidence: EIP-7984 + OZ `IERC7984.sol`]

### 1.3 核心余额与供应量接口

| 方法 | EIP-7984 规范类型 | OZ 参考实现类型 | 结论 |
|---|---|---|---|
| `confidentialTotalSupply()` | `bytes32` | `euint64` | ERC-7984 要求总供应量也以 confidential pointer 表示；OZ 用 FHE encrypted uint64 handle |
| `confidentialBalanceOf(address)` | `bytes32` | `euint64` | 返回 account 的机密余额 handle，而非明文余额 |

注意：EIP-7984 把 totalSupply 作为必需方法；ERC-7945 则只在 Rationale 中提出可选 `confidentialTotalSupply()`，原因是如果所有用户都可解密 totalSupply，mint/burn 前后差值会泄露发行或销毁金额。[source_confidence: EIP-7984/EIP-7945 对照]

### 1.4 Transfer 函数族

ERC-7984 标准化 8 个 transfer 变体，来自三个维度组合：

| 维度 | 选项 | 目的 |
|---|---|---|
| 资金来源 | `confidentialTransfer` / `confidentialTransferFrom` | 自己转账或 operator 代表 holder 转账 |
| 证明/额外数据 | with `bytes data` / without `data` | `data` 承载实现特定 proof、ACL、后端信息 |
| 接收回调 | with `AndCall` / without callback | 合约接收方可在收到 token 后执行回调 |

规范版本使用 `bytes32 amount` 与 `bytes calldata data`。OpenZeppelin 参考实现把这拆成两类重载：使用 `externalEuint64 encryptedAmount + bytes inputProof` 的外部输入版，以及使用 `euint64 amount` 的已授权 handle 版。OZ 的 `inputProof` 是 fhEVM 特定参数，对应 EIP 中更泛化的 `data` 机制。[source_confidence: EIP-7984 + OZ `IERC7984.sol`]

| EIP-7984 方法族 | 必要条件 | 返回值 | 事件 |
|---|---|---|---|
| `confidentialTransfer(to, amount)` | sender 余额足够；实现可在不足时 revert 或转 0 | 实际转移的 pointer | `ConfidentialTransfer` |
| `confidentialTransfer(to, amount, data)` | 同上，`data` 可含 proof | 实际转移的 pointer | `ConfidentialTransfer` |
| `confidentialTransferFrom(from, to, amount)` | caller 必须是 `from` 的 operator | 实际转移的 pointer | `ConfidentialTransfer` |
| `confidentialTransferFrom(from, to, amount, data)` | caller 必须是 operator；`data` 可含 proof | 实际转移的 pointer | `ConfidentialTransfer` |
| `confidentialTransferAndCall(...)` | transfer 后对接收方执行 callback | 实际转移的 pointer | `ConfidentialTransfer` |
| `confidentialTransferFromAndCall(...)` | operator + callback | 实际转移的 pointer | `ConfidentialTransfer` |

OZ `ERC7984._update` 的行为也值得注意：它使用 `FHESafeMath.tryDecrease/tryIncrease` 和 `FHE.select`，如果余额不足或溢出，实际 `transferred` 可能变成 0，而不是像 ERC-20 一样总是 revert。README 也提示：confidential contracts 中很多函数不会像普通合约那样在失败时 revert。[source_confidence: OZ `ERC7984.sol` + README]

### 1.5 Operator 模型

ERC-7984 的 operator 模型由两个函数定义：

```solidity
function isOperator(address holder, address spender) external view returns (bool);
function setOperator(address operator, uint48 until) external;
```

`setOperator` 授权 operator 在 `until` timestamp 前代表 caller 转移任意金额；一个 account 可以同时拥有多个 operator。EIP Rationale 给出的理由是：time-limited operator 可支持 DeFi 集成和自然过期，且不需要外部系统跟踪加密 approval amount。[source_confidence: EIP-7984 Rationale]

工程风险：

| 优点 | 风险 |
|---|---|
| 不需要维护 encrypted allowance；接口和状态更轻 | 授权期间是无限额转出能力 |
| 多 operator 并行，适合 vault、router、settlement agent | 用户需高度信任 operator |
| 到期时间天然降低长期授权风险 | 不能表达“只允许最多转 X”的细粒度额度 |

OZ 文档补充了一个重要边界：operator 不自动拥有其他地址 balance handle 的解密/重加密权限，所以不能直接“转出全部余额”；但是如果 operator 已持有某个 amount handle 或可提交 external input proof，仍可在授权期内转移 holder 资产。[source_confidence: OZ docs]

### 1.6 Events 与 disclosure

| 事件 | 规范含义 | 隐私影响 |
|---|---|---|
| `ConfidentialTransfer(address indexed from, address indexed to, bytes32 indexed amount)` | 每次 confidential transfer 触发，包括 0 value transfer；mint 建议 from=0x0 | `from`、`to`、时间、交易存在性公开；amount 仅为 handle |
| `OperatorSet(address indexed holder, address indexed operator, uint48 until)` | 每次 operator 设置成功触发 | operator 关系与有效期公开 |
| `AmountDisclosed(bytes32 indexed handle, uint256 amount)` | 当某个 pointer amount 通过实现特定机制公开披露时 SHOULD 触发 | 明文 amount 被公开；披露机制不是核心标准的一部分 |

OZ 参考实现还增加了 `AmountDiscloseRequested(euint64,address)`，并通过 `FHE.makePubliclyDecryptable` 与 `FHE.checkSignatures` 处理公开解密请求/证明。这是 fhEVM 具体实现，不是 EIP 的通用要求。[source_confidence: OZ `ERC7984.sol`]

### 1.7 Receiver callback 与退款语义

`AndCall` 函数在转账逻辑完成后，对 `to` 调用：

```solidity
function onConfidentialTransferReceived(address operator, address from, bytes32 amount, bytes calldata data) external returns (bytes32 success);
```

EIP 指定的流程：

1. 如果 `to` 不是合约，callback no-op。
2. 调用 receiver 的 `onConfidentialTransferReceived`。
3. 如果调用 revert，则整体 revert。
4. 如果返回 false pointer，token 合约尝试把 token 退回给原 holder。

OZ 实现给了两个额外安全警告：退款是 best-effort；如果 receiver 在 callback 中转出、销毁或降低余额，即使返回 false，退款也可能是 0；退款还会走普通 transfer validation，因此可能被 hook validation 等原因拦截。[source_confidence: EIP-7984 + OZ `ERC7984.sol`]

### 1.8 item-1 小结

ERC-7984 的核心接口把“机密金额”提升为一等 token 数据类型，并围绕它重建了 transfer、operator、callback 和 disclosure 事件。它适合作为 confidential token 的 anchor standard，但不是 ERC-20 兼容增量；与 ERC-20 生态互操作需要 wrapper 或专门 adapter。

---

## item-2: 技术中立性 - bytes32 指针与可替换后端架构

### 2.1 标准层技术中立性如何成立

ERC-7984 的技术中立性建立在三个接口决策上：

1. **金额统一为 `bytes32` pointer**：标准不规定 pointer 是密文、commitment、offchain key、enclave state id，还是 future privacy mechanism。
2. **pointer resolution / manipulation / location implementation specific**：标准不要求金额数据必须在链上，也不要求链下。
3. **`bytes calldata data` 承载后端信息**：transfer 可附带 proof、access permission 或隐私机制特定信息。

因此 ERC-7984 的最小互操作承诺是：应用可以调用同一套 token 接口，但是否能验证 pointer、解读 proof、请求解密、处理失败，取决于具体实现后端。[source_confidence: EIP-7984 原文]

### 2.2 diag-1: bytes32 指针分层架构图

```text
应用 / 钱包 / DEX / 结算系统
        |
        | calls IERC7984
        v
+---------------------------------------------------+
| ERC-7984 interface layer                          |
| - amount: bytes32 pointer                         |
| - data: bytes proof / permission / backend info   |
| - events: ConfidentialTransfer, AmountDisclosed   |
+---------------------------------------------------+
        |
        | implementation-specific interpretation
        v
+-------------------+-------------------+-------------------+-------------------+
| FHE backend       | ZK backend        | TEE backend       | MPC/backend       |
| euint64 handle    | commitment handle | enclave state id  | shared ciphertext |
| inputProof/ACL    | zk proof/data     | attestation/data  | protocol metadata |
| KMS/coprocessor   | verifier/nullifier| enclave service   | committee service |
+-------------------+-------------------+-------------------+-------------------+
        |
        v
隐私目标: token amount / balance value-level privacy
非目标: 合约业务逻辑、合约状态整体、身份、交易图、mempool/order-flow
```

### 2.3 FHE / ZK / TEE / MPC 后端可行性

| 后端 | `bytes32` 可表示什么 | `data` 可承载什么 | 可行性判断 |
|---|---|---|---|
| FHE / fhEVM | FHE ciphertext handle；OZ 中为 `euint64` handle | external input proof、ACL 授权、decryption proof | 已有 OZ 参考实现；成熟度最高 |
| ZK | commitment id、encrypted note id、nullifier/commitment pair handle | transfer validity proof、range proof、membership proof | 接口上可行；缺少公开 ERC-7984 ZK 参考实现 |
| TEE | enclave 内部加密状态索引或 sealed-state handle | remote attestation、session proof、policy proof | 接口上可行；信任边界转向硬件与 enclave operator |
| MPC | 分片密文 handle 或 threshold decryption request id | committee signature、session transcript、DKG/KMS metadata | 接口上可行；同步性、延迟和 liveness 需实现自证 |

关键结论：ERC-7984 的规范中立性并不自动带来“后端可替换的用户体验”。如果钱包/DEX 需要生成 proof、请求 reencryption 或处理 decryption，仍需知道后端 SDK、ACL 与密钥管理流程。接口只统一 token 合约方法，不统一隐私计算运维层。[source_confidence: EIP 原文 + 研究者推论]

### 2.4 OZ 参考实现与 EIP 规范的耦合度

OpenZeppelin `IERC7984.sol` 是 “Draft interface for a confidential fungible token standard utilizing the Zama FHE library”。它与 EIP 的差异如下：

| 维度 | EIP-7984 | OZ Confidential Contracts |
|---|---|---|
| amount 类型 | `bytes32` | `euint64` / `externalEuint64` |
| proof 参数 | 通用 `bytes data` | `bytes inputProof`；由 `FHE.fromExternal` 处理 |
| public disclosure | `AmountDisclosed(bytes32,uint256)` | `AmountDisclosed(euint64,uint64)` + `AmountDiscloseRequested` |
| ACL | 标准不定义 | 深度依赖 `FHE.allow`、`allowTransient`、`isAllowed` |
| total supply | `bytes32` | `euint64` |
| decimals | 无推荐值 | 默认 6 |

这说明 OZ 实现不是 EIP 的“泛型 bytes32 实现”，而是把 ERC-7984 映射到 Zama fhEVM 类型系统。它在工程上最可用，但也会把集成方带入 fhEVM coprocessor、Gateway、KMS、ACL 等体系。[source_confidence: OZ `IERC7984.sol`, `ERC7984.sol`, OpenZeppelin docs]

### 2.5 Zama fhEVM 部署信任边界

Zama 协议文档把 FHE on blockchain 架构拆为 host contracts、coprocessors、Gateway、KMS、relayer 等组件：host contracts 运行在 EVM 链上并触发加密计算；coprocessors 验证 encrypted inputs、运行 FHE computation 并提交结果；Gateway 协调 ACL、跨链 ciphertext 与 coprocessor/KMS；KMS 是 threshold MPC 网络，负责 FHE key generation/rotation 和 verifiable decryption。[source_confidence: Zama Protocol docs, 2026-06-23]

对 ERC-7984 评估的含义：

| 组件 | 对 ERC-7984 的作用 | 信任/运维风险 |
|---|---|---|
| Host contracts | token state、operator、events、ACL entrypoint | 合约升级、hook、role 配置风险 |
| Coprocessor | 执行 FHE 运算，返回 encrypted result | liveness、正确性证明、operator 集中度 |
| Gateway | 协调 ACL、ciphertext、decryption request | 中央协调层可用性和策略正确性 |
| KMS | threshold key management / decryption | 阈值假设、密钥轮换、安全审计 |
| Relayer/SDK | 用户 proof/decryption 请求入口 | 集成复杂度、UX、可用性 |

因此在 WHI-254 信任模型轴上，ERC-7984 标准本身是 interface-level；OZ/fhEVM 路径则是 **Cryptographic Trust (FHE) + Organizational/Operational Trust (coprocessor, Gateway, KMS operators)**。[source_confidence: Zama docs + WHI-254 rubric 推论]

### 2.6 技术中立性的边界：只覆盖值级隐私

ERC-7984 覆盖的是 token ledger 中的 amount/balance 值级隐私：

| WHI-254 数据维度 | ERC-7984 覆盖 | 说明 |
|---|---:|---|
| R1 交易金额 | 强 | `ConfidentialTransfer.amount` 是 handle |
| R2 账户余额 | 强 | `confidentialBalanceOf` 返回 handle |
| R3 身份 | 不覆盖 | `from/to/operator` 地址公开 |
| R4 业务逻辑/合约状态 | 不覆盖 | token 逻辑、hook 是否存在、restriction 状态等仍由合约结构暴露；底层 fhEVM 可做更广泛加密计算，但 ERC-7984 本体不是执行隐私标准 |
| R5 交易图 | 不覆盖 | 转账双方和时序公开 |
| R6 合规可审计 | 部分 | 取决于 Observer/Rwa/Hooked 等扩展和实现 |
| R7 选择性披露 | 部分 | 本体只有 `AmountDisclosed` 事件；机制靠扩展 |
| R8 订单流/mempool | 不覆盖 | calldata/交易提交阶段不由 ERC-7984 保护 |

结论：ERC-7984 是 confidential token standard，不是 private smart-contract execution standard。把它描述为“合约逻辑隐私方案”会越界。[source_confidence: WHI-254 final + EIP-7984 推论]

---

## item-3: 选择性披露扩展生态评估

### 3.1 扩展生态总览

OpenZeppelin Confidential Contracts 在 ERC-7984 核心之上提供多个扩展，覆盖观察、冻结、限制、RWA 角色、hooks、wrapper、omnibus 事件、votes 等能力。

### diag-4: ERC-7984 扩展生态层级图

```text
IERC7984 / ERC7984 core
  |-- balances, transfers, operators, callbacks, AmountDisclosed
  |
  +-- Compliance / disclosure extensions
  |     |-- ERC7984ObserverAccess
  |     |     |-- per-account observer
  |     |     |-- permanent ACL access to balance and transfer handles
  |     |
  |     |-- ERC7984Freezable
  |     |     |-- confidential frozen amount
  |     |     |-- transfer amount is clipped to unfrozen balance
  |     |
  |     |-- ERC7984Restricted
  |     |     |-- blocklist by default
  |     |     |-- can be overridden into allowlist
  |     |
  |     |-- ERC7984Rwa
  |     |     |-- admin / agent roles
  |     |     |-- mint, burn, freeze, pause, block, recover, force transfer
  |     |
  |     +-- ERC7984Hooked
  |           |-- trusted pre/post transfer modules
  |           |-- module ACL grants may persist after uninstall
  |
  +-- Interop / utility extensions
        |-- ERC7984ERC20Wrapper: ERC-20 <-> ERC-7984 wrap/unwrap
        |-- ERC7984Omnibus: encrypted omnibus sub-account events
        |-- ERC7984Votes: confidential voting units / delegation
        +-- BatcherConfidential: wrapper-to-wrapper routing primitive
```

### 3.2 ObserverAccess：账户级观察者，不是普通可撤销披露

`ERC7984ObserverAccess` 的注释写明：每个 account 可以添加一个 observer，该 observer 被给予对该账户 transfer and balance amounts 的 **permanent ACL access**；observer 可随时添加或移除。代码行为：

| 行为 | 代码含义 | 披露向量 |
|---|---|---|
| `setObserver(account,newObserver)` | account 可设置 observer；旧 observer 只能 abdicate 到 `address(0)` | authority = key-holder/account |
| 设置新 observer 时 | 如果已有 balance handle，则 `FHE.allow(balanceHandle,newObserver)` | payload = balance |
| 每次 `_update` 后 | 对 from/to observer 授予 `confidentialBalanceOf` 和 `transferred` handle ACL | payload = balance + transfer amount |
| 移除 observer | `_observers[account] = address(0)`，没有撤销历史 handle ACL 的代码 | revocability = future-only / historical unverified |

因此，ObserverAccess 的准确表述是：它提供 **per-account、user-controlled、ACL-based disclosure**，适合审计员、会计、托管操作方等角色查看后续余额和转账金额；但旧 observer 是否不能再访问历史 handle，源码没有证明。若底层 ACL 没有可验证撤销语义，历史披露应视为永久。[source_confidence: OZ `ERC7984ObserverAccess.sol`]

### 3.3 Hooked：可编程合规，但 hook module 是 trusted contract

`ERC7984Hooked` 支持安装多个 module，在 transfer 前运行 `preTransfer`，transfer 后运行 `postTransfer`。如果任何 module 返回 encrypted false，转账金额会变成 0；如果 module revert，则整笔交易 revert。

关键风险来自源码注释：hook modules 是 trusted contracts，它们能访问 token 可访问的 private state；这种任意 ACL access 允许 module 给自身或任何其他地址授予任何 handle 的查看权限；而 module 授予的 ACL allowances 即使在 module uninstall 后仍然 persist。[source_confidence: OZ `ERC7984Hooked.sol`]

这意味着 Hooked 不能简单被写作“可卸载、可撤销的合规模块”。更准确的风险标签：

| 维度 | 结论 |
|---|---|
| Authority | token admin / module manager |
| Trigger | transfer pre/post hook |
| Payload | module 可访问 token 可访问的任意 handle |
| Scope | global per-token module，影响所有 transfer |
| Revocability | module list 可卸载；已授予 ACL allowance 不保证撤销 |
| Leakage | 取决于 module；最坏情况可扩散给任意地址 |

### 3.4 Freezable / Restricted / Rwa

`ERC7984Freezable` 对每个账户保存 `confidentialFrozen(account)`，并在 `_update` 时用 encrypted comparison 将转账金额限制为不超过 unfrozen balance。失败语义不是 revert，而是 amount 被选择为 0，这与 confidential token 的“不泄露失败原因”目标一致，但对上层 UX 和审计提出额外要求。[source_confidence: OZ `ERC7984Freezable.sol`]

`ERC7984Restricted` 默认是 blocklist：`canTransact(account)` 返回 `getRestriction(account) != BLOCKED`。文档注释指出开发者可以 override 成 allowlist。该扩展暴露了某个 account 的 restriction 状态（DEFAULT/BLOCKED/ALLOWED），属于合规准入信息泄露。[source_confidence: OZ `ERC7984Restricted.sol`]

`ERC7984Rwa` 组合了 Freezable、Restricted、Pausable、AccessControl 和 Multicall，引入 admin/agent 角色。agent 可以 mint/burn、pause/unpause、block/unblock、设置 frozen amount、recover lost address、force transfer。源码明确说 force transfer / recovery 可绕过 pause 和部分 restriction checks，但 frozen tokens 仍需先解冻。RWA 扩展覆盖了机构 token 常见合规动作，但信任模型转为强 admin/agent 权限，适合 permissioned asset issuer，不适合追求最小治理信任的公共 DeFi token。[source_confidence: OZ `ERC7984Rwa.sol`]

### 3.5 ERC20Wrapper / Omnibus / Votes

`ERC7984ERC20Wrapper` 将明文 ERC-20 包装为 ERC-7984 token。wrap 是明文 ERC-20 transfer-in + confidential mint；unwrap 需要公开解密 burned amount 后再转出底层 ERC-20。源码警告 fee-on-transfer / deflationary token 不支持；unwrap request id 直接使用 ciphertext 也带有 ciphertext uniqueness 假设。[source_confidence: OZ `ERC7984ERC20Wrapper.sol`]

`ERC7984Omnibus` 为 omnibus account 场景扩展事件，记录 encrypted sender/recipient 子账户。源码注释指出 `omnibusFrom` 与 `omnibusTo` 会获得 sender/recipient 的 permanent ACL allowances；这对机构综合账户结算有用，但同样扩大了访问权持久性。[source_confidence: OZ `ERC7984Omnibus.sol`]

`ERC7984Votes` 将 confidential balance 映射为 confidential voting units，并与 `VotesConfidential` 结合做投票权委托。治理场景下需要注意 delegatee 是否能从 voting units 变化推断余额；历史 audit 中也曾列出“delegatees can deduce balances of delegators”的高风险/中高风险相关问题，具体是否已修复需按版本审计报告追踪。[source_confidence: OZ `ERC7984Votes.sol` + 2025-07 audit PDF]

### 3.6 WHI-254 六维选择性披露向量

| 机制 | Authority | Trigger | Payload | Scope | Revocability | Leakage |
|---|---|---|---|---|---|---|
| `AmountDisclosed` | handle holder / implementation-specific | explicit public disclosure request/proof | amount | per-handle | irreversible once emitted | amount becomes public |
| `ObserverAccess` | account / existing observer abdication | `setObserver` + transfer/update | balance + transfer amount | per-account | future-only; historical ACL revocation unverified | observer learns values; tx graph still public |
| `Hooked` | token admin/module manager | every transfer pre/post | any token-accessible handle in worst case | per-token/global | module uninstall does not revoke granted ACL | module or delegated address may learn values |
| `Rwa` agent | admin-appointed agent | compliance action | mint/burn/freeze/force transfer amount | per-token/admin domain | role revocation future-only; prior ACL grants unverified | issuer/agent learns action amounts |
| `Wrapper` unwrap | holder/operator | unwrap finalization | unwrap amount | per-unwrap request | public once finalized | amount is disclosed to release ERC-20 |

对照 WHI-254，ERC-7984/OZ 的披露模型不是“监管方只在需要时看一笔交易”的简单 viewing key，而是一组 ACL 与 role-based 合规动作。它的优点是合规模块丰富；缺点是访问权持久性和审计可验证性不足，需要额外流程证明谁在何时获得、保留、撤销了 handle access。[source_confidence: WHI-254 + OZ code]

### 3.7 合规能力覆盖与缺口

| 合规需求 | ERC-7984/OZ 覆盖 | 缺口 |
|---|---|---|
| AML/CFT 地址准入 | `Restricted` blocklist/allowlist；`Rwa` agent block/unblock | 身份/KYC registry 不是核心标准；需外部 identity layer |
| 金融审计 | `ObserverAccess`、`AmountDisclosed`、agent ACL | 历史 handle 访问不可撤销性需治理/审计日志约束 |
| 制裁/冻结 | `Freezable`、`Rwa` pause/block/freeze/force transfer | admin/agent 权限很强；需多签/治理/审计 |
| Travel Rule | 可通过 observer/agent 披露 amount | 对手方身份仍是地址；Travel Rule payload 不标准化 |
| GDPR/隐私最小化 | 默认 amount/balance 加密 | observer/hook ACL 可能形成长期过度披露 |
| 机构 omnibus | `Omnibus` 扩展 | 子账户身份/地址 handle 的 ACL 持久性需单独治理 |

---

## item-4: ERC-7984 vs ERC-7945 Head-to-Head 对比

### 4.1 标准状态与定位

| 维度 | ERC-7984 | ERC-7945 |
|---|---|---|
| 标题 | Confidential Fungible Token | Confidential Transactions Supported Token |
| EIP 状态 | Draft | Review |
| created | 2025-07-03 | 2025-05-09 |
| authors | Zama/OpenZeppelin 相关作者 | Ant Group / Ant International 相关作者 |
| requires | ERC-165 | ERC-20 |
| 核心目标 | account-based confidential fungible token via pointers | confidential transaction token minimum interoperable surface |
| 隐私对象 | balances + transfer amounts | balances + transfer values |

ERC-7945 Motivation 中直接把自己与 ERC-7984 对比：ERC-7984 使用 `bytes32` pointers 表示 confidential balances，而 ERC-7945 只标准化 account-based model 的 minimum interoperable surface，允许不同 proof systems、ciphertext encodings、compliance workflows 在同一接口后共存。[source_confidence: EIP-7945 原文]

### 4.2 diag-2: 接口对比表

```text
+-------------------------+------------------------------+------------------------------+
| Category                | ERC-7984                     | ERC-7945                     |
+-------------------------+------------------------------+------------------------------+
| Status                  | Draft                        | Review                       |
| Type carrier            | bytes32 pointer              | bytes memory ciphertext/proof|
| Interface detection     | ERC-165, id 0x4958f2a4       | no ERC-165; requires ERC-20  |
| Metadata                | required name/symbol/decimals| optional IERC7945Metadata    |
| Balance                 | confidentialBalanceOf -> b32 | confidentialBalanceOf -> bytes|
| Total supply            | required confidentialTotal   | optional in Rationale        |
| Transfer                | 8 variants + callbacks       | transfer / transferFrom      |
| Proof/data              | bytes data generic           | bytes _proof                 |
| Delegation              | time-bound operator          | encrypted allowance          |
| Approval amount         | none                         | confidentialApprove          |
| Event transfer          | from,to,amount handle        | spender,from,to,value bytes  |
| Disclosure event        | AmountDisclosed              | no standard disclosure event |
| ERC-20 compatibility    | not ERC-20; wrapper needed   | can be fat token with ERC-20 |
+-------------------------+------------------------------+------------------------------+
```

### 4.3 数据类型：`bytes32` vs `bytes memory`

ERC-7984 选择固定长度 `bytes32` pointer。这适合 handle-based 系统：链上事件和状态只存 pointer，实际密文或证明材料可以在其他位置。缺点是钱包/应用如果只看到 `bytes32`，并不知道它如何解码或验证。

ERC-7945 使用 `bytes memory`，更像直接承载 ciphertext、commitment 或 proof-specific serialized value。优点是不同编码长度可变；缺点是 calldata/event 体积和解析格式完全交给实现，互操作层仍需知道编码约定。[source_confidence: EIP-7984/EIP-7945 原文 + 推论]

### 4.4 授权模型：operator vs encrypted allowance

ERC-7984 的 operator 是 unlimited-by-amount、limited-by-time。EIP 设计理由是减少外部系统跟踪 approval amount 的负担。它更适合 router、vault、batcher、settlement agent 等“被授权操作一段时间”的模式。[source_confidence: EIP-7984 Rationale]

ERC-7945 则保留 allowance/approve 概念，但注意它不是 ERC-20 approve 的简单加密版。`confidentialApprove` 会把 caller 的 confidential balance 拆成 allowance part 和 left part；spender 通过 `confidentialTransferFrom` 从 allowance part 多次扣减，直到该 part 归零或 spender 停止使用。再次 approve 会先把现有 allowance part 合并回 owner confidential balance，再用新 `_confidentialValue` 覆盖 allowance part。[source_confidence: EIP-7945 原文]

| 维度 | ERC-7984 operator | ERC-7945 confidential allowance |
|---|---|---|
| 授权粒度 | 时间限制，无金额限制 | 金额限制，encrypted allowance |
| 状态复杂度 | 低：holder->operator->until | 高：owner/spender 的 encrypted allowance part |
| 用户风险 | 授权期内可被拿走任意金额 | proof/allowance 状态复杂，重 approve 语义与 ERC-20 不同 |
| DeFi router 适配 | 类似 session approval | 类似 ERC-20 allowance，但需处理加密余额拆分 |
| 隐私泄露 | operator 关系公开，金额不公开 | allowance ciphertext 公开，实际额度加密 |

### 4.5 ERC-20 兼容策略

ERC-7984 明确不是 ERC-20 compliant。OZ 提供 `ERC7984ERC20Wrapper`，通过 lock/mint 或 burn/public-decrypt/release 把明文 ERC-20 与 confidential ERC-7984 双向转换。这个策略让 ERC-20 互操作位于 wrapper 层，而不是核心 token 层。[source_confidence: OZ docs + wrapper 源码]

ERC-7945 的 requires 是 ERC-20，并在 Rationale 中描述 “Fat Token”：同一 token 合约可以同时实现 ERC-20 和 IERC7945，让账户同时持有明文余额和 confidential balance，并提供 hide/reveal 双向转换。它的互操作哲学更贴近现有 ERC-20 生态，但也把明文/密文双余额管理复杂度留给实现方。[source_confidence: EIP-7945 原文]

### 4.6 成熟度与生态证据

| 维度 | ERC-7984 | ERC-7945 |
|---|---|---|
| 标准成熟度 | Draft；有 Zama ERC-7984 landing page 与 OpenZeppelin reference implementation | Review；EIP 原文提供接口和 Zether-style 示例说明 |
| 参考实现 | OpenZeppelin Confidential Contracts，fhEVM-specific；repo HEAD `41fe10b...` | 未找到同等独立官方参考实现库 |
| 审计 | OZ repo 有 `audits/2025-05-v0.1.pdf`, `2025-07-v0.2.pdf`, `2025-11-v0.3.pdf`, `2026-01-v0.3.1.pdf`, `2026-03-v0.4.pdf`；但 docs 同时声明 moving repo code as-is、无正式保证、无 Immunefi 覆盖 | 未找到公开官方审计报告 |
| Adoption | Zama 官网 `/erc-7984` 宣称面向 financial institutions，支持 encrypted balances/confidential transfers/programmable compliance/verifiability；Zama ecosystem 页面列出 live on testnet/mainnet 的 app/infra 生态。具体 Blockscout/GSR/CTA 等采纳需逐条主证据补强 | 未找到公开生态采纳证据 |
| 工程复杂度 | 高：FHE SDK、ACL、Gateway、KMS、coprocessor、decryption proof | 中高：proof system 自定义；接口较小但实现缺口更大 |

对 outline 中列出的 “Confidential Token Association、Blockscout integration、GSR OTC、BatcherConfidential diff audit” 必须拆开处理：

| 声明 | 本轮证据状态 | 本 draft 处理 |
|---|---|---|
| BatcherConfidential diff audit | OZ repo 中存在 `audits/2026-03-v0.4.pdf`，标题为 “BatcherConfidential and Diff Audit” | 可作为 primary evidence 引用 |
| OpenZeppelin release audits | OZ repo 中存在多份 audit PDF；README 说 npm install latest audited release | 可引用，但不得说 current HEAD 完全 audited |
| Confidential Token Association | 本轮未拿到稳定 primary URL；搜索结果存在但未能打开验证 | 降级为未验证，不计入成熟度得分 |
| Blockscout integration | 本轮未拿到 primary URL | 降级为未验证 |
| GSR OTC | 本轮未拿到 primary URL；不写入成熟度正向结论 | 降级为 reported/unverified |

### 4.7 ERC-7984 vs ERC-7945 结论

| 选型问题 | 更偏 ERC-7984 | 更偏 ERC-7945 |
|---|---|---|
| 需要完整 token UX（callback/operator/wrapper/RWA） | 是 | 否 |
| 希望沿用 ERC-20 approve/allowance 心智 | 否 | 是 |
| 希望接口尽可能小、证明系统可自由编码 | 部分 | 是 |
| 希望有可读参考实现与扩展代码 | 是 | 否/证据不足 |
| 希望避免无限 operator 授权 | 否 | 是 |
| 希望避免 encrypted allowance 状态复杂度 | 是 | 否 |
| 机构/RWA 合规模块 | OZ 扩展较完整 | 需自建 |

---

## item-5: WHI-254 五轴 Rubric 评分 - ERC-7984 与 ERC-7945

### 5.1 评分口径

沿用 WHI-254 五轴：密码学路线、被保护数据维度、信任模型、部署形态、合规-选择性披露。符号：

- `●` 强覆盖/明确能力
- `◐` 部分覆盖/依赖实现
- `○` 不覆盖或无标准化能力
- `?` 证据不足

### diag-3: 五轴 rubric 对比

```text
+----------------------+---------------------------+----------------------------+
| Rubric Axis          | ERC-7984                  | ERC-7945                   |
+----------------------+---------------------------+----------------------------+
| 1. Crypto route      | ● interface-neutral;      | ◐ interface-neutral;       |
|                      |   FHE reference impl      |   no strong ref impl       |
| 2. Data dimension    | ● R1/R2; ○ R3/R4/R5/R8   | ● R1/R2; ○ R3/R4/R5/R8    |
| 3. Trust model       | ◐ std neutral; fhEVM      | ? implementation-defined   |
|                      |   needs coprocessor/KMS   |                            |
| 4. Deployment shape  | ◐ contract + coprocessor  | ◐ contract-level standard  |
| 5. Compliance/discl. | ● rich OZ extensions,     | ◐ audit discussed, not     |
|                      |   but revocation limited  |   standardized             |
+----------------------+---------------------------+----------------------------+
```

### 5.2 轴 1 - 密码学路线

| 标准 | 评分 | 依据 |
|---|---:|---|
| ERC-7984 | `●/◐` | 规范层使用 `bytes32`，明确技术中立；OZ 参考实现基于 Zama fhEVM/FHE，工程证据强；非 FHE 后端缺少公开参考实现 |
| ERC-7945 | `◐` | 使用 `bytes memory` 和自定义 proof，技术中立；EIP 示例偏 Zether/ElGamal；缺少独立官方实现和扩展生态 |

### 5.3 轴 2 - 被保护数据维度

| 数据维度 | ERC-7984 | ERC-7945 | 说明 |
|---|---:|---:|---|
| R1 金额 | `●` | `●` | transfer value/amount 加密 |
| R2 余额 | `●` | `●` | confidential balance |
| R3 身份 | `○` | `○` | 地址公开 |
| R4 业务逻辑/合约状态 | `○` | `○` | 标准层不隐藏执行逻辑；底层 FHE/TEE 另论 |
| R5 交易图 | `○` | `○` | from/to 公开 |
| R6 合规可审计 | `◐/●` | `◐` | 7984 依赖 OZ 扩展；7945 只在 Rationale 讨论 |
| R7 选择性披露 | `◐/●` | `◐` | 7984 有 AmountDisclosed/Observer/Hooked/RWA；撤销性受限 |
| R8 订单流 | `○` | `○` | 均不覆盖 mempool/order-flow |

### 5.4 轴 3 - 信任模型

ERC-7984 标准本身不规定信任模型；实现可采用 FHE/ZK/TEE/MPC。OZ/fhEVM 路线的实际信任模型是：

- Cryptographic Trust：FHE ciphertext 与 encrypted computation。
- Organizational/Operational Trust：coprocessor、Gateway、KMS/threshold operators、relayer、合约 admin/hook module。
- Application Trust：operator、observer、agent、module manager 的权限配置。

ERC-7945 的信任模型更空：接口允许 Zether-style proof，也允许其他 proof/ciphertext encoding。它的抽象更中立，但成熟度和可验证实现更少。[source_confidence: EIP + Zama/OZ docs + WHI-254 推论]

### 5.5 轴 4 - 部署形态与轻量级判定

| 判定条件 | ERC-7984/OZ fhEVM | ERC-7945 |
|---|---|---|
| V1 新链/新 VM | 标准本身不需要；fhEVM 需要支持 coprocessor/host contracts 的链环境 | 标准本身不需要 |
| V2 新桥 | 不需要；wrapper 是 token-level adapter，不是 L2 bridge | 不需要 |
| V3 全节点运维 | token 使用者不需要；隐私后端 operator 需要 infra | 取决于实现 |
| V4 硬分叉 | 不需要 | 不需要 |
| 轻量级结论 | 标准层轻量；OZ/fhEVM 部署是“合约 + 隐私计算后端”，不等同纯合约库 | 标准层轻量；实现复杂度未知 |

对 Mantle：ERC-7984 更像“token privacy bolt-on 标准”，但如果采用 Zama fhEVM，需要评估 Mantle 是否支持对应 host contracts/Gateway/KMS/coprocessor 接入、finality/latency、decryption proof 验证和运维 SLA。ERC-7945 作为接口标准无法直接给出 Mantle 集成路径，除非选择或自建具体 ZK/FHE/TEE 实现。

### 5.6 轴 5 - 合规-选择性披露

ERC-7984/OZ 得分更高，但必须附带 caveat：

| 能力 | 分数 | Caveat |
|---|---:|---|
| 公开披露事件 | `●` | `AmountDisclosed` 公开后不可逆 |
| per-account observer | `●` | permanent ACL；历史撤销未验证 |
| freeze/restrict | `●` | restriction 状态公开；失败可能转 0 |
| RWA admin/agent | `●` | 强特权角色，需要治理/审计 |
| hook compliance | `◐/●` | trusted module；ACL grants persist after uninstall |
| audit trail | `◐` | 事件存在，但 handle ACL 权限变更日志不完整标准化 |

ERC-7945 得分较低但更简单：它在 Rationale 中讨论 audit，可通过把 transfer value 冗余加密给 auditors 来支持审计，也可选 confidentialTotalSupply 给小范围 party 解密；但这些不是标准化接口或扩展。[source_confidence: EIP-7945 Rationale]

### 5.7 总评分

| 标准 | 密码学路线 | 数据维度 | 信任模型 | 部署形态 | 合规披露 | 总体结论 |
|---|---:|---:|---:|---:|---:|---|
| ERC-7984 | 4/5 | 2/5 | 3/5 | 3/5 | 4/5 | 最适合作为 Mantle confidential token anchor standard；需补强 ACL 撤销/审计与后端运维评估 |
| ERC-7945 | 3/5 | 2/5 | 2/5 | 3/5 | 2/5 | 更小的 ERC-20-like confidential token 接口；适合观察 Ant Group 路线，但短期工程落地证据弱 |

评分解释：数据维度低不是因为金额/余额能力弱，而是因为两者都只覆盖 WHI-254 全隐私需求中的 token value-level 子集。ERC-7984 总分高来自参考实现和扩展生态，而非隐私维度更广。

---

## Diagrams

### diag-1: ERC-7984 bytes32 指针架构图

见 item-2 §2.2。

### diag-2: ERC-7984 vs ERC-7945 接口对比表

见 item-4 §4.2。

### diag-3: 五轴 rubric 对比

见 item-5 §5.1。

### diag-4: ERC-7984 扩展生态层级图

见 item-3 §3.1。

---

## Source Coverage

| ID | Source requirement | Coverage | Evidence |
|---|---|---|---|
| src-1 | EIP 规范原文（7984/7945） | 满足 | `https://eips.ethereum.org/EIPS/eip-7984`, `https://eips.ethereum.org/EIPS/eip-7945`; ethereum/ercs commit `56c2308c8d69e75e417bc2d2d551ff6f463ec18d` |
| src-2 | OZ Confidential Contracts 源码分析 | 满足 | OpenZeppelin repo commit `41fe10be35dbcb512d63a334f11bd9ec73a360cf`; files: `IERC7984.sol`, `ERC7984.sol`, `ERC7984ObserverAccess.sol`, `ERC7984Hooked.sol`, `ERC7984Freezable.sol`, `ERC7984Restricted.sol`, `ERC7984Rwa.sol`, `ERC7984ERC20Wrapper.sol`, `ERC7984Omnibus.sol`, `ERC7984Votes.sol` |
| src-3 | Zama/OZ 官方文档和博客 | 部分满足 | Zama docs `https://docs.zama.org/protocol/protocol/overview`, `https://docs.zama.org/protocol/solidity-guides/getting-started/overview`; Zama landing `https://www.zama.org/erc-7984`; OZ docs `https://docs.openzeppelin.com/confidential-contracts`, raw docs content |
| src-4 | Ant Group / Ethereum Magicians ERC-7945 讨论 | 部分满足 | EIP-7945 includes Magicians discussion URL `https://ethereum-magicians.org/t/interface-of-confidential-transactions-supported-token-contract/23586`; not deeply scraped in this round |
| src-5 | WHI-254 隐私全景框架 | 满足 | `evm-privacy-research/research-sections/privacy-landscape-framework/final.md`, main integration commit `5d6c94f6877227aadaf731852a08f46da1213c54` |
| src-6 | CTA / Blockscout / GSR adoption evidence | 未满足/降级 | No primary, stable URLs verified in this round; removed from positive maturity claims except as unverified reported items |

### Primary source index

| Source | URL / path | Version / commit | Access date | Used for |
|---|---|---|---|---|
| ERC-7984 EIP | https://eips.ethereum.org/EIPS/eip-7984 | status Draft; ethereum/ercs `56c2308...` | 2026-06-23 | Interface, rationale, events, callback, tech-neutrality |
| ERC-7945 EIP | https://eips.ethereum.org/EIPS/eip-7945 | status Review; ethereum/ercs `56c2308...` | 2026-06-23 | Interface, allowance semantics, totalSupply rationale, audit rationale, fat token |
| OpenZeppelin Confidential Contracts | https://github.com/OpenZeppelin/openzeppelin-confidential-contracts | `41fe10be35dbcb512d63a334f11bd9ec73a360cf` | 2026-06-23 | Reference implementation and extensions |
| OpenZeppelin docs | https://docs.openzeppelin.com/confidential-contracts | docs raw page fetched 2026-06-23 | 2026-06-23 | Security caveat, fhEVM usage, no formal guarantee for moving repo code |
| Zama protocol docs | https://docs.zama.org/protocol/protocol/overview | page last-updated shown as 2026-01-21 in fetched HTML | 2026-06-23 | fhEVM architecture: host contracts, coprocessor, Gateway, KMS |
| Zama ERC-7984 landing | https://www.zama.org/erc-7984 | Webflow page published 2026-06-19 in fetched HTML | 2026-06-23 | Public positioning and ecosystem messaging |
| OZ audits | `audits/*.pdf` in OZ repo | 2025-05 v0.1; 2025-07 v0.2; 2025-11 v0.3; 2026-01 v0.3.1; 2026-03 v0.4 | 2026-06-23 | Release/diff audit evidence, not blanket current-HEAD assurance |
| WHI-254 framework | `evm-privacy-research/research-sections/privacy-landscape-framework/final.md` | `5d6c94f6877227aadaf731852a08f46da1213c54` | local repo | Rubric, disclosure vector, privacy dimensions |

---

## Gap Analysis

| Gap | Impact | Treatment in this draft | Follow-up |
|---|---|---|---|
| Outline file frontmatter still says `status: candidate` even though Orchestrator dispatch says `outline-approved` | Strict skill validation would normally block candidate outlines | Draft proceeds based on Orchestrator approval state and commit `2e55c62...`; frontmatter caveat recorded | Orchestrator may choose to patch outline status during integration if desired |
| CTA / Blockscout / GSR adoption claims not primary-verified | Could overstate ecosystem maturity | Removed from positive maturity scoring; marked unverified/reported only | Fetch primary announcements before final or downgrade permanently |
| ERC-7945 implementation evidence weak | Maturity comparison may understate non-public Ant implementation | Reported as public evidence gap, not evidence of absence | Check Ant Group repos / Magicians thread / ecosystem docs in review round |
| ACL revocation semantics not proven | Core compliance and privacy risk | ObserverAccess/Hooked revocability set to constrained/historical-unverified | Review Zama ACL docs/source and test whether `allow` grants are revocable |
| Current OZ repo audit status ambiguous | Risk of saying current HEAD fully audited | Separate release audit PDFs from docs caveat that moving repo code is as-is and not formally audited | Tie any production recommendation to a tagged audited npm release, not master HEAD |
| Non-FHE ERC-7984 backend absent | Technology-neutrality may be theoretical | Marked interface-neutral, implementation maturity FHE-heavy | Look for ZK/TEE/MPC prototypes or build feasibility appendix |
| No on-chain adoption data | Maturity scoring remains qualitative | No TVL/tx count included | Query explorer/Dune if deployment addresses become available |

---

## Revision Log

| Round | Date | Changes |
|---|---|---|
| 1 | 2026-06-23 | Initial deep draft from approved outline. Incorporated review caveats: ObserverAccess and Hooked ACL permanence are treated as constrained/unverified revocability; unsupported maturity/adoption claims are downgraded or removed. |
