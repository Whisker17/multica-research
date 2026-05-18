---
topic: "Mantle 当前技术架构全景（2026.05）"
project_slug: mantle-stage1-rollup
topic_slug: mantle-architecture-2026
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: mantle-stage1-rollup/outlines/mantle-architecture-2026.md
  draft: mantle-stage1-rollup/research-sections/mantle-architecture-2026/drafts/round-{n}.md
  final: mantle-stage1-rollup/research-sections/mantle-architecture-2026/final.md
  index: mantle-stage1-rollup/research-sections/_index.md

scope: |
  从数据可用性（DA）、证明系统（Proof，含 SP1VerifierGateway 路由层）、合约治理
  （Governance，区分核心 rollup / MNT token / mETH 三条独立路径）与 Sequencer / Proposer
  中心化程度四个维度，完整刻画 Mantle 在 2026 年 5 月 的技术架构现状：
  Ethereum blobs 主网 DA 集成与 batcher 实现（含 calldata fallback）、OP Succinct + SP1
  zkVM 主网证明系统与 SuccinctL2OutputOracle / SP1VerifierGateway 路由 / optimistic mode
  切换、核心 rollup 合约的 ProxyAdmin + TimelockController 升级权限链与具体 delay
  （与 L1MantleToken 治理路径、mETH 产品级 timelock 路径并列分析）、白名单 Proposer 数量
  与 sequencer 中心化、L1 force-inclusion 路径与延迟、以及全维度 liveness 故障矩阵
  （sequencer / proposer / prover / verifier-gateway / optimistic fallback / pause-guardian /
  permissionless self-propose）。基于此现状逐项对照 L2Beat 当前 CRITICAL / HIGH 风险
  标注与 Stage 1 维度要求，输出三层差距分析矩阵：Stage 0 prerequisites（继承到 Stage 1）/
  实际 Stage 1 要求（Security Council walkaway、非 SC 升级 ≥7d exit window）/ 非阻断风险
  维度与 Stage 2 改进项（permissionless proof submission 等）。聚焦合约接口、链上参数、
  信任假设与代码引用；EigenDA 历史架构仅作背景提及；MNT tokenomics、生态应用层、具体
  升级方案设计（由后续 Wave 1 issue 覆盖）不在 scope 内。

audience: |
  Multica 研究 squad 内部下游 Adversarial Agent 与 Technical Writer；
  Mantle 协议工程师、合约升级与治理负责人；关注 Mantle Stage 1 路径的
  L2 安全研究员、L2Beat 评级团队、Mantle DAO 治理参与者、机构托管 / 风控团队
  与跨链桥集成方。读者熟悉 OP Stack 基础（OptimismPortal、L2OutputOracle、
  ProxyAdmin、TransparentUpgradeableProxy）、Ethereum EIP-4844 blob 机制
  与 L2Beat Stages 框架（含 2026 年针对 ZK setups 的 verifier transparency 补充要求），
  但不一定了解 Mantle 在 2026 年 完成 EigenDA → Ethereum blobs 迁移与 OP Succinct
  主网部署之后的最新合约现状、SP1VerifierGateway 路由层结构、以及 core rollup /
  L1MantleToken / mETH 三条治理路径的分叉。

