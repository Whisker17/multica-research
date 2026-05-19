---
topic: "Mantle Proposer 去中心化与 ZK Verifier 合规分析"
project_slug: mantle-stage1-rollup
topic_slug: proposer-decentralization-zk-compliance
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: mantle-stage1-rollup/outlines/proposer-decentralization-zk-compliance.md
  draft: mantle-stage1-rollup/research-sections/proposer-decentralization-zk-compliance/drafts/round-{n}.md
  final: mantle-stage1-rollup/research-sections/proposer-decentralization-zk-compliance/final.md
  index: mantle-stage1-rollup/research-sections/_index.md

scope: |
  评估 Mantle 在 proposer / verifier 维度从 Stage 0 走向 Stage 1 的两条核心合规路径：
  (A) Proposer 去中心化路径——从当前 SuccinctL2OutputOracle 白名单 proposer 过渡到
  permissionless（或 ≥5 外部 proposer + permissionless fallback）状态提交模型，并对照
  L2Beat 对 "Whitelisted Proposers — withdrawals can be frozen" 与 "≥5 external actors
  who can submit fraud/validity proofs" 的 Stage 1 要求；(B) ZK verifier 可信设置合规
  路径——基于 SP1 zkVM（Plonky3 STARK + Groth16/Plonk BN254 wrap）的实际 trusted setup
  结构（Plonk 走 Aztec Ignition 公开仪式；Groth16 走 Succinct circuit-dependent phase-2
  内部仪式），评估其在 L2Beat 2025.11 新增 "Stage 1 projects can't have proving systems
  with trusted setups rated 🔴" 框架下的预期评级与改进路径，并明确 Mantle 当前 SP1
  部署版本 / Groth16 ceremony participant 集合 / vk reproducibility 对评级的影响。

  研究同时覆盖：(C) SuccinctL2OutputOracle / SP1VerifierGateway 的 access control 与
  permissionless 化的合约层改造点；(D) Sequencer 强制交易（force inclusion）当前 12h
  最大延迟来源与可优化空间（区分合约层 SEQUENCING_WINDOW 限制 vs sequencer 实现限制）；
  (E) Proposer 失效（whitelist 全部 down / prover network down / verifier-gateway down）
  时用户资产安全与提款冻结风险，以及 OP Succinct 上游 FALLBACK_TIMEOUT_FP_SECS
  permissionless fallback 机制能否被 Mantle 直接采用；(F) 三套 permissionless proposer
  方案（A 扩大白名单至 ≥5 外部 / B 完全 permissionless / C 白名单 + permissionless
  fallback）的横向对比、推荐方案选择与实施 roadmap。

  对照 Wave 0 已建立的 Mantle 架构现状（WHI-40 mantle-architecture-2026 outline 中
  item-2 SuccinctL2OutputOracle + SP1VerifierGateway 路由层、item-4 Sequencer/Proposer
  liveness 故障矩阵）与 Stage 1 框架定义（WHI-39 l2beat-stage-framework-2026）以及
  对标案例（WHI-41 stage1-case-studies 中的 Arbitrum BOLD / Scroll / Starknet / OP
  Mainnet）。Out of scope：合约升级机制 / Security Council / exit window
  （由独立 issue 覆盖）、Sequencer 完全去中心化（shared sequencing 等长期方案）、
  证明系统性能优化（proving time / cost）、DA 层变更、Mantle 之外的 ZK rollup
  proposer 集中化问题。

audience: |
  Multica 研究 squad 内部下游 Adversarial Agent 与 Technical Writer；
  Mantle 协议工程师与合约升级负责人；Succinct Labs 团队负责 SP1 verifier ceremony
  与 OP Succinct fallback proposer 实现的工程师；关注 Mantle Stage 1 路径的
  L2 安全研究员、L2Beat 评级团队、Mantle DAO 治理参与者与机构托管 / 风控 / 跨链桥
  集成方。读者熟悉 OP Stack 基础（OptimismPortal、L2OutputOracle、DisputeGameFactory）、
  ZK rollup proving 基础（STARK / SNARK、trusted setup ceremony、KZG / Groth16 / Plonk）、
  L2Beat Stages 框架（含 2025.11 ZK verifier trusted setup 补充要求），但不一定深入
  了解 SP1 / Plonky3 内部实现、OP Succinct fault-proof proposer 与 fallback timeout
  机制、Arbitrum BOLD 的 bond 经济学与 trustless bonding pool 实现细节。

