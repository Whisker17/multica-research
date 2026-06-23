---
topic: "机密计算协处理器/机密层方案分析（Zama / Inco / Fhenix）"
project_slug: "evm-privacy-research"
topic_slug: "confidential-coprocessor"
github_repo: "Whisker17/multica-research"
round: 1
status: draft

artifact_paths:
  outline: "evm-privacy-research/outlines/confidential-coprocessor.md"
  draft: "evm-privacy-research/research-sections/confidential-coprocessor/drafts/round-1.md"
  final: "evm-privacy-research/research-sections/confidential-coprocessor/final.md"

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23"
  outline_round: 1
  outline_commit: "c4df1a5cbf15e649995eb4cd3b7cd6d7b1e0b884"
  outline_approval_ref: "comment 13c24e3b-a75c-4ec7-b787-f0c11dccd68e (outline-approved, severity minor)"
  items_covered: ["item-1", "item-2", "item-3", "item-4", "item-5", "item-6", "item-7"]
  fields_investigated: ["architecture", "handle_acl_model", "decrypt_modes", "erc7984_oz_extensions", "tee_trust_model", "eigenlayer_economic_security", "integration_requirements", "selective_disclosure_vector", "liveness_risk", "performance_benchmark", "rubric_scoring", "deployment_status"]
  diagrams_produced: ["diagram-1", "diagram-2", "diagram-3", "diagram-4"]
  source_requirement_coverage: "first-party docs (docs.zama.org, docs.zama.ai, eips.ethereum.org, docs.openzeppelin.com/confidential-contracts, cofhe-docs.fhenix.zone, inco.org) explicitly distinguished from secondary corroboration (Medium, GlobeNewsWire, EEA report, Figment, KuCoin); cross-referenced from privacy-landscape-framework/final.md"
  caveats_addressed: ["source-taxonomy first-party vs secondary", "deployment-status accuracy (Inco mainnet, Fhenix testnet vs blog)", "ERC-7984/OZ full extension set incl. ERC7984Rwa/ERC7984Omnibus/ERC7984Hooked/ERC7984IdentityCheck"]

multica_issue_id: "085bc80d-f094-4585-98df-692c43731af5"
branch_name: "research/evm-privacy-research/confidential-coprocessor"
base_commit: "c4df1a5cbf15e649995eb4cd3b7cd6d7b1e0b884"
language: "中文"
research_depth: "deep-analysis"
mode: "single-issue-lightweight"

prerequisite_sections:
  - topic_slug: "privacy-landscape-framework"
    final_path: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"
    usage: "五轴评估 rubric、选择性披露 6 维向量 taxonomy、部署形态分类与轻量级判定标准"
---

# 机密计算协处理器/机密层方案分析（Zama / Inco / Fhenix）

> 本 section 属于「Mantle 轻量级机构隐私方案」pre-research 系列，深度分析「机密计算协处理器/机密层」bolt-on 家族。评分口径与术语锚定前置 section [`privacy-landscape-framework/final.md`](../privacy-landscape-framework/final.md)（五轴 rubric、6 维选择性披露向量、轻量级判定标准）。

## 来源分级约定（Source Taxonomy）

> 应 outline review caveat #1。本 section 对每条结论标注证据等级：
>
> - **[一手]** = First-party 官方文档/规范/源码。具体包括：`docs.zama.org`、`docs.zama.ai`（Zama Protocol/fhEVM 文档）、`eips.ethereum.org`（ERC-7984 规范正文）、`docs.openzeppelin.com/confidential-contracts` 与 `github.com/OpenZeppelin/openzeppelin-confidential-contracts`（OZ Confidential Contracts 文档与源码）、`cofhe-docs.fhenix.zone` 与 `fhenix.io`（Fhenix CoFHE 官方文档与博客）、`inco.org`（Inco 官网与博客）。
> - **[二手]** = Secondary corroboration：Medium 解读、GlobeNewsWire/Metaverse Post 等新闻稿、EEA Privacy Working Group 报告、Figment「Inside Zama」、KuCoin Research「FHE 2026」、OpenZeppelin 审计报告（第三方审计视角，介于一手与二手之间，标注为 **[审计]**）。
> - **[推论]** = 研究者基于上述来源的综合推断，非任一来源直接陈述。
>
> 所有访问日期为 **2026-06-23**，除非另行标注。厂商自报性能数据一律标注「未独立验证」。

---

## Executive Summary

本 section 深度分析三个「机密计算协处理器/机密层」方案——**Zama fhEVM**、**Inco Network**、**Fhenix CoFHE**。三者共享同一部署范式：开发者用普通 Solidity + 加密类型编写合约，链上仅存 ciphertext handle（指针）+ ACL，重型加密计算在链下协处理器异步执行。这使它们区别于 token-only 隐私方案（可隐藏**任意合约状态**），也区别于独立机密链（如 Oasis Sapphire）——按**部署形态**而非底层密码学归类，故 Inco（当前 TEE-first）虽用硬件信任仍归此 bolt-on 家族。

核心发现：

1. **信任模型是三者的根本分野**，而非「都是 FHE」：Zama = **密码学信任**（TFHE）+ **门限 MPC**（9-of-13 KMS，≤1/3 恶意容错）[一手]；Inco Lightning = **硬件锚定信任**（Intel TDX TEE），FHE 仅在 roadmap（Atlas）[一手]；Fhenix CoFHE = **密码学信任**（TFHE/BFV）+ **经济信任**（EigenLayer restaking + optimistic 验证）[一手/二手]。

2. **部署成熟度差异显著且必须精确限定**（caveat #2）：**Zama** 已于 2025-12 在 Ethereum 主网上线 [一手/二手]；**Inco Lightning** 自 2025-04 在 Base Sepolia 测试网、并于 **2026-06-15 正式上线 Base 主网**（inco.org 一手公告）[一手]；**Fhenix CoFHE** 官方博客称「live on Ethereum mainnet 与 Arbitrum」，但其一手文档（cofhe-docs.fhenix.zone）的 Quick Start 仅列测试网部署且标注「production mainnet support coming soon」——存在博客叙事与文档现状的张力，本 section 据一手文档将其判定为「测试网为主 + 主网早期/限定」（详见 item-4）[一手/二手，矛盾已限定]。

3. **ERC-7984 + OpenZeppelin Confidential Contracts 已形成完整合规扩展栈**（caveat #3）：除基础的 Wrapper/Freezable/ObserverAccess/Restricted/Votes 外，v0.5 引入 **ERC7984Rwa**（RWA 合规：agent 角色 + mint/burn/pause/freeze/blocklist/force-transfer/账户恢复）、**ERC7984Omnibus**（加密子账户地址的 omnibus 转账，面向交易所间转账的身份隐藏）、**ERC7984Hooked**（hook 模块框架）、**ERC7984IdentityCheck**（ERC-3643 式身份验证）。OZ v0.5 审计发现一个 **critical** 级问题：hook 模块可授予持久 FHE ACL 且 uninstall 后不可撤销 [审计]。