expected_output: |
  - Mantle 2026.05 技术架构全景研究文档，覆盖 DA / Proof / Governance / Sequencer-Proposer
    四个维度，每个维度给出合约级组件清单、关键参数取值、信任假设与已知风险
  - DA 层：Ethereum blobs 集成方式（batcher 路径、blob commitment 处理、calldata fallback
    触发条件）、对应合约（BatchInbox / DataAvailabilityChallenge 如有）、当前 blob 占比
  - 证明系统：SuccinctL2OutputOracle 合约状态机、SP1VerifierGateway 路由层
    （route id 选择机制、route registry 治理、add/freeze route 权限与 owner/multisig、
    route 失效场景与回退路径）、SP1Verifier 实例（含 vk / program hash / circuit ceremony
    reproducibility 与公开度）、optimistic mode 切换权限、proof 生成 pipeline
    （Kona derivation → SP1 zkVM → Succinct Prover Network）
  - 合约治理：三条独立路径并列输出
    1) 核心 rollup 合约升级路径（OptimismPortal / SystemConfig / SuccinctL2OutputOracle /
       SP1VerifierGateway 等的 ProxyAdmin → owner → TimelockController（含 `minDelay()` 实际值）
       → execution；明确这是否是 Stage 1 exit-window 分析所依据的"主路径"）；
    2) L1MantleToken / MNT 治理路径（MNT proxy 的 admin、token-side timelock 配置、与核心
       rollup 治理是否解耦）；
    3) mETH / 产品级 timelock 路径（mETH 或其他 LST 产品合约的 timelock 配置；若无则显式
       记录"无独立 timelock"）；
    并显式标出哪一条路径会被 Stage 1 exit-window / Security Council 评分使用。
  - Sequencer / Proposer：sequencer 单点状态、白名单 proposer 数量与切换权限、force-inclusion
    路径（OptimismPortal.depositTransaction → 12h sequencing window）、最大 censorship delay
  - Liveness 故障矩阵（generalized）：包含 sequencer failure、proposer failure、
    prover failure、SP1VerifierGateway / route failure、optimistic-mode fallback 与
    challenger liveness、pause / Guardian 恢复路径、permissionless self-propose / 自动
    恢复路径（如存在）；2026-04-22 7h28m 异常仅作其中一条故障的具体证据
  - L2Beat 当前对 Mantle 的完整 CRITICAL / HIGH 风险列表（带 L2Beat 项目页引用，每项含
    根因 / 触发条件 / 用户影响），显式包含两条新风险：
      * "Unsafe verifier route id selection by proposer"（proposer 可选择不安全 verifier 路由）
      * "SP1VerifierGateway routing failure"（route registry 故障导致 proof 无法被验证）
  - Stage 1 差距分析矩阵（三层结构）：
      (a) Stage 0 prerequisites inherited by Stage 1（DA on L1、proof system online、
          permissioned proof submission OK 等）
      (b) 实际 Stage 1 要求（Security Council walkaway test、≥7d exit window for non-SC
          upgrades、SC ≥8 members & >75% threshold、ZK verifier transparency 等）
      (c) 非阻断风险维度 / Stage 2 改进项（permissionless proof submission、verifier
          route 去中心化、proposer 集合开放、challenger 去中心化等）
    每行包含 current_state / gap_description / severity / stage_classification /
    blocking_for_stage1 / remediation_owner
  - 关键合约地址与配置参数汇总表：每个 critical contract 必须给出 proxy address /
    implementation address / admin / owner / key getters（minDelay、PROPOSER、
    SEQUENCING_WINDOW、blob settings 等）/ role holders / verified source 状态
    （verified / partially verified / unavailable）/ 来源（Etherscan permalink、官方 docs、
    GitHub commit）；任何 verified source 不可得的合约必须显式标注 "Source unavailable"
    并采用 fallback evidence 规则（spec docs / 链上 storage 读取 / 治理提案）
  - 至少 5 张 Mermaid 图：四维度架构总览（含 SP1VerifierGateway + route registry / owner）、
    交易生命周期（含 verifier route 选择）、三条治理路径权限链（核心 rollup / MNT / mETH）、
    Stage 1 差距热力图（三层结构）、L2Beat 风险根因映射图（含 verifier route 失败路径）
  - 所有事实性数据必须给出代码引用（仓库 / 文件 / commit / 行号）或 Etherscan / L2Beat
    permalink；任何无法获得链上 verified source 或公开 spec 的合约必须显式标注
    "Source unavailable" 并禁止伪造引用

source_requirements_summary: |
  Primary 源：L2Beat Mantle 项目页（含 SP1VerifierGateway 与 unsafe verifier route 相关
  风险条目）、Mantle 官方 docs、Etherscan verified source（含 proxy → implementation
  映射、SP1VerifierGateway route registry 读取）、Mantle GitHub 仓库（mantle-v2 / op-geth /
  kona / op-succinct，含 SP1 verifier 与 vk / program hash 公开度）、Mantle 官方博客与
  Succinct 博客关于 OP Succinct 主网部署与 Ethereum blobs 迁移。
  Secondary 源：OpenZeppelin 对 Mantle op-stack diff 的审计（如可访问）、L2Beat Stages
  框架文档与 ZK setups 补充要求论坛讨论、Mantle 治理论坛 / 提案。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-18T15:23:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-18T15:48:00Z"
---

# Research Outline: Mantle 当前技术架构全景（2026.05）

## Items

### item-1: 数据可用性层（Ethereum blobs DA）

刻画 Mantle 在 2026 年完成 EigenDA → Ethereum blobs 迁移后的 DA 架构：batcher 如何将
L2 transaction data 编码并以 EIP-4844 blob 形式提交至 L1（含 blob versioned hash 写入
BatchInbox 的具体调用路径）、blob 不可得 / blob fee spike 时的 calldata fallback 触发
条件与降级机制、当前主网 blob 与 calldata 的实际占比、与 Fusaka 升级后 blob 容量参数
（BLOB_BASE_FEE_UPDATE_FRACTION、TARGET_BLOB_GAS_PER_BLOCK、blob 价格曲线）的对接。
需要明确：DA 数据是否 100% 上 L1（满足 L2Beat "data availability on L1" 标准）、是否仍
保留任何 off-chain DA 路径或 DA challenge 合约（DataAvailabilityChallenge / DAC 类型
组件），并确认 EigenDA 代码路径在合约和 batcher 中均已移除。EigenDA 历史架构仅作 1-2
段背景提及，不作完整对比。