expected_output: |
  - Mantle proposer / verifier 维度 Stage 1 合规研究文档，覆盖六个主线分析与一个推荐
    实施路线图，所有结论必须给出代码引用（commit SHA + 行号）或 Etherscan / L2Beat
    permalink；任何无法获得 verified source 的合约或参数必须显式标注 "Source unavailable"
    并采用 fallback evidence 规则（spec docs / 链上 storage 读取 / 治理提案 / 官方博客）。

  - **(A) SP1 zkVM verifier 可信设置合规评估**：
    1. SP1 证明系统类型分层说明（Plonky3 STARK base layer + recursive STARK + Groth16 或
       Plonk BN254 final wrap），明确 trusted setup 仅作用在哪一层；
    2. 两条 final-wrap 路径的 ceremony 详情：
       (a) Plonk 路径：Aztec Ignition 2019 公开仪式（176 参与者）的 KZG SRS 复用情况；
       (b) Groth16 路径：Succinct 运行的 circuit-dependent phase-2 内部仪式的参与者数量、
           是否公开 / 可重新生成、circuit digest / vk hash 的公开度与不可变性；
    3. 对照 L2Beat ZK Catalog trusted setup framework（src-4），给出 Mantle 当前 SP1
       部署版本（SP1 v3 / Turbo / 未来 Hypercube）下两条 wrap 路径各自的预期评级
       （🟢 / 🟡 / 🔴）与判定依据；
    4. 如果 Mantle 实际启用的 wrap 路径被评 🔴，列出改进路径（切换到 Plonk + Aztec
       Ignition、参与公开 Groth16 phase-2 ceremony、迁移至 Hypercube 无 trusted setup
       架构、或采用 multi-prover 验证），并标注每条路径的复杂度与时间窗口；
    5. 明确 Mantle 当前在 SuccinctL2OutputOracle / SP1VerifierGateway 部署的具体 SP1
       Verifier 实例对应的 vk / program hash / 仓库 commit，并验证是否与 Succinct 官方
       发布的 vk 一致（reproducibility check）。

  - **(B) SuccinctL2OutputOracle 与 SP1VerifierGateway access control 分析**：
    1. 当前 proposeL2Output 调用是否有 access control，是哪种角色（PROPOSER role / 白名单
       mapping / msg.sender 校验 / 完全 permissionless）；
    2. 白名单 proposer 当前成员地址、人数（必须 ≥5 外部 actor 才满足 Stage 1）、添加 /
       移除 proposer 的权限链（owner → multisig → timelock 或直接 EOA）；
    3. optimistic-mode 切换的权限与触发条件（是否在 proposer 失效场景下能被任何人切换）；
    4. SP1VerifierGateway route id 是 proposer 输入参数还是固定常量，proposer 是否可选择
       不安全 / 已 frozen 的 route（与 WHI-40 item-2 (B) 联动）；
    5. proposeL2Output 的 ZK proof 验证逻辑路径（gateway 路由 vs 直接调用 verifier）与
       gas 成本估算。

  - **(C) Permissionless proposer 三套方案横向对比**：
    每套方案必须以以下七个维度评估（统一为 fields）：
    - `scheme_description`（合约改造点 + 治理流程）
    - `liveness_guarantee`（1-of-N proposer 假设、最坏停摆窗口）
    - `sybil_resistance`（bond 要求 / 资源门槛 / proposer 资格条件）
    - `implementation_complexity`（合约改动行数估算、治理签名次数、上线时间窗口）
    - `gas_cost`（proposeL2Output 调用 gas 估算、bond 锁定成本）
    - `security_assumptions`（依赖哪些 trusted actor、被攻陷后的最坏后果）
    - `l2beat_stage_classification`（满足 Tier b 哪条具体要求 / 不满足哪条）

    三方案：
    - **方案 A**：扩大白名单至 ≥5 个外部 proposer，保留 PROPOSER role 校验；
    - **方案 B**：完全 permissionless（移除 PROPOSER 校验，任何能产出合法 ZK proof 的地址
      均可调用 proposeL2Output）；
    - **方案 C**：混合（白名单 fast-path + permissionless fallback，借鉴 OP Succinct
      FALLBACK_TIMEOUT_FP_SECS 默认 2 周机制，参数化为 Mantle 具体值）。

  - **(D) 强制交易（force inclusion）延迟优化**：
    1. 当前 SEQUENCING_WINDOW = 12h 的合约存储位置与设置历史（与 OP Mainnet 一致还是
       Mantle 自定义）；
    2. 12h 延迟拆解：sequencer 接受 deposit 的时间 + sequencer commit batch 到 L1 的时间
       + L1 finalization 时间，识别哪一段是合约层硬约束 vs sequencer 软实现；
    3. Stage 1 对 force inclusion 的具体要求（用户在不依赖 permissioned operator 的情况下
       完成 L1 提款）；
    4. 可优化方案：缩短 SEQUENCING_WINDOW、引入 sequencer batch posting deadline、
       L1 即时 deposit 队列（Arbitrum 风格）等，每条方案的 trade-off（sequencer 收入、
       censorship resistance window、L1 gas 成本）。

  - **(E) Proposer 失效风险与用户资产安全缓解方案**：
    1. 失效场景分层：
       (a) 单 proposer 失效（其他白名单 proposer 接管）；
       (b) 全部白名单 proposer 失效（提款冻结风险量化：state root 不更新 → withdrawal
           finalization 阻塞）；
       (c) Prover Network 失效（proof 无法生成，即使 proposer 在线也无法提交）；
       (d) SP1VerifierGateway / route failure（已在 WHI-40 item-4 故障矩阵中归类）；
    2. 当前 Mantle 各场景下的恢复路径：是否有 permissionless self-propose、是否能切换至
       optimistic 模式（谁有权限）、Guardian / pause 能否解冻提款；
    3. OP Succinct 上游 FALLBACK_TIMEOUT_FP_SECS（默认 1209600 秒 = 14d）机制说明、
       Mantle 是否已部署、若未部署的合约改造需求；
    4. 推荐参数（fallback timeout、permissionless proposer 启用阈值），考虑 Mantle TVL
       和用户提款分布。

  - **(F) 对标案例横向参考**：
    必须独立成表，覆盖至少四个对标对象的 proposer / validation 机制设计：
    - **Arbitrum BOLD**：bond 机制、trustless bonding pool、bond size 经济学、
      RollupCore.sol + ChallengeManager 架构；
    - **OP Mainnet permissionless fault proofs**（2024.06 上线）：DisputeGameFactory
      模型、bond 大小、proposer 集合开放程度；
    - **Scroll**：当前 proposer 状态（permissioned / permissionless）、ZK trusted setup
      情况、L2Beat Stage 判定；
    - **Starknet**：whitelisted operator + StarknetSCMinorityMultisig（3/12 Security
      Council minority）censorship resistance 机制；
    每条对标案例给出对 Mantle 方案选择的具体借鉴点（哪些可以直接复用、哪些需调整、
    哪些不适用），并明确这些案例是否已被对应 L2Beat 项目页验证为 Stage 1 资格。

  - **(G) 推荐方案与实施 roadmap**：
    1. 基于 (A)-(F) 的发现，推荐 Mantle 应采用的 proposer 去中心化方案（默认假设为
       方案 C 混合，但需在 draft 中给出严格论证或反驳）；
    2. ZK verifier 合规方面，给出短期（保持当前 SP1 wrap 路径 + 补齐 vk reproducibility
       与 ceremony transparency 文档）与中长期（迁移至 Hypercube 或采用 multi-prover）
       两条路径的选择建议；
    3. 强制交易延迟优化建议（具体目标值与合约改动）；
    4. 实施步骤（合约改造 → testnet 部署 → 监控期 → mainnet 部署），每步给出预估时间
       和治理签名要求；
    5. 监控 KPI（proposer 多样性、proof 提交间隔、permissionless fallback 触发次数等）；
    6. 风险与缓解清单（permissionless proposer 引入的 spam / DoS 风险、bond 经济学失衡、
       SP1 ceremony transparency 改进的兼容性风险等）。

  - 至少 5 张 Mermaid 图：当前 vs 推荐 proposer 流程对比、SP1 证明系统架构与
    verifier 信任链、强制交易延迟拆解 timeline、三方案决策树、proposer 失效恢复
    状态机。

