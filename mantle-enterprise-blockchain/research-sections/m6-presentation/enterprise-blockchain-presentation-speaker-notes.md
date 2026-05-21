# Enterprise Blockchain Decision Presentation — Speaker Notes

| 字段 | 值 |
|------|-----|
| Issue | WHI-398 |
| 对应 Deck | `m6-presentation/deck/enterprise-blockchain-decision-presentation.html` |
| 日期 | 2026-05-12 |
| Deck 总页数 | 51 页 (含 5 页 section 过渡页、12 页附录) |

---

## 一、10 分钟 Executive Brief

### 选择的 Slides（约 15 页）

> 以下为 10 分钟版本的推荐讲解序列。标注 **[SKIP]** 的 slide 在短版中不展示。

| 序号 | Slide ID | 标题 | 是否讲 | 时间 |
|------|----------|------|--------|------|
| 1 | s1 | Title | 讲 | 15s |
| 2 | s2 | The One Question | 讲 | 30s |
| 3 | s3 | TL;DR 推荐策略 | 讲 | 60s |
| 4 | s2b | 阅读路径与章节结构 | [SKIP] | — |
| 5 | s3b | 5 个领导层决策 | 讲 | 45s |
| 6 | s4 | 为什么 ≠ 公链+白名单 | 讲 | 30s |
| 7 | s5 | 8 个耦合设计决策 | [SKIP] | — |
| 8 | s5b | 约束链 | [SKIP] | — |
| 9 | s6 | Transition: 参考项目 | [SKIP] | — |
| 10 | s7 | Canton | [SKIP] | — |
| 11 | s8 | Prividium | [SKIP] | — |
| 12 | s9 | Tempo/Zones | [SKIP] | — |
| 13 | s10 | Paladin | [SKIP] | — |
| 14 | s11 | 参考项目对比 | 讲 | 45s |
| 15 | s11b | EVM 硬约束 | [SKIP] | — |
| 16 | s11c | Mantle Sequencer 定位 | [SKIP] | — |
| 17 | s12 | Transition: 三条路径 | [SKIP] | — |
| 18 | s13 | L1 架构 | [SKIP] | — |
| 19 | s14 | L1 适用场景 | [SKIP] | — |
| 20 | s15 | L2 架构 | [SKIP] | — |
| 21 | s16 | L2 适用场景 | [SKIP] | — |
| 22 | s17 | L3 架构 | [SKIP] | — |
| 23 | s18 | L3 适用场景 | [SKIP] | — |
| 24 | s19 | Transition: 水平对比 | [SKIP] | — |
| 25 | s19b | 不能承诺什么 | [SKIP] | — |
| 26 | s20 | 模块×路径控制权矩阵 | [SKIP] | — |
| 27 | s21 | Master 对比矩阵 | 讲 | 45s |
| 28 | s22 | 能力深度 vs 上市时间 | 讲 | 30s |
| 29 | s23 | 决策树 | 讲 | 45s |
| 30 | s24 | 业务场景→路径映射 | [SKIP] | — |
| 31 | s25 | Transition: 路线图 | [SKIP] | — |
| 32 | s25b | 路线图口径 | [SKIP] | — |
| 33 | s26 | 分阶段路线图 | 讲 | 60s |
| 34 | s27 | 5 个决策门 | 讲 | 45s |
| 35 | s27b | 前 90 天计划 | [SKIP] | — |
| 36 | s27c | 12-24 月信号 | [SKIP] | — |
| 37 | s27d | 长期组合愿景 | [SKIP] | — |
| 38 | s27e | 风险与缓解 | 讲 | 45s |
| 39 | s28 | 领导层今天的决策 | 讲 | 60s |
| 40-51 | 附录 | 术语/来源/架构图等 | [SKIP] | — |

**10 分钟版实际讲 13 页，合计约 9 分 15 秒 + 45 秒缓冲。**

---

### 10 分钟版 — 逐页 Speaker Notes

**Slide 1 (s1) — Title**
> 开场简短。"今天的汇报来自 M1 到 M5 的完整研究——对 Canton、Prividium、Tempo/Zones、Paladin 四个参考项目的深度调研，以及三条技术路径的对比分析。我会直接给结论，然后解释为什么。"

**Slide 2 (s2) — The One Question**
> "核心问题只有一个：Mantle 要进入企业级区块链市场，走哪条技术路径？自建 L1、企业 L2 并行链、还是 L3 应用链平台？三条路径对应完全不同的投资规模、上市时间和客户类型。"

→ *过渡*：接下来直接看我们的推荐。

**Slide 3 (s3) — TL;DR 推荐策略**
> "推荐分阶段策略：Phase 1 用 OP Stack 做 Enterprise L2 MVP，0-3 个月、$400-600K；Phase 2 做 L3 应用链平台，给每个企业一条专属链；L1 是有条件的战略期权——不是默认路径，必须同时通过客户、技术、资金、人才四个门。底部公式是核心判断逻辑：客户买的是受监管的 Ethereum 扩展走 L2，买专属环境走 L3，买主权结算基础设施才走 L1。"

→ *过渡*：在工程启动之前，有 5 个问题需要领导层先回答。

**Slide 5 (s3b) — 5 个领导层决策**
> "这 5 个问题决定后续所有架构选择。第一，目标切入点——先服务 RWA 发行方还是银行联盟？第二，Operator 定位——Mantle 是否愿意成为受监管的 Sequencer operator？这直接影响法律责任。第三到第五分别是隐私承诺深度、最终性承诺、和 L1 触发条件。如果这些问题没有答案，团队会自然滑向通用基础设施建设。"

→ *过渡*：为什么这是个架构问题而不是配置问题？

