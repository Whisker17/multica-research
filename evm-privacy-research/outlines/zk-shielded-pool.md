---
topic: "ZK Shielded-Pool 范式分析 — Railgun / Privacy Pools / Starknet STRK20 / Tornado（教训），核心交付 Starknet vs Railgun/PP head-to-head"
project_slug: "evm-privacy-research"
topic_slug: "zk-shielded-pool"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/zk-shielded-pool.md"
  draft: "evm-privacy-research/research-sections/zk-shielded-pool/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/zk-shielded-pool/final.md"
  index: "evm-privacy-research/research-sections/_index.md"

scope: |
  分析 ZK shielded-pool / 私密转账范式的四个代表方案——Railgun、Privacy Pools (0xbow)、
  Starknet STRK20、Tornado Cash（作为合规反面教训）。核心交付物是 Starknet STRK20 与
  Railgun/Privacy Pools 的 head-to-head 对比，直接回应用户的问题：「Starknet 与 Privacy Pool
  类方案到底有什么具体区别」。四方案同属 note-commitment + nullifier 的 shielded-pool/私密转账
  范式，表层非常相似，但在【证明系统（STARK 透明无 setup/PQ vs Groth16 需 trusted setup/非 PQ）】、
  【运行基底（validity rollup 原生 app 层 + 客户端证明 vs 通用 EVM 链上 verifier 合约套件）】、
  【note/nullifier 模型】、【合规-选择性披露模型（链上加密 viewing key vs viewing key + PPOI 排除
  vs association set 包含/排除 + ASP）】、【可移植性（绑定 Cairo VM vs 跨多条 EVM 链）】、
  【成熟度/匿名集】上存在实质差异。Tornado 因「无任何选择性披露」成为监管死局：2022-08 OFAC SDN
  制裁 + 生态回避（前端下架 / TORN 交易所 delist）构成死局本身，正是催生 Railgun/PP/Starknet 三者
  合规设计的因果起点；其后 2024-11 Van Loon v. Treasury 判决（IEEPA "property" 定性，范围有限）与
  2025-03 OFAC 移出 SDN 属于法律纠偏，不改变设计教训。
  评分须套用框架 issue（privacy-landscape-framework）的 5 轴 rubric、8 项企业需求与选择性披露
  6 维向量模型，确保口径统一。

audience: "Mantle 工程团队、协议/基础设施负责人、隐私方案选型决策者；以及对『Starknet 与 Privacy Pool 类方案区别』有具体疑问的内部读者"

expected_output: |
  一份中文结构化研究 section，包含：
  - 通用 shielded-pool 模型说明（note commitment + nullifier + Merkle 树 + 客户端证明 + 链上池）
  - Railgun / Privacy Pools / Starknet STRK20 各自的方案剖析（证明系统、运行基底、合规模型、部署/成熟度）
  - 四方案技术对照表（证明系统 / 运行基底 / 合规模型 / 入口）
  - Starknet STRK20 vs Railgun/Privacy Pools head-to-head 专表，覆盖六维：① 证明系统 ② 运行基底
    ③ note/nullifier 模型 ④ 合规模型 ⑤ 可移植性 ⑥ 成熟度/匿名集
  - Railgun（PPOI 排除）与 Privacy Pools（association set 包含/排除 + ASP）合规模型差异（含运营姿态）专项辨析
  - Tornado Cash 合规史时间线，三事件分列：(i) 2022-08 OFAC 制裁 + 生态回避/交易所 delist（死局）→ (ii) 2024-11 Van Loon v. Treasury（范围有限）→ (iii) 2025-03 OFAC 移出 SDN（法律纠偏，不反转教训），及其对后续设计的因果链
  - 套用框架 rubric 的 5 轴评分 + 8 需求映射 + 选择性披露 6 维向量
  - 对 Mantle「轻量级 bolt-on」偏好的适配结论
  每个结论附 URL + 访问日期 + commit SHA（代码类）。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23T09:22:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23T09:55:00Z"

multica_issue_id: "ee0d50ac-75b7-4cbd-9f1e-825aad2504e5"
branch_name: "research/evm-privacy-research/zk-shielded-pool"
base_commit: "eceaef1e1b4f7a17d7fc3eb4dd91560207f40629"
language: "中文"
research_depth: "deep-comparative"
mode: "single-issue-lightweight"

