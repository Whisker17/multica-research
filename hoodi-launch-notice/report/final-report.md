---
project_slug: hoodi-launch-notice
topic_slug: final-report
github_repo: Whisker17/multica-research
status: final
branch: research/hoodi-launch-notice/final-report

source_sections:
  - issue_id: de2f6b68-b0e4-424a-a50b-28db4c320a09
    topic_slug: reference-notice-analysis
    final_path: hoodi-launch-notice/research-sections/reference-notice-analysis/final.md
    main_merge_commit: "7338f6c"
  - issue_id: 56f09aef-bbee-4e60-baf7-b739a9bf28b8
    topic_slug: reth-adoption-trends
    final_path: hoodi-launch-notice/research-sections/reth-adoption-trends/final.md
    main_merge_commit: "4d1765e"

synthesized_by: "agent:technical-writer-agent (f69d6430-0f11-47b4-b96c-c09b167f5000)"
synthesized_at: "2026-05-27T07:30:00Z"
---

# Hoodi 测试网上线通告：最终报告

## Executive Summary

本报告基于两项已完成的调研——**Mantle Arsia 通告格式与内容结构分析**（[de2f6b68](hoodi-launch-notice/research-sections/reference-notice-analysis/final.md)）和 **reth 技术优势及行业采用趋势调研**（[56f09aef](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md)）——综合输出 Hoodi 测试网上线通告的写作框架、技术叙事素材和质量标准。

核心结论：

1. **通告结构已就绪**：Arsia/Limb 通告验证了 Mantle 的 5 段式公告模板（Overview → Purpose → What's New → Impact → Summary）；结合 Optimism 和 Base 的行业最佳实践（激活时间表、版本表、逐步操作指南），本报告产出一套 9 章节的 Hoodi 通告模板和 12 项发布前检查清单，可直接用于起草。

2. **reth 技术叙事有据可依**：reth 的模块化 Rust crate 架构、MDBX 存储、staged sync、REVM 和 ExEx 扩展点有充分文档证据；Base 的公开 archive benchmark 提供了存储和 provisioning 优势的基准级数据；但运营级 TPS / 空块声明仅为公告级别（reported / not benchmark-grade），不应直接移植到 Hoodi。

3. **行业采用趋势支撑"顺势而为"叙事**：Optimism 正式弃用 op-geth（EOL 2026-05-31）、Base Azul 选择 base-reth-node 作为唯一支持客户端、BNB Chain 将 Reth-BSC 纳入官方客户端矩阵（Erigon 日落）、Polygon CDK / X Layer 维护 reth fork——这些信号足以支撑"reth 正从单一客户端扩展为多链 EVM 执行层基座"的表述。

4. **并行执行必须降级表述**：上游 reth 有 staged/concurrent pipeline 和 feature-gated EIP-7928/BAL 工作，但通用生产级并行执行不是当前默认能力。Hoodi 应将此定位为"面向未来的扩展潜力"。

5. **关键事实缺口待项目方填充**：Chain ID、RPC endpoint、Explorer、Faucet、Bridge、已知限制、Support channel 等操作级信息需 Mantle/Hoodi 项目方提供，通告不应以占位符发布。

---

## 1. 背景与定位

### 1.1 Hoodi 测试网起源

Hoodi 是 Ethereum Foundation 为解决 Holesky 测试网在 Pectra 激活后 validator exit queue 过长问题（约需一年才能完全清退）而推出的新测试网。其定位为 Validators 和 Staking providers 的测试环境（预期 EOL 2028-09-30），与 Sepolia（应用和工具开发者，EOL 2026-09-30）形成互补。Pectra 激活时间为 Epoch 2048（2025-03-26 14:37:12 UTC）。

*来源：[reference-notice-analysis](hoodi-launch-notice/research-sections/reference-notice-analysis/final.md) §7.1, EF Blog*

### 1.2 Mantle 在 Hoodi 上的技术转型

Mantle 的 Hoodi 测试网上线标志着 sequencer 执行层从 op-geth 路径切换到 Mantle 适配的 reth，基于 Arsia 升级版本。这一转型对齐了 OP Stack 上游正在发生的客户端迁移趋势——Optimism 已宣布 op-geth 支持截止日期为 2026-05-31，此后 op-geth 将不支持 Glamsterdam hardfork。

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.3, OP 弃用通知 [S11]*