4. **三者均通过框架「轻量级 bolt-on」判定**（无新链/新桥/全节点/硬分叉），但各有关键瓶颈：Zama 受 FHE 性能限制（CPU ~20 TPS，GPU 路线图 500-1000 TPS）[一手]；Inco 受 Intel 硬件信任 + 侧信道风险约束；Fhenix 受经济安全成熟度与主网状态约束。

5. **合规-选择性披露能力排序：Inco ≈ Zama > Fhenix**。Inco 有 Circle 联合框架 + ERC-3643 协会成员的显式机构叙事；Zama 有 OZ 完整扩展栈（尤以 ERC7984Rwa/ObserverAccess 强）；Fhenix 的 permit-based sealing 较基础，合规生态弱。

6. **Mantle 集成建议**：在轻量级偏好下，Zama（密码学信任 + 主网就绪 + OZ 合规栈）与 Inco（机构合规叙事 + Base 主网已上线，但需扩展支持 Mantle + TEE 信任进入安全叙事）是两条主候选路径；Fhenix 因经济安全成熟度与合规弱势暂列备选。

---

## item-1: Zama fhEVM 架构深度解析 — 五组件模型、handle/ACL、解密模式与 ERC-7984

### 1.1 组件架构与数据流

Zama Protocol（fhEVM 的协议化形态）由五类组件协同 [一手 docs.zama.org/protocol]：

| 组件 | 职责 | 关键特性 |
|------|------|---------|
| **fhEVM Solidity Library** | 开发者在普通 Solidity 中使用加密类型（`euint8/16/32/64/128/256`、`ebool`、`eaddress`、`ebytes64/128/256`）和 FHE 操作（加减乘、比较、`select`/cmux 条件选择） | 无需新语言；标准 Solidity 工具链 |
| **Host Contracts（fhEVM Executor）** | 部署在 host chain 的合约。**不执行** FHE 运算，仅产生 symbolic pointer（handle）并 emit event 通知协处理器；维护链上 ACL | host chain 不因 FHE 减速；非 FHE 交易正常速度 |
| **Coprocessors** | 去中心化节点网络，监听 host chain 事件，基于 `TFHE-rs` 执行实际 FHE 运算，返回加密结果；多节点并行 + majority agreement；有质押要求 | FHE 操作可并行（非顺序）执行 |
| **Gateway** | 协议控制面：验证加密输入、聚合 ACL、跨链桥接 ciphertext、协调 Coprocessor↔KMS 通信 | fhEVM v0.7（2025-07）引入为核心组件 [二手] |
| **KMS（门限密钥管理）** | 门限 MPC 网络，负责 FHE 密钥生成/轮换、CRS 生成、门限解密；底层是一条带 web API 的 L1 链 | 见 §1.4 去中心化分析 |

**数据流** [一手 + 推论]：用户本地 encrypt → host chain symbolic execution（产生 handle）→ Coprocessor 执行 FHE 计算 → 结果 handle 回写 host chain → 解密请求经 ACL 验证 → Gateway 转发 KMS → 门限解密 → 明文上链（public decrypt）或 re-encrypt 后返回用户（user decrypt）。

### 1.2 Handle 模型（Symbolic Execution）

- **Handle = ciphertext 的链上指针（bytes32）**，而非实际加密数据本身；实际 ciphertext 存储在 Coprocessor 网络 [一手]。
- **Symbolic execution**：host chain 上的 FHE 操作不产生实际结果，只产生指向结果的 pointer——类似编程语言的 lazy evaluation。Handle 可链式组合（chaining），不需等前一操作完成即可发起下一操作 [一手/推论]。
- 全局 FHE 公钥用于加密所有输入和状态；解密需门限 KMS 协作，单方不可解 [一手]。

> **架构优势**：链上仅存 handle（pointer）而非膨胀的 ciphertext，大幅降低链上存储压力——这是其满足框架「FHE 路线轻量级」指标（密钥/密文不直接上链）的关键。

### 1.3 ACL（访问控制列表）权限系统

ACL 是 Zama 选择性披露能力的技术底座 [一手 docs.zama.org ACL 章节]：

- **两层 ACL**：链上 ACL 合约（per host chain，记录「谁可解密什么」）+ Gateway 聚合 ACL（跨链统一视图，供 KMS 鉴权）。每次合约 `allow` 一个地址使用 ciphertext，emit event → Coprocessor relay → Gateway 聚合。
- **持久权限**：`FHE.allow(ciphertext, address)` / `FHE.allowThis(ciphertext)`——跨交易持久化。
- **临时权限**：`FHE.allowTransient(ciphertext, address)`——单笔交易内有效，用 transient storage 省 gas。
- **验证**：`FHE.isSenderAllowed(ciphertext)`——检查调用方是否被授权。
- **公开解密标记**：`FHE.makePubliclyDecryptable(ciphertext)`——永久标记为可公开解密。
- ACL 不仅控解密，也控**计算权限**：合约必须被 allow 才能对 ciphertext 执行 FHE 操作。

> **撤销性 caveat**：当前文档描述了 `allow`（授权）但未见明确的「`disallow`/revoke」原语。持久授权一旦设定，能否在 ACL 层面单方撤销需进一步确认——这与 OZ v0.5 审计发现的「FHE ACL 不支持撤销」一致（见 §1.5）。本 section 在 item-5 向量中据此标注 Zama 的 revocability 为待验证。

### 1.4 KMS 门限 MPC 去中心化（caveat 相关，量化）

[一手 docs.zama.org KMS + 二手 Figment「Inside Zama」]：

- **节点数与阈值**：KMS 当前 **13 个 MPC 节点**，门限解密需**至少 9 个节点（9-of-13）**参与才能稳健解密。Zama Protocol 采用 DPoS，初期 18 个 operator（13 KMS 节点 + 5 FHE Coprocessor，逐步增加）。
- **密码学基础**：基于 Galois Ring 上的 Shamir Secret Sharing，提供 **Guaranteed Output Delivery**（保证输出交付）；当 ≤ t 方恶意时，诚实方仍能恢复正确结果。**安全前提：至多 1/3 节点恶意**。
- **硬件加固**：每个 MPC 节点默认运行在 **AWS Nitro Enclave** 内——即使节点运营方也无法访问自己的密钥分片，缓解内部人风险。（注：这意味着 Zama KMS 的信任模型并非纯密码学，而是「门限 MPC + TEE 加固」的混合形态。）
- **密钥恢复**：每个节点将密钥分片再切成加密 fragment 分发给独立 custodian；丢失时由 custodian quorum 协作恢复，恢复操作全程链上可审计。

