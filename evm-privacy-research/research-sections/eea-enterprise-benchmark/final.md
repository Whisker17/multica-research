---
topic: "EEA 企业隐私实现 Benchmark（7 方案 × 8 需求）"
project_slug: "evm-privacy-research"
topic_slug: "eea-enterprise-benchmark"
github_repo: "Whisker17/multica-research"
round: 1
status: final

artifact_paths:
  outline: "evm-privacy-research/outlines/eea-enterprise-benchmark.md"
  draft: "evm-privacy-research/research-sections/eea-enterprise-benchmark/drafts/round-1.md"
  final: "evm-privacy-research/research-sections/eea-enterprise-benchmark/final.md"

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23"
  outline_round: 1
  outline_commit: "570a51c451a151f38baf2eee6cdc4013ea509190"
  approval_evidence: "Review Verdict outline-approved, severity minor, comment ID 16ca1aed-5b69-410f-ac20-8013b82917cb"
  items_covered: ["item-1", "item-2", "item-3", "item-4", "item-5", "item-6", "item-7"]
  fields_investigated: ["eea_section_ref", "requirement_coverage", "contract_logic_privacy", "trust_model", "disclosure_vector", "settlement_model", "deployment_pattern", "maturity_readiness", "mantle_relevance", "reuse_provenance", "source_confidence"]
  diagrams_produced: ["diag-1", "diag-2", "diag-3", "diag-4", "diag-5", "diag-6"]
  review_caveats_addressed: ["M1-COTI-split-in-R4-table", "M2-matrix-caption", "M3-controlled-vocabulary"]
  source_requirement_coverage: "framework (WHI-254 final.md) reused as primary EEA口径; Paladin 3 internal sources reused with commit SHA; 6 solution profiles anchored to EEA §10 via framework + official-doc corroboration; 4 sidebar projects freshly researched with primary docs + access dates"

promotion_metadata:
  promoted_from: "evm-privacy-research/research-sections/eea-enterprise-benchmark/drafts/round-1.md"
  approved_draft_round: 1
  approved_draft_commit: "568e12ed8d68c52af5f205a7db485002a8004457"
  approval_evidence: "Review Verdict: approve, severity minor, comment ID ad00a3be-8bd4-4697-be02-48e5ee89ab0c, round 1"
  promoted_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  promoted_at: "2026-06-23"

multica_issue_id: "2b1c69d1-809b-4857-9e4d-083774dc4c15"
branch_name: "research/evm-privacy-research/eea-enterprise-benchmark"
base_commit: "eceaef1e1b4f7a17d7fc3eb4dd91560207f40629"
language: "中文"
research_depth: "deep-analysis"
mode: "single-issue-lightweight"
---

# EEA 企业隐私实现 Benchmark（7 方案 × 8 需求）

> 本 section 按 EEA Privacy Working Group 报告（*State of Privacy on Ethereum for Enterprise*, Version 1, April 2026，访问日期 2026-06-23）自身的标准化框架，benchmark 其 §10 profile 的 7 个企业隐私方案，对照 8 项企业需求，全部以 privacy-landscape-framework（WHI-254）的五轴 rubric、R1–R8 需求体系、选择性披露 6 维向量、轻量级判定标准为统一评分口径，确保与本项目其他 issue 横向可比。
>
> **方法论与复用边界**：本 issue 不重做框架已完成的逐方案深挖。WHI-254 final.md 已直接抓取 EEA 报告 HTML 并提炼了 7 方案的 §09 Readiness、§10 Profile、§08 信任模型、五轴评分与 6 维披露向量（经 review 接受）。本 benchmark 复用这些结论并重组为「按需求成矩阵 + 合约逻辑隐私标注 + 对 Mantle 决策」视角；Paladin 复用 3 份既有内部深度调研（不重做源码级深挖，仅核验易变事实）；4 个 sidebar 方案（Oasis Sapphire / Secret / Automata / Solana Confidential Transfers）为本轮新增调研，附官方来源 + 访问日期。每条结论标注 source_confidence 与 reuse_provenance。

> ⚠️ **Carry-forward caveat（来自 adversarial review，随 final.md 保留）**：本 benchmark 的 EEA 事实层（§09 Readiness Matrix、§10 Solution Profiles、§11 Decision Framework）继承自 WHI-254 同日（2026-06-23）的 HTML 提取，而非本轮独立重新推导。这与 lightweight 复用授权一致，并已在 Source Coverage（及 Gap Analysis G1）透明标注。**任何下游消费者若据本 section 做对外/销售面决策，应在具备网络访问的环境中直接重新核验 EEA §09/§10 原文。**

## Executive Summary

EEA 报告 §10 profile 的 7 个企业隐私方案——Paladin、Prividium、Linea Enterprise、Nightfall、COTI、Polygon CDK Enterprise、Silent Data——覆盖 6 类技术家族（GC/ZK/TEE/Privacy Groups/FHE/validium），无单一方案覆盖全部 8 项企业需求。本 benchmark 的核心结论：

1. **合约逻辑/业务状态隐私（R4）是真正的分水岭**。7 方案中只有 **Nightfall 是纯 token-only（值级）隐私**；其余 6 个方案均提供某种程度的合约逻辑/业务状态隐私（Silent Data/Linea/Prividium/Polygon CDK 完全；Paladin 通过 Pente、COTI 通过开发者标注机密参数提供部分）。对追求 institutional 业务（RWA 全生命周期、机构间合约、合规计算）的 Mantle，token-only 方案不能替代需要业务状态隐私的场景——这是本 issue 相对「附加未 profile 项」补全的实质缺口 [WHI-254 §2.4, §6.3; 本 issue item-4]。

2. **「轻量级 bolt-on vs 生产成熟度」的 tradeoff 决定 Mantle 候选空间极窄**。套用框架 4 项一票否决（新链/VM、新桥、全节点运维、硬分叉），7 方案中 5 个独立链方案（COTI-L2、Silent Data、Linea Enterprise、Prividium、Polygon CDK）被一票否决；Nightfall 因需运维 rollup operator 落入中量级；**仅 Paladin（sidecar，轻量~中量级）与 COTI-Coprocessor（multichain 协处理器，架构轻量但仅 Pilot）通过轻量级判定** [WHI-254 §5.6]。而成熟度最高（GA）的 COTI-L2 恰恰被否决。

3. **成熟度梯队**（EEA §09 Readiness Matrix，框架直接 HTML 提取）：COTI-L2 = General Availability（唯一 GA，证据均来自 COTI L2 网络部署）；Silent Data = Early Production（但 EEA 强制披露「Last audit firm + date: Not disclosed」，审计透明度缺口）；其余 5 方案 + COTI-Coprocessor = Pilot [WHI-254 §1.4]。厂商自报客户/性能数据一律标注「未独立验证」。

4. **Mantle verdict（item-7）**：**候选** = Paladin（提供 R4 执行级隐私 + sidecar bolt-on + 已有本项目深度调研 MPL/Sidecar 集成方案）、COTI-Coprocessor（架构 bolt-on，但需承担 Pilot 成熟度与能力未独立验证风险）；**参考** = Silent Data（TEE 执行隐私范式 + Automata on-chain attestation 可使其更 trust-minimized）、Prividium（合规向量最完整）、Nightfall（值级机密代币 + X.509 企业身份标准）、Polygon CDK（可配置隐私光谱）、Linea Enterprise（Private Validium 状态级隐私范式）；**出局** = COTI-L2（GA 但触发 V1/V2 一票否决，部署模式与 Mantle 轻量级偏好根本冲突）。

5. **Sidebar 替代信任模型**补充了 EEA 7 方案之外的选项：Oasis Sapphire（机密 EVM ParaTime，TEE，提供 R4，但需独立网络/OPL 桥，参考）；Secret Network（**机密 EVM 路线 2026 已暂停**，仅余 cross-chain CCL，参考/出局）；Automata（链上 TEE attestation verifier，**真正可 bolt-on 的验证积木**，可强化 TEE 方案信任最小化，候选/参考）；Solana Confidential Transfers（非 EVM、token-only、ZK ElGamal 程序 2025-06 起因漏洞被禁用至今，仅作机构机密代币对照）。

---

## Item Findings

### item-1: Benchmark 框架与列定义 — 8 企业需求 × Readiness Matrix × 框架 rubric 对齐

本 benchmark 的「列」（评估维度）全部锚定 WHI-254 框架，不自行新造维度 [reuse_provenance: 框架定义，复用既有]。

#### 1.1 Dispatch 8 需求 → 框架 R1–R8 映射