### 1.3 通告场景定位

通过对 Arsia 通告的环境验证（置信度：高），确认 Arsia 为 Sepolia 测试网升级通告。因此，Hoodi 通告的对比框架应为 **"测试网升级通告 vs 测试网上线通告"**，而非主网场景。两者的核心差异：

| 维度 | 测试网升级通告（如 Arsia） | 测试网上线通告（Hoodi） |
|------|--------------------------|----------------------|
| 核心动词 | upgrade / update / migrate | connect / deploy / test / explore / report |
| 行动强度 | 强制升级（不升级=断联） | 邀请参与（不参与=错过测试机会） |
| 时间压力 | fork activation deadline | 上线日期 + 开放式里程碑 |
| 链接密度 | 低（2 处文内链接） | 高（RPC、explorer、faucet、bridge、docs、status page） |
| 受众优先级 | node operators > developers > users | developers > node operators > ecosystem > testers |

*来源：[reference-notice-analysis](hoodi-launch-notice/research-sections/reference-notice-analysis/final.md) §8, §9*

---

## 2. 通告结构设计

### 2.1 Mantle 公告模板分析

Arsia 和 Limb 通告共享稳定的 5 段式结构：Overview → Purpose → What's New → Impact Assessment → Summary。DA-to-Blobs 是较早期变体，结构更扁平但核心要素完整。

Arsia 通告的信息排序遵循 **"价值先行 → 技术展开 → 影响评估 → 记忆压缩"** 逻辑：标题 + Overview（~100 词）建立第一印象；Purpose（~200 词）用 numbered drivers 解释动机；What's New（~800 词）逐项展开技术变化；Impact Assessment（~150 词）按受众分组；Summary（~80 词）压缩为 4 个记忆点。

**关键缺口**：Arsia 通告缺少激活 timestamp、版本号表和 changelog 链接——这是与 Optimism / Base 通告的主要差距。

*来源：[reference-notice-analysis](hoodi-launch-notice/research-sections/reference-notice-analysis/final.md) §2, §5*

### 2.2 行业标杆对照

| 维度 | Mantle Arsia | Optimism Upgrade 14 / Holocene | Base Azul (Guide + Blog) |
|------|-------------|-------------------------------|-------------------------|
| 激活时间 | 无 timestamp | 精确 UTC timestamp + 日期 | 激活日期（存在跨页面版本差异） |
| 软件版本 | 未提供 | op-node/op-geth release 版本号 | 版本表（base-reth-node v0.9.0+） |
| 操作步骤 | "See changelog" | 逐步配置说明 | 逐步 Docker 命令 |
| 风险/兼容性 | "required upgrade"一句 | Fault proof 升级要求 | "op-geth/nethermind no longer supported" |
| Roadmap | 无 | 无 | 后续 2 个升级计划 |

**Hoodi 可借鉴项**：激活时间表、必需软件版本表、逐步迁移指南、tl;dr 开头、Feature taxonomy 表（Change / What / Why）、后续里程碑。

**不可照搬项**：多链升级协调格式（Hoodi 是单链测试网）、Fault proof 版本绑定、客户端 EOL 声明（测试网首发不适用）。

*来源：[reference-notice-analysis](hoodi-launch-notice/research-sections/reference-notice-analysis/final.md) §6*

### 2.3 推荐模板（9 章节）

| 章节 | 内容 | 来源 | 建议篇幅 |
|------|------|------|---------|
| 1. 标题 | `[Hoodi 测试网上线]: [核心价值副标题]` | Arsia 标题格式 | — |
| 2. TL;DR / Overview | 上线状态、测试目标、谁应关注、核心入口 | Arsia Overview + Base tl;dr | 80-120 词 |
| 3. Why Hoodi / 测试目标 | 上线目的、验证能力、与 Sepolia/Holesky 关系 | Arsia Purpose drivers | 150-200 词 |
| 4. Network Information | Chain ID、RPC、Explorer、Faucet、Bridge、Docs、Status Page（表格） | Base Guide + Hoodi 新增 | 表格 |
| 5. What's Available | 功能范围、已部署服务、兼容性、限制 | Arsia What's New（改写） | 200-300 词 |
| 6. Who Should Do What | 按受众分组的行动路径（开发者/运营者/生态/测试用户） | Arsia Impact + Base 逐步风格 | 表格 + 简述 |
| 7. Known Limitations | 非生产声明、可能重置、Faucet 限制、SLA 边界 | Hoodi 新增 | 100-150 词 |
| 8. Feedback & Support | Issue tracker、Discord、Forum、反馈表单 | Hoodi 新增 | 50-80 词 |
| 9. Next Steps | 后续里程碑、更新频道、迁移计划 | Base Roadmap | 80-120 词 |