**Slide 6 (s4) — 为什么 ≠ 公链+白名单**
> "白名单只解决了'谁能进来'，没有解决'进来之后怎么管'。企业需要的是协议层原生隐私、执行层不可绕过的合规引擎、确定性最终性、数据主权。这是 Canton、Prividium、Tempo 等项目存在的根本原因——它们重新设计了底层架构。"

→ *过渡*：我们研究了四个参考项目，快速看对比结论。

**Slide 14 (s11) — 参考项目对比**
> "这张表是四个参考项目的核心维度对比。Canton 在隐私和最终性上做到了最好，但它是非 EVM 的，生态壁垒高。Prividium 用 ZK 证明状态转换，但 Sequencer 仍然看到明文。Tempo 提供了 L1 参考架构——Reth + BFT、600ms 最终性。Paladin 是隐私中间件，定位是独立产品评估。没有一个项目完美适配 Mantle，但它们共同定义了能力要求。"

→ *过渡*：基于这些参考，我们从 9 个维度对比了三条路径。

**Slide 27 (s21) — Master 对比矩阵**
> "这是核心对比矩阵。L1 在隐私深度、合规深度、数据主权上全面领先，但上市时间最慢、成本最高。L2 是最快入市路径，3-6 个月可上线，但在隐私和最终性上有结构性限制——Sequencer 看到明文、soft confirmation 不是法律结算。L3 在租户隔离上最强，但跨 L3 原子结算是未解决问题。不存在无条件最优路径。"

**Slide 28 (s22) — 能力深度 vs 上市时间**
> "这张图直观展示三条路径的定位。L2 在左下角——快速但能力浅。L1 在右上角——深度最强但耗时最长。推荐路径是从 L2 出发，逐步扩展到 L3，只有满足条件才启动 L1。注意左上角——深度能力+快速交付的象限不存在。"

**Slide 29 (s23) — 决策树**
> "这是给产品和销售团队的实用工具。从客户的硬需求出发：Q1，客户是否需要 sub-second 确定性最终性？如果是，只有 L1。Q2，是否需要完全数据主权？Q3，是否需要协议层合规？Q4，是否需要租户隔离？如果都不需要，L2 就够了。"

→ *过渡*：明确了路径选择逻辑，来看执行计划。

**Slide 33 (s26) — 分阶段路线图**
> "12 个月内有 5 条并行轨道。Phase 1 是 L2 MVP，M0 到 M3。Phase 2 是 L3 平台，M3 到 M6。L1 PoC 从 M0 开始平行推进，M6 出 benchmark 结果。Paladin 评估也在 M0-M6。总预算 $2.5M-$3.9M，不含 L1 full build。"

**Slide 34 (s27) — 5 个决策门**
> "每个决策门有明确的 Go/No-Go 标准。G2 在 M3-M6，验证付费需求——没有付费客户信号就不扩大投资。G4 在 M6，L1 PoC 技术验证。G1 是最重要的门，在 M12——L1 full build 只有在客户、技术、资金、人才四个条件同时通过时才批准。"

→ *过渡*：快速看主要风险。

**Slide 38 (s27e) — 风险与缓解**
> "最大风险不是技术失败。第一，L2-first 可能只吸引低价值客户——缓解方式是并行做 L1 discovery。第二，Mantle 作为 regulated sequencing operator 的法律暴露——D0-D30 必须明确 legal posture。第三，L3 模板无法复用变成 bespoke 项目。第四，finality 被误卖。第五，L1 full build 过早启动。"

**Slide 39 (s28) — 领导层今天的决策**
> "今天需要批准四件事：第一，启动 Phase 1 Enterprise L2 MVP，8-10 人、$400-600K。第二，启动 L1 PoC benchmark，2-3 人、$200-400K。第三，启动 Paladin 独立评估，1-2 人、$100-200K。第四，设定 G2 决策门。不需要今天决定的是 L1 full build、L3 全量投资和 Paladin 长期合作。五个核心结论在右侧——企业链不是公链加白名单、三条路径不是成熟度阶梯、L2 先行是风险最低的入市策略、L1 是有条件期权、决策门确保每步投资有验证。"

---

## 二、30 分钟 Full Version

### 逐页 Speaker Notes

> 以下覆盖全部 51 页。标注 **[可跳过]** 的 slide 在时间不够时优先跳过。

### 逐页重点提示