| Dispatch 8 需求 | 框架对应 | 在 benchmark 中的列 | source |
|---|---|---|---|
| transaction privacy（交易隐私） | R1 交易金额隐私（+R5 交易图） | R1（主）+ R5（补充列） | [WHI-254 §1.2] |
| balance privacy（余额隐私） | R2 账户余额隐私 | R2 | [WHI-254 §1.2] |
| smart contract privacy（智能合约隐私） | **R4 业务逻辑/合约状态隐私** | R4（本 issue 重点，见 item-4） | [WHI-254 §1.2] |
| regulatory compliance（合规） | R6 合规可审计性 | R6 | [WHI-254 §1.2] |
| selective disclosure（选择性披露） | R7 选择性披露 | R7 → 6 维向量 | [WHI-254 §1.2, item-4] |
| mainnet settlement（主网结算） | settlement 维度（部署形态相关） | settlement 列（受控词表，见 M3/§1.4） | 本 issue |
| technology stack（技术栈） | 轴 1 密码学路线 + 轴 4 部署形态 | 技术栈列（受控词表） | [WHI-254 §3.1] |
| trust model（信任模型） | 轴 3 信任模型 | 信任模型列（受控词表，对齐 EEA §08） | [WHI-254 §1.3, §3.1] |

**R3/R5/R8 补充列说明**：R3（对手方身份隐私）、R5（交易图隐私）、R8（执行策略/反 MEV-mempool）虽未在 dispatch 8 需求中显式列出，但属框架 R1–R8 完整体系。benchmark 矩阵保留这三列为「补充列」以保证与其他 issue（Aztec/ERC-7984/EIPs）完全同口径；缺少 EEA 证据时标注「未明确」 [推论；保证横向可比]。

#### 1.2 EEA Readiness Matrix（成熟度列）

直接复用框架从 EEA §09 HTML 提取的三阶段判定标准（不重新定义）[WHI-254 §1.4; reuse_provenance: 复用既有]：

| 阶段 | EEA 判定标准（原文要点） |
|------|-------------|
| **Pilot** | 有可演示系统；有命名参与方/合作伙伴；无需承载实时受监管流量 |
| **Early Production** | ≥1 命名客户生产上线；≥3 月连续运营；≥1 次第三方审计（最近 18 月）；处理真实资金/受监管流量 |
| **General Availability** | ≥3 命名客户跨 ≥2 机构类别；≥12 月运营；≥2 次审计（最近 24 月）；公开交易量/TVL |

#### 1.3 五轴 rubric（评分骨架）

复用框架五轴 [WHI-254 §3.1]：轴 1 密码学路线 / 轴 2 被保护数据维度（7 项）/ 轴 3 信任模型 / 轴 4 部署形态 / 轴 5 合规-选择性披露（6 维向量）。本 benchmark 中：「7×8 benchmark 矩阵」= 轴 2（7 数据维度）+ R6/R7 + settlement/技术栈/信任模型 的逐方案填充（item-5 §5.1）；「rubric 评分」= 五轴完整填充（item-5 §5.2）。

#### 1.4 受控词表（M3 — 类别列可比性）

为使 settlement / 技术栈 / 信任模型 三列跨方案可比（而非自由文本），预定义受控词表。单元格可携带多个标签：

- **settlement ∈** `{L1-settled, validium-DA, state-root+proof, optimistic-L2-batch, bridged, coprocessor-callback}`
  - `L1-settled`：commitments/nullifiers/proofs 直接锚定在结算 EVM 链上（如 Paladin 锚定到宿主链）
  - `validium-DA`：交易数据存链下 DA（机构自有或 DAC），不上 L1
  - `state-root+proof`：仅 state root + validity/ZK proof 上 L1
  - `optimistic-L2-batch`：作为 optimistic L2 将 batch 提交到 L1
  - `bridged`：资产须跨桥迁移到独立网络
  - `coprocessor-callback`：隐私计算在链下协处理器执行，结果回调宿主链
- **技术栈（密码学路线）∈** `{GC, ZKP, TEE, PG(Privacy Groups), FHE, validium, configurable, hybrid}`（对齐 EEA §06 6 类技术家族 + validium/configurable）
- **信任模型 ∈** `{Cryptographic, Hardware-Anchored, Organizational, Hybrid}`（对齐 EEA §08 三类 + 混合）[WHI-254 §1.3]

**source_confidence**：1.1–1.3 为框架直接复用（框架本身引 EEA §06/§08/§09/§10/§11）；1.4 受控词表为本 issue 为满足 M3 新增的编码规范（研究者设计，基于框架轴 1/3/4 与 settlement 语义）。

### item-2: Paladin 既有研究复用映射（REUSE ONLY，不重做深挖）

严格遵守 dispatch 边界：**Paladin 不做源码级深挖，仅核验易变事实**。本 item 将 3 份既有内部深度调研无损映射到本项目 rubric，并标注每条结论的 reuse_provenance。

#### 2.1 复用来源与 rubric 映射

| 内部来源 | 复用内容 | 映射到 rubric 字段 |
|---|---|---|
| `202606-internal-sharing/research-sections/Paladin Deep Dive.md`（commit eceaef1 树内） | Noto/Zeto（Layer B）、Pente（Layer C）三类隐私域；五阶段交易流（Init→Assemble→Endorse→Prepare→Submit）；KYC 合规稳定币转账、RWA 债券全生命周期、tokenized equities 工作流；Besu 可替换性；缺陷（notary 单点、Pente N-of-N 不可扩展、Groth16 trusted setup、UTXO 状态爆炸）；MPL standalone vs L2 Sidecar 集成方案 | 轴1（PG+ZKP）、R4（Pente ephemeral EVM 执行级隐私）、轴3（notary/组织信任）、轴5 披露向量、部署形态（sidecar）、Mantle 集成 |
| `202606-internal-sharing/research-sections/enterprise-privacy/final.md`（item-6/7） | 代表性项目隐私案例卡（Paladin: Noto/Zeto/Pente/Atom, base ledger 只见 commitments/nullifiers/proofs, pilot-to-production candidate, "MPL/独立隐私网络可比直接塞进 L2 更现实"）；技术路线对比矩阵（Paladin sidecar: 隐私对象=私有 token/private EVM state, 信任=sidecar domain/ZK/notary, 成熟度=pilot, Mantle fit=中, 适合 MPL）；失败模式（与基础链 finality/DA/费用错配、私有状态恢复复杂） | Mantle fit 定位、失败模式、成熟度交叉印证 |
| `mantle-enterprise-blockchain/report/final-report.md`（§5.5/§5.6） | 隐私四受众（公共观察者/其他租户/operator/监管者）；L1/L2/L3 隐私与合规比较；「L2 operator 隐私默认较弱，sequencer 通常须见明文」；sidecar 在 L1/L2/L3 决策框架中的位置 | 部署形态背景、Mantle operator 信任约束、bolt-on 可行性 |

#### 2.2 本轮核验的「易变事实」（仅这些验证，附来源）

- **EEA §09/§10 对 Paladin 的口径与成熟度**：框架已从 EEA §09 HTML 直接提取 Paladin = **Pilot**，证据为 Bank of Indonesia Digital Rupiah (Project Garuda) PoC / HKMA eHKD Phase 2 / Banco Central do Brasil Drex（均 PoC 阶段）[WHI-254 §1.4, `rm-status pilot`]。本轮核验：与 Paladin Deep Dive 的「pilot-to-production candidate」定位一致 [reuse_provenance: 本轮核验，框架 EEA 提取 + 内部来源交叉一致]。
- **Paladin 项目状态/官方入口**：LF Decentralized Trust (LFDT) 项目，Kaleido 维护；Noto/Zeto/Pente/Atom 域模型 [Paladin Deep Dive §1–§2; LFDT "Announcing Paladin", 2025-02，经框架 §4.3 引用]。本轮核验：与既有调研一致，未发现状态变更 [reuse_provenance: 本轮核验]。
- **与框架 Paladin 向量一致性**：框架 §4.4 给出 Paladin/Noto 向量（authority: `notary/observer`+`key-holder`；trigger: `automatic`+`compliance-gate`；payload: `all`；scope: `domain-wide`；revocability: `partial-auditable-log*`；leakage: `existence`）[WHI-254 §4.3-4.4]。本 benchmark 直接采用该向量 [reuse_provenance: 复用既有]。

#### 2.3 直接复用、不重新验证的结论（附来源路径）

以下为既有深度调研结论，直接引用 [reuse_provenance: 复用既有，Paladin Deep Dive]：

- **Noto**（confidential UTXO + notary 背书）：链上只存 opaque state ID / `_unspent` / `_locked` / lock hash；mint/transfer/burn/createLock 由 notary 背书提交；信任锚是部署时指定的单一 notary 地址 → 组织信任，单点风险 [Paladin Deep Dive §2.1.1]。
- **Zeto**（ZK token）：commitment = `Poseidon(value, salt, ownerPubKey)`，nullifier = `Poseidon(value, salt, ownerPrivKey)`；链上验证 Groth16 proof；变体含 `AnonNullifierKyc` 等支持 KYC；Groth16 trusted setup + 电路升级成本是主要限制 [Paladin Deep Dive §2.1.2]。
- **Pente**（ephemeral EVM，**R4 执行级隐私的关键**）：在隐私域内按需实例化 Besu Java EVM，执行私有 Solidity 合约，捕获 account state diff，仅把 input/read/output state hash + EIP-712 成员签名锚定到 Layer A；合约代码、storage diff、参数在组内分发不上链；当前语义 N-of-N（100%）背书，成员集合创建后不可变 → 适合 2-10 人小组，成员离线阻塞交易 [Paladin Deep Dive §2.2]。
- **Atom**：一次性原子交换合约，支撑 DvP（Noto bond ↔ Zeto cash 同笔 EVM 交易原子结算）[Paladin Deep Dive §3.2]。
- **部署形态**：Paladin 是运行在基础 EVM 旁的 privacy transaction runtime（sidecar），不分叉 EVM client；通过 17 个标准 EVM JSON-RPC 方法连接结算链；Mantle op-geth 已基本满足（BN254 预编译、`newHeads`、`eth_getBlockReceipts` 等）[Paladin Deep Dive §1.1, §4, Q1]。
- **缺陷**：Noto 单点 notary 风险；Pente N-of-N 不可动态管理成员（类老式状态通道）；Go/Java 混合运行时复杂；UTXO 状态爆炸；Groth16 trusted setup 与电路升级成本；早期协议（MPC、合规原生设计待实现）[Paladin Deep Dive Q2]。