### 1.5 ERC-7984 标准与 OpenZeppelin 完整扩展栈（caveat #3）

**ERC-7984（Confidential Fungible Token）** [一手 eips.ethereum.org/EIPS/eip-7984]：

- 状态：**DRAFT**（2025-07 提交）。作者含 Zama + OpenZeppelin 团队（Aryeh Greenberg、Ernesto García、Hadrien Croubois 等）[一手/二手]。
- **非 ERC-20 兼容**——全新接口设计。所有金额用加密 handle（bytes32）表示，合约本身不知余额数值。
- **核心接口**：`confidentialTotalSupply()`、`confidentialBalanceOf(address)`、`confidentialTransfer(address, bytes32)`、`confidentialTransferFrom(...)`、`setOperator(address, uint48)`（带时间限制的 operator 授权）。
- 落地里程碑 [二手]：2025-12 Zama 在 Ethereum 主网完成首笔加密 USDT 转账（屏蔽 >1.21 亿 USDT）；2026-03 GSR × Zama 完成首笔加密 OTC 交易。

**OpenZeppelin Confidential Contracts 扩展栈** [一手 docs.openzeppelin.com/confidential-contracts + github 源码；审计来自 OZ 审计报告]。版本历史：v0.1.0（2025-06-05）、v0.2.0（2025-08-15）、v0.3.0（2025-11-28）、v0.3.1（2026-01-07）、v0.4.0（2026-03-30）、**v0.5（最新）**：

| 扩展 | 引入版本 | 功能 | 合规/披露相关性 |
|------|---------|------|----------------|
| `ERC7984ERC20Wrapper` | 早期 | 将 ERC-20 双向包装为 confidential token | 与现有 ERC-20 资产互通 |
| `ERC7984Freezable` | 早期 | freezer 角色冻结/解冻 | 合规冻结 |
| `ERC7984ObserverAccess` | 早期 | 每账户可加 observer（审计员/监管方），授予查看余额和转账金额的权限 | **选择性披露核心** |
| `ERC7984Restricted` | 早期 | 账户级转账限制（合规控制） | KYC/AML 准入 |
| `ERC7984Votes` | 早期 | 保密投票跟踪与委托 | 保密治理 |
| **`ERC7984Rwa`** | — | **RWA 合规扩展**。基于 OZ AccessControl 定义 `DEFAULT_ADMIN_ROLE`（指派/撤销 agent）与 `AGENT_ROLE`。Agent 可：mint/burn、pause/unpause、block/unblock 账户、设置 confidential frozen balance、**恢复被盗地址**、执行**绕过 pause 和 sender-restriction 的 force-transfer** | **RWA/机构合规关键**：构建于 Freezable + Restricted 之上，提供监管级强制干预能力 |
| **`ERC7984Omnibus`** | — | 为 omnibus 转账 emit 额外 event，事件中含**加密的子账户 sender/recipient 地址**。链上无子账户记账，集成方须链下跟踪余额 | **地址/身份隐藏**：在转账中隐藏子账户地址，尤适交易所间 ERC-7984 转账 |
| **`ERC7984Hooked`** | v0.5 | hook 模块框架（`IERC7984HookModule` 接口 + 抽象 `ERC7984HookModule` 基类 + 示例模块如 per-investor/per-holder 余额上限）。通过抽象 `_authorizeModuleChange` 谓词暴露安装/卸载 | 转账前后合规检查可插拔 |
| **`ERC7984IdentityCheck`** | v0.5 | ERC-3643 式身份验证扩展 | 与 RWA 身份合规对齐 |

> **⚠️ OZ v0.5 审计 critical 发现** [审计 openzeppelin.com/news/...v0.5-diff-audit]：hook 模块框架存在一个 critical 级问题——**已安装的 hook 模块可在任意 handle 上授予持久 FHE ACL 给任意第三方账户，且这些授权在模块 uninstall 后仍然存续，因为 FHE library 不支持撤销**。OZ 文档明确警示「模块安装是对 token 加密状态的不可逆机密性决策」，应在 admin 层严格门控。此发现对 Mantle 评估有直接意义：**FHE ACL 的不可撤销性是 GDPR right-to-be-forgotten 合规的结构性障碍**（见 item-5、item-7）。

- **Priority**: high | **Dependencies**: none

---

## item-2: Inco 深度解析 — Lightning(TEE) 当前能力 + Atlas(FHE) Roadmap + RWA 合规定位

### 2.1 Inco Lightning 架构（TEE-based，当前生产）

Inco 定位为**现有链的「机密层」（confidentiality layer），类比 TLS/SSL**——不是新链 [一手 inco.org]。四组件 [一手 inco.org/blog + 二手 Metaverse Post]：

1. **Smart Contract Library**：Solidity 工具包，扩展 EVM 支持加密类型（`euint`、`ebool`、`eaddress`）和机密计算（`e.add()`、`e.mul()`、`e.div()`、加密随机数 `e.randEuint8()`）。
2. **Confidential Compute Nodes**：TEE enclave 节点网络（当前 **Intel TDX**），链下执行加密计算；即使节点运营方也看不到 enclave 内数据。
3. **Decryption Nodes + Callback Relayer**：基于 quorum 的 TEE 网络，处理解密/re-encryption 请求，签名结果，通过验证的 callback 交易回写链上。
4. **Client-side JS Library**：前端 SDK，本地加密输入、管理密钥/签名、解密输出。

> **开发者体验** [一手]：import Solidity library 即获得 encrypted state，无需新链/新钱包；官方称「20 分钟内」可写出 confidential 合约并部署。

### 2.2 TEE 信任假设与风险（与 Zama/Fhenix 的本质区别）

- **本质**：信任 **Intel TDX 硬件**的安全隔离保证——这是 **Hardware-Anchored Trust**，与 Zama/Fhenix 的 **Cryptographic Trust** 有本质区别 [推论，对齐框架 §1.3]。
- **Intel TDX**：CPU 内存加密引擎硬件隔离，host OS/hypervisor 可管理 VM 生命周期但读不到 VM 内存；提供 Remote Attestation。
- **侧信道风险**：继承 SGX/TDX 侧信道攻击面（Spectre/Meltdown/Plundervolt/ÆPIC Leak/Downfall 类）；安全性依赖 Intel 硬件无漏洞 + Remote Attestation 服务可用（单点信任）[二手/推论]。
- **活性风险**：TEE 节点运营方控制可用性——TEE 节点集群下线则机密层不可用。与 Sapphire/Phala 同类型风险画像。
- **非 post-quantum**：TEE 不具备 FHE 的格密码 post-quantum 特性 [推论]。

### 2.3 Atlas（FHE roadmap）