- **Priority**: high
- **Dependencies**: none

### item-2: 证明系统（OP Succinct + SP1 zkVM + SP1VerifierGateway 路由层）

合约级分析 Mantle 在 2026 年完成 OP Succinct 主网部署后的证明系统，必须覆盖两层结构：
**(A) SuccinctL2OutputOracle 提案与验证层**，**(B) SP1VerifierGateway 路由层**。

**(A) SuccinctL2OutputOracle**：作为 L2OutputOracle 的扩展实现 `whenNotOptimistic`
modifier 的具体逻辑、proposeL2Output 对 validity proof bytes 的处理路径与 verifier
调用路径（gateway vs. 直连 verifier 实例）、`whenNotOptimistic` / optimistic mode 切换
的权限与触发条件（是否仍可在故障时回退到 optimistic 模式、由谁触发、是否走 timelock）、
permissioned proposer 集合的存储位置与变更入口、SuccinctL2OutputOracle 的状态机
（pending output → proven → finalized / challenged）。

**(B) SP1VerifierGateway 路由层（first-class research target）**：必须独立成段，覆盖：

- **route id 选择机制**：proposeL2Output 调用如何选定本次 proof 应被哪个 verifier route
  验证（route id 是 proposer 输入参数、合约状态、还是固定常量？是否允许 proposer 选择
  不安全 / 已 frozen 的 route？）；
- **route registry 治理**：哪个合约 / mapping 维护 route id → SP1Verifier 实例的映射、
  add route / freeze route / remove route 的权限分布、route owner 是 EOA / multisig /
  TimelockController；
- **route 生命周期与回退**：当唯一可用 route 失效（被 freeze、SP1Verifier 漏洞、
  vk 不可用）时的 fallback 行为（cease 提交、强制 optimistic、需治理介入）；
- **verifier 可重现性 & 程序哈希**：每个有效 route 背后的 SP1Verifier 部署地址、
  verifying key（vk）来源、是否 immutable 还是 governance-updatable、程序哈希 / circuit
  digest 是否公开可比对、ceremony 是否可重新生成、源代码 commit SHA 与 release 关联；
- **route 治理与 transparency 风险点**：直接映射到 L2Beat 当前列出的
  "unsafe verifier route id selection by proposer" 与 "SP1VerifierGateway routing failure"
  两条风险（与"validity proof cryptography broken"是**独立**风险）。

**链下 proof pipeline**（背景补充，不重复 (A)/(B) 内容）：Mantle Succinct Server 从 L1 /
DA 取 batch → Kona 进行 block derivation → SP1 zkVM 生成 range proof → aggregated
groth16 proof → proposer 提交。

需识别 L2Beat 当前对 Mantle 列出的至少四类与 proof 相关的已知风险在合约层的具体位点：
"funds can be stolen if validity proof cryptography is broken or implemented incorrectly"、
"funds can be frozen if permissioned proposer fails"、"unsafe verifier route id selection"、
"SP1VerifierGateway routing failure"。

- **Priority**: high
- **Dependencies**: none

### item-3: 合约治理与升级机制（三条独立路径并列分析）

合约升级与治理路径必须**显式拆分为三条独立子结构**，分别独立给出合约清单、admin / owner
链、TimelockController 部署地址与 `minDelay()` 实际值、PROPOSER / EXECUTOR /
TIMELOCK_ADMIN_ROLE 角色持有者、紧急升级 / pause / Guardian 旁路、以及与 Stage 1
exit-window 分析的关系：

**(a) 核心 rollup 合约升级路径（Stage 1 评估主路径）**

- 列出关键 proxy 合约：OptimismPortal、L1StandardBridge、L1CrossDomainMessenger、
  SuccinctL2OutputOracle、SP1VerifierGateway（含 route registry 自身的升级权限）、
  SystemConfig、AddressManager 等的 admin 字段现值（onchain ProxyAdmin 地址）；
- ProxyAdmin 合约的 owner（EOA / multisig / Timelock 地址），并追踪 owner 是否进一步
  指向 TimelockController；
- TimelockController 的实际部署地址与链上 `minDelay()` 当前返回值（注意区分 L2Beat 标注
  的 "instant upgradability" 与 mETH 文档中提到的 "默认 delay = 0" 两类来源是否针对**这条
  路径**），以及 PROPOSER / EXECUTOR / TIMELOCK_ADMIN_ROLE 三种角色当前持有者；
- Security Council / multisig 当前签名者数量、阈值、是否 ≥8 人且 >75% 阈值
  （L2Beat Stage 1 Security Council 资格门槛）；