**复用边界声明**：本 item 所有 Paladin 技术机制结论均为复用既有深度调研，本轮仅核验了 §2.2 三项易变事实。未进行任何 Paladin 源码级重新深挖。

**source_confidence**：内部复用（Paladin Deep Dive + enterprise-privacy + mantle-enterprise，均为已接受的内部研究）+ 框架 EEA 提取交叉印证；易变事实本轮核验一致。

### item-3: 6 方案逐方案 deep profile — 对照 8 维度

对 6 个新调研方案逐一 profile。每个方案按统一 8 维模板：①路线/技术家族 ②隐私原语 ③合约逻辑/业务状态隐私（R4）④信任模型 ⑤选择性披露模型 ⑥主网 settlement ⑦技术栈/部署形态 ⑧成熟度/客户。以 EEA §10 为锚（框架已直接提取），官方文档补充/核验，差异标注。**厂商自报性能/客户数据一律标注「未独立验证」**。

#### 3.1 Prividium（ZKsync / Matter Labs）— 许可型 ZK L2

- **①路线/技术家族**：ZKP + Privacy Groups（permissioned ZK Stack L2）。**⑦技术栈** = `ZKP` + `validium`/permissioned。
- **②隐私原语**：仅 state root + ZK validity proof 上链；交易输入/地址/calldata 对公众不可见不可推断 [WHI-254 §4.3 Prividium: "No transaction inputs, addresses, or calldata are visible or inferable from public data"]。
- **③R4 合约逻辑/业务状态隐私**：**完全（A+B 兼备）**——permissioned L2 同时隐藏值和执行，operator 在执行中可见全部数据，但对外仅暴露 state root + proof [WHI-254 §2.4, §6.3]。
- **④信任模型**：`Cryptographic`（ZK validity proof）+ `Organizational`（Proxy RPC + RBAC operator、Okta/Azure IdP）= `Hybrid` [WHI-254 §3.2 轴3]。
- **⑤选择性披露**：authority `smart-contract`+`regulator`；trigger `compliance-gate`+`audit-request`+`automatic`；payload `all`；scope `per-contract`+`chain-wide`（合约-函数级 RBAC）；revocability `permanent`+`auditable-log`（SOC 2 Type I 暗示审计日志）；leakage `none`（对公众）[WHI-254 §4.3-4.4]。**7 方案中合规向量最完整**。
- **⑥settlement**：`validium-DA` + `state-root+proof`（仅 state root + ZK proof 结算到 Ethereum，DA 链下/许可）。
- **⑦部署形态**：独立 permissioned L2 on ZK Stack（需运维 ZK Stack 全套 + Proxy RPC + Admin Dashboard + IdP 集成）→ **C 类独立链** [WHI-254 §5.1]。
- **⑧成熟度**：EEA §09 = **Pilot** [WHI-254 §1.4]。本轮二手检索另见「Deutsche Bank Memento Chain」「Cari Network（5 家美国地区银行，Q3 2026 pilot 目标）」等命名（[二手检索，press-reported，**未独立验证**；EEA §09 仍判 Pilot]）。SOC 2 Type I 报告（2026-05）[WHI-254 §4.3，官方文档补充]。

#### 3.2 Linea Enterprise（Consensys）— Private Validium + ZK

- **①路线/技术家族**：ZKP + Privacy Groups。**⑦技术栈** = `ZKP` + `validium` + `PG`(permissioned)。
- **②隐私原语**：Private Validium——交易数据存机构自有基础设施（链下 DA），仅 cryptographic fingerprint（state root）结算到 Ethereum [WHI-254 §2.4: "only cryptographic fingerprint settles to Ethereum"]。
- **③R4**：**完全（状态级 B）**——Validium 状态不外泄，对公众完全不可观察 [WHI-254 §2.5, §6.3]。
- **④信任模型**：`Cryptographic`（ZK validity proof）+ `Organizational`（permissioned sequencer/operator、Besu plugin）= `Hybrid`；operator 作为 observer 可见全部数据 [WHI-254 §3.2, §4.3]。
- **⑤选择性披露**：authority `smart-contract`+`notary/observer`；trigger `automatic`；payload `all`；scope `domain-wide`；revocability `permanent`(RBAC)；leakage `none`（permissioned 网络内）[WHI-254 §4.3-4.4]。
- **⑥settlement**：`validium-DA` + `state-root+proof`。
- **⑦部署形态**：独立 Validium/permissioned L2 on Lineth stack（需运维 Besu 执行 + Maru 共识 + coordinator + gnark prover）→ **C 类独立链** [WHI-254 §5.1]。
- **⑧成熟度**：EEA §09 = **Pilot**；SWIFT 合作（private testnet, 12+ 银行参与）[WHI-254 §1.4，厂商/press-reported，**未独立验证**]。

#### 3.3 Nightfall（EY）— 开源 ZK 机密代币协议

- **①路线/技术家族**：ZKP（ZK rollup）+ X.509 PKI 身份层。**⑦技术栈** = `ZKP`。
- **②隐私原语**：ZK commitments for ERC-20/721/1155 值传输 [WHI-254 §2.5]。
- **③R4**：**否（纯值级 A / token-only）**——聚焦 token 转账金额/余额隐私，不覆盖通用合约逻辑或合约状态隐私 [WHI-254 §2.4, §3.2 轴2: 逻辑 ○ / 状态 ○]。**7 方案中唯一的 token-only 方案**（见 item-4）。
- **④信任模型**：`Cryptographic`（ZKP）+ `Organizational`（X.509 CA、rollup sequencer 活性）= `Hybrid` [WHI-254 §3.2]。
- **⑤选择性披露**：authority `key-holder`；trigger `compliance-gate`（X.509 KYC-gating）+`viewing-key-share`；payload `amount+identity`；scope `per-tx`；revocability `one-time`*（viewing key 分发后无明确撤销机制）；leakage `graph`+`existence`（deposit/withdraw 关联 L1/L2 地址）[WHI-254 §4.3-4.4]。
- **⑥settlement**：`state-root+proof`（ZK rollup，proof + state root 结算到 L1）。
- **⑦部署形态**：链上 ZK rollup 合约套件（需 rollup operator 运维 sequencer + prover）→ 中量级（V3）；Starknet 集成模式下 prover 可外包，运维负担降低 [WHI-254 §5.6 Nightfall 判定说明]。
- **⑧成熟度**：EEA §09 = **Pilot**；Nightfall_4 升级（2025-04，X.509 企业身份）、Starknet 集成（2026-02 "confidential B2B payments"）[WHI-254 §1.4, §4.3，官方文档补充，**未独立验证**]。

#### 3.4 COTI — 混淆电路（Garbled Circuits）【M1：沿用框架 COTI-L2 / COTI-Coprocessor 拆分】

框架已确立 COTI 须按部署模式拆分（[WHI-254 §1.4/§2.4/§5.6]）；benchmark 保持一致。**两种模式共享同一 GC 技术栈与同一 R4 分类等级（值级 + 执行级部分），差异仅在部署形态与成熟度/置信度**：