| Slide | 重点 |
|-------|------|
| 1 (s1) | 这是 M1-M5 研究压缩后的决策汇报，不是新研究。 |
| 2 (s2) | 领导层要回答的是路径选择和投资节奏。 |
| 3 (s3) | 推荐不是单一路径，而是 L2 MVP -> L3 platform -> gated L1。 |
| 4 (s2b) | 这份 deck 支持 10 分钟和 30 分钟两种阅读路径。 |
| 5 (s3b) | 五个领导层问题必须先定，否则工程会滑向通用建设。 |
| 6 (s4) | 企业链不是 public chain + whitelist，而是协议级保证组合。 |
| 7 (s5) | 8 个模块彼此耦合，不能逐项独立采购。 |
| 8 (s5b) | Privacy、Finality、Compliance 是三条主要约束链。 |
| 9 (s6) | 四个参考项目用于定义能力边界，不是直接照抄对象。 |
| 10 (s7) | Canton 是协议层隐私和确定性最终性的标杆，但非 EVM。 |
| 11 (s8) | Prividium 证明 ZK/Validium 路线价值，但 Sequencer 可见性仍是结构限制。 |
| 12 (s9) | Tempo/Zones 给出 Reth + BFT + Zone 的 L1/L3 参照。 |
| 13 (s10) | Paladin 更适合作为独立 MPL 产品评估，而非默认 sidecar。 |
| 14 (s11) | 参考项目共同说明：没有现成方案完美适配 Mantle。 |
| 15 (s11b) | EVM 是 Mantle 的硬约束，也是差异化机会。 |
| 16 (s11c) | Sequencer 是控制点，也是 regulated operator 责任来源。 |
| 17 (s12) | 三条路径不是成熟度阶梯，而是不同承诺模型。 |
| 18 (s13) | L1 买的是主权结算和全栈控制，代价是成本与时间。 |
| 19 (s14) | 只有客户明确要 sovereign settlement 时才考虑 L1。 |
| 20 (s15) | L2 是最快入市路径，但 soft confirmation 和 Sequencer visibility 必须披露。 |
| 21 (s16) | L2 适合 RWA/Enterprise DeFi pilot，不适合 operator-blind 隐私。 |
| 22 (s17) | L3 的核心价值是 tenant isolation，核心风险是跨 L3 原子性。 |
| 23 (s18) | L3 适合银行账本、B2B payment domain 和企业专属环境。 |
| 24 (s19) | 接下来统一口径比较三条路径。 |
| 25 (s19b) | 这页是销售纪律：明确每条路径不能承诺什么。 |
| 26 (s20) | 控制权深度解释为什么 L1/L2/L3 不是同类替代品。 |
| 27 (s21) | Master matrix 是核心证据页，展示 trade-off 而非赢家。 |
| 28 (s22) | “能力深 + 上市快”的象限不存在。 |
| 29 (s23) | 决策树可直接转给 sales/product 做需求分流。 |
| 30 (s24) | 场景映射是条件性判断，先问 finality、sovereignty、operator trust。 |
| 31 (s25) | 执行计划的关键词是阶段投资和 gate 控制。 |
| 32 (s25b) | 预算口径来自 WHI-396 的运营化设计，不等同 L1 full build。 |
| 33 (s26) | 12 个月内并行跑 L2、L3 foundation、L1 PoC 和 Paladin eval。 |
| 34 (s27) | 每个 gate 都有 go/no-go 标准，不通过就不扩大投入。 |
| 35 (s27b) | 前 90 天最重要的是客户入口、legal posture 和 G2 信号。 |
| 36 (s27c) | 12-24 月按信号分流，不自动扩张。 |
| 37 (s27d) | 长期愿景是 portfolio，不是一次性 all-in。 |
| 38 (s27e) | 最大风险来自误卖承诺和过早 L1，而不是单点技术失败。 |
| 39 (s28) | 今天批准 Phase 1、PoC、Paladin eval、G2 门和 D0-D30 定义。 |
| 40 (s29) | 附录只用于 Q&A deep dive。 |
| 41 (s30) | 术语页帮助统一 Hard Finality、DVP、Validium 等口径。 |
| 42 (s31) | 来源索引用于回答“这些判断从哪里来”。 |
| 43 (s31b) | Finality labels 是防止误卖结算语义的产品机制。 |
| 44 (s31c) | 不同权重模型会导向不同路径，说明没有唯一最优。 |
| 45 (s31d) | 成本页要区分 MVP budget、annual path cost 和 full-build exposure。 |
| 46 (s31e) | Paladin G5 只验证独立价值，不承诺默认集成。 |
| 47 (s31f) | L1 触发条件必须四项同时满足。 |
| 48 (s31g) | 未决问题必须在 30 天和 90-180 天窗口内关闭。 |
| 49 (s32) | L1 架构图用于解释主权结算和多 Zone 设计。 |
| 50 (s33) | L2 架构图用于解释 Enterprise Sequencer 与 policy/bridge controls。 |
| 51 (s34) | L3 架构图用于解释 per-tenant chain 与 Mantle L2 settlement hub。 |

---

#### Section 0: 决策入口 (Slides 1-5)

**Slide 1 (s1) — Title** [15s]
> "今天汇报的是 Mantle 企业级区块链战略路径选择。这份 deck 基于 M1 到 M5 的完整研究——覆盖了 Canton、Prividium、Tempo/Zones、Paladin 四个参考项目，以及对 L1、L2、L3 三条路径的系统对比。"

**Slide 2 (s2) — The One Question** [30s]
> "核心决策问题：Mantle 要进入企业级区块链市场，应该选哪条技术路径？自建 L1 主权链、基于 OP Stack 的企业 L2 并行链、还是在 Mantle L2 上搭建 L3 应用链平台？每条路径对应不同的客户需求、投资规模和上市时间。"

**Slide 3 (s3) — TL;DR 推荐策略** [60s]
> "先给结论：推荐分阶段策略。Phase 1 是 Enterprise L2 MVP，0-3 个月、8-10 人、$400-600K——基于 OP Stack 做企业并行链，Authenticated RPC + 合规 Sequencer，最快路径进入市场。Phase 2 是 L3 应用链平台，3-6 个月、12-15 人、$600-900K——'一企业一链'模型，企业拥有自己的 Sequencer 和合规策略。L1 是有条件启动——必须同时通过客户、技术、资金、人才四个门。底部的判断公式很重要：客户需要受监管的 Ethereum 扩展就走 L2，需要专属环境走 L3，需要主权结算基础设施才走 L1。"

→ *过渡*：接下来看这份文档的阅读路径。

**Slide 4 (s2b) — 阅读路径与章节结构** [30s]
> "这份 deck 是决策文档，不是技术白皮书。结构是先给结论、再给证据、附录用于技术深潜。左侧是 8 个章节的索引。右侧标注了两种阅读路径——如果你只有 10 分钟，看标注的 slide 序列；30 分钟走完整 deck。"