primary_sources:
  - name: "Railgun 官方文档"
    url: "https://docs.railgun.org"
    usage: "viewing key 模型、Private Proofs of Innocence (PPOI) 排除证明、Groth16 电路、部署链清单"
  - name: "Privacy Pools (0xbow) 官方文档"
    url: "https://docs.privacypools.com"
    usage: "association set 包含/排除证明、ASP (Association Set Provider) 运营姿态、ragequit 机制"
  - name: "Buterin, Illum, Nadler, Schär, Soleimani — Blockchain Privacy and Regulatory Compliance: Towards a Practical Equilibrium"
    url: "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4563364"
    usage: "Privacy Pools 理论基础；association set 的『分离均衡 (separating equilibrium)』论证"
  - name: "Starknet 官方文档"
    url: "https://docs.starknet.io"
    usage: "STRK20 / 共享隐私池、S-two 客户端 STARK 证明、链上加密 viewing key、validity rollup 架构"
  - name: "本地链代码库（只读，用于实现核对）"
    url: "/Users/whisker/Work/src/networks/starknet"
    usage: "核对 Starknet Cairo VM / STARK 证明相关实现；如条件允许补核 Railgun/PP 合约与 Circom 电路"

prerequisite_sections:
  - "privacy-landscape-framework (提供 5 轴 rubric / 8 需求 / 选择性披露 6 维向量 / 轻量级判定口径)"
  - "vosa-standards (同 shielded-pool 范式但暴露转账图的变体；本 issue 交叉引用，不重复深挖 VOSA)"
---

# Research Outline: ZK Shielded-Pool 范式分析（Railgun / Privacy Pools / Starknet STRK20 / Tornado）

## Research Questions

1. shielded-pool / 私密转账范式的通用模型是什么？note commitment、nullifier、Merkle 累加器、客户端证明、链上 shielded pool 各自承担什么职责，为什么这套结构能同时实现「面值/对手方隐藏」与「双花防护」？
2. Railgun 的 viewing key 模型与 Private Proofs of Innocence (PPOI) 排除证明如何运作？viewing key 的「只读、不可撤销」特性带来哪些合规与隐私后果？Railgun 已部署哪些链，在 Mantle 上做 bolt-on 的可行性如何？
3. Privacy Pools (0xbow) 的 association set 包含/排除证明、ASP (Association Set Provider) 运营姿态、ragequit 机制如何运作？它如何体现 Buterin et al. 的「分离均衡」理论？与 Railgun 的 PPOI 排除模型相比，合规模型的实质差异（尤其运营姿态）是什么？
4. Starknet STRK20 的「共享隐私池 + S-two 客户端 STARK 证明 + 链上加密 viewing key」如何组合？其 STARK 证明系统的「透明、无 trusted setup、后量子」属性具体指什么？官方关于「形式化 zk / 隐私属性 forthcoming」的口径与其作为「私密转账方案」的市场定位之间是否存在冲突，如何如实标注？
5. 【核心】Starknet STRK20 与 Railgun/Privacy Pools 在以下六维上的实质区别是什么：① 证明系统；② 运行基底；③ note/nullifier 模型；④ 合规模型；⑤ 可移植性；⑥ 成熟度/匿名集？这些区别是落在「基底/证明系统/信任假设」层面，还是仅表层差异？
6. Tornado Cash 的合规事件链——(i) 2022-08 OFAC SDN 制裁 + 生态回避（前端下架 / TORN 交易所 delist，构成「死局」）；(ii) 2024-11 Van Loon v. Treasury 判决（IEEPA "property" 定性，范围有限）；(iii) 2025-03 OFAC 移出 SDN（法律纠偏）——分别说明了什么？为什么 (ii)(iii) 的法律纠偏不改变「缺乏任何选择性披露 = 监管死局」这一设计教训？该教训如何因果性地塑造了 Railgun（PPOI）、Privacy Pools（association set）、Starknet（链上加密 viewing key）三者的合规设计？
7. 套用框架 issue 的 5 轴 rubric、8 项企业需求体系与选择性披露 6 维向量模型，四方案各自得分如何？对 Mantle「轻量级 bolt-on」偏好而言，哪一类方案更契合？