- **①路线/技术家族**：GC（首个将混淆电路用于区块链）。**⑦技术栈** = `GC`（COTI-L2 另探索 +ZKP/MPC）。
- **②隐私原语**：GC 加密 "inputs, balances, on-chain state, and smart contract logic, encrypted end-to-end"；"Standard Solidity (Fully EVM compatible) with parameters specifying confidential data elements"——开发者显式标注机密参数 [WHI-254 §2.4 引 EEA §10 COTI Solution Profile]。
- **③R4**：**部分（值级 A + 执行级 B 部分）**——GC 对开发者标注的合约逻辑/状态加密计算，评 ◐ 而非 ●，因需显式标注而非像 TEE 自动保护全部执行。**COTI-L2 与 COTI-Coprocessor R4 分类等级相同**；COTI-Coprocessor 标注为「announced，multichain 部署下未独立验证」[WHI-254 §2.4, §3.2]。
- **④信任模型**：`Cryptographic`（GC）+ `Organizational`（COTI-L2: L2 网络 operator；COTI-Coprocessor: multichain operator + Axelar 跨链信任）= `Hybrid` [WHI-254 §1.3, §3.2]。
- **⑤选择性披露**：authority `key-holder`（permissioned view-keys）；trigger `viewing-key-share`；payload `amount+identity`；scope `per-tx`+`per-account`；revocability `unverified-revocable`*（声称支持但技术机制未经公开文档确认）；leakage `existence`+`timing`（COTI-Coprocessor 另有跨链路由泄露）[WHI-254 §4.3-4.4]。
- **⑥settlement**：COTI-L2 = `bridged`（"Deploy on COTI network or bridge existing assets"，"use of COTI L2 network required"）；COTI-Coprocessor = `coprocessor-callback`（GC 链下计算 + 宿主链隐私合约接口）[WHI-254 §5.1 引 EEA §10 COTI Integration Requirements]。
- **⑦部署形态**：COTI-L2 = **C 类独立 L2 + 资产桥**；COTI-Coprocessor = **A 类 bolt-on 协处理器**（multichain，"70+ chains planned 2026"）[WHI-254 §5.1]。
- **⑧成熟度**：COTI-L2 = **General Availability**（唯一 GA；证据 Privex $25bn、StaTwig 10M、ECB Digital Euro Pioneer、~14 月主网、5 次审计 Sayfer/Hacken——**均来自 COTI L2 网络部署**）；COTI-Coprocessor = **Pilot**（仅首笔跨链交易 via Axelar，无独立命名客户/生产流量，能力 announced 未独立验证）[WHI-254 §1.4，厂商证据**未独立验证**]。

#### 3.5 Polygon CDK Enterprise — 可配置隐私光谱

- **①路线/技术家族**：可配置（"Privacy on Polygon CDK is a spectrum, not a switch"）。**⑦技术栈** = `configurable`（permissioned access → confidential validium → confidential compute，可叠加 `FHE`/`TEE`）。
- **②隐私原语**：分层——permissioned access（值可见身份门控）/ confidential validium（仅 cryptographic fingerprint 上链）/ confidential compute（FHE/TEE）[WHI-254 §4.3]。
- **③R4**：**可配置（confidential validium/compute 模式下完全 B）**——取决于隐私模块选择，◐→● [WHI-254 §3.2 轴2, §6.3]。
- **④信任模型**：`configurable`/`Hybrid`（取决于模块：FHE 假设 / TEE 硬件信任 / ZK 密码学 + operator 诚信）[WHI-254 §3.2]。
- **⑤选择性披露**：authority `smart-contract`+`notary/observer`（Gateway + enterprise SSO）；trigger `compliance-gate`+`automatic`；payload `all`；scope `chain-wide`；revocability `permanent`；leakage `none`(confidential validium)/`existence`(permissioned access) [WHI-254 §4.3-4.4]。
- **⑥settlement**：`validium-DA` + `state-root+proof`（confidential validium 模式）。
- **⑦部署形态**：独立 private chain/validium（需运维 CDK 全套 + Gateway + permissioned explorer）→ **C 类独立链** [WHI-254 §5.1]。
- **⑧成熟度**：EEA §09 = **Pilot**；T-REX Ledger（Apex Group $100B tokenized RWAs，Zama FHE + ERC-3643，2026-03 公布）[WHI-254 §1.4，厂商/press-reported，**未独立验证**]。

#### 3.6 Silent Data（Applied Blockchain）— TEE-based programmable privacy

- **①路线/技术家族**：TEE（Intel SGX / AWS Nitro）。**⑦技术栈** = `TEE`。
- **②隐私原语**：TEE 隔区内全执行隐私，标准 Solidity，"commercially sensitive data is never visible to the operator"；作为 OP Stack L2 [WHI-254 §2.5, §4.3]。
- **③R4**：**完全（执行级 + 状态级 B）**——TEE 自动保护全部合约执行和状态，无需开发者标注（与 COTI 的关键区别）[WHI-254 §2.4, §3.2]。
- **④信任模型**：`Hardware-Anchored`（TEE 制造商 Intel/AWS 可信、硬件无侧信道、远程证明服务可用）[WHI-254 §1.3, §3.2]。
- **⑤选择性披露**：authority `smart-contract`；trigger `automatic`；payload `all`；scope `chain-wide`；revocability `permanent`+`auditable-log`（ISO/IEC 27001 + 实时密码学证明）；leakage `existence`（OP Stack batch 提交揭示交易存在性/时序）[WHI-254 §4.3-4.4]。
- **⑥settlement**：`optimistic-L2-batch`（OP Stack L2，batch 到 L1）。
- **⑦部署形态**：独立 TEE L2 on Optimism Superchain（需运维独立 L2 节点 + TEE 隔区）→ **C 类独立链** [WHI-254 §5.1]。
- **⑧成熟度**：EEA §09 = **Early Production**，但 **EEA 强制披露「Last audit firm + date: Not disclosed」（审计透明度缺口）** [WHI-254 §1.4, G7]；Archax 代币化基金（Aberdeen/BlackRock/Fidelity/State Street）2026-02、CRYOPDP/DHL SAP 奖 2025-12、Bank of England Digital Pound Lab Phase 1 [WHI-254 §1.4，厂商/press-reported，**未独立验证**]。

**source_confidence（item-3）**：6 方案 profile 主体复用框架 §2.4/§2.5/§3.2/§4.3-4.4 的 EEA §10 直接提取与官方文档补充；Prividium 命名客户为本轮二手检索补充，明确标注 press-reported 未独立验证；所有厂商自报客户/性能数据标注未独立验证。

### item-4: 合约逻辑/业务状态隐私标注（R4）— token-only vs contract-logic privacy

显式回答 Step 3：7 方案中哪些提供合约逻辑/业务状态隐私（R4），哪些仅 token-only。这是本 issue 对 institutional Mantle 的核心增量。

#### 4.1 三层隐私区分（复用框架 §2.4 口径）

- **值级（Value-Level, A）**：仅 token 转账金额/余额（"看不见数字的银行流水"）
- **执行级（Execution-Level, B）**：全/部分智能合约执行逻辑（"看不见代码的计算机"）
- **状态级（State-Level, B）**：链上状态完全不可观察（"看不见存储"）

#### 4.2 7 方案 R4 标注表【M1：COTI 拆分为两行；两模式共享同一 R4 等级】

| 方案 | token-only? | R4 合约逻辑/业务状态隐私 | 层级 | 机制 | source |
|---|---|---|---|---|---|
| Paladin | 否（Pente 提供） | **部分（执行级，域内可见）** | A+B | Pente ephemeral EVM 在隐私域内执行全部合约逻辑；Noto/Zeto 为值级 | [Paladin Deep Dive §2.2; WHI-254 §6.3] |
| Prividium | 否 | **完全（A+B）** | A+B | permissioned L2 + ZK，同时隐藏值和执行 | [WHI-254 §6.3] |
| Linea Enterprise | 否 | **完全（状态级 B）** | B | Private Validium 状态不外泄 | [WHI-254 §6.3] |
| **Nightfall** | **是（token-only）** | **否（仅值级 A）** | A | ZK commitments，仅 token 值传输 | [WHI-254 §2.4, §6.3] |
| **COTI-L2** | 否（部分） | **部分（开发者标注机密参数）** | A+B(部分) | GC encrypted computation on 标注的 logic/state | [WHI-254 §2.4, §6.3] |
| **COTI-Coprocessor** | 否（部分） | **部分（同 COTI-L2 等级；announced，未独立验证）** | A+B(部分, announced) | 声称继承同一 GC 栈；multichain 部署下未验证 | [WHI-254 §6.3, G8] |
| Polygon CDK | 否（可配置） | **可配置（confidential validium/compute 模式下完全 B）** | A+B(可配置) | 可配置 FHE/TEE/Validium | [WHI-254 §6.3] |
| Silent Data | 否 | **完全（执行级+状态级 B）** | B | TEE 全执行隐私（自动，无需标注） | [WHI-254 §2.4, §6.3] |

**M1 一致性说明**：COTI 在本表拆分为 COTI-L2 / COTI-Coprocessor 两行，与 item-3.4 / item-5.1 / item-7.1 口径一致。**两种模式共享同一 R4 分类等级（A+B 部分）**——Coprocessor 声称继承 COTI-L2 的 GC 技术栈，差异仅在 multichain 部署下能力未独立验证（标注 announced），不改变 R4 等级本身。

#### 4.3 对 Mantle 的意义

- **唯一 token-only = Nightfall**：只能隐藏「数字」（金额/余额），不能隐藏业务逻辑/状态。适合机密支付/机密代币场景，但无法承载需要合约逻辑隐私的 institutional 业务（如机构间私有合约、RWA 簿记、合规计算）。
- **提供合约逻辑/业务状态隐私（R4）= 其余 6 方案**：其中 Silent Data/Linea/Prividium/Polygon CDK 为完全 B（状态级，链上不可观察）；Paladin（Pente）和 COTI 为部分（执行级，分别为域内可见 / 开发者标注）。
- **隐私账本二义判定**（引框架 [WHI-254 item-6]）：Nightfall = A（Token Ledger）；Silent Data/Linea = B（Business-State Ledger）；Prividium/Polygon CDK/Paladin/COTI = A+B 兼备（来源不同：准入控制 / 密码学 / TEE / GC）。
- **结论**：institutional Mantle 若目标包含业务状态隐私，候选必须落在「提供 R4」的 6 个方案中，再叠加轻量级判定（item-7）——这把候选进一步压缩到 Paladin（Pente 提供执行级 R4 且 bolt-on）。

