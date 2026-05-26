---
topic: "Reth 与 Op-Reth 在 Ethereum Hardfork 中的迭代依赖关系分析"
project_slug: mantle-base-codebase-evaluation
topic_slug: reth-op-reth-hardfork-dependency
github_repo: Whisker17/multica-research
round: 3
status: final

artifact_paths:
  outline: "mantle-base-codebase-evaluation/outlines/reth-op-reth-hardfork-dependency.md"
  draft: "mantle-base-codebase-evaluation/research-sections/reth-op-reth-hardfork-dependency/drafts/round-3.md"
  final: "mantle-base-codebase-evaluation/research-sections/reth-op-reth-hardfork-dependency/final.md"
  index: "mantle-base-codebase-evaluation/research-sections/_index.md"

draft_metadata:
  created_by: deep-research-agent
  created_at: "2026-05-26T10:00:00Z"
  outline_commit: c3519db
  prior_draft_commit: 89a08af
  items_covered: [item-1, item-2, item-3, item-4, item-5, item-6, item-7]
  fields_investigated: [dependency_mechanism, modification_surface, upstream_sync_workflow, version_timeline, lag_quantification, op_activation_milestones, el_vs_l2_readiness_gap, cascading_rebase_cost, upgrade_cost_model, switching_benefit]
  diagrams_produced: [diag-1, diag-2, diag-3]
  source_requirements_coverage: {src-1: met, src-2: met, src-3: met, src-4: met, src-5: met, src-6: met}
  adversarial_findings_addressed:
    - finding: "Fusaka/Jovian timeline off by one year"
      severity: major
      resolution: "Corrected all dates to 2025; reframed as completed historical events (round-2, preserved)"
    - finding: "Hardfork lag model conflates maintenance drift with hardfork readiness"
      severity: major
      resolution: "Separated three distinct metrics; corrected 5-month lag claim; added actual Mantle activation dates (round-2, preserved)"
    - finding: "Base switching benefit grounded in wrong evidence; Base Azul must be incorporated"
      severity: major
      resolution: "Split Base activation timeline into Track A (OP/Superchain inherited: Isthmus/Jovian) and Track B (Base-native: Azul). Added three-timeline comparison table. Retired 1-3 day and 14x-37x improvement claims. Base-native Azul lag is ~176 days after Fusaka, vs Mantle Limb at 42 days."
---

# Reth 与 Op-Reth 在 Ethereum Hardfork 中的迭代依赖关系分析

## Executive Summary

本研究量化分析了三种 upstream reth 依赖模型在 Ethereum hardfork 跟进维度的表现差异。以 Pectra（2025-05-07 L1 激活）和 Fusaka（2025-12-03 L1 激活）两个已完成的 hardfork 为核心案例，我们追踪了从 `paradigmxyz/reth` EL 代码就绪到各 L2 网络实际激活的端到端延迟链路。

**关键方法论修正（round-2 → round-3）**：

Round-2 将"hardfork 延迟"拆分为三个独立度量指标（hardfork 兼容客户端 lag / 维护漂移 / L2 激活 lag），纠正了 round-1 中将版本维护漂移等同于 hardfork 跟进延迟的错误。**Round-3 进一步修正了 Base 切换收益评估中的证据错误**：round-2 使用 Base/Isthmus 和 Base/Jovian 的 1-2 天激活数据来论证切换到 Base codebase 可获得 14x-37x 的 hardfork 跟进改善，但 Isthmus 和 Jovian 是 **OP/Superchain 共享激活**——所有 OP Stack 链（包括 OP Mainnet、Base、Zora 等）同时激活，它们不能作为 Base **自有 codebase** 带来更快 hardfork 跟进的证据。

Round-3 引入 **Base Azul** 作为 Base 首个独立于 OP Stack 的 Base-native 升级。Azul 是 Base 脱离 OP Stack 客户端后的首次自主 hardfork，仅 `base-reth-node` 和 `base-consensus` 支持，采纳了 Ethereum Osaka 执行层 EIP。Azul Sepolia 已于 2026-04-20 激活，mainnet 代码时间戳设为 2026-05-28（距 Fusaka L1 激活 ~176 天）。

| 度量指标 | 定义 | 对 Mantle 的含义 |
|---------|------|----------------|
| **Hardfork 兼容客户端版本 lag** | 从 L1 hardfork 激活到首个支持该 hardfork 的 reth/op-reth 版本发布的时间 | Mantle 当前 pin 的 reth v1.9.3 **已包含 Pectra 和 Fusaka 支持**——hardfork 客户端兼容性 lag 为零 |
| **上游最新版本维护漂移** | Mantle 当前 pin 版本与 upstream reth 最新版本的差距 | v1.9.3（2025-11-18）vs v2.2.0（2026-04-30）= **约 5 个月 + 1 个大版本**，反映维护债务而非 hardfork 风险 |
| **L2 协议激活 lag** | 从 L1 hardfork 激活到 L2 网络实际完成等价升级的时间 | Skadi（Pectra 等价）: **112 天**；Limb（Fusaka 等价）: **42 天**——趋势显著改善 |

**修正后的核心发现**：

1. **OP monorepo git-rev pin 模型**的 reth → op-reth EL 代码跟进延迟中位数仅 **2 天**（6 个样本，范围 0-11 天），表明该模型在 hardfork 跟进速度上非常高效。
2. **Base tag-pin 模型**直接 pin upstream reth git tag，升级仅需 bump tag + 适配 trait 变更，涉及 1 个仓库、0 个 rebase 操作，是三种模型中维护成本最低的方案。
3. **Mantle full fork 模型**当前 fork 基于 reth v1.9.3（2025-11-18）。该版本已包含 Fusaka 主网支持（v1.9.0 引入），因此 Mantle 的 reth pin **在 hardfork 兼容性层面并不落后**。但 upstream reth 已演进至 v2.2.0（2026-04-30），维护漂移达 5 个月和一个完整大版本。
4. **Mantle 的实际 hardfork 激活 lag 正在显著缩短**：Skadi（Pectra 等价）在 Pectra L1 激活后 112 天上线，Limb（Fusaka 等价）在 Fusaka L1 激活后 42 天上线。
5. **OP/Superchain 共享激活与 Base-native 激活是两个不同的轨道**：
   - **Track A — OP/Superchain 共享激活**（Isthmus/Jovian）：所有 OP Stack 链同时激活，1-2 天内完成（甚至先于 L1）。这不是 Base codebase 的独特优势，而是 OP Stack 生态的集体能力。
   - **Track B — Base-native 独立激活**（Azul）：Base 首个独立升级，采纳 Osaka EL EIP，Sepolia 2026-04-20、mainnet 代码时间戳 2026-05-28，距 Fusaka L1 约 **176 天**。这反映了 Base 自有 codebase 路径的实际 hardfork 跟进速度。
6. **切换到 Base codebase 的 hardfork 跟进收益需要重新评估**：round-2 估计的 14x-37x 改善幅度基于 OP/Superchain 共享激活数据，不可归因于 Base 自有 codebase。如果以 Base-native Azul（~176 天）与 Mantle Limb（42 天）对比，Mantle 在 Fusaka 等价的 Base-native 激活上反而**更快**。切换到 Base codebase 的核心收益在于**维护成本降低**（O(1) vs O(N)）和**依赖链简化**，而非 hardfork 激活速度的直接提升。

## 1. 三种 Upstream Reth 依赖模型分类与技术分析

### 1.1 OP Monorepo Git-Rev Pin 模型

**依赖机制**：Op-reth 并非 `paradigmxyz/reth` 的 fork，而是位于 Optimism monorepo（`ethereum-optimism/optimism`）内 `rust/op-reth/` 目录下的独立 crate 集合。这些 crate 通过 workspace 级别的 `rust/Cargo.toml` 以 git-rev 方式 pin upstream reth：

```toml
reth = { git = "https://github.com/paradigmxyz/reth", rev = "81c026181e96ef33a823f3ef4d2a28940e9fa4fe" }
```

当前 workspace 包含 **15 个 op-reth crate**（chainspec、cli、consensus、evm、exex、flashblocks、hardforks、node、payload、primitives、reth、rpc、storage、trie、txpool），以及 bin 目录和 examples。此外，workspace 还包含 kona（证明系统）、op-alloy、alloy-op-evm、alloy-op-hardforks、op-revm 等相关 crate。