*来源：[reference-notice-analysis](hoodi-launch-notice/research-sections/reference-notice-analysis/final.md) §10.1*

### 2.4 发布前检查清单（12 项）

| # | 检查项 | 分类 |
|---|-------|------|
| 1 | 标题直接陈述测试网上线事件，不使用主网升级口径 | 风格 |
| 2 | Overview/TL;DR 在 120 词内回答"是什么、为什么、谁应关注" | 结构 |
| 3 | Network Information 表格所有参数已填入可访问的真实值 | 事实 |
| 4 | 每类受众有明确的行动路径（做什么→怎么做→去哪里） | 行动 |
| 5 | Known Limitations 涵盖非生产风险、重置可能、faucet 限制、已知 issues | 风险 |
| 6 | 所有技术术语要么在正文中解释，要么链接到文档 | 可读性 |
| 7 | 所有链接（RPC、explorer、faucet、docs、support）已验证可访问 | 链接 |
| 8 | 不包含未经验证的主网承诺或确定性收益表述 | 事实 |
| 9 | 反馈渠道（issue tracker、Discord、forum）至少有一个 | 支持 |
| 10 | Summary 在 5 个 bullet points 内压缩全文核心信息 | 结构 |
| 11 | 涉及 Arsia 对比的表述使用"Arsia Upgrade on Sepolia"（经环境验证） | 环境 |
| 12 | 风格与 Mantle 文档站已有通告（Arsia、Limb）保持一致 | 品牌 |

*来源：[reference-notice-analysis](hoodi-launch-notice/research-sections/reference-notice-analysis/final.md) §10.2*

---

## 3. reth 技术基座

### 3.1 核心架构

Paradigm 将 reth 定义为 Rust 编写、Apache/MIT 双许可、生产就绪、可扩展且组件化的 Ethereum execution client。其架构由以下核心机制组成：

| 机制 | 含义 | Hoodi 相关性 |
|------|------|-------------|
| Rust 实现 | 内存安全语言默认、强类型系统、异步生态 | 工程信心；不应声称"消除所有 bug" |
| 模块化 crate 架构 | 执行、存储、网络、RPC、共识、txpool 等暴露为可复用 crate | 使链特定 fork / OP Stack 变体更易隔离 |
| Staged sync pipeline | Sync 分解为可重启的阶段，有助于运维恢复和性能分析 | 可安全描述为快速 / 可观测的同步架构 |
| MDBX 数据库 | Reth 使用 MDBX 和 flat/provider 层进行状态访问 | 配合 benchmark 可支撑存储优势声明 |
| REVM 集成 | Rust EVM，跨 reth / op-reth / 多个 fork 使用 | 支撑"高性能 Rust EVM 基座"表述 |
| ExEx / node builder | 执行扩展和节点构建器模式，用于自定义 indexer / rollup 节点 | 强匹配 Hoodi 可扩展性叙事 |

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.1, Reth docs [S1][S2][S3]*

### 3.2 性能数据与证据边界

公开可引用的最强量化数据集来自 Base 的 Reth vs Geth archive 基准测试（2024-12-18），后续方法论文章（2025-11-13）披露了硬件规格（AWS i7ie.48xlarge, GCP z3-highmem-88-highlssd）和开源测试工具：

| 指标 | 数值 | 证据等级 | Hoodi 可用性 |
|------|------|---------|-------------|
| Archive 节点 provisioning | ~15h (Geth) → ~3h (Reth) | Benchmark-grade | 强：存储/运维证据 |
| Archive 磁盘占用 | 16.61 TB (Geth) → 2.74 TB (Reth) | Benchmark-grade | 强：存储证据 |
| 每周磁盘增长 | ~560 GB → ~50 GB | Benchmark-grade | 强：存储运维证据 |
| Block-building p99 | 2319 ms → 698 ms | Benchmark-grade | 中：架构证据 |
| Mgas/s 执行上限 | Geth ~40 → Reth ~100 | Benchmark-grade（Base 标注为近似模拟） | 中：架构证据，非 Hoodi 保证 |
| Base 突发吞吐量 | 多次 5,000 TPS bursts | Reported / not benchmark-grade | **不应用于强表述** |
| Base 空块减少 | ~200/day → ~2/day | Reported / unvalidated | **不应用于强表述** |