**source_confidence（item-4）**：R4 分层与方案分类直接复用框架 §2.4/§6.3（框架引 EEA §10）+ Paladin Deep Dive §2.2（Pente）；M1 拆分为本 issue 应 review 要求处理。

### item-5: 7×8 Benchmark 矩阵 + 五轴 rubric 评分填充

#### 5.1 Benchmark 矩阵（核心交付物，见 diag-1）

**【M2 矩阵口径说明】** 本矩阵满足验收标准 #1「按 8 项企业需求成矩阵」，但实际呈现为 **8 行 × 11 列**，原因如下，避免被误读为严格 7×8 网格不匹配：

- **行（8 行）**：7 个 EEA 方案，其中 **COTI 按框架口径拆分为 COTI-L2 / COTI-Coprocessor 两行**（其余 6 方案各 1 行）= 8 行。
- **列（11 列）**：dispatch 的 8 项企业需求映射为——R1 金额 / R2 余额 / R4 合约逻辑 / R6 合规 / R7 披露（5 列 ●◐○ 等级）+ settlement / 技术栈 / 信任模型（3 列类别标签，受控词表见 §1.4）= 8 需求对应 8 列；**另加 R3 身份 / R5 图 / R8 订单流 3 个补充列**（保证与框架及其他 issue 完全同口径）= 11 列。
- **图例**：● 完全保护 / ◐ 部分保护 / ○ 不保护 / —— 未明确。类别列用受控词表标签。COTI-Coprocessor 的数据维度评分继承 COTI-L2 并标 †（multichain 未独立验证）。

| 方案 | R1 金额 | R2 余额 | R4 合约逻辑 | R6 合规 | R7 披露 | settlement | 技术栈 | 信任模型 | R3 身份 | R5 图 | R8 订单流 |
|---|:--:|:--:|:--:|:--:|:--:|---|---|---|:--:|:--:|:--:|
| Paladin | ● | ● | ◐ | ◐ | ● | L1-settled | PG+ZKP | Org+Crypto(Hybrid) | ◐ | ○ | ○ |
| Prividium | ● | ● | ● | ● | ● | validium-DA, state-root+proof | ZKP+validium | Hybrid | ◐ | ◐ | ◐ |
| Linea Ent. | ● | ● | ● | ◐ | ● | validium-DA, state-root+proof | ZKP+validium+PG | Hybrid | ◐ | ◐ | ◐ |
| Nightfall | ● | ● | ○ | ◐ | ◐ | state-root+proof | ZKP | Crypto+Org(Hybrid) | ◐ | ◐ | ○ |
| COTI-L2 | ● | ● | ◐ | ◐ | ◐ | bridged | GC | Hybrid | ◐ | ◐ | ○ |
| COTI-Coproc. | ●† | ●† | ◐† | ◐† | ◐† | coprocessor-callback | GC(announced) | Hybrid | ◐† | ◐† | ○ |
| Polygon CDK | ● | ● | ◐→● | ● | ● | validium-DA, state-root+proof | configurable(FHE/TEE/ZK) | Hybrid/config | ◐ | ◐ | ◐ |
| Silent Data | ● | ● | ● | ◐ | ● | optimistic-L2-batch | TEE | Hardware-Anchored | ◐ | ◐ | ◐ |

注：R1/R2 所有方案 ● 为核心卖点 [WHI-254 §3.2]。R6 合规列以「向量是否含 regulator/compliance-gate/auditable-log」综合判定（Prividium/Polygon CDK 最强 ●；Paladin/Nightfall/COTI/Silent Data/Linea ◐——存在 unverified/partial 标签或缺审计日志）[WHI-254 §4.5]。R7 披露列以 6 维向量完备度判定。数据维度评分整体复用 [WHI-254 §3.2 轴2]。

#### 5.2 五轴 rubric 填充（见 diag-3）

直接复用框架 §3.2 各方案五轴评分，按 benchmark 视角汇总 [reuse_provenance: 复用既有 WHI-254 §3.2]：

| 方案 | 轴1 密码学路线 | 轴2 数据维度（R1/R2/R4 摘要） | 轴3 信任模型 | 轴4 部署形态（轻量级判定） | 轴5 披露向量摘要 |
|---|---|---|---|---|---|
| Paladin | PG+ZKP（Zeto trusted setup 取决于电路） | 值级● + 执行级◐(Pente) | Org+Crypto（notary/组成员） | sidecar 合约套件 → **轻量~中量级** | notary/observer+key-holder, all, domain-wide |
| Prividium | ZKP（ZK Stack） | A+B 全● | Hybrid（ZK+RBAC operator） | 独立 L2 → **一票否决** | smart-contract+regulator, all, per-contract |
| Linea Ent. | ZKP（gnark, 计划 RISC-V zkVM） | 状态级● | Hybrid（ZK+permissioned seq） | 独立 Validium → **一票否决** | smart-contract+observer, all, domain-wide |
| Nightfall | ZKP（proof system 决定 setup） | 仅值级●（R4 ○） | Hybrid（ZK+X.509 CA） | ZK rollup → **中量级**（V3） | key-holder, amount+identity, per-tx |
| COTI-L2 | GC（无 trusted setup） | 值●+执行◐ | Hybrid（GC+L2 operator） | 独立 L2+桥 → **一票否决**（V1/V2） | key-holder, amount+identity |
| COTI-Coproc. | GC(announced) | 值●†+执行◐† | Hybrid（GC+Axelar） | bolt-on 协处理器 → **轻量级**（非 GA） | key-holder†, amount+identity† |
| Polygon CDK | configurable（FHE 支持→后量子较好） | 可配置 A+B | configurable/Hybrid | 独立 private chain → **一票否决** | smart-contract+observer, all, chain-wide |
| Silent Data | TEE（不需 trusted setup） | 执行+状态级● | Hardware-Anchored | 独立 TEE L2 → **一票否决** | smart-contract, all, chain-wide, auditable-log |

#### 5.3 横向对齐校验

将本 benchmark 评分与框架 final.md 及已完成 issue 对照：

- **与框架 §3.2/§4.4 一致**：本 benchmark 轴2 数据维度、披露向量、信任模型直接复用框架同口径表，无差异（同一 EEA 提取、同一访问日期）[reuse_provenance: 复用既有]。
- **与 zk-privacy-chain-aztec 对照**：Aztec（非 EEA 成员）= 密码学级全执行隐私（R4 完全 ●，纯 Cryptographic Trust），部署为 C 类独立非 EVM 链（一票否决 V1/V2），成熟度 Pilot-Alpha（有未修复关键漏洞）。在 benchmark 谱中 Aztec 隐私最高但部署最重、成熟度最低——可作为 R4「密码学级上限」参照，EEA 7 方案中无人达到 Aztec 的密码学级 R4（Silent Data 以硬件信任达到执行级，但非密码学级）[zk-privacy-chain-aztec/final.md 对照；推论]。
- **与 erc7984-confidential-token 对照**：ERC-7984（FHE 机密代币标准）与 Nightfall 同属值级（A，token-only），是 Nightfall/COTI 值级隐私的标准化对照 [erc7984 issue 对照；推论]。

**source_confidence（item-5）**：矩阵与 rubric 填充直接复用框架 §3.2/§4.4/§4.5（EEA §10 提取）；M2 口径说明与受控词表为本 issue 处理；横向对照基于本项目已完成 issue 的 final.md。

### item-6: 替代信任模型 Sidebar — Oasis Sapphire / Secret / Automata（+ 可选 Solana）

EEA 7 方案之外的替代信任模型补充参考（**本轮新增调研**，附官方来源 + 访问日期 2026-06-23）。明确标注为「补充参考」，调研深度低于 7 方案，仅填信任模型 + 部署形态 + R4 + Mantle 参考价值。

#### 6.1 Oasis Sapphire — 机密 EVM ParaTime（TEE）