- Guardian / pause / emergency upgrade 路径（OptimismPortal 的 pause、SystemConfig 的紧急
  参数调整、SP1VerifierGateway route freeze 等）；
- 跨链 admin（任何 L1 → L2 admin 消息或反向 admin 路径）。
- **明确陈述**：此条路径是否被 Stage 1 exit-window 评分采用？是否存在 ≥7d exit window？

**(b) L1MantleToken / MNT 治理路径**

- L1MantleToken proxy 的 admin、owner、MNT token-side TimelockController（如有）的部署
  地址与 `minDelay()`；
- 升级 / mint / 参数变更权限（owner、minter 角色、emergency pause）；
- 与 (a) 核心 rollup 治理是否解耦（同一 multisig、不同 multisig、还是单纯 EOA owner）；
- 是否会被 Stage 1 评分使用：通常不直接影响 rollup exit-window，但若发现共享 multisig /
  共享 timelock，必须显式上报。

**(c) mETH / 产品级 timelock 路径**

- mETH 或其他 LST 产品合约的 timelock 配置、admin、owner；
- 与 (a)/(b) 的关系：是否独立、是否复用同一 Security Council 与 TimelockController；
- 若不存在独立 timelock，须显式记录 "无独立产品级 timelock，受 (a) 或 (b) 同一治理覆盖"
  或 "Source unavailable"。

所有结论以 Etherscan verified source + 链上状态读取为准；任何不可获得 verified source
的合约须显式标注 "Source unavailable" 并使用 src-3 中规定的 fallback evidence 规则。

- **Priority**: high
- **Dependencies**: none

### item-4: Sequencer / Proposer 中心化、Force Inclusion 与 Liveness 故障矩阵

刻画 Mantle 当前 sequencer / proposer 中心化程度、抗审查路径，以及**全维度 liveness 故障
矩阵**（不再以 2026-04-22 单一事件为研究边界）：

**Sequencer / Proposer 静态状态**：

- **Sequencer**：节点数量、运营方、地址、是否存在 fallback / standby sequencer、
  sequencer key 持有者、sequencer revenue 流向；
- **Proposer**：SuccinctL2OutputOracle / L2OutputOracle 中 `PROPOSER` 角色或 whitelist
  集合的当前成员数与地址，proposer 替换 / 添加的权限路径；明确 "如果所有 whitelisted
  proposer 全部失效，提款是否被冻结" 的结论与链上证据；
- **Force inclusion 路径**：OptimismPortal `depositTransaction` 的调用模式、sequencing
  window（默认 12h）当前是否被修改、Max Time Drift（30 min）配置位置、用户从 L1 deposit 到
  L2 强制执行的端到端延迟、是否覆盖任意 calldata 调用（即不仅是 ETH/ERC20 deposit，也包括
  任意 L2 合约 call）。

**Liveness 故障矩阵（generalized）**：以下每条故障必须列为独立行，给出 detection
mechanism / current recovery path / required actor / max recovery delay / 用户提款是否受阻：

1. **Sequencer failure**：sequencer 长时间宕机时用户能否仅通过 L1 force-inclusion 在
   ≤12h+ 内完成提款；
2. **Proposer failure**：所有 whitelisted proposer 全部失效场景下的提款冻结风险与恢复路径；
3. **Prover failure**：Succinct Prover Network / Mantle Succinct Server 长时间无法产出
   proof 时的影响（state root 不更新 → 提款 finality 阻塞）；
4. **SP1VerifierGateway / verifier-route failure**：当唯一可用 verifier route 被 freeze、
   或路由层异常导致 proof 无法被验证时的影响与恢复路径（治理介入 / optimistic 回退）；
5. **Optimistic-mode fallback liveness**：optimistic 模式是否仍存在、challenger 集合
   （是否 permissioned / 是否可用）、若 challenger 全部失效是否仍能 finalize；
6. **Pause / Guardian 恢复路径**：OptimismPortal pause、SystemConfig 紧急调整、
   SP1VerifierGateway route freeze 等紧急操作的权限分布与最长生效延迟；
7. **Permissionless self-propose / 自动恢复路径**：是否存在 "在 permissioned proposer 长期
   不出 output 后任何人都可代为提交" 的链上机制？若不存在，须显式记录 "No permissionless
   self-propose path"。

**历史 liveness 事件证据**：2026-04-22 07:44–15:12 UTC（7h 28m）状态更新中断的根因
复盘（sequencer down vs proposer down vs proof generation stalled vs verifier-gateway
issue）仅作为上述故障矩阵中**某一条具体故障**的实证案例引用，不再作为整个 item 的主轴。

- **Priority**: high
- **Dependencies**: none

### item-5: L2Beat 风险标注完整列表与解读