**Rust workspace 统一时间线**：2026-02-10，commit `48a7a09bfcce`（"feat(rust): unify workspaces (#19034)"）将原本分散的 Rust 项目统一到 Optimism monorepo 的 `rust/` workspace 下。

**修改范围**：Op-reth crate 实现了 OP Stack 特定的 EL 逻辑（chainspec、consensus 规则、EVM 扩展、payload 构建等），但不修改 upstream reth 代码本身。所有定制通过 reth 提供的 trait 扩展点实现。

**更新工作流**：
1. 更新 `rust/Cargo.toml` 中的 rev hash（所有 reth-* crate 使用同一 rev）
2. 适配 upstream API 变更（crate 级别的 trait 签名变化）
3. 在同一 monorepo 内一次性 CI 验证

**自动化程度**：中。Rev bump 本身是机械操作，但 API 适配可能需要手动工作。从历史记录看，大多数 bump 是同日或次日完成的单 PR 操作。

### 1.2 Base Tag-Pin 模型

**依赖机制**：Base（`base/base`）直接 pin upstream `paradigmxyz/reth` 的 git tag，主 workspace `Cargo.toml` 中声明：

```toml
reth-db = { git = "https://github.com/paradigmxyz/reth", tag = "v2.2.0" }
```

当前 pin 的是 reth **v2.2.0**，涉及 60+ 个 reth-* crate。

**关键区别**：Base 的主 workspace **零 op-reth、零 kona、零 op-alloy 依赖**。所有 OP Stack 特定逻辑均在 `base-*` crate 中自研实现。Base 仓库共 127 个 root workspace member（含 SP1 guest 子 workspace 共 130 crate）。

**修改范围**：对 upstream reth 零修改。Base 通过 reth 提供的 trait 扩展点和泛型组合实现所有定制，与 reth 的交互面（conflict surface）仅限于 trait API 签名。

**更新工作流**：
1. 在 `Cargo.toml` 中 bump tag 版本（如 `v2.1.0` → `v2.2.0`）
2. 适配 reth trait API 变更
3. 1 个仓库、1 个 PR

**自动化程度**：高。Tag bump 是纯声明性操作，仅需处理 trait 层面的 breaking change。由于 Base 不依赖 op-reth/kona/op-alloy 中间层，没有级联传播延迟。

### 1.3 Mantle Full Fork 模型

**依赖机制**：Mantle 采用完整 fork 模式，`mantle/reth` 仓库的 `Cargo.toml` workspace 版本为 `1.9.3`（对应 reth v1.9.3，发布于 2025-11-18）：

```toml
[workspace.package]
version = "1.9.3"
homepage = "https://paradigmxyz.github.io/reth"
repository = "https://github.com/paradigmxyz/reth"
authors = ["Mantle Core Contributors"]
```

**依赖 fork 链**：

| 仓库 | Fork 来源 | 说明 |
|------|----------|------|
| `mantle/reth` | `paradigmxyz/reth` v1.9.3 | 主 EL 客户端 fork |
| `mantle/revm` | `bluealloy/revm` | EVM 实现 fork |
| `mantle/alloy-evm` | `alloy-rs/evm` | EVM 接口 fork |
| `mantle/op-alloy` | `alloy-rs/op-alloy` | OP 类型 fork |
| `mantle/kona` | `op-rs/kona` | 证明系统 fork |

共 5 个主仓库 + 4 个依赖 fork = **9 个仓库需要协同管理**。

**修改范围**：Mantle 在 fork 中做了深度修改，包括：
- 新增 `crates/mantle-hardforks/` 定义 Mantle 特有的 hardfork（Skadi = Prague-equivalent, Limb = Osaka-equivalent, Arsia）
- 在 `crates/optimism/` 目录下修改 OP Stack 相关逻辑
- 在 revm fork 中新增 `OpSpecId::ARSIA` 等自定义 spec
- tokenRatio 计算、MNT 原生代币支持等 Mantle 特有功能

**更新工作流**：
1. 从 upstream `paradigmxyz/reth` 的目标版本 rebase/merge 到 `mantle/reth`
2. 解决 reth fork 中的 merge conflict
3. 同步更新 4 个依赖 fork
4. 确保 5 个仓库间的依赖版本一致
5. 全量 CI 验证

**自动化程度**：低。级联 rebase 需要人工解决 conflict，尤其是核心文件的 fork diff 已达高 rebase 风险等级。

### 1.4 三种模型对比总览

| 维度 | OP (git-rev pin) | Base (tag-pin) | Mantle (full fork) |
|------|------------------|----------------|--------------------|
| 依赖方式 | git rev pin in workspace Cargo.toml | git tag pin in Cargo.toml | full repo fork + merge |
| 对 upstream reth 的修改 | 零（独立 crate 通过 trait 扩展） | 零（独立 crate 通过 trait 扩展） | 深度修改（散布在 fork 中） |
| 需变更的仓库数 | 1（optimism monorepo, rust workspace） | 1（base monorepo） | 9（5 main + 4 dep forks） |
| 依赖层数（到 reth） | 1（workspace rev pin reth） | 1（直接 tag pin reth） | 3（mantle-reth → reth fork → upstream reth） |
| 需 rebase 的仓库数 | 0（rev bump, not rebase） | 0（tag bump, not rebase） | 9 |
| Merge conflict risk | 低（仅 crate API 变更） | 低（仅 trait API 变更） | 高（级联跨 9 仓库） |
| OP Stack 中间层依赖 | 原生（op-reth 就是 OP Stack 的一部分） | 零（自研所有 OP 逻辑） | 需额外适配 OP 激活配置 |

## 2. Reth Pectra/Fusaka Hardfork 迭代时间线

### 2.1 Ethereum Hardfork 时间线（已完成）

截至 2026-05-26，Pectra 和 Fusaka 均已在 L1 主网成功激活：

| Hardfork | L1 主网激活日期 | 状态 |
|----------|--------------|------|
| **Pectra** (Prague+Electra) | **2025-05-07** | 已完成 |
| **Fusaka** (Fulu+Osaka) | **2025-12-03** 21:49:11 UTC | 已完成 |
| Fusaka BPO1（Blob 扩容第一阶段） | 2025-12-09 14:21:11 UTC | 已完成 |
| Fusaka BPO2（Blob 扩容第二阶段） | 2026-01-07 01:01:11 UTC | 已完成 |

Fusaka 是 Ethereum 首个采用三阶段滚动激活的 hardfork：主 fork（2025-12-03）→ BPO1（2025-12-09）→ BPO2（2026-01-07），核心特性为 PeerDAS（EIP-7594）和 Blob 容量从 6 → 10 → 15 target 的分阶段扩容。

### 2.2 Reth 版本迭代时间线

| 版本 | 发布日期 | 说明 |
|------|---------|------|
| v1.3.0 | 2025-03-12 | Pectra 准备阶段开始 |
| v1.3.5 ~ v1.3.12 | 2025-04-02 ~ 2025-04-17 | Pectra 主网激活前密集发布（8 个版本/16 天） |
| **v1.4.1** | **2025-05-16** | **首个 Pectra 主网后 stable release**（Pectra+9 天） |
| v1.4.3 ~ v1.5.0 | 2025-05-20 ~ 2025-06-26 | Pectra 后持续优化 |
| v1.6.0 ~ v1.8.0 | 2025-07-22 ~ 2025-09-23 | |
| v1.8.2 | 2025-09-30 | Fusaka Holesky 测试网支持 |
| **v1.9.0** | **2025-11-05** | **Fusaka 主网支持引入** |
| v1.9.1 | 2025-11-07 | Fusaka hotfix（修复 EIP-7928 EVM 回归） |
| v1.9.2 | 2025-11-11 | OP Stack 补丁 |
| **v1.9.3** | **2025-11-18** | **OP Stack + Jovian 补丁；Mantle fork 基点** |
| v1.10.0 | 2026-01-15 | |
| v1.11.0 ~ v1.11.3 | 2026-02-16 ~ 2026-03-12 | |
| **v2.0.0** | **2026-04-08** | **大版本升级**（breaking changes） |
| v2.1.0 | 2026-04-20 | |
| **v2.2.0** | **2026-04-30** | **Base 和 Op-Reth 当前 pin 版本** |