**关键限制**：Base benchmark 是 Base 主网 archive 工作负载，不是 Hoodi sequencer 工作负载。所有数字必须标注其特定工作负载上下文。Azul 运营声明（TPS、空块）属于公告级别，缺乏方法论、原始数据和独立验证。

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.2, Base [S5][S5b][S15]*

### 3.3 并行执行：现状与边界

上游 reth 当前具备 pipeline-level 并发和相邻并行能力，但不支持"通用交易级并行执行已生产可用"的表述：

- **Parallel prewarming**（reth#13713，已关闭）：在一个区块内并行执行每笔交易以填充状态缓存。这是缓存优化，不是完整的并行交易执行。
- **EIP-7928 / BAL tracking**（reth#18253）：Block-Level Access Lists 的主跟踪 issue，覆盖并行/批量 BAL 执行路径。Feature-gated，默认关闭。
- **Internal parallel state root**（reth#17652）：提议在单个 trie 节点内进行 16 路并行哈希。

**Hoodi 推荐表述**：使用"并行化与高吞吐优化空间"或"面向未来的并行执行演进潜力"，不使用"reth 原生已全面并行执行"。

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.1 parallel-execution caveat, [S9][S10]*

---

## 4. 行业采用趋势

### 4.1 采用全景

reth-family 客户端正在从单一 Ethereum L1 客户端扩展为多链 EVM 执行层基座。以下证据链支撑这一判断：

| 项目 | 采用深度 | 状态 | 关键证据 |
|------|---------|------|---------|
| **Optimism / OP Stack** | op-reth crate（一级 OP 执行客户端） | op-geth 弃用中（EOL 2026-05-31） | 弃用通知 [S11]、OP docs [S12]、monorepo [S13] |
| **Base** | reth-based 自定义 stack（base-reth-node） | Azul 主网 2026-05-13（唯一支持 EL） | "Scaling Base With Reth" [S5]、Azul specs [S16] |
| **BNB Chain** | Reth-BSC 扩展（NodeBuilder API） | 官方支持客户端；Erigon-BSC 日落 2025-12-31 | 客户端更新 [S20]、reth-bsc GitHub [S22] |
| **Polygon CDK** | 栈集成（op-reth 作为执行层选项） | 文档级集成 | CDK docs [S24] |
| **OKX X Layer** | xlayer-reth fork | 公开 GitHub 仓库 | okx/xlayer-reth [S26] |
| **Flashblocks / rollup-boost** | 基础设施集成 | Base / OP 生态 | Flashblocks blog [S18a]、rollup-boost docs [S28] |

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.3–§2.6*

### 4.2 Optimism：op-geth → op-reth 迁移

Optimism 的官方弃用通知明确指出：op-geth 和 op-program 的支持将持续到 2026 年 5 月 31 日，此后不支持 Glamsterdam hardfork；激活时仍在运行 op-geth 的链将无法跟随规范链。迁移路径是 op-reth 和 cannon-kona。

Op-reth 不只是"带 flag 的 reth"——它是在 Optimism monorepo 中以 Rust crate 形式实现的 OP Stack 执行客户端，pin 到上游 reth / alloy / revm 依赖。OP 特定行为存在于 chain spec、EVM、payload、RPC、txpool、proof / storage 和 rollup 特定模块中。

**Hoodi 叙事角度**：Hoodi 的 reth 切换与 OP Stack 上游迁移方向一致，不是孤立决策。

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.3, [S11][S12][S13]*

### 4.3 Base：reth-based 单客户端路径

Base Azul 是公开证据中最强的 reth-based L2 案例。Azul 规范要求唯一使用 `base-reth-node` 和 `base-consensus`，运行 op-node / op-geth 或其他客户端的 operator 必须在激活前更新。

Base 的架构不是通用 OP Stack op-reth——它使用 Base 维护的 Rust 栈，直接 pin 到上游 `paradigmxyz/reth` 标签，并添加了大量 Base overlay：cached execution、precompile cache、parallel state-root、Flashblocks sender recovery 等。