- **路线/信任模型**：TEE-based 机密 EVM ParaTime on Oasis Network（Intel SGX/TDX），默认加密合约状态与 calldata；信任模型 `Hardware-Anchored`（SGX 远程证明 + Oasis Key Manager 分发密钥）[docs.oasis.io/build/sapphire/，访问 2026-06-23]。
- **R4 合约逻辑隐私**：**完全（执行级+状态级 B）**——加密合约执行 + 加密状态，`eth_getStorageAt` 返回 0，全 Solidity 兼容；提供「合约逻辑隐私的 EVM 兼容路径」参考。caveat：访问模式/状态大小可能泄露 [docs.oasis.io/build/sapphire/develop/concept/，访问 2026-06-23，部分 Medium 二手]。
- **选择性披露**：EIP-712 签名 view call 按用户授权读取；未认证 `eth_call` 的 `msg.sender` = `address(0)` [docs.oasis.io/build/sapphire/develop/authentication/，访问 2026-06-23]。
- **部署形态/settlement**：独立 ParaTime（主网 2022-07，chainId 23294），**非 bolt-on**——须部署在 Oasis 或通过 Oasis Privacy Layer (OPL) 消息桥（Celer IM/Hyperlane/Router）让 Mantle 等宿主链调用 Sapphire 上的机密合约、结果回传。settlement = `bridged`/OPL coprocessor 式 [docs.oasis.io/build/opl/，访问 2026-06-23]。
- **成熟度**：主网 2022-07 起；集成 Ocean Predictoor、illumineX（厂商自报，**未独立验证**）；正式安全审计细节官方未充分披露 [oasis.net blog，访问 2026-06-23]。
- **Mantle 相关性**：**参考**——Sapphire 的「默认加密状态 + EIP-712 认证读取」是机密 EVM 的可借鉴设计范式；实际集成需以 Sapphire 作 co-processor（经 OPL 桥），资产/用户留 Mantle、敏感逻辑外包 Sapphire，但这引入独立网络与桥，非 1:1 L2 隐私替代。

#### 6.2 Secret Network — 机密 EVM 路线 2026 已暂停

- **路线/信任模型**：TEE-based 机密 CosmWasm「secret contracts」（Intel SGX），加密默认状态；信任模型 `Hardware-Anchored`（SGX + 远程证明）+ 网络级加密密钥；2026-01 因 TEE 层漏洞（Wiretap.fail / TEE.fail）转向半许可模型 + MPC 分布式 seed + 计划 AMD SEV-SNP [docs.scrt.network，scrt.network/blog/secret-network-2026-roadmap，访问 2026-06-23]。
- **EVM 状态（关键）**：**机密 EVM（SecretEVM）路线 2026 已正式暂停**——2026 roadmap 原文："decided to pause both Gramine migration and EVM compatibility … the cost-to-benefit ratio did not justify continued investment at this stage"；现仅提供 cross-chain Confidential Computing Layer (CCL) via SecretPath 作为 EVM 链的机密计算服务层（非原生 EVM rollup）[scrt.network/blog/secret-network-2026-roadmap，访问 2026-06-23]。
- **R4**：完全（机密合约执行 + 加密状态，CosmWasm）；但 EVM 路径不可用。
- **部署形态**：独立 Cosmos-SDK L1（非 EVM L2 bolt-on），主网 2020 起。
- **Mantle 相关性**：**参考/出局**——机密 EVM 路线已暂停，原生集成近期不可行；仅余 cross-chain CCL 作外部机密计算服务（机构成熟度低于成熟 L2 隐私方案）。作为「曾尝试机密 EVM 但路线受阻」的对照案例，提示 TEE 机密 EVM 的工程性价比挑战。

#### 6.3 Automata — 链上 TEE attestation verifier（可 bolt-on 验证积木）

- **是什么**：模块化 attestation 层——链上 TEE attestation 验证器（Intel DCAP SGX/TDX quote 的 Solidity 链上验证），含 On-Chain PCCS（去中心化证书缓存）与 Multi-Prover；**本身不是机密执行引擎，而是验证 TEE 真实性的验证层** [docs.ata.network/tee-overview/tee-verifiers，github.com/automata-network/automata-dcap-attestation，访问 2026-06-23]。
- **信任模型贡献**：把 TEE attestation 从厂商中介的不透明流程变为链上可验证（任何人可在链上验证 TEE quote 而非信任厂商证明服务）——可使 Silent Data / Oasis 等 `Hardware-Anchored` 方案更 **trust-minimized**。
- **bolt-on 性质（关键）**：DCAP verifier 开源、经 Trail of Bits 审计（2025-03）、可部署到任意 EVM 链而无需新建链——**真正可 bolt-on 的验证积木**；开发者 import `DcapLibCallback` 守卫函数（"仅当 DCAP 验证通过才执行"）[github.com/automata-network/automata-dcap-attestation，访问 2026-06-23]。截至 2025-11 部署 24+ 主网/测试网（含 Ethereum/Optimism/Base）；**未发现 Mantle 集成的一手证据** [vendor-reported，访问 2026-06-23]。
- **R4**：N/A（Automata 不提供交易/合约隐私，仅验证 TEE）。
- **Mantle 相关性**：**候选（作为积木）/参考**——若 Mantle 采用任何 TEE 路线（如借鉴 Silent Data 或自建 TEE sequencer），可 bolt-on Automata DCAP verifier 作为「硬件证明的链上验证原语」，提升信任最小化，无需新建链。是少数真正满足 bolt-on 判定的组件（但其本身非隐私引擎，须与 TEE 执行环境组合）。

#### 6.4 Solana Confidential Transfers（可选，非 EVM 对照）

- **路线/信任模型**：SPL Token-2022「confidential transfer / confidential balances」扩展——Twisted ElGamal 加密余额/金额 + ZK proofs（sigma + Bulletproofs range proofs），由原生 ZK ElGamal Proof Program 链上验证；信任模型 `Cryptographic`（无 TEE）[solana.com/docs/tokens/extensions/confidential-transfer，docs.anza.xyz/runtime/zk-elgamal-proof，访问 2026-06-23]。
- **隐藏什么（token-only）**：隐藏转账**金额**和**余额**，**不隐藏地址/交易图**（保密 ≠ 匿名）；**严格值级（token-only），不提供合约/业务状态隐私（R4 否）** [chainstack.com/solana-confidential-transfers/，访问 2026-06-23]。
- **选择性披露/合规**：可选全局 auditor ElGamal 公钥（指定审计方可解密金额）；ciphertext-validity proof 确保为 sender/receiver/auditor 三方正确加密 [solana-program.com/docs/confidential-balances/zkps，访问 2026-06-23]。
- **成熟度（关键 caveat）**：**ZK ElGamal Proof Program 因 2025-06 Fiat-Shamir 漏洞（Phantom Challenge Soundness）于 mainnet-beta epoch 805（≈2025-06-19）被禁用，截至 2026-06-23 仍禁用、待审计完成再启用**；PYUSD 等已初始化该扩展但**未启用上线** [solana.com/news/post-mortem-june-25-2025，github.com/solana-program/token-2022/issues/657，访问 2026-06-23，press/vendor，**未独立验证**]。
- **非 EVM**：Solana 原生（SPL Token-2022/SVM），**非 EVM 兼容，不可直接集成 Mantle**。
- **Mantle 相关性**：**仅参考（非 EVM、token-only）**——其 auditor-key 合规模型与双状态余额设计对机构 UX 有借鉴价值；EVM 等价物应看 ERC-7984/fhEVM（见 erc7984 issue）。两者均刻意选择「保密（隐金额、露地址）而非匿名」以保留监管可见性。

**source_confidence（item-6）**：4 个 sidebar 均为本轮新增一手调研，关键事实附官方文档 URL + 访问日期 2026-06-23；厂商自报客户/集成与未启用/暂停状态已标注 press/vendor 与 unverified。

### item-7: 逐方案 Mantle 相关性 + bolt-on 可行性 + 候选/参考/出局判定

Step 5：套用框架「轻量级判定标准（4 项一票否决 V1 新链/VM、V2 新桥、V3 全节点运维、V4 硬分叉）」得出部署形态判定，据此给出三档 verdict。

#### 7.1 轻量级判定结果（复用框架 §5.6，benchmark 视角汇总）

| 方案 | V1 | V2 | V3 | V4 | 部署形态 | 轻量级判定 | bolt-on 可行性 |
|---|:--:|:--:|:--:|:--:|---|---|---|
| Paladin | ✗ | ✗ | ✗(sidecar 非全节点) | ✗ | sidecar+链上 verifiers | **轻量~中量级** | **较高**（应用层 sidecar，本项目已有 MPL/Sidecar 集成方案） |
| COTI-Coprocessor | ✗ | ✗ | ✗ | ✗ | bolt-on 协处理器 | **轻量级（非 GA）** | **高**（架构）但成熟度 Pilot |
| COTI-L2 | ✓ | ✓ | ✗ | ✗ | 独立 L2+桥 | **一票否决** | 低 |
| Nightfall | ✗ | ✗ | ✓(rollup operator) | ✗ | ZK rollup 合约套件 | **中量级** | 中（Starknet prover 外包可降负担） |
| Prividium | ✓ | ✓ | ✓ | ✗ | 独立 permissioned L2 | **一票否决** | 低 |
| Linea Enterprise | ✓ | ✓ | ✓ | ✗ | 独立 Validium L2 | **一票否决** | 低 |
| Polygon CDK | ✓ | ✓ | ✓ | ✗ | 独立 private chain | **一票否决** | 低 |
| Silent Data | ✓ | ✓ | ✓ | ✗ | 独立 TEE L2 | **一票否决** | 低（但 TEE 范式 + Automata 验证可借鉴） |

[全部复用 WHI-254 §5.6 判定结果；Paladin sidecar 不等同 V3 全节点运维，处轻量~中量级边界 — Paladin Deep Dive §4 + WHI-254 §5.6]

#### 7.2 三档 verdict