source_requirements_summary: |
  Primary 源：Succinct SP1 官方 docs（含 security model 页与 Plonky3 实现文档）、
  Succinct 官方博客（SP1 Hypercube / Turbo 发布说明、trusted setup 公告）、L2Beat ZK
  Catalog SP1 页与论坛 "New Stage 1 requirements for ZK setups" / "trusted setups
  framework" 两条主帖、Mantle 官方 docs 与 Etherscan verified source（SuccinctL2OutputOracle
  / SP1VerifierGateway / 当前白名单 proposer 地址）、Mantle GitHub 仓库
  （mantlenetworkio/mantle-v2、mantle-xyz/op-succinct、mantle-xyz/kona）与 Succinct
  GitHub 仓库（succinctlabs/sp1、succinctlabs/op-succinct）。

  Secondary 源：Arbitrum BOLD 官方 docs 与 Medium 公告、Optimism permissionless fault
  proofs 上线公告（2024.06）、Scroll / Starknet 官方 docs 与 L2Beat 项目页、SP1 与
  OP Succinct 的公开审计报告（如 OpenZeppelin / Cantina / Sigma Prime）、Aztec
  Ignition ceremony 公开记录。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-19T03:30:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-19T03:30:00Z"
---

# Research Outline: Mantle Proposer 去中心化与 ZK Verifier 合规分析

## Items

### item-1: Mantle 当前 Proposer 机制基线与 SuccinctL2OutputOracle Access Control

刻画 Mantle 在 2026.05 主网当前的 proposer 机制基线，作为后续所有改造方案的参照系。
必须覆盖：

1. **SuccinctL2OutputOracle 合约层**：proposeL2Output 函数签名、调用者校验逻辑
   （PROPOSER role 校验 / 白名单 mapping 校验 / msg.sender 比对 / 无校验）、调用必须
   提供的 validity proof 参数格式、`whenNotOptimistic` modifier 的具体实现与可被绕过
   的入口；输出对应 Etherscan permalink + 源码 commit SHA + 行号；
2. **当前白名单 proposer 集合**：链上读出的当前所有具备 proposeL2Output 调用权限的
   地址清单、人数、运营方归属（Mantle Foundation / Mantle Labs / 第三方）；记录每个
   proposer 在最近 30 天 的实际 state root 提交次数（用于评估是否所有白名单成员都活跃）；
3. **白名单维护权限**：添加 / 删除 proposer 的入口函数、调用者角色（owner / multisig /
   TimelockController）、是否经过 timelock delay（与 WHI-40 mantle-architecture-2026
   item-3 (a) 治理路径联动，但本研究不重复推导 timelock 链路，直接引用结论）；
4. **State root 提交流程**：单次 proposeL2Output 调用的端到端流程（off-chain proof
   generation → proposer broadcast → L1 transaction → verifier gateway 路由 → finalize
   queue）、当前 submission interval（每 N 区块或每 M 秒一次）、L1 gas 成本估算；
5. **Optimistic-mode 当前状态**：当前是否处于 optimistic 模式、切换 modifier 的权限
   持有者、若处于 optimistic 模式 challenger 集合是否仍为 permissioned；