## Items

### item-1: 通用 shielded-pool / 私密转账模型

剖析四方案共享的底层范式，作为后续逐一分析与对比的公共词汇表。须讲清：(a) **note commitment**——存款时用户在链上写入一个对（面值、所有者密钥、随机盐）的 commitment（通常 Pedersen/Poseidon 哈希），隐藏面值与所有者；(b) **nullifier**——花费时公布一个由 note 秘密派生、与 commitment 单向绑定的 nullifier，链上记录已用 nullifier 集合以防双花，但 nullifier 与 commitment 在链上不可链接；(c) **Merkle 累加器**——所有 commitment 进入一棵 append-only Merkle 树，花费时证明「我的 note 在树中」而不暴露是哪一个；(d) **客户端证明**——用户在本地用 note 秘密 + Merkle 路径生成 ZK 证明，链上 verifier 只验证证明有效性；(e) **链上 shielded pool**——持有资产、维护 Merkle 根与 nullifier 集合的合约/应用。须明确这套结构如何同时给出「隐私（面值/对手方/链接性隐藏）」与「正确性（无超额提取、无双花）」，并指出 UTXO-note 模型与账户模型的差别。本项是后续所有 head-to-head 维度的概念基线。

- **Priority**: high
- **Dependencies**: none

### item-2: Railgun — viewing key + Proof of Innocence（排除模型）

剖析 Railgun。须覆盖：(a) **证明系统**：Groth16（需 trusted setup / 方案专属或通用 CRS，须核实是哪一类 ceremony；非后量子）；电路语言与约束规模。(b) **运行基底**：部署为通用 EVM 链上合约套件（非独立链），核对已部署链清单（Ethereum 主网 / 各 L2）。(c) **合规模型**：**viewing key**——只读、用户可分享给审计方/监管方以披露其交易历史，但**不可撤销**（一旦分享，持有者永久可读），须分析其隐私后果；**Private Proofs of Innocence (PPOI)**——基于**排除（exclusion）**逻辑，用户证明自己的资金「不来自」某个已知非法来源黑名单，与 Privacy Pools 的「包含」逻辑形成对照。(d) **匿名集/成熟度**：上线时间、TVL、活跃度、审计报告。(e) **Mantle bolt-on 可行性**：作为链上合约套件，Railgun 是否可在 Mantle 上以「轻量级 bolt-on」形态部署（对照框架 issue 的轻量级判定与一票否决条件）。每个结论附 docs.railgun.org 对应页 URL + 访问日期；代码/合约结论附 commit SHA。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Privacy Pools (0xbow) — association set（包含/排除）+ ASP + ragequit

剖析 Privacy Pools。须覆盖：(a) **证明系统**：Groth16 / Circom 电路；与 Railgun 同为 Groth16 但实现栈不同之处。(b) **运行基底**：通用 EVM 链上合约。(c) **合规模型（重点）**：**association set**——用户在提款时证明自己的 note 属于（包含证明）或不属于（排除证明）某个由 **ASP (Association Set Provider)** 维护的地址集合，从而把「诚实用户」与「非法资金」在密码学上分离；须讲清 ASP 的**运营姿态**（谁来维护集合、是中心化还是可竞争、用户能否选择 ASP），以及 **ragequit**（用户在不满意时单方退出、取回原始存款而放弃匿名集的逃生舱）。(d) **理论基础**：引 Buterin, Illum, Nadler, Schär, Soleimani《Blockchain Privacy and Regulatory Compliance: Towards a Practical Equilibrium》(SSRN 4563364) 的「分离均衡 (separating equilibrium)」论证——诚实用户有激励加入合规 association set，非法资金被自然排除。(e) **与 Railgun 合规模型的实质对照**：association set（包含/排除，可由用户选择 ASP）vs PPOI（仅排除）vs viewing key（事后只读披露）的差异，尤其在「运营姿态」与「谁承担合规举证责任」上。(f) **匿名集/成熟度**：部署链、TVL、审计。每个结论附 docs.privacypools.com / SSRN URL + 访问日期。