[一手 inco.org + 二手 Metaverse Post]：Atlas 是**即将推出（upcoming）**的协议，利用 FHE + MPC 提供 trustless 链上可编程机密性，用以替代/补充 Lightning 的 TEE 信任。信任模型变化：Hardware-Anchored（TEE）→ Cryptographic（FHE/MPC）。**上线时间未给确切日期**——本 section 据一手来源仅判定「roadmap，未上线」，不引用旧的「later this year」表述（避免过期叙事）。

### 2.4 Confidential ERC-20 与 RWA 合规

[一手 inco.org/blog + circle.com 联合框架 + 二手]：

- **Circle × Inco Confidential ERC-20 Framework**：将标准 ERC-20 转为隐藏余额/金额的 confidential 版本。**核心设计选择：confidentiality（隐藏金额/余额）而非 anonymity（隐藏地址）——地址公开，金额加密**。
- **访问控制与选择性披露**：Delegated viewing（授权审计员/监管方查看账户详情，无需分享私钥）；可编程解密规则；智能合约级转账规则（AML、黑名单、交易限额、管辖权限制）。
- **ERC-3643 Association 成员**：Inco 加入 RWA 合规 token 标准协会，贡献 confidentiality 能力 [一手 inco.org/blog/inco-joins-erc3643-association]。
- **Confidential Token Association**：Inco 与 OpenZeppelin、Zama 共同创立（2025-04）[二手]。

### 2.5 平台成熟度与部署状态（caveat #2 — 精确限定）

- **融资**：累计 **$10M**（自 2024-02 跨 3 轮），投资方含 a16z CSX、Coinbase Ventures、Circle Ventures、1kx [二手 GlobeNewsWire/coinlaunch]。
- **部署时间线（已用一手源核实并限定）**：
  - **2025-04**：Inco Lightning 在 **Base Sepolia 测试网**上线 [一手 inco.org/blog/inco-lightning-launched-on-base-sepolia；二手 GlobeNewsWire 发布稿]。
  - **2026-06-15**：Inco Lightning **正式上线 Base 主网**（inco.org 官方公告/社媒）[一手 inco.org + 二手 Metaverse Post 同日报道]。
  - **结论**：截至 2026-06-23，**Inco Lightning 已在 Base 主网生产可用**，且仅 Base——其他链（含 Mantle）需 Inco 团队扩展支持。这澄清了 outline 中标注的「多源矛盾」：早期「Base Sepolia」与近期「live on Base mainnet」并非矛盾，而是**测试网（2025-04）→ 主网（2026-06-15）的时间演进**。
- **技术定位演进**：原为 FHE-first pitch，2025 年 pivot 到 TEE-first（Lightning）以加快交付，FHE 留给 Atlas [二手/推论]。

### 2.6 Force-Exit / 逃生通道

作为 bolt-on 机密层，host chain 资产理论上安全不依赖机密层活性——但 outline 提出的「force-exit/escape hatch」具体机制**在现有一手文档中未找到明确描述**。标注为 **Gap**（见 Gap Analysis），后续需向 Inco 团队确认：当 TEE 解密网络长期不可用时，加密余额能否被用户单方恢复。

- **Priority**: high | **Dependencies**: none

---

## item-3: 轻量级集成评估 — 在现有 EVM L2 接入各需什么

### 3.1 三方案集成要求对比

| 维度 | Zama fhEVM（Coprocessor 模式） | Inco Lightning | Fhenix CoFHE |
|------|------------------------------|----------------|--------------|
| **链改动** | 无（host chain 不改，无需 precompile） | 无（bolt-on 机密层） | 无（协处理器模式） |
| **链上部署** | fhEVM host contracts（ACL + Executor）[一手] | Inco 合约套件 [一手] | Fhenix relay/coprocessor 合约 [一手 cofhe-docs] |
| **开发者工具** | import fhEVM Solidity library + encrypted types | import Inco Solidity library + encrypted types | cofhesdk（TypeScript）+ FHE Solidity library |
| **基础设施依赖** | Zama/自建 Coprocessor + Gateway + KMS | Inco 运营 TEE Compute Nodes + Decryption Quorum + Callback Relayer | CoFHE Coprocessor + Threshold Decryption Network + EigenLayer operators |
| **底层密码学** | TFHE（FHE）+ 门限 MPC | TEE（Intel TDX）；FHE/MPC roadmap | TFHE/BFV（FHE）+ EigenLayer |
| **信任假设** | ≥9/13 KMS 诚实 + Nitro Enclave | Intel TDX 无漏洞 + TEE 节点诚实 | ≥ EigenLayer stake 诚实 + 挑战窗口活性 |
| **合约状态隐私覆盖** | 任意合约状态 | 任意合约状态 | 任意合约状态 |
| **许可证** | 开源 BSD-3-Clause-Clear，商用需 Zama 许可 [一手] | 见 Gap（许可条款未在一手文档定位） | 见 Gap |

**Zama Native 模式（路径 B，深度集成）** [一手/二手]：用 `fhEVM-go` 修改 go-ethereum，添加 FHE precompile（默认地址 0x93），依赖 `tfhe-rs` 本地编译。适用于想原生支持 FHE 的链——但侵入性高（属框架「中量级」），**不推荐用于 Mantle 轻量级目标**。

### 3.2 合约逻辑/状态隐私覆盖度（家族共性）

三方案均**超越 token-only 隐私，可隐藏任意合约状态** [一手三方文档 + 推论]：覆盖余额、转账金额、合约变量、比较结果、条件分支结果（通过 cmux/select）。**共同限制**：地址/身份不隐藏（与 ZK 方案如 Aztec 的区别）；交易图/资金流可见（地址公开）。Inco 的 Omnibus（经由 OZ ERC7984Omnibus 类比能力）与 Circle 框架明确把「地址公开、金额加密」作为设计取舍。

### 3.3 对齐框架部署形态判定

三方案均为 bolt-on Coprocessor/机密层模式，**不需要新链/新桥/全节点运维/硬分叉**——通过框架 §5.2 四项一票否决。初步判定：均为「**轻量级 bolt-on**」（详细判定见 item-7 §7.0）[推论，对齐 privacy-landscape-framework §5]。

- **Priority**: high | **Dependencies**: item-1, item-2

---

## item-4: Fhenix CoFHE 差异分析 — 经济安全、协处理器 vs 链

### 4.1 CoFHE 架构（queue-driven pipeline）

[一手 cofhe-docs.fhenix.zone + fhenix.io/blog；二手 KuCoin/Medium]：CoFHE 从早期单体「aggregator」升级为**显式的、队列驱动的执行 pipeline，明确分离 validation → computation → publishing → decryption 四阶段**。组件：

- **Relay Contract**（host chain）：监听 FHE 计算事件。
- **Relay Node**：桥接调用到 Fhenix 计算层。
- **FHE 计算层（CoFHE）**：执行加密计算。
- **Threshold Decryption Network**：授权解密网络，仅向被授权方揭示明文。
- 设计理念：「encrypted memory 的权限系统」而非传统黑盒计算 [一手/二手]。