6. **proposeL2Output 之外的相关入口**：propose / challenge / finalize 周边函数是否对
   proposer 失效场景有补救（例如 OP Succinct 上游的 fallback timeout 入口在 Mantle
   是否已部署）。

输出："Mantle 当前 proposer baseline" 一张表与一段叙述，作为 item-3 ~ item-7 所有
改造方案的差量基准。

- **Priority**: high
- **Dependencies**: none

### item-2: SP1 zkVM 证明系统架构与 Trusted Setup 详细分析

合约级 + 密码学级分析 Mantle 主网当前使用的 SP1 zkVM 证明系统的 trusted setup 结构。
必须独立覆盖三层：

**(A) SP1 内核证明系统层（无 trusted setup 的 STARK 部分）**：基于 Plonky3 toolkit
的 STARK，使用 AIR arithmetization + FRI-based polynomial commitment scheme + LogUp
lookup arguments，运行在 BabyBear 有限域；STARK 部分不依赖 trusted setup，但其安全性
依赖 proximity gaps conjecture（SP1 Turbo 100 bits security 是 conjectural；SP1 Hypercube
基于 multilinear polynomial 与 sumcheck，安全性已 unconditional）。需明确 Mantle 当前
部署的具体 SP1 版本（Turbo / Hypercube / 旧版），并标注该版本的 security model。

**(B) Final SNARK Wrap 层（trusted setup 的实际作用点）**：SP1 通过 STARK recursion
将多个 chunk proof 聚合后，使用 gnark 实现的 Groth16 或 Plonk over BN254 curve 进行
final compression，得到约 300k gas 的 onchain verifier。必须独立分析两条 wrap 路径
当前在 Mantle 部署中的实际状态：

1. **Plonk 路径**：Aztec Ignition 2019 KZG SRS（176 公开参与者、circuit-independent
   universal setup）；记录该 SRS 的公开 retrieval URL、size、Mantle 是否实际启用 Plonk
   wrap；
2. **Groth16 路径**：Succinct 运行的 circuit-dependent phase-2 ceremony；必须查证：
   - 参与者数量与身份（公开 vs 内部）；
   - ceremony 是否产生公开 transcripts 可供 audit；
   - 该 phase-2 是否针对 Mantle 当前 SP1 circuit version 单独运行（每次 SP1 升级须
     重新做 phase-2）；
   - 生成的 verifying key（vk）是否与链上 SP1VerifierGateway 中某 route 对应的
     SP1Verifier 实例硬编码 vk 一致（reproducibility check）。

**(C) Verifier 实例与 vk 公开度**：链上每个有效 SP1Verifier route 实例的 vk hash /
program hash / circuit digest、对应 Succinct 仓库的 commit SHA、是否可由独立第三方
重新生成 verifier 字节码并比对部署字节码（bytecode reproducibility）。

输出：一张 "SP1 trusted setup 结构图" + 一份 "Mantle 当前 SP1 部署 wrap 路径与 vk
来源清单"，作为 item-3 L2Beat 合规评估的输入。

- **Priority**: high
- **Dependencies**: none

### item-3: L2Beat ZK Setup Stage 1 合规评级映射与改进路径

以 L2Beat 2025.11 "New Stage 1 requirements for ZK setups"（forum post 409）与
"trusted setups framework for ZK Catalog"（forum post 381）为评级基准，对 item-2 输出
的 Mantle SP1 trusted setup 结构进行 Tier b 合规评估。覆盖：

1. **评级框架解读**：L2Beat trusted setup framework 的 🟢 / 🟡 / 🔴 三档评级标准
   （ceremony participant 多样性、是否公开开放、transcripts 可用性、能否独立验证 SRS
   或 circuit-specific output）；明确 Stage 1 要求 "no 🔴 trusted setups"；
2. **Mantle 实际启用 wrap 路径的预期评级**：根据 item-2 (B) 结论分别评估 Plonk 与
   Groth16 路径的预期 L2Beat 评级；若 Mantle 同时部署多个 SP1Verifier route，每个 route
   单独评级；
3. **L2Beat 已有评级（如存在）**：L2Beat ZK Catalog SP1 页（https://l2beat.com/zk-catalog/sp1）
   当前对 SP1 trusted setup 的评级、引用日期、retrieval permalink；记录评级理由原文；
4. **改进路径**（仅在评级为 🔴 或 🟡 时列出）：
   - 路径 1: 切换至 Plonk + Aztec Ignition（已有公开仪式，可立即评 🟢，但需重新做
     SP1 + Plonk 集成与 gas 重新评估）；
   - 路径 2: 运行公开的 Groth16 phase-2 ceremony，邀请社区 / Mantle DAO 参与者参与
     （估算 ceremony 时长、参与者门槛、Mantle 需要承担的运营成本）；
   - 路径 3: 等待 / 强制 Mantle 迁移至 SP1 Hypercube（multilinear polynomial 系统、
     无需 trusted setup 的 final wrap）；估算迁移时间窗口、对 onchain verifier gas
     的影响、是否需要 SP1VerifierGateway 添加新 route；
   - 路径 4: Multi-prover 验证（同时运行多个独立的 ZK 系统，例如 SP1 + 第二个 zkVM 或
     fraud-proof fallback），降低 single trusted-setup 失效风险；