| Verdict | 方案 | 理由 |
|---|---|---|
| **候选 Candidate** | **Paladin** | 提供 R4 执行级隐私（Pente）；sidecar bolt-on 可行（不分叉 EVM、标准 JSON-RPC、Mantle op-geth 已基本满足）；本项目已有 MPL standalone / L2 Sidecar 两套集成方案与缺陷分析 [Paladin Deep Dive §4]。信任为 notary/组织模型（非密码学级），且 Pente N-of-N 不可扩展是关键约束。 |
| **候选 Candidate** | **COTI-Coprocessor** | 架构上真正 bolt-on（无新链/桥/全节点/硬分叉）；提供值级+执行级(部分) R4。但成熟度仅 Pilot（仅首笔跨链交易），multichain 隐私能力未独立验证，revocability 未验证、无 auditable-log——选此需承担技术成熟度风险。 |
| **参考 Reference** | **Silent Data** | TEE 执行级+状态级 R4 范式（自动保护全执行）；不可 bolt-on（独立 TEE L2）但 TEE 路线 + Automata 链上 attestation 验证可借鉴用于 Mantle 自建/借鉴 TEE 能力；审计透明度缺口（EEA「Not disclosed」）。 |
| **参考 Reference** | **Prividium** | 合规向量 7 方案最完整（regulator+compliance-gate+audit-request+auditable-log）；不可 bolt-on（独立 L2）但其 validium + Proxy RPC + RBAC + Selective Disclosure 是 Mantle L3/合规设计的强参考 [enterprise-privacy item-6: "private DA + Proxy RPC + forced tx filter 是 Mantle L3 模板"]。 |
| **参考 Reference** | **Nightfall** | 值级机密代币 + X.509 企业身份 PKI 标准；token-only（无 R4）；不可 bolt-on（rollup operator）。作为机密代币/企业身份门控的标准参考（与 ERC-7984 对照）。 |
| **参考 Reference** | **Polygon CDK** | 可配置隐私光谱（permissioned→confidential validium→confidential compute）；不可 bolt-on（独立 private chain）。其「隐私是光谱」的分层配置思路对 Mantle 隐私路线分阶段设计有参考价值。 |
| **参考 Reference** | **Linea Enterprise** | Private Validium 状态级隐私范式（仅 fingerprint 上 Ethereum）；不可 bolt-on（独立 Validium L2）。作为「状态级隐私 + 主网锚定」范式参考。 |
| **出局 Out** | **COTI-L2** | GA 成熟度最高，但部署模式（需 COTI L2 网络 + 资产桥）触发 V1/V2 一票否决，与 Mantle 轻量级偏好根本冲突；其 GA 能力无法在不使用 COTI L2 网络的前提下获得。 |

#### 7.3 候选方案 tradeoff（核心决策）

Mantle 面临「轻量级 bolt-on vs 生产成熟度 vs R4 能力」三角权衡 [WHI-254 §5.6 Mantle 启示]：

- **Paladin**：轻量（sidecar）+ 提供 R4（Pente 执行级）+ 已有本项目集成方案 → **最现实的候选**；代价是 notary/组织信任（非密码学级）、Pente 成员不可扩展、UTXO 状态管理复杂、Groth16 trusted setup（Zeto）。
- **COTI-Coprocessor**：轻量（协处理器）+ 部分 R4 → 候选；代价是 Pilot 成熟度、multichain 能力未独立验证、合规缺口（revocability 未验证、无 auditable-log）。
- **二者之外**：若 Mantle 接受非 bolt-on，最高隐私参照是 Aztec（密码学级 R4，但独立非 EVM、Pilot-Alpha）；TEE 路线可借鉴 Silent Data + Automata（链上 attestation 验证）组合提升信任最小化。

#### 7.4 Mantle 相关性总结（见 diag-5）

institutional Mantle 的隐私决策应是：(1) 若需轻量 bolt-on + 业务状态隐私 → Paladin（Pente）为首选候选，COTI-Coprocessor 为次选（承担成熟度风险）；(2) 合规设计参考 Prividium，TEE 路线参考 Silent Data+Automata，机密代币/身份参考 Nightfall/ERC-7984，分层隐私参考 Polygon CDK；(3) COTI-L2 出局；(4) 与 mantle-enterprise §5.5 一致——L2 operator 默认见明文，sidecar/L3 是承载敏感数据的现实路径，高敏感场景需叠加 encrypted mempool/TEE/MPC [mantle-enterprise §5.5-5.6]。

**source_confidence（item-7）**：轻量级判定复用框架 §5.6（框架引 EEA §10 + 轻量级标准）；Paladin 集成方案与缺陷复用 Paladin Deep Dive §4/Q2；Mantle 部署背景复用 mantle-enterprise §5.5-5.6；verdict 为研究者综合判定（基于复用证据 + 本轮 sidebar 调研）。

---

## Diagrams

### diag-1: 7×8 Benchmark 矩阵（核心交付图）

见 item-5 §5.1 完整表格。**口径（M2）**：8 行（7 方案，COTI 拆 L2/Coprocessor）× 11 列（8 需求映射列：R1/R2/R4/R6/R7 五个 ●◐○ 列 + settlement/技术栈/信任模型 三个受控词表类别列；外加 R3/R5/R8 三个补充列保证横向同口径）。图例：● 完全 / ◐ 部分 / ○ 不保护 / —— 未明确 / † COTI-Coprocessor 继承 L2 评分但 multichain 未独立验证。

### diag-2: 合约逻辑隐私分类图（R4 — token-only vs contract-logic）

```
                        EEA 7 方案 R4 隐私层级分类
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
   值级 A (token-only)      A+B 部分/兼备           B (Business-State)
   ──────────────          ─────────────           ──────────────
   • Nightfall ★唯一        • Paladin (Pente 执行级,域内可见)   • Silent Data (TEE 执行+状态级)
     (ZK commitments)       • COTI-L2 (GC 标注机密参数)          • Linea Ent. (Private Validium 状态级)
                            • COTI-Coproc.(同等级,announced†)
                            • Prividium (permissioned 全功能)
                            • Polygon CDK (可配置)
        │                         │                         │
   只隐藏「数字」            隐藏数字+部分逻辑           隐藏代码与状态
   (金额/余额)              (开发者标注/域内)          (全执行/链上不可观察)
```

- **Type**: hierarchy / classification（**Applies to**: item-4）
- **关键**：Nightfall 是 7 方案中唯一 token-only；其余 6 方案均提供某种 R4。TW 阶段可转为正式分层图。

### diag-3: 五轴 rubric 对照表

见 item-5 §5.2 完整表格（8 行 × 5 轴）。**Type**: comparison（**Applies to**: item-5）。直接复用 [WHI-254 §3.2]，benchmark 视角汇总。TW 阶段可对候选方案（Paladin/COTI-Coprocessor）转为雷达图。

### diag-4: 部署形态谱 + 轻量级判定（复用并扩展框架 diagram-4）

```
轻量级 ←───────────────────────────────────────────────────────────→ 重量级
                                  │ 轻量级阈值线（一票否决）│
 COTI-Coproc.   Paladin      Nightfall  │  COTI-L2   Silent Data  Linea Ent.  Prividium  Polygon CDK
 (协处理器)     (sidecar)    (ZK rollup)│  (L2+桥)    (TEE L2)     (Validium)  (perm.L2)  (private chain)
 ──────────     ──────────   ──────────│  ────────   ──────────   ──────────  ─────────  ──────────
 bolt-on        合约套件      合约套件   │  独立L2     独立链        独立链       独立链      独立链
 (轻量,非GA)    (轻~中量级)   (中量级)   │  (一票否决) (一票否决)    (一票否决)   (一票否决)  (一票否决)
 ✓通过          ✓通过        V3否        │  V1/V2否     V1/V2/V3否
```

- **Type**: spectrum / positioning（**Applies to**: item-7）。仅 COTI-Coprocessor 与 Paladin 在阈值线左侧（轻量级通过）。

### diag-5: Mantle 相关性总结（决策视角核心图）

| 方案 | Verdict | R4 能力 | 成熟度(EEA) | bolt-on 可行性 | 关键约束 |
|---|---|---|---|---|---|
| Paladin | **候选** | 执行级(Pente) | Pilot | 较高(sidecar) | notary 信任/Pente 不可扩展/UTXO 状态 |
| COTI-Coprocessor | **候选** | 部分(announced) | Pilot | 高(协处理器) | multichain 未验证/合规缺口 |
| Silent Data | 参考 | 完全(TEE) | Early Prod.† | 低(独立 TEE L2) | 审计透明度缺口/TEE+Automata 可借鉴 |
| Prividium | 参考 | 完全(A+B) | Pilot | 低(独立 L2) | 合规向量最完整/L3 模板参考 |
| Nightfall | 参考 | 无(token-only) | Pilot | 低(rollup operator) | 值级标准/X.509 身份 |
| Polygon CDK | 参考 | 可配置 | Pilot | 低(独立链) | 隐私光谱分层思路参考 |
| Linea Enterprise | 参考 | 完全(状态级) | Pilot | 低(独立 Validium) | 状态级隐私范式参考 |
| COTI-L2 | **出局** | 部分 | **GA** | 低(独立L2+桥) | V1/V2 一票否决 |