**安全表述**："Base 的 reth-based stack" 或 "Base 的 base-reth-node"，不是"Base 运行上游原版 reth"。

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.4, [S5][S15][S16][S17]*

### 4.4 BNB Chain：Reth-BSC 与双客户端策略

BNB Chain 于 2025-11-25 正式将 Reth-BSC 纳入支持客户端列表，同时宣布 Erigon-BSC 日落（2025-12-31），确认双客户端策略（Geth + Reth）。Reth-BSC 是通过 reth 的 NodeBuilder API 构建的 BSC 兼容扩展，不是 OP Stack op-reth 衍生。

BNB Chain 最强的并行化证据是 **Parallel Sparse Trie**——这是 BSC 特定的存储/trie 优化，不是通用上游 reth 交易级并行执行。Hoodi 不应声称继承 BSC 的并行 trie 或验证器集假设。

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.5, [S20][S21][S22]*

### 4.5 趋势判断

证据支持一个 **强趋势**：EVM rollup 和高吞吐链的执行客户端正在从 geth/op-geth 主导路径向混合 Rust/reth 客户端家族迁移。但不支持更强的声称"reth 是唯一行业标准"或"所有主要 L2 已完成切换"。

**推荐表述**："reth-family 客户端正在被越来越多的 EVM 生态采用"（increasingly adopted），而非"已成为默认选择"（default）。

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.6–§2.7*

---

## 5. 通告写作指引

### 5.1 reth 表述安全矩阵

| 声明 | 强度 | 推荐表述 | 证据锚点 | 必要注意事项 |
|------|------|---------|---------|-------------|
| reth 提供 Rust-based 高性能执行基座 | 强 | "Hoodi 构建在 reth-based Rust 执行基座上，面向性能、模块化和长期可维护性设计。" | Reth docs [S1][S2], Base/OP adoption | 不承诺具体 TPS |
| reth 采用扩展至 OP Stack 和高吞吐 EVM 生态 | 强 | "Reth-family 客户端正在被 OP Stack、Base、BNB Chain 和 CDK 生态越来越多地采用。" | [S11][S12][S5][S15][S20][S22][S24][S26] | 用"increasingly"而非"universal" |
| Hoodi 顺应模块化 Rust 执行客户端趋势 | 强 | "这使 Hoodi 与更广泛的模块化 Rust 执行客户端迁移趋势保持一致。" | 多项目采用证据 | 避免"唯一标准" |
| reth 实质性改善吞吐 / 延迟 | 中 | "公开 reth-based 基准测试显示，在特定工作负载下存储占用和 block-building 延迟有明显改善。" | Base archive benchmark [S5] | 必须包含 benchmark 上下文 |
| reth 已具备生产级并行执行 | 弱 | "Reth 的架构为并行化和高吞吐执行工作留下了空间。" | BAL/EIP-7928 [S9], prewarming [S9], BSC trie [S21] | 不称为通用生产级 tx-level 并行执行 |
| Rust 内存安全使 Hoodi 更安全 | 中 | "Rust 降低了内存安全风险类别，改善了复杂执行客户端的工程纪律。" | Rust/reth docs [S1] | 不消除共识或逻辑 bug |

### 5.2 推荐通告文案

**中文主表述**：

> Hoodi 采用基于 reth 的 Rust 执行层基座，顺应 EVM 生态从传统 geth / op-geth 路径向模块化、高性能 Rust 客户端演进的趋势。reth 的生产级架构、快速同步与存储设计，以及 Optimism、Base、BNB Chain、Polygon CDK 等生态的采用信号，为 Hoodi 后续性能优化与长期维护提供了更稳固的基础。

**中文补充文案**：

1. `Hoodi 采用基于 reth 的 Rust 执行层基座，面向高性能、模块化和长期可维护性构建。`
2. `reth 已从 Ethereum L1 客户端扩展为多个 EVM / Rollup 生态的执行层基础设施，Optimism op-reth、Base 的 base-reth-node、BNB Chain 的 Reth-BSC 以及 CDK 生态都体现了这一迁移趋势。`
3. `公开基准测试显示，reth-based stack 在 archive 存储占用、节点同步/provisioning、block-building latency 上具备明确优化空间（数据来自 Base 2024-12-18 archive benchmark，测试环境 AWS i7ie.48xlarge / GCP z3-highmem-88-highlssd）；Hoodi 会在自身工作负载下持续验证和公开性能进展。`
4. `我们不会把外部项目的 TPS 或延迟数字直接搬到 Hoodi，而是把 reth 作为后续性能迭代、模块化扩展和客户端演进的技术底座。`