5. **每条改进路径的 Stage 1 时间窗口约束**：Mantle 进入 Stage 1 的目标时间下，哪条路径
   实际可达；
6. **Mantle 当前 vs L2Beat 评级差距矩阵**：直接对接 WHI-40 mantle-architecture-2026
   item-6 Tier (b) "ZK verifier transparency" 与 (c) "Verifier route 去中心化" 两条
   gap 条目，但本 item 给出更深的密码学层面 evidence。

- **Priority**: high
- **Dependencies**: item-2

### item-4: Permissionless Proposer 三方案横向对比（A / B / C）

完整对比三个候选方案，每个方案必须以 `fields` 中定义的统一七维度评估表（见
`scheme_description` / `liveness_guarantee` / `sybil_resistance` /
`implementation_complexity` / `gas_cost` / `security_assumptions` /
`l2beat_stage_classification`）输出。

**方案 A：扩大白名单至 ≥5 个外部 proposer**

- 合约改造：保留 PROPOSER role / 白名单 mapping 校验逻辑，仅扩大成员数量；
- 治理改造：DAO 投票 / Security Council 签名添加 ≥4 个新 proposer 至现有白名单（当前 N
  人 → 目标 ≥5 外部 actor，本 item 需先在 item-1 给出 N 的实际值）；
- 满足 L2Beat Stage 1 "≥5 external actors who can submit fraud/validity proofs"
  字面要求，但仍属 permissioned 状态；
- 风险：5 个 actor 串通失效仍会冻结提款（"5-of-N 串通失效" 假设）；
- 上线复杂度最低，对 SP1VerifierGateway / proposeL2Output 几乎无合约改动；
- 适合作为短期过渡方案。

**方案 B：完全 permissionless proposer**

- 合约改造：移除 PROPOSER role / 白名单校验，任何能产出合法 ZK proof 的地址均可调用
  proposeL2Output；需考虑是否引入 bond / proof submission fee 机制以缓解 spam；
- 治理改造：DAO 投票通过合约升级，通过现有 TimelockController；
- 配合 SP1VerifierGateway route id 锁定（避免 proposer 选不安全 route，与 WHI-40
  item-2 (B) "unsafe verifier route id selection" 风险联动）；
- 最严格满足 Stage 1 与 Stage 2 permissionless 要求（1-of-N proposer 假设、unbounded N）；
- 风险：spam / 重复 proposal、gas 战、需重新设计 proof 排序与去重；
- 上线复杂度最高（合约改动 + 治理签名 + 经济学设计）。

**方案 C：白名单 fast-path + permissionless fallback（混合方案）**

- 合约改造：保留白名单 fast-path（白名单 proposer 可随时调用 proposeL2Output），但增加
  fallback timeout：若距离上一次 state root 更新超过 `FALLBACK_TIMEOUT_FP_SECS`
  （借鉴 OP Succinct 上游默认 14d，本研究需给出 Mantle 推荐参数），任何地址均可调用
  proposeL2Output；
- 治理改造：DAO 投票通过合约升级，TimelockController 延迟内完成；
- 满足 Stage 1 "withdrawals cannot be frozen if proposer fails" 的 liveness 要求，
  同时保持白名单 fast-path 的运营效率；
- 风险：fallback timeout 参数选择不当（过长则 Stage 1 评估不通过，过短则 spam 风险）；
- 上线复杂度中等，与 OP Succinct 上游对齐，迁移路径清晰；
- 推荐为默认建议方案（待 draft 中严格论证）。

每方案末尾给出"切换成本估算"（合约改动行数、testnet 验证时间、mainnet 部署窗口、
治理签名次数）与"回滚路径"（若方案上线后出现严重问题，回退到当前状态需要的合约调用）。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: 强制交易（Force Inclusion）延迟优化

刻画 Mantle 当前 force inclusion 路径的 12h 最大延迟来源，并评估优化空间。覆盖：

1. **当前 12h 延迟拆解**：
   - L1 上 OptimismPortal.depositTransaction 调用 → 进入 deposit queue；
   - Sequencer 在 SEQUENCING_WINDOW（默认 12h）内必须将该 deposit 纳入 L2 batch；
   - 若 sequencer 不纳入，任何用户可在 SEQUENCING_WINDOW 到期后通过 L1 直接强制
     执行；
2. **SEQUENCING_WINDOW 当前实际值**：链上读取 SystemConfig（或对应合约）的 sequencing
   window 参数（验证 Mantle 是否保持 OP 默认 12h 还是自定义）；
3. **延迟构成的合约层 vs 软件层来源**：哪一段是合约层硬约束（SEQUENCING_WINDOW、L1
   block time）、哪一段是 sequencer 实现限制（batch 触发器、batch posting 间隔）；
4. **Stage 1 对 force inclusion 的具体要求**：用户在不依赖 operator 协作的情况下完成
   L1 → L2 deposit 与 L2 → L1 withdrawal 的最长延迟约束（参考 L2Beat Stage 1 文档与
   Vitalik 关于 censorship resistance 的公开论述）；