### 4.2 EigenLayer 经济安全模型（与 Zama 门限 MPC 的对比）

[二手 blog.eigenlayer.xyz/fhenix + blog.arbitrum.io；一手 fhenix.io]：

- Fhenix CoFHE 通过 **EigenLayer restaking** 获得经济安全：operators 对计算有效性做 attestation，恶意 operator 的 stake 被 slash。
- **安全权衡对比**：
  - **Zama**：密码学保证（≥9/13 节点诚实则安全）+ Nitro 加固 + 质押激励——**安全不主要依赖攻击成本**。
  - **Fhenix**：经济博弈保证（攻击成本 > restaked ETH）+ optimistic 验证（有挑战窗口）——**安全依赖 restake 规模充足 + 挑战窗口内有 fraud-proof 激励**。
- **关键含义**：经济安全的强度随 restaked ETH 规模波动；若质押不足，攻击成本可能低于攻击收益（见 item-6）[推论]。

### 4.3 从 FHE L2 到 FHE Coprocessor 的演进

[一手 fhenix.io/manifesto + 二手 Medium FHE Rollup 白皮书]：Fhenix 原为「首个 FHE-powered L2」，已演进为 confidential DeFi 基础设施公司，核心产品 CoFHE（协处理器）。**FHE Rollup 白皮书（2026-03，首版迭代）**描述一个 L2 设计：批量加密交易、向 Ethereum 或兼容 base layer 提交简洁 validity proof、全状态加密、CoFHE 处理计算——但白皮书明确「邀请社区反馈以在 mainnet rollout 前完善设计」，即 **rollup 形态尚未 mainnet**。与 Zama 的关系：Fhenix 使用 Zama 的 `TFHE-rs` 库（Zama 无论哪个 FHE 链胜出都收许可费）[二手]。

### 4.4 技术创新与性能声称

- **Decomposable BFV（2026-02）** [一手/二手]：将大明文值分解为小 ciphertext 片段再加密，允许并行处理，显著提升 exact FHE schemes（金融场景）吞吐量。
- **性能声称（厂商自报，未独立验证）**：解密速度「比竞品快 50x」；门限解密延迟改善 37x、吞吐量提升 20,000x（对比早期方案）。**均无独立第三方 benchmark**。

### 4.5 部署状态（caveat #2 — 博客 vs 文档的张力，已限定）

这是本 section 最需谨慎限定的部署声明：

- **官方博客口径** [一手 fhenix.io/blog]：「CoFHE on Arbitrum — Encrypted Computation Goes Live」；多处叙述称 CoFHE「live on Ethereum mainnet 与 Arbitrum」，并称「mainnet activity 已展示稳定性能」。
- **官方文档口径** [一手 cofhe-docs.fhenix.zone Quick Start / Local Development Setup]：Quick Start 列出的可部署目标以**测试网为主**，并标注「**production mainnet support coming soon**」。
- **时间线锚点** [一手/二手交叉]：CoFHE 测试网先上 Ethereum Sepolia → **Base（2026-02 上线）** → Arbitrum Sepolia 随后。
- **本 section 判定（据一手文档优先于博客营销叙事）**：截至 2026-06-23，CoFHE **以测试网部署为主（Ethereum Sepolia / Arbitrum Sepolia / Base）**；官方博客的「live on Ethereum mainnet/Arbitrum」与文档的「mainnet support coming soon」存在叙事张力。**保守结论：主网状态为「早期/限定，非全面 production GA」**，FHE Rollup 形态尚未 mainnet。后续竞品分析应直接向 Fhenix 团队或链上合约地址核实主网生产合约的实际部署与活跃度。

### 4.6 平台成熟度

[二手 Medium/KuCoin + 一手 fhenix.io]：累计融资 **>$22M**（含 $15M Series A by Hack VC，参投 Amber/Collider/Primitive/GSR/Stake Capital/Dao5；早期 $7M seed by Multicoin/Collider）。合作：EigenLayer（经济安全）、Offchain Labs（Arbitrum）。日本投资（BIPROGY、TransLink Capital）——亚洲隐私稳定币方向。

- **Priority**: medium | **Dependencies**: item-1

---

## item-5: 合规-选择性披露 — 对齐框架 6 维向量模型

> 锚定 [`privacy-landscape-framework/final.md` item-4](../privacy-landscape-framework/final.md) 的 6 维向量：a-Authority / b-Trigger / c-Payload / d-Scope / e-Revocability / f-Leakage。

### 5.1 三方案选择性披露向量

| 维度 | **Zama fhEVM** | **Inco Lightning** | **Fhenix CoFHE** |
|------|---------------|--------------------|------------------|
| **a-Authority** | `key-holder`（ACL allow）+ `smart-contract`（合约自动授权）+ `notary/observer`（OZ ObserverAccess）+ `regulator`（ERC7984Rwa agent）[一手] | `key-holder`（delegated viewing）+ `smart-contract`（可编程解密规则）+ `regulator`（监管查看）[一手] | `key-holder`（permit holder）+ `smart-contract`（合约定义 access rules）[一手 cofhe-docs] |
| **b-Trigger** | `viewing-key-share`（re-encryption，用户提供公钥）+ `on-chain-request`（public decrypt）+ `automatic`（ObserverAccess 持续可见）[一手] | `compliance-gate`（合约级 AML/KYC/黑名单/限额）+ `viewing-key-share`（delegated viewing 不分享私钥）+ `automatic`（ERC-3643 引擎）[一手] | `viewing-key-share`（permit-based unsealing）+ `on-chain-request`（threshold decryption request）[一手] |
| **c-Payload** | `amount`～`all`（取决于合约；ERC7984Omnibus 可隐藏子账户地址）[一手] | `amount`（金额/余额加密，地址公开）；可编程载荷 [一手] | `amount`/`logic`（sealed output 粒度，见 Gap）[一手] |
| **d-Scope** | `per-tx`（allowTransient）+ `per-account`（persistent allow）+ `per-contract`（allowThis）[一手] | `per-tx` + `per-account`（delegated viewing 可选粒度）[一手/推论] | `per-tx`（per-permit）；更细粒度见 Gap [推论] |
| **e-Revocability** | **`unverified-revocable`**：ACL 有 `allow` 但未见明确 revoke 原语；OZ v0.5 审计确认「FHE library 不支持撤销」→ 持久 ACL 实质不可撤销。`auditable-log`（ACL 事件 on-chain emit + Gateway 聚合）[一手 + 审计] | **`unverified-revocable`**：声称支持合规撤销但一手文档未定位具体机制；`auditable-log`（链上可验证）[一手/未验证] | **`one-time`/`unverified`**：permit 分发后撤销机制未在一手文档定位 [Gap] |
| **f-Leakage** | `existence` + `timing`；**地址公开**（除非用 Omnibus 隐藏子账户）[一手/推论] | `existence` + `timing`；**地址公开**（设计取舍：confidentiality≠anonymity）[一手] | `existence` + `timing`；**地址公开** [推论] |

