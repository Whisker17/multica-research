---
topic: "Gas 参数与协议层性能配置对比 (Base vs Mantle)"
project_slug: base-perf-analysis
topic_slug: gas-protocol-perf-config
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: base-perf-analysis/outlines/gas-protocol-perf-config.md
  draft: base-perf-analysis/research-sections/gas-protocol-perf-config/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/gas-protocol-perf-config/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  对比 Base 与 Mantle (mantle-v2) 在协议层 Gas 与计费参数、Block 时序参数、单笔交易 Gas
  上限（EIP-7825）以及关键 precompile/MODEXP 重计价等方面的配置差异，量化这些差异对
  理论 TPS 上限的直接影响，并识别 Mantle 仅通过参数调整即可获得的 quick-win 性能提升。
  不进入执行层客户端实现差异、batcher/DA 层 gas 参数、以及 token 经济学层面的 gas 定价
  分析（由其他课题覆盖）。
audience: |
  Mantle 协议核心工程师、Mantle 性能/Sequencer 团队、关注 L2 吞吐路线图的产品负责人，
  以及需要在不修改执行层代码的前提下评估快速优化空间的运营/治理决策者。读者熟悉 EIP-1559
  与 L2 rollup 基本架构，但不一定熟悉 Base 最近的 Pectra/Azul/EIP-7825 升级细节。
expected_output: |
  - Base vs Mantle 协议层关键参数对比表（gas limit、target gas、elasticity、block time、
    per-tx gas cap、max code size、calldata pricing、MODEXP / precompile 重计价）
  - 基于典型 L2 交易 mix（ERC-20 transfer / Uniswap swap / NFT mint / contract deploy）
    的理论 TPS 计算与 Base/Mantle 上下界对比
  - Quick-wins 清单：至少 2 条 Mantle 可在无 hardfork 或仅最小配置变更下落地的参数调整建议
  - 参数调整的安全风险评估（state growth、DoS surface、re-org/finality 影响）
  - Mermaid 图表：参数对比矩阵 + 参数调整优先级象限 + TPS 敏感度示意

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-20T04:25:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-20T04:25:00Z"
---

# Research Outline: Gas 参数与协议层性能配置对比 (Base vs Mantle)

## Items

### item-1: Block Gas Limit 与 Target Gas 对比

调查 Base 和 Mantle (mantle-v2) 主网当前生效的 block gas limit / target gas / elasticity multiplier
配置，并梳理两条链上历次调整这些参数的 hardfork 时序。需要从 base/base 仓库（chain spec、
genesis、SystemConfig 合约 gasLimit 字段）以及 mantlenetworkio/mantle-v2 与 op-geth fork
的 chain config 中拉取原始数值，并交叉验证 etherscan / mantlescan 主网区块的实际 gasLimit
header。重点厘清 L2 上 elasticity_multiplier 与 base fee 自适应算法（EIP-1559 vs OP
Stack Holocene EIP-1559 修改版）对突发交易吸收能力的差异。

- **Priority**: high
- **Dependencies**: none

### item-2: Block Time 与执行预算

对比 Base 和 Mantle 当前的 block time 设置（含历史变化：Base 2s → 200ms Flashblocks
分片、Mantle 仍以 2s 标准 L2 block）以及 block time 对 sequencer 执行预算、传播延迟、
finality 体验的复合影响。结合 OP Stack 默认 block time 设置、Base 在 Flashblocks /
Azul 路线图中对 block time 的进一步压缩，估算 block time 减半的执行端约束（每个 block
的实际可用 wall-clock 执行时间、batcher commit 周期、L1 数据可用性 cost 边际增长）。

- **Priority**: high
- **Dependencies**: item-1

### item-3: EIP-7825 Per-Transaction Gas Cap

详细考察 Base 在 Pectra/Azul 升级中跟随主网引入的 EIP-7825（单笔交易最多 ~16,777,216 gas，
即 2^24 gas）：执行层语义、对超大 contract deploy / 复杂 swap 的影响、对 sequencer
DoS surface 的保护作用，以及对 block packing 效率的潜在副作用（"几乎填满但放不下"的
碎片化）。然后核实 Mantle 当前是否实施了等效的 per-tx 上限（推测：未实施，仅受 block
gas limit 与 sequencer 软策略约束），如未实施则评估 Mantle 引入 7825-类硬上限的代价
与收益。

- **Priority**: high
- **Dependencies**: item-1

### item-4: Calldata / Blob Gas Pricing 与 OP Stack 特有参数

对比 Base 和 Mantle 在 calldata 计费（标准 16/4 gas per byte vs L2 floor cost）、
EIP-4844 blob gas 引入后的 fjord/granite 公式调整、L1 data fee 计算（OP Stack
SystemConfig 的 scalar / blobScalar 分量），以及 OP Stack 特有的 isthmus/holocene
参数（如 Holocene 的 EIP-1559 dynamic params）。需要量化 calldata 计费方式对常见
L2 交易实际 gas 占用的影响，明确"protocol 层 gas pricing"和"L1 cost 经济学"之间
的边界（后者由 batcher 课题覆盖）。

- **Priority**: high
- **Dependencies**: item-1