5. **优化方案**：
   - 方案 5.1: 缩短 SEQUENCING_WINDOW（例如 12h → 6h 或 3h），评估 sequencer 收入与
     可用性影响；
   - 方案 5.2: 引入 L1 即时 deposit 队列（Arbitrum 风格 delayed inbox），允许用户
     立即在 L1 触发 L2 执行；
   - 方案 5.3: 部署 sequencer batch posting deadline 合约约束（若 sequencer 在 T
     分钟内未 post batch，任何人可代为 post）；
   - 每方案的 trade-off：sequencer 收入下降、L1 gas 成本上升、censorship resistance
     窗口缩短、合约改动复杂度；
6. **推荐参数**：基于 Mantle TVL、用户提款分布、L1 gas 市场，给出 SEQUENCING_WINDOW 或
   force-inclusion timeout 的目标值与论证。

- **Priority**: medium
- **Dependencies**: item-1

### item-6: Proposer 失效风险量化与用户资产安全缓解

完整分析 proposer / prover / verifier 失效场景下的用户资产风险与缓解机制。覆盖：

1. **失效场景分层**（与 WHI-40 mantle-architecture-2026 item-4 liveness 故障矩阵对齐，
   不重复推导，本 item 聚焦经济学影响与 fallback 设计）：
   - 场景 6.a: 单个白名单 proposer 失效（其他白名单 proposer 接管，无用户影响）；
   - 场景 6.b: 全部白名单 proposer 失效（无 fallback 时 state root 不再更新 → 提款
     finalization queue 阻塞 → 提款 effectively frozen）；
   - 场景 6.c: Prover Network 失效（proposer 在线但无 proof 可提交，效果等同 6.b）；
   - 场景 6.d: SP1VerifierGateway / route failure（参考 WHI-40 item-4，本 item 仅引用
     结论）；
2. **当前 Mantle 在每个场景的恢复路径**：
   - 是否有 permissionless self-propose？（如无须显式记录 "No permissionless self-propose
     path"）；
   - 是否能切换至 optimistic 模式以解冻提款（谁有权限切换、是否经 timelock）；
   - Guardian / pause 能否 unfreeze 提款（或反而进一步冻结）；
3. **提款冻结风险量化**：在最坏场景下（场景 6.b），假设全部白名单 proposer 同时失效
   30d / 90d / 180d，估算受影响用户与 TVL（基于 Mantle 当前 TVL 与历史提款分布）；
4. **OP Succinct 上游 FALLBACK_TIMEOUT_FP_SECS 机制详解**：
   - 上游默认 1209600 秒（14d）；
   - 合约层实现入口（OP Succinct fault proof proposer 文档与 op-succinct 仓库
     fp_proposer 模块代码）；
   - 触发条件、谁可调用、bond 要求（若有）；
   - Mantle 当前 op-succinct fork 是否已包含该模块（必须查证 mantle-xyz/op-succinct
     commit），若已包含但未启用，明确启用所需的治理动作；
5. **推荐缓解方案**：综合方案 C（fallback proposer）与方案 5.2-5.3（force inclusion），
   给出 "proposer / prover / force-inclusion" 三重 fallback 设计，明确每条 fallback
   的 timeout、bond、参与者门槛。

- **Priority**: high
- **Dependencies**: item-1, item-4

### item-7: 对标案例横向参考与推荐实施 Roadmap

综合 item-1 ~ item-6 的发现，对照 Wave 0 WHI-41 stage1-case-studies 已研究的 Stage 1
对标案例，输出 Mantle 的最终推荐方案与实施 roadmap。覆盖：

**(A) 对标案例横向参考**（独立成表）：

| 项目 | proposer 机制 | 切换至 permissionless 的关键设计 | ZK trusted setup 状态 | L2Beat 当前 Stage 判定 | 对 Mantle 的借鉴点 |
| --- | --- | --- | --- | --- | --- |

至少覆盖：

- **Arbitrum BOLD**（permissionless validation via bond + trustless bonding pool + RollupCore.sol + ChallengeManager）；
- **OP Mainnet permissionless fault proofs**（2024-06 上线，DisputeGameFactory 模型，
  bond 设计）；
- **Scroll**（permissioned proposer + Plonk-based ZK + Stage 1 demoting 风险）；
- **Starknet**（whitelisted operator + StarknetSCMinorityMultisig 3/12 minority
  censorship resistance）；
- **Polygon zkEVM / ZKsync Era / Linea**（trusted setup 评级参照，与 Mantle SP1
  路径形成对比）。

每行必须直接引用 L2Beat 项目页 permalink + retrieval 日期 + 关键参数（bond size、
fallback timeout、operator 数量等）；本 item 不重复推导这些案例细节，直接引用 WHI-41
stage1-case-studies 的最终结论，但必须验证 WHI-41 已覆盖上述全部对标对象，如未覆盖须
补充。

**(B) 推荐方案（基于 (A) 与 item-3 / item-4 / item-6 的综合论证）**：

- proposer 去中心化：默认推荐方案 C（白名单 fast-path + permissionless fallback），
  fallback timeout 参数推荐值与论证；如选定方案 A 或 B 须给出严格的反驳论证；
- ZK verifier 合规：根据 item-3 结论选择短期 / 中长期路径（默认推荐"短期：补齐
  ceremony transparency + vk reproducibility 文档；中长期：跟进 SP1 Hypercube 迁移"）；
- 强制交易延迟：默认推荐缩短 SEQUENCING_WINDOW（如 12h → 6h）+ 引入 sequencer batch
  posting deadline；如选定其他方案须给出论证。