> **关键合规观察**：三方案的 **e-Revocability 普遍为待验证或不可撤销**——这是 FHE ACL 模型的**结构性**特征（OZ v0.5 审计已就 Zama/FHE 栈坐实），直接制约 GDPR right-to-be-forgotten 合规。框架 item-4 合规映射中「无方案完全满足 GDPR right to be forgotten」的结论在本家族同样成立。

### 5.2 合规扩展能力对比

| 能力 | Zama | Inco | Fhenix |
|------|------|------|--------|
| Observer/审计员访问 | **OZ ERC7984ObserverAccess**（强） | Delegated viewing（强） | Permit-based（基础） |
| 合规转账限制 | **OZ ERC7984Restricted + IdentityCheck**（强） | 合约级规则 + ERC-3643（强） | 见 Gap |
| 冻结/强制干预 | **OZ ERC7984Freezable + ERC7984Rwa**（force-transfer/账户恢复/blocklist，最强） | 见 Gap | 见 Gap |
| 子账户地址隐藏 | **OZ ERC7984Omnibus**（交易所间转账） | confidentiality 模型（地址公开） | 见 Gap |
| 身份验证 | **OZ ERC7984IdentityCheck**（ERC-3643 式） | ERC-3643 Association 成员 | 见 Gap |
| 合规生态伙伴 | OZ、Confidential Token Association | **Circle、OZ、ERC-3643 Association** | 有限 |
| 机构/RWA 定位 | **强**（ERC7984Rwa + OZ 完整栈） | **强**（Circle + RWA 显式叙事） | 弱（DeFi 优先） |

> **caveat #3 落地**：ERC7984Rwa 提供 RWA 监管级强制能力（mint/burn/pause/freeze/blocklist/force-transfer/账户恢复），ERC7984Omnibus 提供地址级隐私（加密子账户），两者共同把 Zama 栈从「token 隐私」抬升到「机构 RWA 合规隐私」量级——这是与 Inco（Circle 框架）正面竞争机构市场的能力基础。

- **Priority**: high | **Dependencies**: item-1, item-2, item-4

---

## item-6: 风险与活性依赖 — KMS quorum、TEE 硬件信任、经济安全、性能

### 6.1 Zama — KMS quorum 去中心化与活性

- **量化阈值**：9-of-13 门限，≤1/3 恶意容错 [一手]。活性依赖：若 <9 个 KMS 节点可用，**所有解密暂停**（计算可继续但取不到结果）。Coprocessor 网络靠质押 + majority agreement。
- **混合信任**：KMS 节点跑在 AWS Nitro Enclave 内——引入对 AWS/Intel 硬件的**附加**信任（纯密码学叙事被打了折扣）[一手/推论]。
- **去中心化成熟度**：初期 18 operator，可能 Zama 自营为主；KMS 底层 L1 链的共识安全性需独立评估 [推论]。

### 6.2 Inco — TEE 硬件信任链

- Intel TDX 侧信道历史攻击面（SGX 系：Spectre/Meltdown/Plundervolt/ÆPIC/Downfall）；Remote Attestation 依赖 Intel 证明服务（单点信任）[二手/推论]。
- TEE 节点运营方控制可用性——节点集群下线则机密层不可用。
- 「今天 = TEE」定性：Hardware-Anchored Trust，非 Cryptographic；非 post-quantum。

### 6.3 Fhenix — EigenLayer 经济安全阈值

- 经济安全随 restaked ETH 规模波动；质押不足时攻击成本可能 < 收益 [推论]。
- Optimistic 验证有挑战窗口——窗口内需足够 fraud-proof 激励；EigenLayer operator 集中度风险；Threshold Decryption Network 去中心化程度需核实 [推论]。

### 6.4 性能基准（厂商自报，均「未独立验证」）

| 指标 | Zama（自报） | Inco（自报） | Fhenix（自报） |
|------|-------------|-------------|---------------|
| 当前吞吐 | ~20 TPS（CPU） | 未公开（TEE 低开销） | 未公开 |
| 路线图吞吐 | 500-1000 TPS（GPU，2026 底前迁移） | — | — |
| 远期目标 | 100,000+ TPS（ASIC） | — | — |
| Bootstrapping | <1ms（H100）；189,000 bootstraps/s（8×H100） | N/A（TEE 无 bootstrapping） | 未公开 |
| 解密 | 门限解密（≤1s for 2048 ciphertexts, 10 方）[一手] | TEE 低延迟解密 | 「50x faster」「延迟 -37x / 吞吐 +20,000x」 |

**所有性能数据未见独立第三方 benchmark**——为厂商自报或厂商赞助文章引用 [一手/二手，明确标注]。

### 6.5 共同风险

- 早期阶段：Zama 刚主网；Inco 主网（Base，2026-06）但仅单链；Fhenix 测试网为主。
- **FHE 密钥长期安全**：密钥泄露 = 所有历史 ciphertext 可解（"harvest now, decrypt later" 在 FHE 下尤需门限保护）。
- 量子威胁：FHE 本身 post-quantum（格密码），但 **TEE（Inco）不具备**该特性。
- **撤销性/合规结构性障碍**：FHE ACL 不可撤销（OZ v0.5 审计）→ GDPR 合规挑战。
- 监管不确定性：全链加密可能被某些管辖权视为 non-compliant。

- **Priority**: high | **Dependencies**: item-1, item-2, item-4

---

## item-7: 框架 Rubric 评分、三方案对比表与 Mantle 集成路径草图

### 7.0 轻量级判定（对齐框架 §5）

| 方案 | V1 新链 | V2 新桥 | V3 全节点 | V4 硬分叉 | 否决 | 最终判定 |
|------|:------:|:------:|:--------:|:--------:|:---:|:-------:|
| Zama fhEVM (Coprocessor) | ✗ | ✗ | ✗ | ✗ | 通过 | **轻量级 bolt-on** |
| Inco Lightning | ✗ | ✗ | ✗ | ✗ | 通过 | **轻量级机密层** |
| Fhenix CoFHE (Coprocessor) | ✗ | ✗ | ✗ | ✗ | 通过 | **轻量级 bolt-on**（主网成熟度待验证） |

注：Zama Native 模式（fhEVM-go + precompile）触发链改动 → 中量级，本评估只采 Coprocessor 模式。Fhenix FHE Rollup 形态若落地将是独立 L2（届时触发 V1）——本判定仅针对 CoFHE 协处理器模式。

### 7.1 五轴 Rubric 评分（对齐框架 item-3）