**Slide 5 (s3b) — 5 个领导层决策** [60s]
> "工程启动之前，领导层必须回答这 5 个问题。第一个是目标切入点——先做 RWA、托管、支付还是 Enterprise DeFi？这决定了第一个客户是谁。第二个是 Operator 定位——Mantle 是否愿意成为受监管的 Sequencer operator？这是法律问题，不是技术问题。第三个是隐私承诺深度——Phase 1 只承诺公众不可见，还是承诺连 operator 也看不到的路线？第四个是最终性承诺——产品暴露哪些 finality 状态，哪些业务动作可以基于 soft confirmation 执行？第五个是 L1 触发条件。如果这些问题没有答案，团队会自然滑向通用基础设施建设。建议 CEO/Strategy 负责市场入口，CTO 负责技术门，Legal 负责 operator liability 边界。"

---

#### Section 1: 为什么不是白名单 (Slides 6-8)

**Slide 6 (s4) — 为什么 ≠ 公链+白名单** [45s]
> "这页解释为什么企业级区块链不是公链加白名单。左边红色列出白名单模式的局限：所有交易对所有验证者可见、无法在执行层强制 KYC/AML、概率性 finality 无法满足 DVP、企业数据存储在公共节点。右边绿色是真正需要的：协议层原生隐私、执行层不可绕过的合规引擎、确定性最终性、数据主权、独立治理。Canton、Prividium、Tempo 的存在正是因为它们重新设计了底层架构。"

**Slide 7 (s5) — 8 个耦合设计决策** [30s]
> "企业级区块链涉及 8 个耦合的设计决策——Execution Layer、Consensus & Finality、Privacy、Compliance & Identity、Access Control、DA & Data Sovereignty、Interoperability、Operations & Business。关键词是'耦合'——隐私选择会改变 DA 模型，DA 模型会改变与 Ethereum 的结算关系，这是连锁反应，不是独立的模块清单。"

→ *过渡*：下一页展示这些约束是怎么传导的。

**Slide 8 (s5b) — 约束链** [45s] **[可跳过]**
> "这页展示了三条主要的约束传导链。第一条从 Privacy 出发：隐私选择决定 DA 模型（敏感数据是否进入 public blobs）、进而决定与 Ethereum 的关系、进而决定桥接设计、最终影响路径偏好。第二条从 Finality 出发：最终性选择决定结算语义（BFT cert vs ZK proof vs L1 settlement 是不同法律语义）、决定 DVP 能力、决定风险标签。Sub-second hard settlement 指向 L1。第三条从 Compliance 出发：合规深度决定 EVM hooks 的修改程度、forced inclusion 过滤、身份跨域迁移。越深的合规越推向 L1 或深度定制的 L3。"

---

#### Section 2: 参考项目 (Slides 9-16)

**Slide 9 (s6) — Transition: 参考项目** [10s]
> "接下来看四个参考项目——Canton、Prividium、Tempo/Zones 和 Paladin。它们不是竞争对手，而是边界条件的参照。"

**Slide 10 (s7) — Canton** [60s]
> "Canton 是 Digital Asset 的企业级区块链平台，是这个领域的标杆。核心架构是 Participant / Synchronizer / Mediator 三角分离，实现 need-to-know 隐私——交易方只看到自己相关的部分。共识协议是 2PC 盲共识，Sequencer 不看交易内容。成果显著：450+ 项目接入，Goldman Sachs、HSBC、Nasdaq 等机构客户。但关键劣势是非 EVM——使用 Daml 语言，生态壁垒高。对 Mantle 的意义：Canton 是'完美形态'参考，但非 EVM 路径不可复制。我们需要在 EVM 生态内实现类似能力。"

**Slide 11 (s8) — Prividium** [45s]
> "Prividium 是 zkSync 的企业版本，基于 ZK Stack Validium。核心是链下 DA + ZK 证明到 L1，用 Airbender RISC-V STARK 证明状态转换的正确性。但三个关键限制：ZK 只证明 correctness，不自动保证 DA、排序公平或权限执行；Sequencer/operator 仍然看到交易明文；官方声称 ZK finality 可达 ~1s，但生产 SLA 和运营假设仍需验证。对 Mantle 的启示：ZK 合规验证方法值得借鉴，但 Sequencer 可见性是结构性问题。L3 路径可以通过让企业运行自己的 Sequencer 解决。"

**Slide 12 (s9) — Tempo/Zones** [45s]
> "Tempo 是基于 Reth SDK + Commonware Simplex BFT 的项目，~600ms 确定性最终性。Payment Lane 是专用的 stablecoin 高吞吐通道。TIP-403 是合规注册表——policy rules 可以跟随 token 跨 Zone 执行。Zone 模型就是'一企业一 Zone'，每个 Zone 有自己的 DA 和合规策略。对 Mantle 的意义：Tempo 是 L1 PoC 的最直接技术参照。Zone 概念直接映射到 L3 应用链模型。但要诚实——Zone sequencer 仍看明文，证明路径成熟度需要作为门控。"

**Slide 13 (s10) — Paladin** [45s]
> "Paladin 不是一条链，而是隐私中间件。包含 Noto（隐私 token）、Zeto（KYC membership proof）、Pente（私有 EVM group）、Atom（跨域原子结算）。MPL 是 Paladin + Besu/QBFT 的独立网络。关键判断：Paladin 的最佳定位是独立产品评估，不是默认嵌入 L2/L3 的 sidecar。WHI-382 评估结果是 26/30，0 个 critical blocker。推荐 $100-200K 做独立评估，G5 决策门在 M6。"