- **Priority**: high
- **Dependencies**: item-1

### item-4: Starknet STRK20 — 共享隐私池 + S-two 客户端 STARK 证明 + 链上加密 viewing key

**存在性验证门（F3，写本项与 item-5 之前必须先完成）**：在落笔 item-4 与 item-5 之前，须先用 src-1（docs.starknet.io 官方文档）+ src-6（本地 starknet 代码库 `/Users/whisker/Work/src/networks/starknet` + commit SHA）核实「**STRK20**」「**链上加密 viewing key**」「**S-two 客户端 prover**」三者各自是**已部署/已发布的真实 artifact**，还是社区非正式命名或纯路线图概念。核实结果须落为一张「名称 / 来源 / 状态（已部署-已审计 / 已部署-未审计 / 路线图-forthcoming / 未能证实）」小表。**任一项无法证实为已部署 artifact 时，必须在 item-4 与 item-5 中显式标注其真实状态，不得按已交付属性书写或参与对等比较。** 此门是 Starknet 侧合规与证明系统对照的事实地基，必须先证后用。

剖析 Starknet 的 STRK20 私密转账方案（在通过上述验证门、明确各 artifact 真实状态的前提下）。须覆盖：(a) **证明系统**：**STARK**——透明（无 trusted setup / 无 ceremony）、后量子（依赖抗碰撞哈希而非配对友好椭圆曲线），与 Groth16 形成根本对照；核对 **S-two** 作为客户端 STARK prover 的角色（用户本地生成证明）。(b) **运行基底**：运行在 Starknet 这条 **validity (ZK) rollup** 的**应用层**，绑定 Cairo VM；与 Railgun/PP「部署在通用 EVM 链上的合约套件」是不同的基底层级。(c) **note/nullifier 模型**：共享隐私池 + note/commitment 结构在 Cairo 下的实现。(d) **合规模型**：**链上加密 viewing key**——viewing key 以加密形式存于链上，与 Railgun 的「链下分享只读 key」不同；分析其披露授权方/触发方式/可撤销性。(e) **口径冲突（必须如实标注）**：官方/社区材料一方面将 STRK20 宣传为私密转账方案，另一方面对「形式化 zero-knowledge / 隐私属性」标注为 **forthcoming（尚未正式形式化/审计完成）**；须如实呈现该口径冲突，区分「已实现并审计」与「路线图承诺」，不得替官方拔高。(f) **成熟度/匿名集**：mainnet/testnet 状态、审计、活跃度。每个结论附 docs.starknet.io URL + 访问日期；实现核对附本地 starknet 代码库路径 + commit SHA。

- **Priority**: high
- **Dependencies**: item-1

### item-5: 【核心交付】Starknet STRK20 vs Railgun/Privacy Pools head-to-head

本项是本 issue 的核心交付物，直接回答用户「Starknet 与 Privacy Pool 类方案的具体区别」。须产出一张 head-to-head 专表，并对每一维给出文字论证，**重点落在「运行基底 / 证明系统 / 信任假设」的实质差异，而非表层相似**（评审重点）。至少覆盖六维：

1. **证明系统**：STARK（透明、无 trusted setup、后量子；但 Starknet 形式化 zk forthcoming）vs Groth16（需 trusted setup ceremony、非后量子、电路成熟且广泛审计）。须落到**信任假设**：trusted setup 的 toxic-waste 信任 vs STARK 的无 setup；后量子安全性差异。
2. **运行基底**：Starknet = validity rollup 原生应用层 + 客户端证明，绑定 Cairo VM、继承 rollup 的 sequencer/prover/DA 信任假设 vs Railgun/PP = 部署在通用 EVM 链上的 verifier 合约套件，继承所在 L1/L2 的信任假设、可跨链复制。
3. **note/nullifier 模型**：commitment 哈希/树结构/nullifier 派生在 Cairo（Starknet）与 Circom-Groth16（Railgun/PP）下的差异；UTXO-note 粒度、面值表达。
4. **合规模型**：链上加密 viewing key（Starknet）vs viewing key + PPOI 排除（Railgun）vs association set 包含/排除 + ASP + ragequit（Privacy Pools）。须对照「披露授权方 / 触发方式 / 可撤销性 / 举证逻辑（包含 vs 排除）」。
5. **可移植性**：Starknet 方案绑定 Cairo VM / Starknet rollup（迁移到其他链需移植 VM 或重写）vs Railgun/PP 作为 EVM 合约套件可跨多条 EVM 链部署（含 Mantle）。
6. **成熟度/匿名集**：上线时间、审计完成度、TVL/匿名集规模、是否 mainnet。