**关键观察**：

1. **Pectra 响应**：reth 在 Pectra L1 激活（2025-05-07）前后密集发布了 v1.3.x 系列。从 Pectra 测试网准备到 mainnet stable release（v1.4.1）仅约 2 个月。
2. **Fusaka 响应**：reth v1.9.0（2025-11-05）在 Fusaka L1 激活（2025-12-03）前约 1 个月就已发布主网支持。v1.9.3（2025-11-18）是 Fusaka 激活前的最终稳定版本，并被 Ethereum Foundation 列为 Fusaka 就绪客户端。
3. **Fusaka 激活后问题**：reth v1.9.3 在 Fusaka 激活当天（2025-12-03）出现了 OOM 问题（paradigmxyz/reth#20110），但总体完成了网络升级。

### 2.3 Hardfork 兼容版本总结

| Hardfork | 首个兼容 reth 版本 | 发布日期 | 距 L1 激活 |
|----------|-------------------|---------|-----------|
| Pectra | v1.3.x（预激活） | 2025-03 ~ 2025-04 | L1 前 1-2 个月 |
| Fusaka | **v1.9.0** | **2025-11-05** | **L1 前 28 天** |

**这意味着 Mantle 当前 pin 的 reth v1.9.3 已完整包含 Pectra 和 Fusaka 的 EL 支持**。Mantle 在 hardfork 客户端兼容性层面并不落后——v1.9.3 就是 Ethereum Foundation 认可的 Fusaka 就绪版本。

## 3. Op-Reth Pectra/Fusaka Hardfork 迭代时间线与 Lag 量化

### 3.1 Op-Reth 发布时间线

Op-reth 自 2026-02-10 Rust workspace 统一后的发布历史：

| 版本 | 发布日期 | 对应 reth 版本 |
|------|---------|---------------|
| op-reth/v1.11.0 | 2026-02-20 | reth v1.11.0 (2026-02-16) |
| op-reth/v1.11.3 | 2026-03-17 | reth v1.11.3 (2026-03-12) |
| op-reth/v1.11.5 | 2026-04-02 | ~reth v1.11.3 |
| op-reth/v2.0.0 | 2026-04-15 | reth v2.0.0 (2026-04-08) |
| op-reth/v2.1.0 | 2026-04-21 | reth v2.1.0 (2026-04-20) |
| op-reth/v2.2.0 | 2026-04-29 | reth v2.2.0 (2026-04-30) |
| op-reth/v2.2.1 | 2026-05-04 | ~reth v2.2.0 |
| op-reth/v2.2.2 | 2026-05-11 | ~reth v2.2.0 |
| op-reth/v2.2.3 | 2026-05-18 | ~reth v2.2.0 |
| op-reth/v2.2.5 | 2026-05-26 | ~reth v2.2.0+ |

### 3.2 Reth Rev Pin 变更记录与 Lag 量化

以下是 `rust/Cargo.toml` 中 reth rev pin 的历史变更记录及与 upstream reth release 的时间差：