| 评估轴 | Zama fhEVM | Inco Lightning | Fhenix CoFHE |
|--------|-----------|----------------|--------------|
| **轴 1 — 密码学路线** | FHE(TFHE) + 门限 MPC；post-quantum；无 trusted setup（TFHE）；KMS 用 Nitro 加固 | TEE(Intel TDX) 当前；FHE/MPC roadmap(Atlas)；非 post-quantum | FHE(TFHE/BFV) + EigenLayer；post-quantum；Decomposable BFV |
| **轴 2 — 数据维度** | 金额● 余额● 身份○ 图○ 逻辑● 状态● 订单流○ | 同 Zama（身份○、可选 Omnibus 类比隐藏） | 同 Zama |
| **轴 3 — 信任模型** | Cryptographic(FHE) + Organizational(KMS) + HW(Nitro) | **Hardware-Anchored(TEE)** | Cryptographic(FHE) + **Economic(EigenLayer)** |
| **轴 4 — 部署形态** | Bolt-on 协处理器 → 轻量级 | Bolt-on 机密层 → 轻量级 | Bolt-on 协处理器 → 轻量级 |
| **轴 5 — 合规披露** | 多维（ObserverAccess/Restricted/Freezable/**Rwa**/**Omnibus**/IdentityCheck） | 多维（Delegated Viewing/Circle/ERC-3643） | 基础（permit-based sealing） |

● = 完全保护 ◐ = 部分 ○ = 不保护

### 7.2 三方案全面对比表

| 维度 | Zama fhEVM | Inco Lightning | Fhenix CoFHE |
|------|-----------|----------------|--------------|
| 架构组件 | 5 组件（Lib/Host/Coprocessor/Gateway/KMS） | 4 组件（Lib/Compute/Decryption+Relayer/JS SDK） | 4 阶段 pipeline（validation/computation/publishing/decryption）+ Relay + Threshold Decrypt |
| 底层技术 | TFHE | Intel TDX TEE | TFHE/BFV（用 Zama TFHE-rs） |
| 安全模型 | 门限 MPC(9/13) + Nitro + FHE | 硬件信任 | EigenLayer 经济 + optimistic |
| 链改动 | 无（Coprocessor）/ 有（Native） | 无 | 无 |
| 合规栈 | **最完整**（OZ 全扩展） | **强**（Circle/ERC-3643） | 弱 |
| 部署状态（2026-06-23） | **Ethereum 主网（2025-12）** [一手/二手] | **Base 主网（2026-06-15）+ Base Sepolia** [一手] | **测试网为主**（ETH Sepolia/Arb Sepolia/Base）；主网状态博客与文档有张力，保守判「早期/限定」 [一手矛盾已限定] |
| 融资 | >$150M（2025-06 FHE 独角兽 $1B） [二手] | $10M [二手] | >$22M [二手] |
| 性能（自报，未验证） | 20→500-1000→100k TPS | TEE 低延迟 | 50x 解密 |
| 许可 | BSD-3-Clause-Clear，商用需许可 [一手] | 见 Gap | 见 Gap |
| Post-quantum | 是 | 否（TEE） | 是 |

### 7.3 Zama 在 Mantle 集成路径草图

前提：Mantle 是 OP Stack（geth fork）Optimistic Rollup L2，gas token MNT。Coprocessor 模式（最轻量）[推论，基于一手集成文档]：

1. 部署 fhEVM host contracts（ACL + Executor）到 Mantle。
2. 配置 Gateway 连接（Zama 或 self-hosted）。
3. 开发者 import fhEVM Solidity library + OZ Confidential Contracts 写 confidential 合约（RWA 场景可用 ERC7984Rwa）。
4. 无需 Mantle 协议层修改。
5. 考量：Zama 商业许可谈判；KMS 信任模型（9/13 + Nitro）对 Mantle 治理叙事的影响；FHE 性能（~20 TPS CPU）对 UX 的影响；FHE ACL 不可撤销对 GDPR 合规的结构性约束。

### 7.4 Inco 在 Mantle 集成路径草图

1. **Inco 当前仅支持 Base**——Mantle 集成需 Inco 团队扩展支持（关键依赖）。
2. 若支持：部署 Inco 合约套件到 Mantle + Inco 运营 TEE 节点连接 Mantle。
3. 无需 Mantle 协议层修改。
4. 考量：TEE 信任模型（Intel 硬件依赖 + 侧信道）对 Mantle 安全叙事的影响；Inco 扩展意愿/时间线；TEE 节点地理分布与延迟；force-exit 机制需确认（item-2 Gap）。

### 7.5 Fhenix 在 Mantle 路径备注

- chain-agnostic 协处理器，理论可扩展到 Mantle，但 EigenLayer 经济安全成熟度不如 Zama KMS，主网状态待核实，合规能力弱——**机构用例支撑力不足，暂列备选**。

- **Priority**: medium | **Dependencies**: item-1~6

---

## Diagrams

### diagram-1: 机密计算协处理器家族架构对比图（三栏）

```
        ┌──────────── Zama fhEVM ────────────┐  ┌──────── Inco Lightning ────────┐  ┌──────────── Fhenix CoFHE ───────────┐
Host    │ Host Contracts (ACL + Executor)    │  │ Inco Contract Suite            │  │ Relay Contract                       │
Chain   │  emit handle event (symbolic exec) │  │  encrypted types               │  │  emit FHE compute event              │
        └──────────────┬─────────────────────┘  └──────────────┬─────────────────┘  └──────────────┬──────────────────────┘
                       ▼                                        ▼                                   ▼
Off-    │ Coprocessors (TFHE-rs, 并行)        │  │ Confidential Compute Nodes      │  │ Relay Node → CoFHE pipeline          │
chain   │            │                         │  │  (Intel TDX TEE enclaves)       │  │  (validation→compute→publish→decrypt)│
        │            ▼                         │  │            │                    │  │            │                          │
        │ Gateway (ACL 聚合/跨链/协调)         │  │            ▼                    │  │            ▼                          │
        │            │                         │  │ Decryption Nodes Quorum         │  │ Threshold Decryption Network         │
        │            ▼                         │  │  + Callback Relayer (TEE)       │  │  + EigenLayer operators (restake)    │
        │ KMS (门限 MPC 9/13, Nitro, L1 链)    │  │                                 │  │                                      │
        └────────────────────────────────────┘  └────────────────────────────────┘  └──────────────────────────────────────┘
信任:     Cryptographic + MPC + HW(Nitro)          Hardware-Anchored (TEE)              Cryptographic + Economic (EigenLayer)
```

### diagram-2: Zama fhEVM 数据流时序图