**英文可选**：

- `Hoodi is aligned with the industry's shift toward modular Rust execution clients.`
- `Reth gives Hoodi a production-ready, extensible execution foundation rather than a one-off fork of the legacy geth/op-geth path.`
- `Public reth-based benchmarks show strong storage and latency improvements under disclosed test conditions, while Hoodi will validate performance claims against its own workloads.`

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.8*

### 5.3 禁用 / 高风险表述

以下表述在通告中**不得使用**：

- `reth gives Hoodi 5,000 TPS` — Base 报告的运营声明，非基准级数据，不可转移
- `reth reduced empty blocks by 99%` — 报告级 / 未验证，Base 特定
- `reth is fully parallel by default` — 不支持作为通用基线；BAL 是 feature-gated
- `all major L2s have migrated to reth` — 过于宽泛
- `Rust makes the execution layer secure by default` — 过度声称语言安全
- `Base Azul proves Hoodi has Base Stack performance` — 错误等价

*来源：[reth-adoption-trends](hoodi-launch-notice/research-sections/reth-adoption-trends/final.md) §2.8*

### 5.4 语气与风格指引

| 维度 | 建议 |
|------|------|
| 保留 | 技术说明的清晰度、分层展开方式、受众分组格式 |
| 弱化 | 价值宣传口径（测试网不应使用主网确定性收益表述） |
| 强化 | 行动指引（测试网需更明确的参与步骤）、风险透明（非生产、可能重置、已知限制） |
| 新增 | 参与邀请（测试目标、希望验证什么）、反馈渠道 |
| 基调 | 清晰、测试导向、邀请参与、透明列出限制 |

*来源：[reference-notice-analysis](hoodi-launch-notice/research-sections/reference-notice-analysis/final.md) §3.4*

---

## Cross-Cutting Analysis

### Consensus

两项调研在以下方面达成一致：

1. **Mantle 公告模板可复用**：Arsia/Limb 的 5 段式骨架经验证为稳定模板，可直接用于 Hoodi——但需从"升级导向"转为"参与导向"。
2. **reth 是经验证的技术选择**：从官方文档、代码仓、公开 benchmark 和多链采用信号来看，reth 作为 Hoodi 执行层基座有充分的技术和生态依据。
3. **测试网通告需更强的操作明确性**：两项调研均指出，Arsia 在激活时间、版本号、操作步骤方面的信息缺失需要在 Hoodi 通告中弥补。行业标杆（Optimism、Base）提供了更高的操作明确性标准。
4. **性能声明需严格限定**：调研一致认为外部 benchmark 数据不可直接转移到 Hoodi，通告应避免无上下文的 TPS / 延迟承诺。

### Conflicts

两项调研之间 **不存在实质性冲突**。唯一的注意点：

- **Hoodi 通告模板（调研 1）将 reth 相关技术内容放在 "What's Available" 章节内**，而 **reth 调研（调研 2）提供的素材量远超单一章节容量**。[TW inference] 最终通告应在 "What's Available" 中精炼 reth 核心优势（3-4 个要点），将详细的行业趋势和 benchmark 数据放在附录或独立 blog post 中，避免通告过长导致读者流失。

### Open Questions

以下问题影响通告的最终质量，需项目方确认后才能发布：

| 编号 | 问题 | 影响 | 来源 |
|------|------|------|------|
| OQ-1 | Hoodi Chain ID | Network Information 表格 | 调研 1 §7.2 |
| OQ-2 | RPC endpoint | Network Information 表格 | 调研 1 §7.2 |
| OQ-3 | Block Explorer URL | Network Information 表格 | 调研 1 §7.2 |
| OQ-4 | Faucet URL | Network Information 表格 | 调研 1 §7.2 |
| OQ-5 | Bridge URL | Network Information 表格 | 调研 1 §7.2 |
| OQ-6 | Status page / Docs 入口 | Network Information 表格 | 调研 1 §7.2 |
| OQ-7 | 已知限制 / Known Issues | Known Limitations 章节 | 调研 1 §7.2 |
| OQ-8 | Support channel (Discord/Telegram) | Feedback & Support 章节 | 调研 1 §7.2 |
| OQ-9 | Mantle 在 Hoodi 上的具体网络参数 | Network Information 表格 | 调研 1 §7.2 |
| OQ-10 | Hoodi-specific 性能基准 | 性能声明需自有 benchmark 支撑 | 调研 2 §5 Gap-1 |
| OQ-11 | op-geth 弃用状态更新（EOL 2026-05-31 临近） | 采用趋势叙事的时效性 | 调研 2 §5 Gap-2 |