**Slide 14 (s11) — 参考项目对比** [45s]
> "这张对比表横向比较四个项目。关注三个结论：第一，隐私模型差异巨大——Canton 是协议层 need-to-know，Prividium 是 ZK state proof，Tempo 是 Zone 隔离，Paladin 是 notarized transaction。第二，Canton 和 Tempo/BFT 提供确定性最终性；Prividium 的 ZK finality 声称需要在生产 SLA 下验证。第三，EVM 兼容性方面，Prividium、Tempo、Paladin 在 EVM 生态内，Canton 不是。没有一个项目完美适配 Mantle，但它们共同定义了企业级区块链的能力边界。"

**Slide 15 (s11b) — EVM 硬约束** [30s] **[可跳过]**
> "EVM 是 Mantle 企业路径的硬约束，不是偏好。Canton 证明了非 EVM 可以做到最好的隐私和最终性，但付出了巨大的生态代价。Mantle 的机会是在 EVM 生态内尽可能接近 Canton 的能力水平。这意味着某些 Canton 级别的能力（比如 sub-transaction 粒度的隐私）可能无法完全复制。"

**Slide 16 (s11c) — Mantle Sequencer 定位** [30s] **[可跳过]**
> "Mantle 的中心化 Sequencer 是双刃剑。作为资产：几乎零新增信任假设就可以做合规控制——Authenticated RPC、Policy Engine、Compliance Registry 都可以直接加。作为责任：Sequencer 看到所有交易明文，这让 Mantle 进入 regulated operator 角色。这个定位选择必须在 D0-D30 就由 Legal 确认。"

---

#### Section 3: 三条路径 (Slides 17-23)

**Slide 17 (s12) — Transition: 三条路径** [10s]
> "进入三条战略路径。关键前提：这三条路径不是成熟度阶梯——它们交付的是不同的企业保证。"

**Slide 18 (s13) — L1 架构** [60s]
> "Path A 是自建主权链。Reth + revm + BFT 共识，多 Zone 架构，可选的 Ethereum anchor。性能目标：~600ms 确定性最终性、主链 3,000-5,000 TPS、Payment Zone 超过 10,000 TPS。投资规模：15-25 名工程师、18-24 个月、$5M-$12M 工程费用 + $850K-$1.7M 审计费用。客户买的是主权结算基础设施——Mantle 完全控制从共识到执行的每一层。"

**Slide 19 (s14) — L1 适用场景** [30s]
> "什么时候选 L1：客户需要 sub-2 秒确定性最终性、有锚定客户愿意做验证节点、监管要求完全数据主权、xStocks 等需要主权结算的场景。什么时候不选：没有 $10M+ 预算、没有锚定客户、Ethereum 叙事对业务很重要、12 个月内必须上线。"

**Slide 20 (s15) — L2 架构** [60s]
> "Path B 是企业 L2 并行链，基于 OP Stack fork。核心组件：Authenticated RPC、Enterprise Sequencer、Policy Engine、Hybrid DA、Identity Registry。Soft confirmation 1-2 秒，ZK hard finality 15-30 分钟。但必须诚实讲结构性限制：Sequencer 看到所有交易明文，这是结构性的，不是过渡性的。Soft confirmation 不是法律意义上的结算。Ethereum L1 的 optimistic 回退窗口是 7 天。这些是产品文档和合同必须披露的。"

**Slide 21 (s16) — L2 适用场景** [30s]
> "什么时候选 L2：3-6 个月快速做 pilot、需要 Ethereum settlement 叙事、RWA 代币化和企业 DeFi 场景。什么时候不选：需要 operator-blind 隐私、需要 sub-second hard finality、需要 per-tenant 完全隔离。"

**Slide 22 (s17) — L3 架构** [60s]
> "Path C 是应用链平台——'一企业一链'。每个企业拥有自己的 Sequencer、DA、合规策略和治理。Mantle L2 作为 settlement hub。关键优势是租户隔离和企业自主权。但结构性限制同样存在：跨 L3 DVP 不是原子的、外部最终性最长（约 1 小时）、流动性在 L3 之间碎片化。"

**Slide 23 (s18) — L3 适用场景** [30s] **[可跳过]**
> "什么时候选 L3：客户需要 per-tenant 策略和自己的 Sequencer、银行账本、B2B 支付域、Multi-Tenant SaaS。什么时候不选：需要跨 L3 原子 DVP、sub-second finality、最大化二级市场流动性、xStocks。"

---

#### Section 4: 水平对比 (Slides 24-30)

**Slide 24 (s19) — Transition: 水平对比** [5s]
> "接下来用同一把尺子横向对比三条路径。"

**Slide 25 (s19b) — 不能承诺什么** [45s]
> "这页非常重要——列出了每条路径不能承诺的内容。L2 不能承诺 operator-blind 隐私和 sub-second hard finality。L3 不能承诺跨 L3 原子 DVP 和 sub-second 外部最终性。L1 不能承诺 12 个月内上线和低于 $5M 的成本。Paladin/MPL 不能承诺在 L2/L3 上的无损集成。这页的目的是销售纪律——确保不会对客户过度承诺。"

**Slide 26 (s20) — 模块×路径控制权矩阵** [30s] **[可跳过]**
> "这张表展示 8 个企业模块在三条路径上的控制权。L1 在所有 8 个模块上都是 Full Control。L2 和 L3 在隐私、共识、DA 等核心模块上是 Partial 或 Inherited。这不是说 L2/L3 不能做——而是控制深度有结构性限制。"

**Slide 27 (s21) — Master 对比矩阵** [60s]
> "这是最核心的对比表。9 个维度：Hard Finality——L1 是 ~600ms BFT，L2 是 15-30 分钟 ZK proof，L3 约 1 小时。Privacy depth——L1 可以做协议层隐私，L2 最多做到公众不可见、operator 仍可见。EVM 兼容性——L2 最高，L1 需要最多定制。Time-to-market——L2 是 3-6 个月，L3 是 6-9 个月，L1 是 18-24 个月。成本——L2 是 $400-600K MVP，L1 是 $5M-$12M 工程。不存在无条件最优路径。"