- **Type**: comparison / summary（**Applies to**: item-7）。

### diag-6: 替代信任模型 Sidebar 对照

| Sidebar 方案 | 信任模型 | R4 | 部署形态 | 对 Mantle | 关键 caveat |
|---|---|---|---|---|---|
| Oasis Sapphire | Hardware-Anchored (TEE) | 完全(B) | 独立 ParaTime + OPL 桥 | 参考 | 需独立网络/桥，非 1:1 L2 隐私替代 |
| Secret Network | Hardware-Anchored (TEE) | 完全(CosmWasm) | 独立 Cosmos L1 | 参考/出局 | **机密 EVM 路线 2026 暂停**，仅余 cross-chain CCL |
| Automata | (验证层, 强化 HW-Anchored) | N/A(非隐私引擎) | **可 bolt-on EVM 验证积木** | **候选(积木)/参考** | 链上 DCAP attestation 验证, 须配 TEE 执行环境 |
| Solana Confidential Transfers | Cryptographic (ElGamal+ZK) | 无(token-only) | Solana 原生(非 EVM) | 仅参考 | **ZK ElGamal 程序 2025-06 起被禁用至今**；非 EVM |

- **Type**: comparison（**Applies to**: item-6）。

---

## Source Coverage

### Primary Source（EEA 报告，经框架直接 HTML 提取复用）

| 来源 | 版本 | 访问日期 | 覆盖 | 引用方式 |
|---|---|---|---|---|
| EEA Privacy Working Group Report (*State of Privacy on Ethereum for Enterprise*) | Version 1, April 2026 | 2026-06-23 | §06/§08/§09/§10/§11 | 经 [WHI-254] 间接引用（框架已直接抓取 HTML 提取 §09 Readiness/§10 Profiles） |

**说明**：本 issue 未重新抓取 EEA 报告 HTML——WHI-254 final.md 已于 2026-06-23 直接抓取并提取 §09 Readiness Matrix（`rm-status` CSS class）、§10 Solution Profiles（含 COTI/Silent Data 强制披露原文）、§08 信任模型，且经 review 接受。本 benchmark 复用该提取为权威 EEA 口径。本轮独立尝试直接抓取报告时，运行环境对 entethalliance.github.io 域名受限（见 Gap G1），故以框架提取 + 官方文档二手交叉印证。

### Framework Reference

| 来源 | 用途 | 引用 |
|---|---|---|
| privacy-landscape-framework (WHI-254) final.md | 五轴 rubric / R1-R8 / 6 维向量 / 轻量级判定 / Readiness / 隐私账本口径 / 7 方案 EEA 提取 | 按 [WHI-254 §N] 引用 |

### Internal Reuse（Paladin，附树内路径，commit eceaef1）

| 来源 | 复用内容 |
|---|---|
| `202606-internal-sharing/research-sections/Paladin Deep Dive.md` | Noto/Zeto/Pente/Atom 机制、五阶段流、集成方案、缺陷 |
| `202606-internal-sharing/research-sections/enterprise-privacy/final.md` | item-6 案例卡 / item-7 技术路线矩阵 / 失败模式 |
| `mantle-enterprise-blockchain/report/final-report.md` | §5.5 隐私比较 / §5.6 合规比较 / sidecar 决策框架 |

### Sidebar（本轮新增一手调研，访问日期 2026-06-23）

| 方案 | 主要来源 |
|---|---|
| Oasis Sapphire | docs.oasis.io/build/sapphire/、/develop/concept/、/develop/authentication/、/build/opl/；oasis.net blog |
| Secret Network | docs.scrt.network；scrt.network/blog/secret-network-2026-roadmap（EVM 暂停原文） |
| Automata | docs.ata.network/tee-overview/tee-verifiers；github.com/automata-network/automata-dcap-attestation；blog.ata.network |
| Solana Confidential Transfers | solana.com/docs/tokens/extensions/confidential-transfer；docs.anza.xyz/runtime/zk-elgamal-proof；solana.com/news/post-mortem-june-25-2025；github.com/solana-program/token-2022/issues/657 |

### Source Requirements 覆盖（对照 outline）

- src-1（EEA §09/§10/§11 anchor，min 1）：✓ 经框架提取复用（G1 直接抓取受限已标注）
- src-2（Paladin 3 内部来源，min 3）：✓ 全部复用，附路径 + commit
- src-3（框架 reference，min 1）：✓ WHI-254 final.md
- src-4（6 方案官方文档，min 6）：◐ 框架已逐方案核验官方文档（复用）；本轮另对 Prividium 做二手补充。以框架 §4.3 各方案官方来源为准
- src-5（sidebar 官方来源，min 3）：✓ 4 个 sidebar 均新增一手来源
- src-6（审计/链上证据，min 2）：◐ COTI 5 次审计、Silent Data ISO 27001（审计机构未披露）、Prividium SOC 2、Automata Trail of Bits、Solana ZK 程序漏洞 post-mortem——多为厂商自报/二手，标注未独立验证

---

## Gap Analysis

| # | 缺口 | 影响 | 建议处理 |
|---|---|---|---|
| G1 | 本轮运行环境直接抓取 EEA 报告 HTML 受限（entethalliance.github.io 域名）| 本 benchmark 的 EEA 事实依赖 WHI-254 已提取并经 review 的内容，而非本轮重新抓取 | 已复用框架同日（2026-06-23）直接 HTML 提取；如 review 要求，可在后续轮次由具备访问的环境重新核验 §09/§10 原文 |
| G2 | Prividium 命名客户（Deutsche Bank Memento Chain / Cari Network）为本轮二手检索，press-reported | 可能与 EEA §09 Pilot 判定的证据口径不完全一致 | 已标注「未独立验证」；EEA §09 仍判 Pilot 为准；后续可查 ZKsync 官方公告核验 |
| G3 | 厂商自报客户/性能数据（COTI Privex $25bn、Silent Data Archax、Polygon T-REX $100B 等）未独立验证 | benchmark 成熟度列依赖厂商/press 证据 | 全部标注「未独立验证」；遵循 mantle-enterprise §5 的 source-confidence 制度，进入销售口径前需 benchmark/审计/客户证据验证 |
| G4 | COTI revocability、Paladin auditable-log 实现细节未经公开技术文档确认 | 合规向量含 `unverified-revocable*` / `partial-auditable-log*` 标签 | 复用框架 G2/G4 既有标注；后续竞品分析查阅技术文档或直接联系确认 |
| G5 | COTI-Coprocessor multichain 隐私能力处 Pilot，未独立验证 | 候选方案之一的能力为 announced | 复用框架 G8；跟踪 multichain 部署与 Axelar 集成进展 |
| G6 | Silent Data 审计透明度（EEA 强制披露「Last audit firm + date: Not disclosed」）| Early Production 判定与审计披露不完全自洽（EEA 自身已归入该阶段）| 复用框架 G7；审计透明度作为后续独立评估维度 |
| G7 | Sidebar 方案（尤其 Automata Mantle 集成、Oasis 正式审计）部分一手证据缺失 | sidebar 为补充参考，深度低于 7 方案 | 已标注「未发现 Mantle 集成一手证据」「正式审计细节官方未充分披露」；sidebar 定位为参考非主体 |

### 无缺口项

- ✓ 7 方案全部 profile，按 8 需求成矩阵（item-3, item-5，M2 口径说明）
- ✓ R4 合约逻辑/业务状态隐私显式标注（item-4，M1 COTI 拆分）
- ✓ Paladin 复用既有研究并映射 rubric，易变事实本轮核验（item-2）
- ✓ 每方案 Mantle 相关性 + bolt-on 可行性 + 候选/参考/出局判定（item-7）
- ✓ Sidebar 替代信任模型（Oasis/Secret/Automata + Solana）（item-6）
- ✓ 受控词表（settlement/技术栈/信任模型）满足 M3
- ✓ 外部结论附访问日期/版本；厂商自报标注未独立验证；内部来源附路径 + commit

---

## Revision Log

| Round | Date | Changes |
|-------|------|---------|
| 1 | 2026-06-23 | Initial deep draft covering all 7 outline items + 6 diagrams. 复用 WHI-254 框架（五轴 rubric / R1-R8 / 6 维向量 / 轻量级判定 / EEA §09-§11 提取 / 7 方案评分）与 3 份 Paladin 内部来源（不重做深挖，仅核验易变事实）；新增 4 个 sidebar 方案一手调研（Oasis Sapphire / Secret EVM 暂停 / Automata DCAP verifier / Solana Confidential Transfers）。Addressed outline-review minor caveats: **M1** COTI 在 R4 表（item-4.2）拆分为 COTI-L2/COTI-Coprocessor 两行并注明共享同一 R4 等级；**M2** 矩阵加口径说明（8 行 × 11 列，8 需求映射）；**M3** settlement/技术栈/信任模型 三列预定义受控词表（§1.4）。所有厂商自报数据标注「未独立验证」，EEA 事实复用框架同日 HTML 提取（G1 直接抓取受限已标注）。 |