**(C) 实施 roadmap**：

| 阶段 | 时间窗口 | 合约改动 | 治理动作 | testnet 验证 | mainnet 部署条件 |
| --- | --- | --- | --- | --- | --- |

至少分 3 个阶段（短期 0-1 month、中期 1-3 months、长期 3-6 months），每阶段对应一组
具体可交付的合约改动与治理签名要求。

**(D) 监控 KPI 与回滚策略**：

- KPI：proposer 多样性指数（白名单实际活跃 proposer 数 / 总 proposer 数）、proof
  提交间隔分布、permissionless fallback 触发次数、SP1Verifier vk 与官方发布 vk 的
  一致性检查；
- 回滚：每个阶段上线后若出现严重问题（例如 permissionless fallback 被恶意滥用导致 spam
  proof 攻击），回滚路径与所需治理签名；

**(E) 风险与缓解清单**：

- permissionless proposer 引入的 spam / DoS 风险；
- bond 经济学失衡（若选 Arbitrum BOLD 风格 bond）；
- SP1 ceremony transparency 改进引入的兼容性风险（vk 重新生成、verifier 部署字节码
  变更对 SP1VerifierGateway route 注册流程的影响）；
- 与 WHI-40 item-2 (B) SP1VerifierGateway 路由层风险的耦合（permissionless proposer
  上线后 unsafe route id selection 风险放大）；