| Reth Release | Reth 发布日期 | Op-Reth Bump Commit | Bump 日期 | Lag（天） |
|-------------|-------------|--------------------|-----------|---------:|
| v1.11.0 | 2026-02-16 | `9ddfb4611b31` (#19240) | 2026-02-19 | **3** |
| v1.11.1 | 2026-02-23 | `c48932131098` (#19292) | 2026-03-06 | **11** |
| v1.11.2 | 2026-03-10 | `d40fb204ed55` (#19472) | 2026-03-11 | **1** |
| v1.11.3 | 2026-03-12 | `7149381de9a8` (#19498) | 2026-03-12 | **0** |
| v2.0.0 | 2026-04-08 | `1e3ee2540a13` (#19989) | 2026-04-10 | **2** |
| v2.2.0 | 2026-04-30 | `7a33d9f2f907` (#20459) | 2026-04-30 | **0** |

**统计分析**：

| 指标 | 值 |
|------|---|
| 样本数 | 6 次 rev bump |
| 中位数 lag | **2 天** |
| 平均 lag | **2.8 天** |
| 最大 lag | **11 天**（v1.11.1，同时升级 MSRV 至 1.92） |
| 最小 lag | **0 天**（v1.11.3、v2.2.0 同日 bump） |

**关键结论**：Op-reth 对 upstream reth 的 rev pin 更新响应非常快速。大多数情况下在 0-3 天内完成。v1.11.1 的 11 天 lag 是异常值，来自同步的 toolchain 变更而非 reth 适配本身的复杂度。此外，op-reth 有时 pin 到 unreleased 的 reth commit，允许在需要时精确锁定到特定 fix，而无需等待 upstream release。

### 3.3 Op-Reth v2.0.0 大版本升级分析

Reth v2.0.0（2026-04-08）是一个包含 breaking changes 的大版本升级。Op-reth 在 **2 天内**（2026-04-10）完成了 bump，并在 5 天后发布了 op-reth/v2.0.0（2026-04-15）。中间还有一个过渡性 commit（2026-04-03），表明迁移分两步完成：先升级核心依赖，再 bump 到正式 tag。

## 4. OP Hardfork 激活配置里程碑与 L2 协议就绪度

### 4.1 EL 代码就绪 vs L2 协议激活就绪

reth/op-reth 的 EL 代码就绪仅仅是 OP Stack L2 网络可以激活 hardfork 的前提之一。完整的 L2 hardfork 激活链路涉及多个组件的协同：

```
Ethereum EIP 规范
    → reth EL 实现
        → op-reth crate 更新（rev pin bump + crate 适配）
            → OP specs hardfork 定义
                → superchain-registry 配置（激活时间戳）
                    → op-node rollup-config 激活逻辑
                        → L2 节点软件发布
                            → L2 网络就绪
```

### 4.2 Isthmus (Pectra-equivalent) 激活里程碑（已完成）

Op-reth hardfork 映射关系（来源：`rust/op-reth/crates/hardforks/src/lib.rs`）：

| OP L2 Hardfork | 对应 L1 Hardfork | 激活状态 |
|---------------|-----------------|---------|
| Canyon | Shanghai | 已完成 |
| Ecotone | Cancun | 已完成 |
| **Isthmus** | **Prague (Pectra-EL)** | **已完成** |
| **Jovian** | **Fusaka** | **已完成** |

Isthmus 激活时间线：

| 里程碑 | 日期 | 时间戳 | 来源 |
|--------|------|--------|------|
| Ethereum Pectra L1 主网激活 | 2025-05-07 | - | Ethereum 官方 |
| Isthmus Sepolia 激活 | 2025-04-17 16:00 UTC | 1744905600 | superchain-registry |
| op-node v1.13.2 发布（Isthmus Mainnet release） | 2025-04-18 | - | GitHub releases |
| **Isthmus OP 主网激活** | **2025-05-09 16:00 UTC** | **1746806401** | superchain-registry |

**EL→L2 时间差**：Isthmus 在 OP 主网的激活时间（2025-05-09）仅比 Pectra L1 激活（2025-05-07）晚 **2 天**。Isthmus Sepolia（2025-04-17）甚至在 Pectra L1 主网激活之前就已完成测试网验证。

**适用范围说明**：Isthmus 是 OP/Superchain 共享激活——所有 OP Stack 链（OP Mainnet、Base、Zora 等）在同一时间窗口内同时激活。这反映的是 OP Stack 生态的集体 hardfork 协调能力，而非任何单条链的 codebase 优势。

### 4.3 Jovian (Fusaka-equivalent) 激活里程碑（已完成）

Jovian 作为 Fusaka 的 OP Stack 等价物，已在 2025 年底成功激活：

| 里程碑 | 日期 | 时间戳 |
|--------|------|--------|
| Jovian Sepolia 激活 | **2025-11-19** 16:00:01 UTC | 1763568001 |
| **Jovian OP 主网激活** | **2025-12-02** 16:00:01 UTC | 1764691201 |
| Ethereum Fusaka L1 主网激活 | **2025-12-03** 21:49:11 UTC | 1764798551 |

**EL→L2 时间差**：Jovian 在 OP 主网的激活（2025-12-02）比 Fusaka L1 激活（2025-12-03）**早 1 天**，延续了 Isthmus 的模式。OP 生态通过 Upgrade 17 将 Fusaka L1 兼容性支持和 Jovian L2 hardfork 打包在同一 prestate 中发布，使得 L2 可以在 L1 激活之前就完成准备。

**适用范围说明**：与 Isthmus 相同，Jovian 是 OP/Superchain 共享激活，所有 OP Stack 链同时受益。

### 4.4 Hardfork 激活配置的技术结构

**`op-core/superchain/types.go`** 中的 `HardforkConfig` 结构定义了所有 OP Stack hardfork 的激活时间字段：

```go
type HardforkConfig struct {
    CanyonTime             *uint64
    DeltaTime              *uint64
    EcotoneTime            *uint64
    FjordTime              *uint64
    GraniteTime            *uint64
    HoloceneTime           *uint64
    IsthmusTime            *uint64
    JovianTime             *uint64
    KarstTime              *uint64
    InteropTime            *uint64
    PectraBlobScheduleTime *uint64
}
```

**Op-reth hardfork 代码**（`rust/op-reth/crates/hardforks/src/lib.rs`）在 Rust 侧镜像了这些配置。OP 主网的 Isthmus/Prague 激活时间戳为 `1746806401`（2025-05-09 16:00:01 UTC），Jovian 激活时间戳为 `1764691201`（2025-12-02 16:00:01 UTC）。

### 4.5 OP 生态 Hardfork 激活效率总结（回顾性评估）

| Hardfork | L1 激活日期 | OP L2 激活日期 | L1→L2 间隔 | 适用范围 |
|----------|-----------|--------------|-----------|---------|
| Pectra → Isthmus | 2025-05-07 | 2025-05-09 | **+2 天** | **OP/Superchain 全链共享** |
| Fusaka → Jovian | 2025-12-03 | 2025-12-02 | **-1 天** | **OP/Superchain 全链共享** |

OP 生态展示了极高的 hardfork 协调效率：EL 代码就绪、OP specs 定义、superchain-registry 配置、op-node 激活逻辑能够在 L1 hardfork 前后 1-2 天内完成全部协调，使 L2 在 L1 激活的同一时间窗口内完成升级。**但这一效率是 OP Stack 生态层面的集体能力，不可归因于任何单条链的 codebase 选择。**

## 5. Mantle 全链路 Hardfork 延迟影响评估

### 5.1 三种延迟度量指标的区分

round-1 草稿中将 Mantle 的 reth v1.9.3 → v2.2.0 版本差距（约 5 个月）等同于"hardfork lag"，这是一个重要的方法论错误。本轮修订将延迟拆分为三个独立度量指标：

#### 指标 1：Hardfork 兼容客户端版本 Lag

**定义**：从 Ethereum hardfork 激活到首个支持该 hardfork 的 reth 版本发布的时间差。这是衡量 reth 客户端是否具备 hardfork 兼容性的操作性指标。

**Mantle 当前状态**：

| Hardfork | 首个兼容 reth 版本 | 版本发布日期 | Mantle pin 版本 | 兼容性状态 |
|----------|-------------------|-----------|----------------|----------|
| Pectra | v1.3.x | 2025-03 ~ 2025-04 | v1.9.3 | **已兼容**（v1.9.3 >> v1.3.x） |
| Fusaka | v1.9.0 | 2025-11-05 | v1.9.3 | **已兼容**（v1.9.3 = Fusaka 就绪版本） |

**结论**：**Mantle 的 reth pin 在 hardfork 兼容性维度的 lag 为零**。reth v1.9.3 是 Ethereum Foundation 明确列出的 Fusaka 就绪客户端版本。Mantle 不需要升级 reth 版本来获得 Pectra 或 Fusaka 的 EL 支持。

#### 指标 2：上游最新版本维护漂移

**定义**：Mantle 当前 pin 的 reth 版本与 upstream 最新 release 之间的版本和时间差距。这衡量的是 Mantle 缺失的非 hardfork 改进（性能优化、安全补丁、API 改进、bug 修复等）。

**Mantle 当前状态**：

| Mantle Pin | Upstream Latest | 版本差距 | 时间差距 | 跨大版本 |
|-----------|----------------|---------|---------|---------|
| **v1.9.3**（2025-11-18） | **v2.2.0**（2026-04-30） | 13 个 minor/patch + 1 个 major | **~5 个月** | **是**（v1.x → v2.x） |

**缺失的主要改进**：
- reth v2.0.0 的 breaking API changes
- v1.10.0 ~ v2.2.0 期间的性能优化和 bug 修复
- 安全补丁（post-Fusaka OOM 修复等）

**结论**：这一差距代表的是**维护债务**，而非 hardfork 跟进风险。它意味着 Mantle 可能错过安全补丁和性能优化，但不影响其对已知 hardfork 的 EL 兼容性。然而，随着未来 hardfork（如 Pectra 之后的新 EIP 规范）引入新的 EL 要求，维护漂移会转化为 hardfork 风险——Mantle 可能需要一次跨越多个大版本的 rebase 才能获得下一个 hardfork 的支持。

#### 指标 3：L2 协议激活 Lag

**定义**：从 Ethereum L1 hardfork 激活到 Mantle L2 网络实际完成等价升级的端到端时间。这是对最终用户和生态影响最大的指标。

**Mantle 实际激活记录**（来源：`mantle/reth` codebase hardfork 配置 + 公开发布记录）：

| Mantle Hardfork | 对应 L1 Hardfork | L1 激活日期 | Mantle 主网激活日期 | **L2 激活 Lag** |
|----------------|-----------------|-----------|-------------------|---------------|
| **Skadi** | Pectra (Prague) | 2025-05-07 | **2025-08-27** | **112 天** |
| **Limb** | Fusaka (Osaka) | 2025-12-03 | **2026-01-14** | **42 天** |

Mantle Sepolia 测试网在主网之前完成验证：
- Skadi Sepolia: 2025-07-16（主网前 42 天）
- Limb Sepolia: 2025-12-03（主网前 42 天，与 Fusaka L1 同日）

**关键发现**：Mantle 的 L2 激活 lag 从 Pectra 时期的 112 天**缩短至** Fusaka 时期的 42 天，**改善幅度达 62.5%**。这表明 Mantle 团队在 hardfork 集成流程上取得了显著进步。

### 5.2 Mantle 激活延迟的根因分析

Mantle 的 L2 激活 lag 并非来自 reth 版本不兼容（如上所述，v1.9.3 已包含 Fusaka 支持），而是来自 full fork 模型固有的集成流程：

1. **自有 hardfork 配置**：Mantle 使用独立的 hardfork 名称体系（Skadi/Limb/Arsia），需要在 `crates/mantle-hardforks/` 中定义映射关系和激活时间戳
2. **多仓库协调**：9 个仓库需要同步适配新 hardfork 逻辑
3. **自有 Sepolia 测试网验证**：Mantle Sepolia 的激活需要独立配置和验证，而非使用 OP Sepolia
4. **Bundled fork 模式**：Mantle 的 Limb Fork（2025-12 ~ 2026-01）将 8 个 OP Stack fork（Canyon through Jovian）打包在一次升级中，降低了升级频率但增加了单次升级的复杂度和测试周期

### 5.3 端到端延迟对比（实际数据——修正后）

| 维度 | OP/Superchain 共享激活 | Base-native 激活 (Azul) | Mantle | 说明 |
|------|---------------------|----------------------|--------|------|
| Pectra L2 激活 lag | 2 天（Isthmus，全链共享） | N/A（Azul 不含 Pectra 内容） | **112 天（Skadi）** | Isthmus 是 Superchain 共享事件 |
| Fusaka L2 激活 lag | -1 天（Jovian，全链共享） | **~176 天（Azul，待激活）** | **42 天（Limb）** | Jovian 共享；Azul 是 Base-native Osaka 对齐 |
| reth hardfork 兼容 lag | 0 天 | 0 天 | **0 天** | 三者均无 |
| 上游维护漂移 | 0 | 0（v2.2.0） | **~5 个月** | 仅 Mantle 存在 |

### 5.4 级联 Rebase 成本量化

| 维度 | 数据 |
|------|------|
| 需 rebase 的仓库数 | 9 |
| 主仓库（有直接修改） | 5（reth, revm, alloy-evm, op-alloy, kona） |
| 高 conflict risk 文件 | `state_transition.go`、`rollup_cost.go` 等核心路径 |
| 典型 rebase 时间（单次小版本） | 数天至 1-2 周 |
| 跨大版本 rebase（如 v1.x → v2.x） | 数周至数月 |
| CI 验证周期 | 每个仓库需独立跑通完整 CI |

**当前跨大版本升级困境**：如果 Mantle 需要从 v1.9.3 升级到 v2.x，需要一次性跨越 v2.0.0 的 breaking changes，这在 9 个仓库的级联 rebase 场景下工程量极大。虽然当前 v1.9.3 对 Pectra/Fusaka 是兼容的，但下一个需要 v2.x 才能支持的 hardfork 到来时，Mantle 将面临更大的升级压力。

## 6. Base 激活时间线的双轨分析（Round-3 新增）

### 6.1 为什么必须区分 OP/Superchain 共享激活与 Base-native 激活

Round-2 使用 Base 的 Isthmus（+2 天）和 Jovian（-1 天）数据来评估切换到 Base codebase 的 hardfork 跟进收益。这一论证的关键缺陷在于：**Isthmus 和 Jovian 是 OP/Superchain 共享激活**——它们不是 Base 自有 codebase 路径决定的结果，而是所有 OP Stack 链共同参与的 Superchain 升级协调。任何运行在 OP Stack 上的链（OP Mainnet、Base、Zora、甚至在评估期的 Mantle）都可以在同一窗口内获得这些激活。

要评估"切换到 Base codebase 是否加快 hardfork 跟进"，必须使用 **Base 在脱离 OP Stack 共享升级轨道后、独立推进的 hardfork 激活数据**。Base Azul 正是这样的数据点。

### 6.2 Base Azul：Base 首个独立升级

**Base Azul** 是 Base 脱离 OP Stack 客户端后的首个自主 hardfork（来源：`base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md`）。

**关键事实**：
- **客户端要求**：仅 `base-reth-node`（执行）和 `base-consensus`（共识）支持 Azul。`op-node`、`op-geth`、op-reth 和其他 OP Stack 客户端在激活后不再被支持。这是 Base 首次以"dropping support"口径发布升级公告。
- **EVM 对齐**：Azul 在执行层采纳了 7 项 Ethereum Osaka 执行层 EIP——5 项核心 EVM 变更：EIP-7825（交易 gas 上限 2^24）、EIP-7823（MODEXP 输入限制）、EIP-7883（MODEXP 计价提升）、EIP-7939（CLZ opcode）、EIP-7951（secp256r1 gas 翻倍），以及 2 项网络/配置层变更：EIP-7642（`eth/69` 协议升级）和 EIP-7910（`eth_config` 配置交换）。通过 `BaseUpgrade::Azul => SpecId::OSAKA` 映射（来源：`base-azul-upgrade/research-sections/osaka-evm-changes/final.md`）。
- **其他特性**：Multiproof 系统（TEE + ZK 双证明）、客户端整合、Flashblocks payload 精简。

**激活时间线**：

| 网络 | 激活日期 | 时间戳 | 来源 | 状态 (2026-05-26) |
|------|---------|--------|------|-----------------|
| **Sepolia** | **2026-04-20** 18:00 UTC | `1_776_708_000` | `config.rs:412` + `overview.md:21` 一致 | **已激活** |
| **Mainnet** | 代码设定 **2026-05-28** 18:00 UTC | `1_779_991_200` | `config.rs:340`；spec overview 仍标记 TBD | **待激活（+2 天）** |

**激活时间线详细说明**：
- Blog 最初公告的日期为 2026-05-13（来源：`blog.base.dev/introducing-base-azul`）
- 2026-05-16，commit `5e3a68de`（"chore: delay azul to 28th may (#2724)"）将 mainnet 时间戳从 `1_779_386_400`（2026-05-21 18:00 UTC）改为 `1_779_991_200`（2026-05-28 18:00 UTC），同时将 spec overview 表格改回 TBD
- 公开 governance 确认前不应视为正式承诺日期，但代码时间戳是当前最佳估计

### 6.3 三轨时间线对比表

| 轨道 | 升级名称 | L1 参照 | Sepolia 激活 | 主网激活 | 距 L1 激活天数 | 性质 |
|------|---------|---------|-------------|---------|-------------|------|
| **Track A: OP/Superchain 共享** | Isthmus | Pectra (2025-05-07) | 2025-04-17 | 2025-05-09 | **+2 天** | Superchain 全链协调激活 |
| **Track A: OP/Superchain 共享** | Jovian | Fusaka (2025-12-03) | 2025-11-19 | 2025-12-02 | **-1 天** | Superchain 全链协调激活 |
| **Track B: Base-native** | **Azul** | Fusaka/Osaka (2025-12-03) | **2026-04-20** | **2026-05-28** (code) | **~176 天** | Base 独立升级，仅 base-reth-node + base-consensus |
| **Track C: Mantle fork** | Skadi | Pectra (2025-05-07) | 2025-07-16 | 2025-08-27 | **+112 天** | Mantle 独立升级 |
| **Track C: Mantle fork** | Limb | Fusaka (2025-12-03) | 2025-12-03 | 2026-01-14 | **+42 天** | Mantle 独立升级 |
| **Track C: Mantle fork** | Arsia | Mantle-specific | - | 2026-04-22 | N/A | Mantle 特有 fork（无 L1 对应） |

### 6.4 Azul 与 Jovian 的关系解析

一个需要澄清的问题是：**Azul 和 Jovian 对 Base 来说是什么关系？**

- **Jovian**（Track A, 2025-12-02）：OP/Superchain 协调激活的 Fusaka 等价升级。Jovian 在网络层面为 Base 提供了 Fusaka 兼容性（blob 扩容、PeerDAS 等 L1 共识层变更的 L2 映射）。这是 Base 作为 OP Stack 链自动获得的升级，不依赖 Base 自有 codebase。
- **Azul**（Track B, 2026-05-28）：Base 在脱离 OP Stack 客户端后的首次独立升级。Azul 在**执行层**采纳 Osaka EIP，实现 EVM 级别的 L1 等价性。Azul 还包含 Multiproof 和客户端整合等非 hardfork 内容。

因此，Base 的 Fusaka/Osaka 支持实际上分两步完成：
1. **网络级 Fusaka 兼容**：通过 Jovian（Superchain 共享），-1 天
2. **EVM 级 Osaka 对齐**：通过 Azul（Base-native），~176 天

Mantle 的 Limb 在一次升级中打包了两个层面的内容，42 天完成。

### 6.5 重新评估 Base 切换收益——Hardfork 激活速度维度

Round-2 的核心论点是"切换到 Base codebase 可将 hardfork 激活 lag 从 42-112 天缩短至 1-3 天，改善 14x-37x"。**此论点需要根本性修正**：

**被废弃的论据**：
- "1-3 天" 来自 Isthmus/Jovian 的 OP/Superchain 共享激活数据。所有 OP Stack 链（包括当前的 Mantle 架构）都能参与这些共享激活。切换到 Base codebase 不是获得这一速度的前提。
- "14x-37x 改善" 是用 OP/Superchain 共享数据与 Mantle 独立升级数据的对比，逻辑上不成立。

**修正后的分析**：

| 对比维度 | Mantle 当前 (Limb) | Base-native (Azul) | 倍数关系 |
|---------|-------------------|-------------------|---------|
| Fusaka/Osaka EVM 对齐 lag | 42 天 | ~176 天 | **Mantle 快 4.2x** |
| 网络级 Fusaka 兼容 | 42 天（独立升级，含在 Limb 中） | -1 天（通过 Jovian，Superchain 共享） | OP/Superchain 轨道更快 |

**关键洞察**：在 Base-native 独立升级维度上，Mantle 的 Limb（42 天）实际上比 Base 的 Azul（~176 天）更快。这并不意味着 Mantle 的架构更优——Azul 是 Base 脱离 OP Stack 后的**首次**独立升级，包含了大量非 hardfork 工作（Multiproof、客户端整合），不纯粹是 hardfork 跟进。但它确实说明：**切换到 Base codebase 不能自动加速 hardfork 激活**。hardfork 激活速度取决于团队的工程优先级和协调效率，而非依赖模型本身。

## 7. 三种依赖模型在 Hardfork 跟进维度的对比（修正后）

### 7.1 升级成本模型

| Dimension | Base (tag-pin) | OP op-reth (monorepo git-rev pin) | Mantle (full fork) |
|-----------|---------------|----------------------------------|-------------------|
| 依赖方式 | git tag pin in Cargo.toml | git rev pin in workspace Cargo.toml | full repo fork + merge |
| 需变更的仓库数 | **1** | **1** | **9** |
| 依赖层数 | **1** | **1** | **3** |
| 需 rebase 的仓库数 | **0** | **0** | **9** |
| reth 版本跟进速度 | tag bump，与 upstream 同步 | rev bump，中位 2 天 | 需 cascading rebase，周至月级 |
| Hardfork 客户端兼容 lag | 0 | 0 | **0**（当前 v1.9.3 已兼容） |
| 上游维护漂移 | 0 | 0 | **~5 个月 + 1 大版本** |
| Merge conflict risk | **低** | **低-中** | **高** |
| OP/Superchain 共享激活 | 参与（作为 OP Stack 链） | 原生支持 | 需独立适配 |
| Base-native 独立升级 | 自主（Azul: ~176 天） | N/A | N/A |
| Mantle 独立升级 | N/A | N/A | Skadi 112 天 / Limb 42 天（趋势改善） |

### 7.2 成本复杂度分析

**Base 模型**：**O(1)** 升级复杂度。无论 reth 有多少变更，升级操作始终是"bump tag + adapt traits"。conflict surface 仅限于 reth 公开的 trait 签名变更。

**OP 模型**：**O(1)** 升级复杂度（接近 Base）。Rev bump 是声明性操作，crate API 适配工作量与 reth 的 breaking changes 数量成比例，但由于 op-reth 不修改 reth 代码，不存在 merge conflict。

**Mantle 模型**：**O(N)** 升级复杂度，其中 N = 需要同步更新的 fork 仓库数量（当前 N=9）。每个仓库的 rebase 工作量与该仓库中 Mantle 特有修改的代码量和 upstream 变更的冲突面积成正比。虽然 Mantle 的 Pectra→Fusaka 响应时间从 112 天缩短到 42 天，但这一改善更可能来自团队熟练度提升和 bundled fork 策略，而非模型本身的效率改进——每次升级仍需在 9 个仓库中执行级联 rebase。

### 7.3 自动化可行性

| 维度 | Base | OP | Mantle |
|------|------|----|----|
| 版本 bump 自动化 | 高（Dependabot/Renovate） | 高（可脚本化 rev bump） | 低（需人工解决 conflict） |
| CI 复杂度 | 低（单仓库） | 中（monorepo CI） | 高（9 仓库 CI） |
| 回滚难度 | 低 | 低 | 高（9 仓库协调回滚） |

## 8. Hardfork 跟进维度的 Mantle 切换建议（修正后）

### 8.1 切换收益重新评估

**Round-3 修正**：round-2 的 14x-37x 改善估计基于错误证据（OP/Superchain 共享激活数据归因于 Base codebase），已被废弃。修正后的收益评估区分两个维度：

#### 维度 A：OP/Superchain 共享激活参与权

| 当前状态 | 切换后 | 收益 |
|---------|-------|------|
| Mantle 不参与 OP/Superchain 协调激活，需独立跟进每个 hardfork | 如切换到 OP Stack / Base 模型，**有可能**参与 Superchain 协调激活 | 理论上可从 42-112 天缩短至 1-2 天 |

**但这一收益取决于**：Mantle 切换后是否真正作为 Superchain 成员参与协调激活，还是仍需维护自有的 hardfork 配置和激活流程。如果 Mantle 仍需保留自有的 Skadi/Limb 风格 hardfork 命名和独立测试网验证，Superchain 共享激活的速度优势将被部分抵消。

#### 维度 B：维护成本降低（核心收益，证据充分）

| 收益维度 | 当前状态 | 切换后预期 | 改善幅度 |
|---------|---------|-----------|---------|
| 上游维护漂移 | ~5 个月 + 1 大版本 | 0（与 upstream 同步） | **完全消除** |
| 需 rebase 的仓库数 | 9 | 0 | **完全消除** |
| 大版本升级风险 | 极高（需跨 v2.0.0） | 低（tag bump） | **显著降低** |
| Merge conflict 频率 | 高（每次 rebase） | 低（仅 trait API 变更） | **显著降低** |
| 升级复杂度模型 | O(N), N=9 | O(1) | **量级降低** |

**这一维度的收益不依赖于 hardfork 激活速度的对比**，而是来自依赖模型本身的结构性差异。即使 Base-native Azul 的激活速度不如 Mantle Limb，tag-pin 模型在每次 upstream 更新时的维护成本仍然远低于 full fork 模型。

#### 维度 C：未来 hardfork 跟进风险（前瞻性）

当前 Mantle pin 的 v1.9.3 对 Pectra 和 Fusaka 都是兼容的。但下一个 Ethereum hardfork（如 Glamsterdam，预计 2026 年 H2）可能需要 reth v2.x+ 才能支持。届时 Mantle 将面临从 v1.9.3 跨越 v2.0.0 breaking changes 的大规模 rebase，这在 9 个仓库的级联场景下是极高风险操作。切换到 tag-pin 模型可以从根本上消除这一累积风险。

### 8.2 关于维护漂移风险的独立评估

虽然 Mantle 的 v1.9.3 对 Pectra 和 Fusaka 是兼容的，但 5 个月的维护漂移带来两类风险：

1. **安全风险**：reth v1.9.3 ~ v2.2.0 之间发布的安全补丁未被 Mantle 采纳。例如 Fusaka 激活当天的 OOM 问题（#20110）在后续版本中修复，但 Mantle 的 fork 可能仍然存在该问题。
2. **未来 hardfork 升级成本**：当下一个 hardfork 需要 v2.x 才能支持时，Mantle 将面临从 v1.9.3 直接跳到 v2.x 的大规模 rebase，跨越 v2.0.0 breaking changes。维护漂移越大，这次升级的难度越高。切换到 tag-pin 模型可以彻底消除这一累积风险。

### 8.3 切换成本与风险

| 成本/风险 | 说明 |
|----------|------|
| **迁移工程量** | 需将 Mantle 在 9 个 fork 中的所有定制逻辑迁移到独立 crate（类似 Base 的 `base-*` crate 模式） |
| **Mantle 特有功能重实现** | MNT 原生代币、tokenRatio、自定义 hardfork（Skadi/Limb/Arsia）等需在 trait 扩展点中重新实现 |
| **OP Stack 兼容性** | 切换到 Base 模型意味着不再依赖 op-reth，需要自研所有 OP Stack EL 逻辑（或选择性采纳） |
| **测试覆盖重建** | 需要重建完整的测试套件 |

### 8.4 分阶段实施路径

**阶段 1（短期，0-3 月）：评估与概念验证**
- 建立 Mantle 独立 crate 架构原型（参考 Base 的 `base-*` crate 模式）
- 识别 Mantle fork 中的最小定制集合
- 评估哪些 OP Stack 功能需要保留

**阶段 2（中期，3-9 月）：核心迁移**
- 将 Mantle 特有逻辑迁移到独立 crate
- 切换到 upstream reth tag-pin 依赖（从 v1.9.3 直接跳到当时最新版本）
- 消除 4 个依赖 fork

**阶段 3（中长期，9-18 月）：优化与验证**
- 建立 hardfork 跟进自动化流程（Dependabot/Renovate + CI）
- 在下一个 Ethereum hardfork 中验证新模型的跟进速度
- 评估是否需要参考 Base 自研 derivation pipeline

### 8.5 Pectra/Fusaka 案例端到端对比（回顾性——修正后）

以 Pectra 和 Fusaka 两次已完成的 hardfork 为案例，区分三种激活轨道：

| 里程碑 | reth (upstream) | OP/Superchain 共享 | Base-native (Azul) | Mantle |
|--------|---------------|-------------------|-------------------|--------|
| **Pectra (2025-05-07)** | | | | |
| EL 代码就绪 | v1.3.x (2025-03~04) | 同步跟进 | 同步跟进 | 已含在 v1.9.3 |
| L2 主网激活 | - | **2025-05-09** (Isthmus, +2 天, 全链共享) | N/A | **2025-08-27** (Skadi, +112 天) |
| **Fusaka (2025-12-03)** | | | | |
| EL 代码就绪 | v1.9.0 (2025-11-05) | 同步跟进 | 同步跟进 | v1.9.3 |
| 网络级 L2 激活 | - | **2025-12-02** (Jovian, -1 天, 全链共享) | (继承 Jovian) | **2026-01-14** (Limb, +42 天) |
| EVM 级 Osaka 对齐 | - | 由各链自行实现 | **2026-05-28** (Azul, +176 天) | 已含在 Limb |
| **当前状态 (2026-05-26)** | | | | |
| reth 版本 | v2.2.0 (2026-04-30) | pin 到 ~v2.2.0+ | v2.2.0 | **v1.9.3** |
| Hardfork 兼容性 | 基准 | 基准 | 基准 | **Pectra+Fusaka 兼容** |
| 维护漂移 | 基准 | ~0 | 0 | **~5 个月** |

### 8.6 综合结论

1. **切换到 Base/tag-pin 模型的核心收益在于维护成本结构性降低**，而非 hardfork 激活速度的直接提升。O(1) vs O(N) 的升级复杂度差异、0 vs 9 的 rebase 仓库数、消除维护漂移和大版本跨越风险——这些都是切换到 tag-pin 模型后确定可获得的收益。

2. **Hardfork 激活速度的收益取决于 Mantle 是否加入 Superchain 协调轨道**。如果 Mantle 仅切换依赖模型但仍独立运营升级流程，其 hardfork 激活速度将主要取决于自身工程能力，而非依赖模型。当前 Mantle 的 Limb（42 天）已展示了显著的改善趋势。

3. **即使不考虑 hardfork 激活速度的对比，维护成本和未来升级风险的降低已足以支撑切换建议**。特别是在 Mantle 面临 v1.9.3 → v2.x 的跨大版本 rebase 困境时，越早切换到 tag-pin 模型，未来的维护负担越轻。

## Diagrams

### diag-1: Reth/Op-Reth/Mantle/Base-Azul Pectra+Fusaka Hardfork 时间线对比

```mermaid
gantt
    title Reth/Op-Reth/Mantle/Base-Azul Hardfork 时间线（三轨对比）
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m

    section Ethereum L1
    Pectra L1 主网激活           :milestone, pectra, 2025-05-07, 0d
    Fusaka L1 主网激活           :milestone, fusaka, 2025-12-03, 0d
    Fusaka BPO1                 :milestone, bpo1, 2025-12-09, 0d
    Fusaka BPO2                 :milestone, bpo2, 2026-01-07, 0d

    section reth (upstream)
    v1.3.x Pectra 准备           :active, r13, 2025-03-12, 2025-04-17
    v1.4.1 Pectra 后首个 stable  :milestone, r14, 2025-05-16, 0d
    v1.9.0 Fusaka 主网支持       :milestone, r19, 2025-11-05, 0d
    v1.9.3 (Mantle fork 基点)   :milestone, r193, 2025-11-18, 0d
    v2.0.0 大版本               :milestone, r20, 2026-04-08, 0d
    v2.2.0 (当前 Base/OP pin)   :milestone, r22, 2026-04-30, 0d

    section Track A: OP/Superchain 共享激活
    Isthmus Sepolia              :milestone, istsep, 2025-04-17, 0d
    Isthmus OP 主网 (+2天)       :milestone, istmn, 2025-05-09, 0d
    Jovian Sepolia               :milestone, jovsep, 2025-11-19, 0d
    Jovian OP 主网 (-1天)        :milestone, jovmn, 2025-12-02, 0d

    section Track B: Base-native 独立升级
    Azul Sepolia                 :milestone, azsep, 2026-04-20, 0d
    Azul 主网 (code: 05-28)      :milestone, azmn, 2026-05-28, 0d
    Fusaka → Azul lag            :crit, azlag, 2025-12-03, 2026-05-28

    section Track C: Mantle fork 激活
    Skadi Sepolia                :milestone, sksep, 2025-07-16, 0d
    Skadi 主网 (Pectra equiv)    :milestone, skmn, 2025-08-27, 0d
    Pectra 激活 lag              :crit, sklag, 2025-05-07, 2025-08-27
    Limb Sepolia                 :milestone, lmsep, 2025-12-03, 0d
    Limb 主网 (Fusaka equiv)     :milestone, lmmn, 2026-01-14, 0d
    Fusaka 激活 lag              :crit, lmlag, 2025-12-03, 2026-01-14
    Arsia 主网                   :milestone, arsia, 2026-04-22, 0d

    section 上游维护漂移
    Mantle 漂移区间 (v1.9.3→v2.2.0) :crit, mlag, 2025-11-18, 2026-04-30
```

### diag-2: 三种依赖模型 Hardfork 跟进流程对比

```mermaid
flowchart LR
    subgraph Base["Base (tag-pin) — O(1) 升级"]
        style Base fill:#d4edda
        B1["reth upstream<br/>发布新 tag"] --> B2["bump Cargo.toml<br/>tag 版本"]
        B2 --> B3["适配 trait<br/>API 变更"]
        B3 --> B4["1 repo / 1 PR<br/>CI pass"]
        B4 --> B5["升级完成"]
    end

    subgraph OP["OP (git-rev pin) — O(1) 升级"]
        style OP fill:#cce5ff
        O1["reth upstream<br/>发布新版本/commit"] --> O2["更新 rust/Cargo.toml<br/>rev hash"]
        O2 --> O3["适配 crate<br/>API 变更"]
        O3 --> O4["1 monorepo<br/>CI pass"]
        O4 --> O5["升级完成"]
    end

    subgraph Mantle["Mantle (full fork) — O(N) 升级, N=9"]
        style Mantle fill:#f8d7da
        M1["reth upstream<br/>发布新版本"] --> M2["rebase/merge<br/>mantle/reth"]
        M2 --> M3["解决 reth<br/>merge conflicts"]
        M3 --> M4["更新 4 个<br/>依赖 fork"]
        M4 --> M5["Mantle hardfork<br/>配置 + 映射"]
        M5 --> M6["Sepolia 测试<br/>+ 验证"]
        M6 --> M7["跨 9 仓库<br/>CI 验证"]
        M7 --> M8["主网激活"]
    end
```

### diag-3: OP Stack L2 Hardfork 激活全链路依赖图（含双轨标注）

```mermaid
flowchart TB
    subgraph EL_Path["EL (Execution Layer) 路径"]
        style EL_Path fill:#e8f4fd
        EIP["Ethereum EIP 规范<br/>(如 Prague/Osaka EIPs)"]
        RETH["reth EL 实现<br/>(paradigmxyz/reth)"]
        OPRETH["op-reth crate 更新<br/>(rev pin bump + API adapt)"]
        EIP --> RETH
        RETH --> OPRETH
    end

    subgraph CL_Path["CL/Protocol 路径 — Track A: OP/Superchain 共享"]
        style CL_Path fill:#fef3cd
        SPECS["OP specs hardfork 定义<br/>(Isthmus / Jovian spec)"]
        REGISTRY["superchain-registry 配置<br/>(IsthmusTime / JovianTime)"]
        OPNODE["op-node rollup-config<br/>激活逻辑"]
        SPECS --> REGISTRY
        REGISTRY --> OPNODE
    end

    subgraph Release["Track A: 共享发布与激活 (1-2 天)"]
        style Release fill:#d4edda
        SW["L2 节点软件发布<br/>(op-node + op-reth/op-geth)"]
        NET["OP/Superchain 全链<br/>同时激活"]
        OPRETH --> SW
        OPNODE --> SW
        SW --> NET
    end

    subgraph Base_Path["Track B: Base-native 独立路径"]
        style Base_Path fill:#e8daef
        BAZUL["base-reth-node<br/>Azul 升级实现"]
        BCON["base-consensus<br/>配置"]
        BTEST["Base Sepolia 验证"]
        BMAIN["Base 主网激活<br/>(Azul: ~176 天)"]
        RETH --> BAZUL
        BAZUL --> BCON
        BCON --> BTEST
        BTEST --> BMAIN
    end

    subgraph Mantle_Path["Track C: Mantle 独立路径"]
        style Mantle_Path fill:#f8d7da
        MFORK["mantle-reth fork<br/>rebase + 9 repo sync"]
        MHARK["Mantle hardfork 配置<br/>(Skadi/Limb/Arsia)"]
        MSEP["Mantle Sepolia 验证"]
        MNET["Mantle 主网激活<br/>(Limb: 42 天)"]
        MFORK --> MHARK
        MHARK --> MSEP
        MSEP --> MNET
    end

    L1["Ethereum L1 hardfork<br/>主网激活"]
    L1 -.->|"触发 Track A 激活窗口"| NET
    L1 -.->|"触发 Track B/C 独立跟进"| BAZUL
    L1 -.->|"触发 Track B/C 独立跟进"| MFORK
    RETH --> MFORK

    style EIP fill:#fff3cd
    style RETH fill:#cce5ff
    style OPRETH fill:#cce5ff
    style SPECS fill:#fef3cd
    style REGISTRY fill:#fef3cd
    style OPNODE fill:#fef3cd
    style SW fill:#d4edda
    style NET fill:#d4edda
    style L1 fill:#f8d7da
    style BAZUL fill:#e8daef
    style BCON fill:#e8daef
    style BTEST fill:#e8daef
    style BMAIN fill:#e8daef
    style MFORK fill:#f8d7da
    style MHARK fill:#f8d7da
    style MSEP fill:#f8d7da
    style MNET fill:#f8d7da
```

## Source Coverage

| 需求 ID | 类型 | 描述 | 状态 | 使用的源 |
|---------|------|------|------|---------|
| src-1 | code_analysis | 本地 Cargo.toml 和 crate 结构分析 | **met** | OP `rust/Cargo.toml` (rev pin), Base `Cargo.toml` (tag pin v2.2.0), Mantle `Cargo.toml` (fork v1.9.3), `mantle-hardforks/src/lib.rs` (激活时间戳), Base `config.rs` (Azul 激活时间戳) |
| src-2 | official_docs | paradigmxyz/reth GitHub releases | **met** | 完整 release 列表 v1.3.0 ~ v2.2.0，含 Fusaka 支持时间线 |
| src-3 | official_docs | Optimism monorepo op-reth commit/release 历史 | **met** | `rust/Cargo.toml` path commits + op-reth release tags |
| src-4 | code_analysis | OP specs / superchain-registry / op-node hardfork 配置源码 | **met** | `op-core/superchain/types.go`, `op-node/rollup/types.go`, `op-reth/crates/hardforks/src/lib.rs`, `chain_metadata.rs` (Jovian timestamp 1764691201) |
| src-5 | code_analysis | 已有内部研究文件 | **met** | `comparison-execution-client/final.md`, `base-rust-monorepo-architecture/final.md`, `base-advantages-assessment/final.md`, `executive-summary.md`, `base-strategy-azul-overview/final.md` (Azul 激活时间线+代码时间戳), `osaka-evm-changes/final.md` (Osaka EIP 实现细节) |
| src-6 | official_docs | Ethereum Pectra/Fusaka 规范时间线 | **met** | Pectra 主网 2025-05-07, Fusaka 主网 2025-12-03 (1764798551), Optimism Docs (Upgrade 17: Jovian), Ethereum Foundation Fusaka 公告, Base Azul blog announcement (blog.base.dev) |

## Gap Analysis

| Gap ID | 描述 | 影响 | 缓解措施 |
|--------|------|------|---------|
| gap-1 | Mantle Skadi 和 Limb 的实际激活日期来源于 codebase 中的 hardfork 配置时间戳，而非 Mantle 官方公告发布日期 | 时间戳是链上激活时间，可能与节点软件发布或公告时间有差异 | 使用链上配置时间戳作为激活日期的权威来源，辅以 web search 结果交叉验证 |
| gap-2 | Base Azul mainnet 激活日期存在不确定性：blog 公告 2026-05-13、code 时间戳 2026-05-28、spec overview 仍标 TBD | ~176 天的 lag 计算可能在实际激活后需要微调 | 使用 code 时间戳（2026-05-28）作为当前最佳估计；明确标注 spec TBD 状态 |
| gap-3 | op-reth 在 2025 年的 reth rev pin 历史不可用（Rust workspace 统一前） | item-3 的 lag 量化仅覆盖 2026-02 之后的数据（6 个样本） | 样本虽少但一致性高（中位数 2 天），足以支持结论 |
| gap-4 | Mantle 在 fork 上的实际 rebase 耗时没有公开的 PR/commit 记录 | 42-112 天的端到端 lag 包括了 rebase、测试、配置等多个环节，无法精确拆分各环节耗时 | 使用端到端激活 lag 作为综合指标，结合模型分析推断各环节贡献 |
| gap-5 | 无法确认 Mantle 是否已采纳 post-Fusaka 的安全补丁（如 OOM fix #20110） | 维护漂移的安全影响评估基于推断 | 明确标注为推断；建议 Mantle 团队审查 v1.9.3 ~ v2.2.0 期间的安全相关 release notes |
| gap-6 | Base Azul 包含大量非 hardfork 内容（Multiproof、客户端整合），因此 ~176 天的 lag 不能完全归因于 hardfork 跟进延迟 | 可能高估 Base-native 的 hardfork 跟进 lag | 在分析中明确说明 Azul 是综合升级而非纯 hardfork 跟进；未来 Base 的后续独立升级将提供更纯粹的数据点 |

## Revision Log

| Round | Action | Description |
|-------|--------|-------------|
| 1 | initial_draft | 基于已批准大纲的首轮深度草稿，覆盖所有 7 个 item 和 10 个 field，包含 3 个 mermaid 图表。 |
| 2 | revision | **修正 Finding 1（Major）**：将所有 Fusaka/Jovian 日期从 2026 修正为 2025。Fusaka L1 激活 2025-12-03（非 2026-12-03），Jovian OP 主网 2025-12-02（非 2026-12-02），Jovian Sepolia 2025-11-19（非 2026-11-19）。所有 Pectra→Fusaka→Jovian 事件重新定义为已完成的历史数据，建议和结论改为回顾性评估。**修正 Finding 2（Major）**：将"5 个月 hardfork lag"拆分为三个独立度量指标：(1) Hardfork 兼容客户端版本 lag = 零（v1.9.3 是 Fusaka 就绪版本）；(2) 上游维护漂移 = ~5 个月 + 1 大版本（维护债务而非 hardfork 风险）；(3) L2 协议激活 lag = Skadi 112 天、Limb 42 天（趋势改善）。新增 Mantle 实际 hardfork 激活时间线数据（来源：`mantle-hardforks/src/lib.rs`），新增 gap-5（安全补丁评估）。更新 diag-1 增加 Fusaka/Jovian 已完成里程碑和 Mantle 激活时间线，更新 diag-2 使用实际数据替代估算范围，更新 diag-3 增加 Mantle 额外步骤路径。 |
| 3 | revision | **修正 Finding（Major）**：Base 切换收益论据基于错误证据——round-2 的 1-3 天和 14x-37x 改善幅度来自 Isthmus/Jovian（OP/Superchain 共享激活），不可归因于 Base 自有 codebase。Round-3 引入 Base Azul 作为 Base 首个独立升级的关键数据点（来源：`base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` + `osaka-evm-changes/final.md`）。新增内容：(1) 新增 §6「Base 激活时间线的双轨分析」，将 Base 激活分为 Track A（OP/Superchain 共享：Isthmus/Jovian）和 Track B（Base-native：Azul）；(2) 新增三轨时间线对比表（§6.3），包含 OP 共享、Base-native、Mantle fork 三条轨道；(3) Base Azul 详细分析（§6.2），含 Sepolia 2026-04-20、mainnet code 时间戳 2026-05-28、~176 天 lag、blog 延迟历史；(4) 废弃 1-3 天和 14x-37x 改善估计，重新定位切换核心收益为维护成本结构性降低（O(1) vs O(N)），而非 hardfork 激活速度直接提升。所有 §4 中的 Isthmus/Jovian 里程碑添加「OP/Superchain 全链共享」适用范围标注。§5.3 端到端对比表改为区分三种激活轨道。§7 升级成本模型和 §8 切换建议全面修正。新增 gap-6（Azul 综合升级 vs 纯 hardfork 跟进的区分）。更新 3 个 mermaid 图表增加 Track B: Base-native 轨道和双轨标注。保留 round-2 的所有修正（日期纠正、三指标分离、Mantle 时间戳）。 |