**Slide 28 (s22) — 能力深度 vs 上市时间** [30s]
> "这张散点图直观展示定位。Canton 在右上角作为参考标杆。L2 快但浅、L1 深但慢、L3 居中。推荐路径是从 L2 出发向右上角移动。左上角——深度能力+快速交付——不存在。"

**Slide 29 (s23) — 决策树** [45s]
> "这是实用工具。五个问题：Q1，客户是否需要 sub-second 确定性最终性？是→L1。Q2，是否需要完全数据主权？是→倾向 L1。Q3，是否需要协议层合规？是→L1 或深度定制 L3。Q4，是否需要 per-tenant 隔离？是→L3。Q5，时间和成本优先还是能力深度优先？速度优先→L2。这个决策树可以直接给到销售和产品团队使用。"

**Slide 30 (s24) — 业务场景→路径映射** [30s] **[可跳过]**
> "8 个具体业务场景的路径映射。RWA 代币化优选 L2，xStocks 主路径是 L1、L2 只在非 HFT/非主权结算场景条件性可行，跨境 B2C 支付 L1 最优、L2/L3 需按 operator trust 和流动性约束判断，Enterprise DeFi 走 L2，银行账本和 B2B Payment 更适合 L3，证券 DVP 走 L1，Multi-Tenant SaaS 走 L3。大部分是条件性推荐——要先问 finality、sovereignty、operator trust。"

---

#### Section 5: 路线图与决策门 (Slides 31-39)

**Slide 31 (s25) — Transition: 路线图** [5s]
> "进入执行计划——12 个月路线图、5 个决策门、总预算 $2.5M-$3.9M。"

**Slide 32 (s25b) — 路线图口径** [30s] **[可跳过]**
> "口径说明：M5 Final Report 给出了战略方向，WHI-396 把它运营化为具体的阶段和决策门。这份 deck 的预算数字来自 WHI-396 而不是直接来自 M5。阶段预算和 L1 full build program exposure 是不同口径——不能混在一起比较。"

**Slide 33 (s26) — 分阶段路线图** [60s]
> "12 个月路线图有 5 条轨道。Track 1：Enterprise L2 MVP，M0-M3，8-10 人，$400-600K——Auth RPC、Policy Engine、Enterprise Bridge、合规 Sequencer。Track 2：L3 Platform，M3-M6，12-15 人，$600-900K——ZonePortal、L3 Template、Private DA、Multi-Tenant。Track 3：平台产品化，M6-M12，15-20 人，$1.2M-$1.8M。Track 4：L1 PoC，M0-M6 平行推进，2-3 人，$200-400K——Reth+BFT benchmark、Payment Lane prototype。Track 5：Paladin 评估，M0-M6，1-2 人，$100-200K。决策门标注在时间线上：G2 在 M3-M6、G4 在 M6、G5 在 M6、G3 在 M9、G1 在 M12。"

**Slide 34 (s27) — 5 个决策门** [60s]
> "五个决策门的细节。G2 在 M3-M6——验证付费需求，标准是至少 2 个 design partner + 1 个 paid/LOI signal，通过则扩大 L2/L3 投资，不通过则暂停扩张。G3 在 M9——L3 平台可行性，标准是 2 个不同配置的 L3 同时运行且 ops 可 provisioning。G4 在 M6——L1 PoC 技术验证，Reth+BFT 达到 benchmark 标准、Payment Lane 达到吞吐目标、privacy deposit audit 通过且 policy bypass red-team 无 critical。G1 在 M12——这是最关键的门——L1 full build，必须同时通过锚定客户承诺、技术 PoC、资金 >$10M、人才计划。G5 在 M6——Paladin MPL 独立价值验证，通过则资助到 V1，不通过则使用 L2/L3 原生隐私。"

**Slide 35 (s27b) — 前 90 天计划** [45s] **[可跳过]**
> "前 90 天的具体执行时间表。D0-D15 选择 2 个入口客户——RWA/托管的 L2 + 租户隔离的 L3。D0-D30 确定 Operator/Legal 定位——这是不能拖的。D15-D45 做 L3 foundation brief——第一个 template、ZonePortal API。D30-D75 做 L2 MVP + L1 PoC——Auth RPC、Policy Engine、Bridge Filter、Reth/BFT benchmark 计划。D75-D90 是 G2 checkpoint——至少 2 个 design partner、至少 1 个 paid/LOI signal。每行都有失败时的动作——不是'继续等'，而是明确的 stop/pivot 指令。"

**Slide 36 (s27c) — 12-24 月信号** [30s] **[可跳过]**
> "12 个月后做 portfolio review。继续信号：L2 有 3+ 可信企业客户付费、L3 客户要求 dedicated environment、MPL 有 2+ institutional partner、L1 trigger 条件同时满足。暂停信号：pilots 仍是 unpaid experiments、客户拒绝 operator trust 或 delayed finality、每个 L3 都变成 bespoke 项目。核心原则是按信号分流，不是自动扩张。"

**Slide 37 (s27d) — 长期组合愿景** [30s]
> "长期视角：L2 是受监管的 access layer，服务 RWA 和 Enterprise DeFi。L3 是企业链 SaaS 平台，服务银行账本和 B2B payment。L1 是主权金融基础设施，服务金融联盟和确定性 DVP。三者对应三种公司形态和三种收入模型。战略问题：Mantle 是只做 enterprise rollup provider，还是更广义的 enterprise settlement platform？建议先用 L2/L3 验证答案，再用客户证据触发 L1。"