- Stage 1 时间窗口约束下的优先级排序冲突。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| high_level_summary | 该 item 的 2-4 句 high-level 概括，作为最终章节首段素材；必须直接陈述结论（不是叙述路径） | all |
| current_state | Mantle 当前实际状态的事实性描述：链上参数、合约函数、proposer 集合、SP1 部署版本等，禁止与"应当 / 计划 / 建议"混用；需引用 evidence_sources | item-1, item-2, item-3, item-5, item-6 |
| security_assumptions | 该维度的信任假设：依赖哪些 trusted actor（proposer / multisig / ceremony participant / verifier vk owner）、被攻陷的最坏后果（funds stolen / frozen / censored 三类） | item-1, item-2, item-3, item-4, item-5, item-6 |
| l2beat_stage_mapping | 该 item 对应到 L2Beat Stage 1 框架的哪条要求（按 WHI-40 item-6 三层结构归类：Tier a / Tier b / Tier c），并给出"当前是否满足"的初步判定；ZK setup 评级须给出 🟢/🟡/🔴 预期 | item-1, item-2, item-3, item-4, item-5, item-6 |
| comparable_implementations | 该 item 涉及哪些对标案例（Arbitrum BOLD / OP Mainnet / Scroll / Starknet 等），引用 WHI-41 stage1-case-studies 的对应结论或独立给出具体参数；每条对标必须含 L2Beat permalink + retrieval 日期 | item-3, item-4, item-5, item-6, item-7 |
| implementation_complexity | 方案 / 改造的实施复杂度估算：合约改动行数（量级，如 < 100 / 100-500 / > 500）、治理签名次数、testnet 验证周期、mainnet 部署窗口、是否需要新 SP1Verifier ceremony | item-3, item-4, item-5, item-7 |
| trade_offs | 方案的 trade-off：security ↔ liveness ↔ cost ↔ decentralization 之间的权衡，需明确每条 trade-off 的量化或定性方向 | item-3, item-4, item-5, item-7 |
| recommendation_summary | 该 item 输出的推荐结论：默认方案、备选方案、明确反驳的方案；item-7 的 recommendation 必须覆盖 proposer / verifier / force-inclusion 三个维度 | item-3, item-4, item-5, item-6, item-7 |
| evidence_sources | 主要引用源：L2Beat permalink（含 retrieval 时间）、Etherscan verified source、Succinct / Mantle 官方 docs / blog、GitHub commit URL；区分 primary / secondary；任何 verified source 不可得须按 src-3 fallback 规则处理 | all |
| code_references | 代码引用：仓库（succinctlabs/sp1、succinctlabs/op-succinct、mantle-xyz/op-succinct、mantlenetworkio/mantle-v2、mantle-xyz/kona）/ 文件 / commit SHA / 行号；禁止伪造引用，无法获取须显式标注 "Source unavailable — fallback to spec / docs / on-chain read" | item-1, item-2, item-4, item-5, item-6 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Mantle 当前 proposer 流程 vs 推荐 permissionless 流程对比图：左侧为当前白名单 proposer 流程（user / off-chain prover → whitelisted proposer → SuccinctL2OutputOracle.proposeL2Output → SP1VerifierGateway → SP1Verifier → finalize），右侧为推荐方案 C 混合流程（增加 fallback timeout 路径与 permissionless proposer 入口），并以颜色区分 access-controlled / permissionless 节点 | mermaid | item-1, item-4, item-7 |
| diag-2 | architecture | SP1 证明系统架构与 verifier 信任链图：自底向上分层显示 RISC-V program → Plonky3 STARK chunks（无 trusted setup，依赖 BabyBear FRI + proximity gaps conjecture）→ STARK recursion → final SNARK wrap（Groth16 路径：Succinct phase-2 ceremony；Plonk 路径：Aztec Ignition KZG SRS）→ onchain SP1Verifier（vk hardcoded）→ SP1VerifierGateway route → SuccinctL2OutputOracle；高亮 trusted setup 层与对应 ceremony 参与者节点 | mermaid | item-2, item-3 |
| diag-3 | timeline | 强制交易（force inclusion）延迟拆解 timeline：横轴为时间（0 → 12h+），纵轴标出关键事件节点（user calls OptimismPortal.depositTransaction → sequencer must include → SEQUENCING_WINDOW expiry → permissionless force include path on L1）；并标注每段延迟的合约层 / 软件层来源，叠加优化方案后的目标 timeline（如 SEQUENCING_WINDOW 6h 或 3h） | mermaid | item-5 |
| diag-4 | comparison | 三方案决策树：根节点为 "Mantle proposer 去中心化方案选择"，分支为方案 A / B / C，每个分支节点附带 fields 七维度评估结果（用 ✓ / ✗ / 部分满足 标注），叶子节点为推荐 / 备选 / 反驳标签 | mermaid | item-4, item-7 |
| diag-5 | flow | Proposer 失效恢复状态机图：状态节点 = {normal / single-proposer-down / all-whitelist-down / prover-down / fallback-active / optimistic-mode / paused}，迁移边标注触发条件（timeout 超时、Guardian 操作、permissionless fallback 启用）与所需 actor / 治理签名；高亮 "withdrawal frozen" 状态与对应的解冻路径 | mermaid | item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Succinct SP1 官方 docs（docs.succinct.xyz/docs/sp1，含 security/security-model 页与 Plonky3 / Hypercube 子页）、Succinct 官方博客（SP1 Hypercube / Turbo / testnet 发布、trusted setup 公告）、OP Succinct book（succinctlabs.github.io/op-succinct，含 architecture / fault_proofs/proposer 两页）、Mantle 官方 docs（docs.mantle.xyz）与 Mantle / Succinct 关于 OP Succinct 主网部署的公告 | 5 |
| src-2 | official_docs | L2Beat ZK Catalog SP1 / SP1 Turbo 页（l2beat.com/zk-catalog/sp1、l2beat.com/zk-catalog/sp1turbo）、L2Beat Mantle 项目页（l2beat.com/scaling/projects/mantle），含 proposer / verifier / stage 标注，retrieval 时间必须标注 | 3 |
| src-3 | on_chain_data | Mainnet Etherscan verified source 与状态读取，覆盖以下合约的关键参数：SuccinctL2OutputOracle（proposeL2Output 调用者、PROPOSER role / 白名单 mapping、submission interval、whenNotOptimistic 状态）、SP1VerifierGateway（route registry、当前所有有效 route id 与对应 SP1Verifier 地址、route owner / freeze 权限）、所有有效 SP1Verifier 实例（vk hash、program hash、verified source 状态）、SystemConfig（SEQUENCING_WINDOW、max time drift）、OptimismPortal（pause 状态、Guardian 地址）；任一合约 verified source 不可得时须显式标注 "Source unavailable" 并写明 fallback evidence | 6 |
| src-4 | governance_proposals | L2Beat 论坛主帖：(a) "New Stage 1 requirements for ZK setups"（forum.l2beat.com/t/409，2025-11）；(b) "The trusted setups framework for ZK Catalog"（forum.l2beat.com/t/381，2025-07）；(c) Mantle 治理论坛 / 提案中涉及 proposer 白名单调整、SP1Verifier route add/freeze、SEQUENCING_WINDOW 调整、Stage 1 路线图的提案（若无相关提案存在须明示） | 3 |
| src-5 | code_analysis | GitHub 仓库源码：(a) succinctlabs/sp1（含 prover / verifier / circuit 子目录，记录 STARK + Groth16/Plonk wrap 实现 commit SHA）；(b) succinctlabs/op-succinct（含 fp_proposer / contracts 子目录，含 FALLBACK_TIMEOUT_FP_SECS 默认值与触发逻辑）；(c) mantle-xyz/op-succinct（Mantle 对 OP Succinct 的 fork，须明确 commit 与上游 diff）；(d) mantlenetworkio/mantle-v2（含 packages/contracts/L1 下的 SuccinctL2OutputOracle / SP1VerifierGateway / SystemConfig 源码）；(e) mantle-xyz/kona（derivation pipeline，作为 proof 生成上游补充）；每条引用须给出 commit SHA 与行号 | 5 |
| src-6 | industry_reports | Arbitrum BOLD 官方 docs（docs.arbitrum.io/how-arbitrum-works/bold）与 Medium 公告、Optimism permissionless fault proofs 上线公告（2024-06）、Scroll / Starknet 官方 docs 与 L2Beat 项目页（用于对标）；至少覆盖每个对标项目 1 个 primary 来源 | 4 |
| src-7 | audit_reports | SP1 / OP Succinct 公开审计报告（如 OpenZeppelin / Cantina / Sigma Prime / Trail of Bits 等如有）、Mantle op-stack diff 审计（如可访问）；若审计无公开版本须显式说明并改用 spec + 链上读 + 官方博客 | 1 |
| src-8 | expert_commentary | Vitalik 关于 multiproof / Stage 1 censorship resistance 的公开论述、L2Beat 团队博客（Stages update / Security Council walkaway）、Aztec Ignition ceremony 公开记录与第三方 ceremony 评论（用于 SP1 Plonk 路径分析） | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