逐项整理 L2Beat Mantle 项目页（https://l2beat.com/scaling/projects/mantle）当前对 Mantle
标注的所有 CRITICAL 与 HIGH 风险项，**必须显式覆盖**以下类别（如 L2Beat 页面有调整，须按
当时实际列表完整收录，并标明 retrieval 时间）：

- "Instant Upgradability — no exit window for unwanted upgrade"
- "Whitelisted Proposers — withdrawals can be frozen"
- "Funds can be stolen if validity proof cryptography is broken or implemented incorrectly"
- "Funds can be stolen if optimistic mode is enabled and no challenger checks"
- "Funds can be frozen if permissioned proposer fails to publish state roots"
- **"Unsafe verifier route id selection by proposer"**（proposer 可在 SP1VerifierGateway
  上选定不安全 / 未审计 / 已 frozen 的 verifier route）
- **"SP1VerifierGateway routing failure"**（route registry 故障 / 无有效 route 导致 proof
  无法被验证、出现 funds frozen 风险）
- "Liveness anomaly 2026-04-22 7h28m gap"（及任何后续 L2Beat 记录的 liveness 事件）

每条风险给出：

1. L2Beat 原文措辞与 permalink（含 retrieval 时间戳）；
2. 根因映射到 item-1 ~ item-4 的哪个具体合约 / 参数 / actor（verifier-route 类风险须明确
   映射到 item-2 (B) SP1VerifierGateway 路由层与 item-3 (a) 路由层升级权限）；
3. 触发条件与最坏用户影响（funds stolen / funds frozen / funds censored）；
4. L2Beat 标注的严重度（CRITICAL / HIGH / MEDIUM）；
5. 与 Stage 0 / Stage 1 / Stage 2 阶段判定的关系（按 item-6 三层结构归类）。

需校验 L2Beat 截图 / 文本与 Mantle 链上实际状态是否一致；不一致处需在 draft 中明确指出。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4

### item-6: Stage 1 差距分析矩阵（三层结构）

以 L2Beat Stages 框架的最新 Stage 1 定义为基础，构建**三层差距分析矩阵**，每条要求作为
一行，每行明确归入下列三个 tier 之一：

**Tier (a)：Stage 0 prerequisites inherited by Stage 1**（Stage 1 默认继承的 Stage 0 前置
条件，未达将连 Stage 0 都失格）

- DA on L1：交易数据是否 100% 上 L1（含 blob 与 calldata fallback 两种路径）；
- 完整且功能正常的 proof system online：proof 是否对所有 state transition 生效、链上 finality
  是否依赖该 proof；
- 关键合约源码 verified / spec 公开度。

**Tier (b)：实际 Stage 1 要求（blocking_for_stage1 = yes 的真实门槛）**

- **Security Council walkaway test**：在 Security Council 失效场景下，用户是否仍能通过 L1
  完成提款；
- **非 SC 升级 ≥7d exit window**：所有不通过 Security Council 直接执行的核心 rollup 合约
  升级（item-3 (a)）是否经过至少 7d timelock 且用户在生效前可完成 L1 提款；
- **Security Council 资格**：≥8 成员、阈值 >75%、签名者多样性；
- **ZK verifier transparency（2026 新补充要求）**：SP1Verifier vk 公开度、program hash
  可重现性、SP1VerifierGateway route registry 治理透明度（包括 add/freeze route 必须有
  公开记录与治理签名）。

**Tier (c)：非阻断风险维度 / Stage 2 改进项（blocking_for_stage1 = no，但仍记入 gap 表）**

- **Permissionless proof submission**：fraud / validity proof 是否任何参与方都能提交
  （L2Beat 当前 Stage 1 框架下，该项属于 Stage 2 改进项，除非它是满足 Tier (b) liveness
  要求的唯一机制）；
- **Verifier route 去中心化**：SP1VerifierGateway route add/freeze 权限是否仍属
  permissioned actor；
- **Proposer 集合开放**：从 whitelist proposer 走向 permissionless proposer；
- **Challenger 去中心化**：若 optimistic mode 仍保留，challenger 集合是否开放。

矩阵每个 cell 标注：

- `current_state`（链上实证，含 evidence link）
- `gap_description`
- `severity`（critical / major / minor）
- `stage_classification`（Tier a / Tier b / Tier c）
- `blocking_for_stage1`（yes / no — 仅 Tier (b) 允许为 yes；Tier (a) 项若未达直接 fail Stage 0；
  Tier (c) 一律 no）
- `remediation_owner`（Mantle Foundation / Security Council / Mantle Labs / Succinct /
  外部 ceremony 参与方）