**Slide 38 (s27e) — 风险与缓解** [45s]
> "五个最大风险。第一，L2-first 验证低价值客户——最高价值机构可能第一天就拒绝 operator trust 和 delayed finality，缓解方式是并行 L1 discovery。第二，合规责任——Legal 必须在 D0-D30 确认 Mantle 是否能承担 regulated operator 角色。第三，L3 模板复用失败——G3 要求 2 个不同配置 L3 同时运行。第四，Finality 被误卖——需要 typed finality API 和合同级定义。第五，L1 过早——全部条件同时通过才做 funding review。每个风险都有明确的 owner。"

**Slide 39 (s28) — 领导层今天的决策** [60s]
> "收尾。今天需要批准的：启动 Phase 1 L2 MVP（8-10 人、$400-600K）、启动 L1 PoC benchmark（2-3 人、$200-400K）、启动 Paladin 独立评估（1-2 人、$100-200K）、设定 G2 决策门标准，并在 D0-D30 锁定 target entry point、operator/privacy/finality commitments。不需要今天决定：L1 full build（G1 在 M12）、L3 全量投资（G2/G3 之后，但 Phase 1 做 L3 foundation）、Paladin 长期合作（G5 在 M6）。右侧是 5 个核心结论，作为这次汇报的 takeaway。"

---

#### Section 6: 附录 (Slides 40-51)

> 附录不需要主动讲解，仅在被追问时翻到对应页面。

**Slide 40 (s29) — Transition: 附录** [5s]
> "以下是附录部分，包含术语表、来源索引、详细架构图和补充分析。我不逐页讲，但这些是可以深潜的参考材料。"

**Slide 41 (s30) — 术语表**
> 被追问术语定义时使用。Hard Finality、Soft Confirmation、DVP、Validium、BFT 等 16 个核心术语。

**Slide 42 (s31) — 研究来源索引**
> 被追问"数据来源是什么"时翻到。列出 M1-M4 深度研究（WHI-334 到 WHI-368）和 M5-M6 综合分析（WHI-386 到 WHI-396）。

**Slide 43 (s31b) — Finality Labels**
> 被追问"soft confirmation 可以做什么"时翻到。5 种 finality 状态（SOFT_CONFIRMED 到 BFT_FINAL）各自允许和禁止的业务动作。

**Slide 44 (s31c) — 三种权重模型**
> 被追问"为什么不直接选 L1"或"L1 在某些维度不是最好的吗"时翻到。三种目标函数导向不同最优路径。

**Slide 45 (s31d) — 成本与预算口径**
> 被追问"总共要花多少钱"时翻到。明确区分阶段预算、年度路径成本、L1 full-build program exposure。

**Slide 46 (s31e) — Paladin G5 评估标准**
> 被追问"Paladin 怎么评估"时翻到。5 个评估维度和 threshold。

**Slide 47 (s31f) — L1 Full Build 触发条件**
> 被追问"什么时候做 L1"时翻到。4 个必须同时满足的条件。

**Slide 48 (s31g) — 未决问题清单**
> 被追问"还有什么没解决"时翻到。30 天和 90-180 天两批未决问题。

**Slide 49 (s32) — L1 架构详图**
> 被追问 L1 full build 技术边界时翻到。重点说明 Reth/revm execution、BFT finality、Payment Lane、多 Zone 和可选 Ethereum anchor 如何组成主权结算基础设施。

**Slide 50 (s33) — L2 架构详图**
> 被追问 Enterprise L2 MVP 如何落地时翻到。重点说明 Authenticated RPC、Enterprise Sequencer、Policy Engine、Hybrid DA 和 Bridge Filter 是 Phase 1 的核心控制面。

**Slide 51 (s34) — L3 架构详图**
> 被追问“一企业一链”如何运作时翻到。重点说明每个 L3 tenant 拥有自己的 Sequencer、DA 和 policy stack，Mantle L2 作为 settlement hub，但跨 L3 原子结算仍需门控验证。

---

## 三、Q&A 准备

### 预期高管提问与建议回答

**Q1: 为什么不直接做 L1？如果最终可能要走到 L1，为什么不一步到位？**

> **建议回答：** L1 full build 需要 15-25 名工程师、18-24 个月、$5M-$12M 工程费用。在没有锚定客户承诺的情况下，这是一个风险极高的投入。L2-first 策略让我们在 3 个月内以 $400-600K 的成本验证市场需求。如果验证结果指向 L1，我们的 L1 PoC 会在 M6 给出技术可行性数据，G1 决策门在 M12 做正式 go/no-go。L2/L3 的能力和客户关系在此期间是资产，不是沉没成本。
>
> **来源：** WHI-390 §7.1, §8.2; WHI-396 decision gate G1

**Q2: Sequencer 看到所有交易明文，这怎么面对企业客户的隐私需求？**

> **建议回答：** 这是结构性限制，我们不回避。L2 路径的 Sequencer 确实看到明文，这意味着 Mantle 作为 operator 需要承担相应的保密和合规义务。对于需要 operator-blind 隐私的客户，L3 路径让企业运行自己的 Sequencer 解决此问题。长期看，L1 路径可以实现 Canton 式的 need-to-know 隐私。Phase 1 的 legal 定位工作（D0-D30）会明确 Mantle 作为 operator 的具体责任边界。
>
> **来源：** WHI-390 §5.12; WHI-393 Privacy 模块; Slide 19b (不能承诺什么)

**Q3: $2.5M-$3.9M 的预算够不够？这个估算可靠吗？**