**成熟度不对称标注（F2，head-to-head 专表强制要求）**：Railgun 与 Privacy Pools 是已上线、已审计的生产系统，而 Starknet STRK20 的隐私属性为 forthcoming/未审计。专表**每一维**对 Starknet 的属性都必须显式标注其交付状态——`shipped/audited`（已部署已审计）/ `shipped/unaudited`（已部署未审计）/ `claimed/roadmap/forthcoming`（声称/路线图/未交付）/ `unverified`（未能证实，承接 item-4 验证门结论）——并以此为前提与 Railgun/PP 的*已交付*属性比较，**禁止把「声称属性」与「已交付属性」等价对比**。尤其须落实于：
- **证明系统维**：STARK 的「透明 / 无 trusted setup / 后量子」属性是针对一个其隐私组件仍 `forthcoming` 的系统而言；优势叙述须绑定该成熟度状态，不得脱离 caveat 单独记优。
- **合规模型维**：「链上加密 viewing key」须明确是已部署且已审计、还是仅为计划/路线图（承接 item-4 验证门）。

须明确指出：四者表层都是「note + nullifier + 客户端证明 + 链上池」，但 Starknet 与 Railgun/PP 的根本分野在于「**基底层级（rollup 原生应用层 vs 通用链上合约）**」与「**证明系统的信任假设（透明 STARK vs 需 setup 的 Groth16）**」，合规模型则是三套不同的选择性披露设计——且这些分野中，Starknet 一侧的多项优势属于「声称/未交付」，比较时必须带成熟度折扣。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4

### item-6: Tornado Cash 合规史与教训 —「无披露 = 死局」及其对前者设计的因果

剖析 Tornado Cash 作为「无任何选择性披露」的范式原型，及其合规事件链如何因果性地塑造了后三者的合规设计。**关键要求：本项必须把三个语义不同的事件拆开并按因果角色定序，不得让 2025 年的法律纠偏稀释「必须有选择性披露」的设计教训。**

(a) **技术定位**：Groth16 固定面额混币池，note + nullifier，但**无 viewing key、无 association set、无任何合规披露通道**——这是其与后三者的根本分野，也是「死局」的技术根因。

(b) **三事件分离与定序（必须按下列结构呈现，每个事件附日期 + 一手来源 + 访问日期）**：

| # | 事件 | 时间 | 性质 / 因果角色 |
|---|------|------|----------------|
| (i) | **OFAC SDN 制裁 + 生态回避（"死局"）** | 2022-08 | OFAC 将 Tornado Cash 合约地址列入 SDN 清单 → Circle/GitHub/RPC/交易所等生态整体回避（前端下架、TORN 在交易所 delist）。**这是构成「死局」的事件**：因缺乏选择性披露，诚实资金无法与非法资金在密码学上切割，监管只能整体封禁。**这是后三者（Railgun/PP/STRK20）需要选择性披露的因果根源。** |
| (ii) | **Van Loon v. Treasury（第五巡回）** | 2024-11 | 法院裁定不可变智能合约不属于 IEEPA 下可制裁的 "property"。**范围限定**：仅为狭义的成文法（statutory）解释，**未**否定 AML 政策动机，**未**认可「无披露的隐私」为可接受。 |
| (iii) | **OFAC 将 Tornado Cash 移出 SDN 清单** | 2025-03 | 司法 + 监管层面的**法律纠偏**（对 (i) 中制裁措施本身的撤销），**不是**对设计教训的反转。 |