```
User                Host Chain          Coprocessor        Gateway            KMS (9/13)
 │  encrypt(input)     │                    │                 │                  │
 ├────────────────────>│ symbolic exec      │                 │                  │
 │                     ├───emit handle─────>│ FHE compute      │                  │
 │                     │<──result handle────┤                 │                  │
 │  decrypt request    │                    │                 │                  │
 ├────────────────────>│ ACL check          │                 │                  │
 │                     ├──────────relay ACL──────────────────>│ verify perms     │
 │                     │                    │                 ├──threshold dec──>│
 │                     │                    │                 │<──signed plain───┤
 │   (public) plaintext on-chain  OR  (user) re-encrypt under user pubkey         │
 │<────────────────────────────────────────────────────────────────────────────┤
```

### diagram-3: 信任模型对比矩阵

```
                  Cryptographic   Hardware-Anchored   Economic       Organizational
                  (FHE/MPC)       (TEE)               (restake)      (operator)
Zama fhEVM          ███ (TFHE)      ██ (Nitro 加固)     ░ (质押激励)    ██ (KMS operator)
Inco Lightning      ░ (Atlas 未来)  ███ (Intel TDX)     ░              ██ (TEE 节点)
Fhenix CoFHE        ███ (TFHE/BFV)  ░                   ███ (EigenLayer) █ (operator)
```

### diagram-4: Mantle 集成路径草图

```
            ┌─────────────── Mantle L2 (OP Stack, MNT gas) ───────────────┐
            │  [开发者合约: Solidity + encrypted types + OZ ERC7984*]      │
            └───────────────┬──────────────────────┬──────────────────────┘
                            │ 路径 A: Zama          │ 路径 B: Inco
                            ▼                        ▼
              部署 fhEVM host contracts      部署 Inco 合约套件
              (ACL + Executor)               (需 Inco 扩展支持 Mantle)
                            │                        │
                            ▼                        ▼
              Zama/self-host Coprocessor      Inco TEE Compute + Decryption
              + Gateway + KMS(9/13)           Quorum + Callback Relayer
                            │                        │
              无协议层修改 | 商用许可          无协议层修改 | TEE 信任叙事
```

---

## Source Coverage（应 caveat #1，分级核对）

### 一手源（First-party，已使用）

| 源 | URL | 覆盖内容 |
|----|-----|---------|
| Zama Protocol Docs | docs.zama.org/protocol（KMS/ACL/Litepaper） | 五组件、9/13 门限、Galois Ring SSS、Nitro Enclave、解密流程 |
| Zama fhEVM Docs | docs.zama.ai/fhevm | encrypted types、symbolic exec、ACL 原语 |
| ERC-7984 EIP | eips.ethereum.org/EIPS/eip-7984 | 标准接口、DRAFT 状态、作者 |
| OZ Confidential Contracts | docs.openzeppelin.com/confidential-contracts + github | 全扩展栈、ERC7984Rwa/Omnibus/Hooked/IdentityCheck、版本史 |
| Inco | inco.org + inco.org/blog | Lightning 四组件、Base Sepolia(2025-04)、Base 主网(2026-06-15)、ERC-3643、Atlas roadmap |
| Circle × Inco | circle.com/blog（confidential ERC-20 framework） | confidentiality≠anonymity、delegated viewing |
| Fhenix CoFHE Docs | **cofhe-docs.fhenix.zone**（Quick Start / Local Dev） | pipeline 架构、permit、**主网「coming soon」限定** |
| Fhenix | fhenix.io（blog/manifesto/ecosystem） | CoFHE on Arbitrum/Base、Decomposable BFV、FHE Rollup 白皮书 |

### 审计源（第三方审计，介于一手与二手）

- OpenZeppelin Confidential Contracts v0.5 Diff Audit（openzeppelin.com/news）— **critical: hook 模块持久 FHE ACL 不可撤销**；v0.3.0 Release Audit。

### 二手源（Secondary corroboration）

- EEA Privacy Working Group Report（框架 rubric 对齐，cross-ref）；Figment「Inside Zama」（KMS 量化交叉验证）；GlobeNewsWire / Metaverse Post（Inco 发布/主网报道）；blog.eigenlayer.xyz、blog.arbitrum.io（Fhenix 经济安全/集成）；Medium（FHE Rollup 白皮书解读、Leosereinn「Encrypted Compute, Ranked」）；KuCoin Research「FHE 2026」；coinlaunch（Inco 融资）。

### 前置 section 交叉引用

- [`privacy-landscape-framework/final.md`](../privacy-landscape-framework/final.md)：五轴 rubric、6 维选择性披露向量、轻量级判定标准、信任模型三分法。

---

## Gap Analysis（诚实标注）

1. **Inco force-exit/escape hatch 机制**：一手文档未找到当 TEE 解密网络长期不可用时用户单方恢复加密余额的明确机制。**需向 Inco 团队确认。**
2. **Fhenix 主网真实状态**：官方博客（「live on Ethereum mainnet/Arbitrum」）与一手文档（「production mainnet support coming soon」）存在叙事张力。本 section 据文档保守判定「测试网为主 + 主网早期/限定」。**需链上合约地址或团队确认。**
3. **Fhenix 合规细节**：转账限制、冻结、observer、revocability 等在一手文档中粒度不足，多处标 Gap。
4. **Inco / Fhenix 许可证条款**：未在一手文档定位明确商业许可条款（Zama 为 BSD-3-Clause-Clear + 商用许可，已确认）。
5. **撤销性（三方共性）**：FHE ACL 不可撤销已由 OZ v0.5 审计就 Zama 栈坐实；Inco/Fhenix 的撤销机制均为 `unverified`。GDPR 合规影响为本家族结构性问题。
6. **性能**：全部为厂商自报，无独立第三方 benchmark。
7. **KMS 底层 L1 链共识安全 + operator 去中心化真实度**：需独立评估。

---

## Revision Log

- **Round 1（2026-06-23）**：基于 outline-approved（commit c4df1a5，approval ref 13c24e3b，severity minor）首次成稿。三项 outline review caveat 已落地：
  1. **Source taxonomy**：新增「来源分级约定」+ Source Coverage 分级表，全文标注 [一手]/[二手]/[审计]/[推论]，`cofhe-docs.fhenix.zone` 明确列为 Fhenix 一手源。
  2. **Deployment-status accuracy**：Inco 用一手源澄清 Base Sepolia(2025-04)→Base 主网(2026-06-15) 时间演进，消解「矛盾」；Fhenix 用一手文档「mainnet coming soon」限定博客「live」叙事，保守判定「测试网为主 + 主网早期/限定」；Zama 主网 2025-12 标注一手/二手。所有部署声明均带日期 + 来源 + 限定。
  3. **ERC-7984/OZ 完整扩展集**：补全 ERC7984Rwa（agent 角色/force-transfer/账户恢复）、ERC7984Omnibus（加密子账户地址）、ERC7984Hooked、ERC7984IdentityCheck + v0.5 版本史 + critical 审计发现（FHE ACL 不可撤销）。