> **建议回答：** 这个预算覆盖 12 个月三条轨道的执行，不含 L1 full build。具体拆分是 Phase 1 L2 MVP $400-600K、Phase 2 L3 $600-900K、Phase 3 产品化 $1.2M-$1.8M、L1 PoC $200-400K、Paladin 评估 $100-200K。数字来自 WHI-396 的估算，基于 M5 研究中的人力需求分析。L1 full build 如果触发，是另一个 $8M-$18M 级别的单独投资决策，需要走 G1 门控。
>
> **来源：** WHI-396 §3.2; WHI-390 §2.4, §3.8; Slide 31d (成本口径附录)

**Q4: Canton 已经做到了，为什么我们不直接用 Canton 或者跟 Digital Asset 合作？**

> **建议回答：** Canton 确实是这个领域的标杆，但它有两个根本性限制使得直接使用不可行。第一，非 EVM——Canton 使用 Daml 语言，与 Ethereum/Mantle 生态完全隔离。第二，Canton 的价值主张是 Digital Asset 的商业模式，不是 Mantle 的。我们的目标是在 EVM 生态内实现接近 Canton 水平的企业能力，同时利用 Mantle 已有的 OP Stack 基础设施和运维能力。
>
> **来源：** WHI-392 Canton 深度研究; WHI-334–336; Slide 15 (EVM 硬约束)

**Q5: 什么信号会让我们在 M12 决定做 L1 full build？**

> **建议回答：** 必须同时满足四个条件：第一，有锚定客户承诺——不是 LOI，是明确的 commitment 或 co-funding。第二，L1 PoC 通过技术 benchmark——Reth+BFT 集成 ≤2s finality、Payment Lane ≥10K TPS。第三，资金到位——>$10M 的工程预算已获批或有外部融资。第四，人才计划——15-25 名有 BFT/DA/密码学经验的工程师可招聘。四个缺一个就不做。
>
> **来源：** WHI-390 §7.4, §8.3; WHI-396 decision gate G1; Slide 31f (L1 触发条件附录)

**Q6: L3 的"一企业一链"模型会不会太碎片化？跨企业的互操作怎么解决？**

> **建议回答：** 碎片化是 L3 模型的真实代价——跨 L3 的 DVP 不是原子的，流动性在 L3 之间分散。解决方案是 Mantle L2 作为 settlement hub，ZonePortal 作为跨 L3 消息和资产路由。但必须坦诚：跨 L3 原子结算目前是未解决的工程问题，G3 决策门会验证这个能力。如果无法解决，需要 DVP 的场景就要走 L1 路径。
>
> **来源：** WHI-394 L3 架构分析; WHI-390 §4.7; Slide 18 (L3 限制)

**Q7: 竞争对手在做什么？我们的时间窗口有多长？**

> **建议回答：** Canton 已经在生产环境，有 Goldman Sachs、HSBC 等客户。Prividium 已有较多机构验证但生产 SLA 仍待验证，Tempo/Zones 也仍处在早期落地阶段。我们的差异化在于 EVM 生态——Canton 的非 EVM 路径创造了一个市场空白：需要企业级能力但不愿意离开 EVM 的客户。这个窗口不会永远存在——如果 Prividium 或其他 ZK Stack 项目先到达 production-grade，窗口会关闭。Phase 1 的 3 个月时间框架是为了快速占位。
>
> **来源：** WHI-342 行业调研; WHI-392 参考项目对比

**Q8: 如果 Phase 1 的 L2 MVP 上线后没有客户愿意付费怎么办？**

> **建议回答：** 这正是 G2 决策门存在的原因。G2 在 M3-M6，标准是至少 2 个 design partner 和至少 1 个 paid/LOI signal。如果 G2 不通过，明确的动作是：暂停广泛的平台扩张，收缩到只服务已有的 design partner，不投入 L3 全量建设。90 天计划的每一行都有"失败时动作"——不是继续等，而是明确的 stop 或 pivot。最坏情况下，L2 MVP 的 $400-600K 投入产出的是市场洞察和技术资产，这些在其他 Mantle 产品线中也有价值。
>
> **来源：** WHI-396 decision gate G2; Slide 27b (90 天计划); Slide 27c (暂停信号)

**Q9: 为什么 Paladin 要单独评估，不直接集成到 L2/L3？**

> **建议回答：** WHI-382 的分析结论是：Paladin 强行做 L2 sidecar 会损失其核心优势——Atom 的原子结算语义依赖同步的 Besu/QBFT 网络，嫁接到 async 的 OP Stack L2 上会丢失确认一致性。MPL（Paladin + Besu/QBFT standalone network）作为独立产品的评分是 26/30、0 个 critical blocker。所以推荐方式是独立评估 MPL 的市场价值，G5 决策门在 M6 验证。如果有 partner demand 和商业 case，资助 MPL 到 V1 作为独立 privacy product，通过 bridge/proof 与 Mantle 组合。
>
> **来源：** WHI-382 Paladin 评估; Slide 10 (Paladin 定位); Slide 31e (G5 评估标准附录)

**Q10: M5 报告和这个 Deck 的推荐一致吗？有没有偏差？**

> **建议回答：** 核心推荐完全一致——都是"L2 先行、L3 产品化、L1 有门控"的分阶段策略。Deck 在 M5 基础上做了三个运营化扩展：第一，阶段时间从 M5 的 0-4/4-8/8-12 月调整为 0-3/3-6/6-12 月。第二，引入了 G1-G5 正式决策门结构。第三，增加了 Paladin/MPL 作为第四条 portfolio 评估轨道。这些扩展来自 WHI-396 的运营化设计和 WHI-382 的 Paladin 评估，都在 deck 中有明确标注。
>
> **来源：** WHI-390 §8.2; WHI-396; Slide 25b (路线图口径)