---

## Appendix

### A. Input Research Sections

| Order | Topic Slug | Issue ID | Final Path | Main Merge Commit | Adversarial Approval | Round Count |
|-------|-----------|----------|------------|-------------------|---------------------|-------------|
| 1 | reference-notice-analysis | de2f6b68-b0e4-424a-a50b-28db4c320a09 | hoodi-launch-notice/research-sections/reference-notice-analysis/final.md | [7338f6c](https://github.com/Whisker17/multica-research/commit/7338f6c961b244a9368aab631d47a9e51d61a623) | comment 4673dccb (approve, severity: minor) | outline=2, deep=1 |
| 2 | reth-adoption-trends | 56f09aef-bbee-4e60-baf7-b739a9bf28b8 | hoodi-launch-notice/research-sections/reth-adoption-trends/final.md | [4d1765e](https://github.com/Whisker17/multica-research/commit/4d1765e) | comment d8c7ec61 (approve) | outline=2, deep=2 |

### B. Sections Index Reference

```markdown
# Research Sections Index — hoodi-launch-notice

| order | topic_slug | multica_issue_id | final_path | dependencies | status |
|-------|------------|------------------|------------|--------------|--------|
| 1 | reference-notice-analysis | de2f6b68-b0e4-424a-a50b-28db4c320a09 | hoodi-launch-notice/research-sections/reference-notice-analysis/final.md | - | done |
| 2 | reth-adoption-trends | 56f09aef-bbee-4e60-baf7-b739a9bf28b8 | hoodi-launch-notice/research-sections/reth-adoption-trends/final.md | - | done |
```

### C. Diagram Assets

以下 Mermaid 图表来自源调研，可在通告或附属文档中复用：

**From reference-notice-analysis:**
- diag-1: 通告结构总览图（绿色=Arsia 已有；橙色=Hoodi 新增）
- diag-2: Arsia vs Hoodi 内容映射图
- diag-3: 读者行动路径图（按受众分组的测试网参与流程）

**From reth-adoption-trends:**
- diag-1: Industry reth adoption timeline
- diag-2: reth vs geth/op-geth technical comparison
- diag-3: reth-based Rollup/EVM execution ecosystem map
- diag-4: Hoodi wording decision matrix (quadrant chart)

所有图表均为 Mermaid 格式，可在支持 Mermaid 的文档系统中直接渲染。源文件路径见附录 A。

### D. Methodology Notes

**调研方法**：

- **调研 1（reference-notice-analysis）**：通过 GitBook .md alternate 和 curl HTML 提取获取 Mantle（Arsia、DA-to-Blobs、Limb）、Optimism（Upgrade 14 .mdx 源、Holocene .mdx 源）和 Base（Azul operator guide、Azul blog）的通告原文，逐节拆解和横向对比。Hoodi 上下文来自 EF 官方 blog。覆盖 7 类源，所有核心来源置信度为 High。
- **调研 2（reth-adoption-trends）**：通过 GitHub 仓库、官方文档、官方 blog、协议规范和内部已有研究，调查 reth 核心技术机制和多链采用案例。Round 2 修订了所有源引用的精确 URL 和日期、限定了性能指标的方法论上下文、降级了 Base 空块数据的证据等级。覆盖 30+ 主要源，8 类源需求全部满足。

**两项调研的局限性**：

1. 调研团队无法直接访问 Mantle/Hoodi 项目方的内部参数和基础设施信息（Chain ID、RPC 等），这些信息标记为"缺口"。
2. 所有性能数据来自外部项目的公开 benchmark 或运营声明，不代表 Hoodi 自身工作负载的性能。
3. OP Stack 迁移状态具有时效性——op-geth EOL 2026-05-31 临近，链级别迁移进度应在发布前重新验证。
4. Living docs（Optimism docs、Polygon CDK docs、Base specs、reth docs）的内容可能在调研完成后变更，发布前应重新验证关键 URL。