**必须显式写出的结论**：(ii)+(iii) 是「制裁措施被司法纠偏/撤销」，其范围仅及于「不可变合约能否被 IEEPA 制裁」这一法律定性；**法律层面的纠偏不改变「缺乏选择性披露使诚实资金无法与非法资金切割」这一设计教训**——后三者的合规设计因果依旧成立。须明确区分两类「delist」：(i) 中 2022 年的「交易所/前端 delist」是生态回避的*后果*（死局的一部分），与 (iii) 中 2025 年的「OFAC 移出 SDN」（法律纠偏）语义相反，绝不可混为一谈或写成「Van Loon → 交易所 delist」的顺序。

(c) **教训 → 因果**：基于 (i) 论证「无选择性披露 → 诚实用户无法切割 → 监管只能整体封禁 → 死局」这一逻辑链，并说明它如何直接催生：Railgun 的 PPOI 排除、Privacy Pools 的 association set 包含/排除（Buterin et al. 论文明确以 Tornado 困境为出发点）、Starknet 的链上加密 viewing key。本项为前述合规模型提供「为什么必须有选择性披露」的历史与法律论据；(ii)+(iii) 仅作为「制裁工具的法律边界」补充，不作为「隐私无需披露」的论据。

- **Priority**: high
- **Dependencies**: item-1

### item-7: 框架 rubric 打分与 Mantle 轻量级 bolt-on 适配综合

套用框架 issue（privacy-landscape-framework）的统一口径为四方案打分，确保与项目其他 section 可比。须产出：(a) **5 轴 rubric 评分表**：对每个方案在「轴1 密码学路线 / 轴2 被保护数据维度（金额/余额/身份/图/逻辑/状态/订单流）/ 轴3 信任模型（Cryptographic/HW/Org/混合）/ 轴4 部署形态（bolt-on/合约套件/独立链）/ 轴5 合规-选择性披露 6 维向量」逐轴打分。**成熟度折扣（F2，强制）**：凡 Starknet 的得分依据的是「声称/路线图/未交付」属性（如 PQ、无 trusted setup 透明性、链上加密 viewing key——承接 item-4 验证门与 item-5 状态标注），评分须同步附「成熟度折扣」备注，明确该项优势尚未交付/未审计，不得与 Railgun/PP 的已交付得分等价计入。(b) **8 需求映射**：标注每个方案满足 R1-R8 中的哪些（尤其 R1 金额、R3 对手方、R5 转账图、R6 合规、R7 选择性披露）。(c) **选择性披露 6 维向量**：用框架的 authority × trigger × payload × scope × revocability × leakage 给四方案各填一个向量（如 Railgun viewing key = key-holder / viewing-key-share / amount+identity / per-account / permanent（不可撤销）/ ...；Privacy Pools = ... association-set ...；Starknet = ... on-chain encrypted key ...）。(d) **轻量级判定**：套用框架的一票否决条件，判定哪些方案对 Mantle 可作「轻量级 bolt-on」（Railgun/PP 作为 EVM 合约套件更可能通过；Starknet 绑定独立 rollup/Cairo VM 大概率触发「需独立链」否决）。(e) **结论**：面向 Mantle 选型，给出哪一类方案更契合「轻量级 + 合规-选择性披露」偏好的综合判断（含 caveats）。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| proof_system | 证明系统类型（STARK/Groth16）、是否需 trusted setup 及 ceremony 类型、后量子性、证明生成位置（客户端 prover）、电路语言与约束规模 | item-1, item-2, item-3, item-4, item-5 |
| runtime_substrate | 运行基底层级：通用 EVM 链上 verifier 合约套件 vs validity rollup 原生应用层；对特定 VM（Cairo）/特定链的绑定程度；继承的链级信任假设 | item-1, item-2, item-3, item-4, item-5, item-7 |
| note_nullifier_model | note commitment 哈希方案与结构、nullifier 派生与防双花、Merkle 累加器类型/深度、UTXO-note vs 账户模型、面值表达 | item-1, item-2, item-3, item-4, item-5 |
| compliance_model | 选择性披露机制：viewing key（只读/可否撤销）/ PPOI 排除 / association set 包含+排除 / ASP 运营姿态 / ragequit / 链上加密 viewing key；举证逻辑（包含 vs 排除）与披露授权方 | item-2, item-3, item-4, item-5, item-6, item-7 |
| trust_assumptions | 信任假设全集：密码学假设、trusted setup toxic-waste、客户端 prover 诚实性、rollup 的 sequencer/prover/DA 信任、ASP/运营方信任、后量子威胁模型 | item-1, item-2, item-3, item-4, item-5 |
| portability | 可移植性/部署形态：跨多条 EVM 链可复制 vs 绑定 Cairo VM/单一 rollup；迁移成本；对 Mantle 的可部署性 | item-2, item-3, item-4, item-5, item-7 |
| maturity_anonymity_set | 成熟度：mainnet/testnet 状态、审计报告、上线时间；匿名集规模、TVL、活跃度 | item-2, item-3, item-4, item-5 |
| framework_alignment | 对齐框架 rubric：5 轴评分、R1-R8 需求映射、选择性披露 6 维向量、轻量级判定（含一票否决） | item-5, item-7 |
| regulatory_history | 合规-法律事实：OFAC 制裁、Van Loon v. Treasury 判决范围、delist 事件；日期 + 来源 + 访问日期 | item-6 |
| mantle_relevance | 对 Mantle 轻量级 bolt-on 偏好的具体启示或约束 | item-2, item-5, item-7 |
| source_confidence | 证据等级：官方文档直引 / 论文直引 / 代码核对 / 行业分析推断；不确定性与口径冲突（如 Starknet「形式化 zk forthcoming」）须显式标注 | all |