### item-5: MODEXP / Precompile Gas 重计价与合约部署成本

梳理 Pectra/Prague 引入的 MODEXP 重计价（EIP-7883，最小 gas 翻倍至 500、平方项系数
上调）、EIP-7951 secp256r1 precompile 重新计价、EIP-7823 MODEXP 输入大小上限，以及
EIP-3860 init code 上限对合约部署成本的影响。需要确认 Base 已经在哪个 fork 启用、
Mantle 当前的 precompile gas 表（包含 BLS12-381、point evaluation 等）与对应 cost
是否落后于 Prague 主网，并评估升级到 Prague 等价 precompile 表对 RIP-7212 / Account
Abstraction 类应用 TPS 的影响。

- **Priority**: medium
- **Dependencies**: item-1

### item-6: 典型 L2 交易 Mix 下的理论 TPS 计算

基于上面四类参数差异，对四种典型 L2 交易（ERC-20 transfer ≈ 21k–50k gas、Uniswap v3
exactInputSingle swap ≈ 130k–180k gas、ERC-721 mint ≈ 80k–150k gas、合约部署 ≈ 1M+ gas）
建立 TPS 模型：理论上限 = block_gas_limit / (avg_tx_gas × block_time)。
分别给出 Base 当前参数下的 TPS（含 Flashblocks 折算）、Mantle 当前参数下的 TPS、
以及"Mantle 参数升级到 Base 水平"的边际增益。对结果给出敏感度分析与置信区间（哪些
数字基于实测，哪些基于 chain spec 推算）。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

### item-7: Quick Wins 清单与参数调整优先级矩阵

将所有可被参数调整覆盖的优化点按"预期 TPS 收益 / 安全或经济风险 / 工程复杂度"三维
打分，输出 quick-wins 清单（至少 2 条无需代码修改、可通过 SystemConfig 或 chain config
hardfork-fork-bound 参数变更落地的建议），以及一张优先级象限图。明确每条建议的：
当前值、推荐值、变更途径（链上 SystemConfig 调用 / hardfork 配置 commit）、预期影响、
回滚策略。

- **Priority**: high
- **Dependencies**: item-6

### item-8: 安全风险评估与 DoS Surface

对所有 quick-wins 候选项展开安全风险评估：state growth 加速（更大 gas limit + 更便宜
SSTORE 触发 trie 增长）、sequencer DoS surface（无 per-tx cap 下的 worst-case block
执行时间）、re-org 与 finality 影响（缩短 block time 时与 L1 inclusion 节奏的耦合）、
batcher cost 上涨（更大 block ⇒ 更大 calldata/blob 提交）、价格震荡（base fee
elasticity 调整对 wallet UX 的影响）。给出每项风险的可观察指标与降级路径。

- **Priority**: medium
- **Dependencies**: item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| current_value | Base / Mantle 主网当前生效的参数数值（含数据来源与时间戳） | item-1, item-2, item-3, item-4, item-5 |
| activation_fork | 该参数当前值是在哪个 hardfork 设置或最近一次调整的 | item-1, item-2, item-3, item-4, item-5 |
| source_evidence | 主要证据：仓库路径与 commit、链上 RPC 查询、官方 spec 链接 | all |
| theoretical_tps_impact | 该参数对理论 TPS 的边际影响（公式或定量估算） | item-1, item-2, item-3, item-6 |
| safety_implication | 调整该参数的安全 / DoS / state growth / re-org 影响 | item-1, item-2, item-3, item-4, item-5, item-8 |
| recommendation | 针对 Mantle 的具体推荐（保持 / 调整 / 升级到 Prague 等价值） | item-1, item-2, item-3, item-4, item-5, item-7 |
| implementation_path | 落地方式：SystemConfig 链上调用、chain config commit、hardfork 升级 | item-7 |
| confidence | 高 / 中 / 低：基于实测 / spec 推算 / 类比 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Base vs Mantle 协议层关键参数对比矩阵 | mermaid | item-1, item-2, item-3, item-4, item-5 |
| diag-2 | flow | 典型 L2 tx 在 Base / Mantle 当前参数下的 gas 占比与 TPS 推导链 | mermaid | item-6 |
| diag-3 | hierarchy | Quick-wins 优先级象限（收益高/低 × 风险高/低） | mermaid | item-7 |
| diag-4 | timeline | Base 与 Mantle gas 相关 hardfork 时序对照（含 Pectra/Azul/Holocene 锚点） | mermaid | item-1, item-3, item-5 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Ethereum EIP（1559, 7825, 7883, 7951, 7823, 3860, 4844）官方规范 | 4 |
| src-2 | code_analysis | base/base 仓库（chain spec / SystemConfig）与 mantlenetworkio/mantle-v2 / op-geth 仓库 chain config | 3 |
| src-3 | on_chain_data | Base mainnet 与 Mantle mainnet 区块 header 实测 gasLimit / gasUsed / baseFeePerGas | 2 |
| src-4 | official_docs | OP Stack specs（system config、Holocene EIP-1559 dynamic params） | 2 |
| src-5 | expert_commentary | Pectra/Prague & Base Azul 升级公开分析（Base blog、Mantle blog、协议研究文章） | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