最终输出一份排序后的 Stage 1 blocker 清单（仅来自 Tier (b)），供下游 Wave 1 issue
（upgrade-exitwindow-securitycouncil、proposer-decentralization-zk-compliance、
stage1-roadmap-recommendation）作为输入；另输出独立的 Tier (a) 与 Tier (c) 提示列表，
分别用于 Stage 0 健康度复核与 Stage 2 改进路线图。**本 item 不设计具体升级方案**，仅识别
差距与严重度。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| high_level_summary | 该 item 的 2-4 句 high-level 概括，作为最终章节首段素材，需直接陈述当前架构现状（不是 EigenDA 历史） | all |
| architecture_components | 该维度涉及的链上 / 链下组件清单：合约名、proxy → implementation 映射、关键 actor、外部依赖（item-2 须独立列出 SP1VerifierGateway 与 route registry 组件） | item-1, item-2, item-3, item-4 |
| contract_addresses_and_config | 关键 proxy / implementation / admin 地址与可读的链上参数取值（mainnet 优先，sepolia 补充）：blob settings、`minDelay()`（每条治理路径分别记录）、`PROPOSER` 集合、`SEQUENCING_WINDOW`、Security Council 成员与阈值、SP1VerifierGateway route registry 当前 route id 与对应 verifier 地址；含 Etherscan permalink | item-1, item-2, item-3, item-4 |
| trust_assumptions | 该维度的信任假设：哪些 actor / 密钥 / 多签 / verifier vk / route owner 是 trusted、被攻陷会导致的最坏后果（funds stolen / frozen / censored 三类） | item-1, item-2, item-3, item-4 |
| l2beat_risk_mapping | 该 item 对应到哪些 L2Beat 风险标签（含 permalink）：item-2 / item-5 必须覆盖 unsafe verifier route id selection 与 SP1VerifierGateway routing failure；并标注 L2Beat 措辞与链上现状是否一致 | item-1, item-2, item-3, item-4, item-5 |
| stage1_requirement_mapping | 该 item 涉及哪些 Stage 1 要求（按 item-6 三层结构归类：Tier a / Tier b / Tier c），并给出"当前是否满足"的初步判定 | item-1, item-2, item-3, item-4, item-6 |
| gap_severity | 与 Stage 1 要求的差距严重度：critical / major / minor；并标注 `stage_classification`（Tier a/b/c）与 `blocking_for_stage1`（yes 仅限 Tier b） | item-5, item-6 |
| liveness_failure_mode | 该组件出现 liveness 故障时的检测机制、恢复路径、所需 actor、最大恢复延迟（用于 item-4 故障矩阵） | item-2, item-3, item-4 |
| 2026_changes_from_prior_state | 该维度在 2026 年内的变化：blob 迁移、OP Succinct 主网部署（含 SP1VerifierGateway 引入）、proposer 集合调整、timelock 配置变化等；需对比 2025 年末状态 | item-1, item-2 |
| evidence_sources | 主要引用源：L2Beat permalink（含 retrieval 时间）、Etherscan verified source、Mantle 官方 docs / blog、GitHub commit URL；区分 primary / secondary 并显式标注每条数据的来源；任何 verified source 不可得须按 src-3 fallback 规则处理 | all |
| code_references | 代码引用：仓库（mantlenetworkio/mantle-v2、op-geth、mantle-xyz/kona、mantle-xyz/op-succinct）/ 文件 / commit SHA / 行号；任何无法获取 verified source 的合约必须显式标注 "Source unavailable — fallback to spec / docs / on-chain read"，禁止伪造行号 | item-1, item-2, item-3, item-4 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Mantle 2026.05 四维度架构总览图：L1 侧标出 OptimismPortal / L1StandardBridge / L1CrossDomainMessenger / BatchInbox / SuccinctL2OutputOracle / **SP1VerifierGateway（含 route registry 与 route owner / multisig）** / 多个 SP1Verifier route 实例 / ProxyAdmin / TimelockController（核心 rollup 路径） / L1MantleToken proxy（独立标注其 admin 路径） / mETH 产品合约（如有，独立标注） / Security Council multisig；L2 侧标出 op-geth sequencer / Mantle Succinct Server / Kona derivation；标注 EigenDA 已 deprecated；以颜色区分 DA / Proof / Governance / Sequencer-Proposer 四个维度 | mermaid | item-1, item-2, item-3, item-4 |
| diag-2 | sequence | 交易从用户提交到 L1 finality 的端到端生命周期序列图：User → Sequencer → op-geth → Batcher → BatchInbox（blob）→ Mantle Succinct Server (Kona derivation + SP1 proof) → Proposer → SuccinctL2OutputOracle.proposeL2Output → **SP1VerifierGateway 按 route id 路由 → 对应 SP1Verifier 实例.verify** → finalized；并附 force-inclusion 子图（User → OptimismPortal.depositTransaction → 12h sequencing window → 强制执行）；附 calldata fallback 分支 | mermaid | item-1, item-2, item-4 |
| diag-3 | hierarchy | 合约升级权限与依赖关系图（三条并列子图）：(a) 核心 rollup 路径：所有关键 proxy 合约（含 SP1VerifierGateway 自身）→ ProxyAdmin → owner → TimelockController（标注 minDelay 实际值）→ Security Council multisig（标注成员数 / 阈值）；高亮 instant-upgrade 路径（若存在）与 Guardian / pause 旁路；显式标出是否存在 ≥7d exit window；(b) L1MantleToken / MNT 治理路径；(c) mETH / 产品级 timelock 路径。三子图共享同一 Security Council 时须画出共享节点 | mermaid | item-3 |
| diag-4 | comparison | Stage 1 差距分析热力图 / 矩阵：行按 item-6 三层结构（Tier a / Tier b / Tier c）分组，列为 Mantle 当前状态、差距描述、严重度、stage_classification、是否阻断 Stage 1；以颜色编码 severity（critical = red, major = orange, minor = yellow, ok = green） | mermaid | item-6 |
| diag-5 | flow | L2Beat CRITICAL / HIGH 风险根因映射图：每条风险节点 → 对应的合约 / 参数 / actor / Stage 1 要求；按 funds stolen / frozen / censored 三类用户影响分组；**必须显式包含**：unsafe verifier route id selection 路径（proposer → SP1VerifierGateway → 不安全 route → SP1Verifier → 错误 proof 接受）、SP1VerifierGateway routing failure 路径（route registry 故障 → 所有 route freeze / 无有效 route → proof 无法验证 → funds frozen）、以及 route owner / multisig 节点作为这两类风险的治理控制点 | mermaid | item-5 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | L2Beat Mantle 项目页（https://l2beat.com/scaling/projects/mantle）：风险表（含 unsafe verifier route id selection、SP1VerifierGateway routing failure 两条新风险）、参数表、Stage 分类、liveness 异常记录；retrieval 时间戳必须标注；同页面对 Stages 框架要求的当前定义（Stages 页 + 论坛 ZK setups 补充要求） | 2 |
| src-2 | official_docs | Mantle 官方 docs（https://docs.mantle.xyz）与 Mantle 官方博客 / Succinct 官方博客关于 OP Succinct 主网部署、SP1VerifierGateway 路由机制、Ethereum blobs 迁移、proof 架构、timelock 配置的说明 | 3 |
| src-3 | on_chain_data | Mainnet（必要时 Sepolia）Etherscan verified source 与状态读取。覆盖范围采用 **exhaustive critical-contract coverage**（不再以 min_count=N 计），每个 contract 必须独立成行并给出下列六项：(1) proxy address (2) implementation address (3) admin / owner (4) 关键 getter 返回值（minDelay、PROPOSER、SEQUENCING_WINDOW、blob settings、route id、verifier 地址等，按合约语义选择）(5) role holders（PROPOSER / EXECUTOR / TIMELOCK_ADMIN_ROLE / GUARDIAN 等）(6) verified source 状态（verified / partially verified / unavailable）+ fallback 来源（spec docs / chain storage read / governance proposal）。Critical-contract 清单至少包含：OptimismPortal、L1StandardBridge、L1CrossDomainMessenger、BatchInbox、SuccinctL2OutputOracle、SP1VerifierGateway、当前所有有效 SP1Verifier route 实例、ProxyAdmin（核心 rollup）、TimelockController（核心 rollup）、SystemConfig、AddressManager、Security Council multisig、L1MantleToken proxy 与其 admin/owner、L1MantleToken-side TimelockController（如有）、mETH / 产品级合约（如适用）、Guardian / pause executor。任一合约 verified source 不可得时必须显式标注 "Source unavailable" 并写明改用的 fallback 规则；禁止以未引用源代码的形式断言参数或权限 | n/a — 见 Description 中的 exhaustive coverage 规则 |
| src-4 | code_analysis | GitHub 仓库源码：mantlenetworkio/mantle-v2（含 packages/contracts、op-batcher、op-proposer、op-node 等子目录）、mantlenetworkio/op-geth、mantle-xyz/kona、mantle-xyz/op-succinct（含 SP1VerifierGateway / SP1Verifier 源码与 vk / program hash 公开度）；每条引用须给出 commit SHA 与行号；覆盖 batcher blob 提交、proposer SP1 proof 提交、verifier-gateway 路由逻辑、derivation pipeline | 4 |
| src-5 | audit_reports | OpenZeppelin 对 Mantle op-stack diff 的审计报告（如可访问）、其他 Mantle 公开审计（Sigma Prime / OtterSec / Trail of Bits 等如有）、SP1 / Succinct 公开审计（含对 SP1VerifierGateway 与 route 机制的审计如有）；若审计无公开版本，须显式说明并改用 spec + 链上读 | 1 |
| src-6 | expert_commentary | L2Beat Stages 框架文档（https://l2beat.com/stages）、L2Beat Medium 文章（Stages update、Security Council walkaway test、ZK setups verifier transparency 补充要求）、Vitalik 关于 multiproof / Stage 1 的公开论述 | 3 |
| src-7 | governance_proposals | Mantle 治理论坛 / 提案与社区讨论（涉及 timelock 配置、proposer 白名单调整、SP1VerifierGateway route add/freeze 提案、Stage 1 路线图）；若无相关提案存在，须明示 | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-2 | Add SP1VerifierGateway as first-class research target (route id selection mechanism, route registry governance, route owner/multisig, verifier reproducibility, program hash & source availability). Distinct risk dimension from validity proof breakage. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 (accepts adversarial finding from comment c64a00ef-cc73-48b5-81c0-b839395994cd, major) |
| 2 | modify_item | item-3 | Split governance into three independent sub-paths: (a) core rollup contracts upgrade path (ProxyAdmin → Timelock → execution, actual minDelay), (b) L1MantleToken/MNT governance path, (c) mETH/product-specific timelocks. Explicitly state which path feeds Stage 1 exit-window analysis. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 (major) |
| 2 | modify_item | item-4 | Expand liveness scope from single 2026-04-22 incident to a generalized liveness-mode matrix covering sequencer failure, proposer failure, prover failure, verifier-gateway failure, optimistic-mode fallback / challenger liveness, pause/guardian recovery, and any permissionless self-propose / auto-recovery path. Historical 2026-04-22 incident kept as evidence row. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 (minor, required) |
| 2 | modify_item | item-5 | Add missing L2Beat risk rows: "Unsafe verifier route id selection by proposer" and "SP1VerifierGateway routing failure"; require root-cause mapping to item-2 (B) verifier-gateway layer and item-3 (a) route-registry upgrade authority. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 (major) |
| 2 | modify_item | item-6 | Restructure gap matrix into three tiers: (a) Stage 0 prerequisites inherited by Stage 1, (b) actual Stage 1 requirements (SC walkaway, ≥7d exit window for non-SC upgrades, SC ≥8/>75%, ZK verifier transparency), (c) non-blocking risk dimensions / Stage 2 improvements (permissionless proof submission, verifier route decentralization, etc.). Only Tier (b) rows may have blocking_for_stage1=yes. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 (major) |
| 2 | modify_source_req | src-3 | Replace `min_count=8` with exhaustive critical-contract coverage. For each contract require six fields: proxy address, implementation address, admin/owner, key getters, role holders, verified source status + explicit fallback rule when source unavailable. Critical-contract list enumerated explicitly (includes SP1VerifierGateway, all active SP1Verifier route instances, L1MantleToken proxy, optional mETH/product contracts). | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 (minor, required) |
| 2 | modify_diagram | diag-1 | Add SP1VerifierGateway, route registry, route owner/multisig, multiple SP1Verifier route instances, plus independent nodes for L1MantleToken admin path and mETH product path. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
| 2 | modify_diagram | diag-2 | Add SP1VerifierGateway route-id routing step between proposeL2Output and SP1Verifier.verify in the end-to-end transaction lifecycle sequence. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
| 2 | modify_diagram | diag-3 | Split hierarchy diagram into three parallel sub-diagrams matching item-3 (a)/(b)/(c) governance paths; show shared Security Council node where applicable. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
| 2 | modify_diagram | diag-4 | Reorganize Stage 1 gap heatmap rows by Tier a/b/c grouping per restructured item-6 matrix. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
| 2 | modify_diagram | diag-5 | Add explicit verifier-route failure paths: (1) unsafe verifier route id selection by proposer, (2) SP1VerifierGateway routing failure (no valid route / route registry failure), plus route owner/multisig as governance control node. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
| 2 | modify_field | l2beat_risk_mapping | Require item-2 / item-5 coverage of verifier route id and SP1VerifierGateway routing failure risks. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
| 2 | modify_field | stage1_requirement_mapping | Replace flat Stage 1 mapping with three-tier classification (Tier a/b/c) aligned with restructured item-6. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
| 2 | modify_field | gap_severity | Add `stage_classification` (Tier a/b/c) and constrain `blocking_for_stage1=yes` to Tier (b) only. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
| 2 | add_field | liveness_failure_mode | New field to support generalized liveness matrix in item-4 (detection mechanism, recovery path, required actor, max recovery delay). | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
| 2 | modify_field | contract_addresses_and_config | Add SP1VerifierGateway route registry / route id / per-route verifier address; require per-path `minDelay()` for the three governance paths. | Orchestrator gate decision 3dc02a4a-9399-4417-b68c-6ce863a4e560 |