## Diagrams

### diagram-1: 通用 shielded-pool 数据流

deposit → note commitment 写入 → 进入 append-only Merkle 树 → 用户本地用 note 秘密 + Merkle 路径生成客户端 ZK 证明 → 链上 verifier 校验 + 记录 nullifier → withdraw/transfer。标注「面值/对手方在链上隐藏」与「nullifier 防双花、与 commitment 不可链接」两条性质落在流程的哪一步。

- **Type**: flow
- **Format**: mermaid
- **Applies to**: item-1

### diagram-2: 四方案技术对照 + Starknet vs Railgun/PP head-to-head 矩阵

以「证明系统 / 运行基底 / note-nullifier 模型 / 合规模型 / 可移植性 / 成熟度-匿名集」为行，四方案为列的对照矩阵；并高亮 Starknet 这一列与 Railgun/PP 列在「运行基底」「证明系统」「信任假设」上的实质分野。

- **Type**: comparison
- **Format**: ascii
- **Applies to**: item-5

### diagram-3: 三套合规-选择性披露模型对照

并列展示：Railgun = viewing key（事后只读、不可撤销）+ PPOI（排除证明）；Privacy Pools = association set（包含/排除）+ ASP（可选）+ ragequit；Starknet = 链上加密 viewing key。沿「举证逻辑（包含 vs 排除 vs 事后披露）」「披露授权方」「可撤销性」「运营姿态」四个对照轴排列。

- **Type**: comparison
- **Format**: mermaid
- **Applies to**: item-2, item-3, item-4

### diagram-4: Tornado Cash 合规史时间线 → 后续设计因果

时间线须把三个事件分列、标明语义，不得让末端事件读成「死局的延续」：部署 → **(i) 2022-08 OFAC SDN 制裁 + 生态回避（前端下架 / TORN 交易所 delist）= 死局** → **(ii) 2024-11 Van Loon 判决（IEEPA "property" 定性，范围有限）** → **(iii) 2025-03 OFAC 移出 SDN（法律纠偏，非教训反转）**。因果箭头只从 **(i) 死局** 节点引出三条，分别指向 Railgun PPOI、Privacy Pools association set、Starknet 加密 viewing key；(ii)(iii) 标为「法律纠偏支线」，明确不削弱设计教训。用颜色/分组区分「死局事件」与「法律纠偏事件」两类，避免 2022 delist 与 2025 SDN-removal 混读。

- **Type**: timeline
- **Format**: mermaid
- **Applies to**: item-6

### diagram-5: 可移植性/部署形态谱 — bolt-on 合约套件 vs 绑定 rollup/VM

线性谱：左端「跨多 EVM 链可复制的合约套件（Railgun/PP，含 Mantle 可部署）」→ 右端「绑定单一 rollup + Cairo VM 的原生应用（Starknet）」；标注框架的「轻量级」阈值线与一票否决触发点。

- **Type**: spectrum
- **Format**: ascii
- **Applies to**: item-5, item-7

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | 四方案官方文档：docs.railgun.org（viewing key/PPOI/部署链）、docs.privacypools.com（association set/ASP/ragequit）、docs.starknet.io（STRK20/共享隐私池/S-two/加密 viewing key）；每个结论附页面 URL + 访问日期 | 4 |
| src-2 | academic_papers | Buterin, Illum, Nadler, Schär, Soleimani《Blockchain Privacy and Regulatory Compliance: Towards a Practical Equilibrium》(SSRN 4563364)；STARK 与 Groth16 的奠基/综述论文（透明性、后量子、trusted setup 信任假设） | 2 |
| src-3 | legal_regulatory | Tornado Cash 合规史一手来源，须覆盖**三个语义不同的事件**各自的来源（附日期 + 来源 + 访问日期）：(i) 2022-08 OFAC SDN 制裁公告 + 生态回避/交易所 TORN delist 记录；(ii) 2024-11 Van Loon v. Treasury 第五巡回判决文书或权威报道（须能界定其 IEEPA "property" 的有限范围）；(iii) 2025-03 OFAC 移出 SDN 清单的公告/权威报道。须能据此区分 2022 年的「交易所/前端 delist」（死局）与 2025 年的「OFAC 移出 SDN」（法律纠偏） | 3 |
| src-4 | audit_reports | Railgun / Privacy Pools / Starknet STRK20 的审计报告或安全评估，用于核实证明系统、电路与合约实现及成熟度声明 | 2 |
| src-5 | on_chain_data | 部署地址、TVL、匿名集规模、活跃度等链上/数据面板指标，用于支撑「成熟度/匿名集」维度 | 2 |
| src-6 | code_analysis | 实现核对：本地 starknet 代码库（/Users/whisker/Work/src/networks/starknet）核对 Cairo/STARK 相关实现；如条件允许，核对 Railgun/PP 的 Circom 电路与 Solidity 合约；附 commit SHA | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create | (initial outline) | Round 1 初始 outline，无历史变更 | agent:research-agent (Deep Research Agent) |
| 2 | modify_item | item-6 | F1（major）：拆分 Tornado 三事件并修正因果链——(i) 2022-08 OFAC 制裁+生态回避=死局；(ii) 2024-11 Van Loon（IEEPA property，范围有限）；(iii) 2025-03 OFAC 移出 SDN（法律纠偏）。显式声明法律纠偏不改变设计教训；区分 2022 delist 与 2025 SDN-removal | Review F1 / Orchestrator Revision Request (round 1→2) |
| 2 | modify_item | item-5 | F2（minor）：head-to-head 专表逐维强制标注 Starknet 属性交付状态（shipped/audited vs claimed/roadmap/forthcoming vs unverified），禁止声称属性与已交付属性等价对比；尤其证明系统与合规模型维 | Review F2 / Orchestrator Revision Request |
| 2 | modify_item | item-7 | F2（minor）：Starknet 凡依据未交付属性记优，rubric 评分须附「成熟度折扣」备注，不与 Railgun/PP 已交付得分等价计入 | Review F2 / Orchestrator Revision Request |
| 2 | modify_item | item-4 | F3（minor）：新增「存在性验证门」——写 item-4/item-5 前须用 src-1+src-6 核实 STRK20 / 链上加密 viewing key / S-two prover 各自的真实交付状态，未证实者须显式标注 | Review F3 / Orchestrator Revision Request |
| 2 | modify_diagram | diagram-4 | F1：时间线分列三事件并标明语义，因果箭头仅从「死局」节点引出，(ii)(iii) 标为法律纠偏支线 | Review F1 / Orchestrator Revision Request |
| 2 | modify_source_req | src-3 | F1：legal_regulatory 来源须覆盖三事件各自一手来源（2022 制裁+delist / 2024-11 Van Loon / 2025-03 SDN 移出），min_count 2→3 | Review F1 / Orchestrator Revision Request |
