# Mantle Hoodi Testnet is Live

## TL;DR

Mantle's Hoodi testnet is now open. We switched the sequencer execution client from op-geth to a Mantle-adapted version of reth, building on the Arsia upgrade foundation. This gives Hoodi a production-ready, modular Rust execution base aligned with where the broader OP Stack ecosystem is heading. Connect now, deploy your contracts, and tell us what breaks.

## Why Hoodi

We launched Hoodi to test Mantle's reth-based execution stack in a live network before wider rollout. Three things drove this:

1. **Validate the reth migration.** Hoodi runs on a Mantle-adapted reth — the same Rust execution client family powering op-reth, Base's base-reth-node, and BNB Chain's Reth-BSC. Optimism has set op-geth EOL at 2026-05-31. Hoodi lets us validate our reth integration before mainnet.

2. **Mirror the mainnet execution environment.** Developers need a testnet that reflects what mainnet will actually run. Hoodi's reth-based stack is that environment.

3. **Collect early signal.** Integration feedback, bug reports, and tooling compatibility data — we want all of it before broader rollout. Hoodi is the low-stakes place to send it.

Hoodi is scoped specifically for reth execution validation. It complements Sepolia, which remains the primary environment for application and tooling development.

## Network Information

| Parameter | Value |
|-----------|-------|
| Network Name | Mantle Hoodi Testnet |
| Chain ID | *[TBD — confirm before publishing]* |
| RPC Endpoint | *[TBD]* |
| WebSocket | *[TBD]* |
| Block Explorer | *[TBD]* |
| Faucet | *[TBD]* |
| Bridge | *[TBD]* |
| Status Page | *[TBD]* |
| Docs | *[TBD]* |

> **Note to publishing team:** Fill in all TBD values before release. Do not publish with placeholders.

## What's Available

**Execution client.** The sequencer runs on a Mantle-adapted reth. Reth is a Rust-based, modular Ethereum execution client developed by Paradigm. Its staged sync pipeline, MDBX storage layer, REVM integration, and ExEx extension points give us a production-ready foundation — and a path to ongoing performance and maintainability improvements.

**EVM compatibility.** Hoodi supports the same EVM behavior as Mantle mainnet. Existing contracts and developer tooling — Hardhat, Foundry, ethers.js, viem — work without changes. Standard RPC methods are supported.

**Arsia baseline.** Hoodi's reth integration builds on the Arsia upgrade. The execution improvements from Arsia carry over, plus reth's operability and storage characteristics.

**What's not available yet.** This is a testnet — no SLA guarantees, no confirmed performance benchmarks against Hoodi's own workload. Public reth benchmarks (e.g., Base's archive benchmark: ~83% reduction in storage, ~5× faster provisioning) reflect Base's specific workload, not ours. We'll publish Hoodi-specific data as we gather it.

## Who Should Do What

| Audience | Action |
|----------|--------|
| **Smart contract developers** | Connect to the Hoodi RPC, deploy contracts, test EVM behavior. Report any compatibility issues or unexpected RPC responses. |
| **Node operators** | Set up a Hoodi node using the reth-based client package. Check the docs for configuration requirements and version pinning. |
| **Bridge and tooling teams** | Test cross-chain integration against the Hoodi bridge. Verify your tooling against the new execution client behavior. |
| **General testers** | Get test ETH from the faucet, send transactions, interact with deployed contracts. Report anything that behaves unexpectedly. |

## Known Limitations

- **Not production.** Do not use Hoodi for production workloads, financial settlements, or anything that requires uptime guarantees.
- **May be reset.** We may reset chain state during the testing period. Do not rely on persistent on-chain data.
- **Faucet rate limits apply.** If you hit faucet limits, check our Discord for alternatives.
- **Performance numbers are pending.** We will not claim external benchmark numbers as Hoodi guarantees. Our own workload benchmarks will be published separately.
- **Some network parameters are pending.** See the Network Information table — all values will be confirmed before launch.

## Feedback & Support

- **Bug reports**: [GitHub Issues — TBD]
- **Developer discussion**: [Discord — TBD]
- **Forum**: [TBD]
- **Status and incidents**: [Status page — TBD]

If something breaks, file a report. That's why Hoodi exists.

## Next Steps

- **[Date TBD]**: Hoodi stability window. We'll announce any planned chain resets in advance.
- **[Date TBD]**: Hoodi-specific performance benchmarks published.
- **[Date TBD]**: Mainnet reth migration timeline update.

Follow updates in [Discord / blog / docs — TBD].

## Summary

- Mantle Hoodi testnet is live. The sequencer runs on Mantle-adapted reth, a Rust-based modular execution client.
- This aligns with where the OP Stack ecosystem is heading: Optimism sunsets op-geth on 2026-05-31; Base and BNB Chain have already moved to reth-based stacks.
- Connect via the Hoodi RPC, deploy contracts, and test against the execution environment we're building toward at mainnet.
- This is a testnet: no SLA, possible chain resets, faucet rate limits.
- Report issues on [GitHub / Discord]. We need your feedback to validate before mainnet.

---
---

# Mantle Hoodi 测试网正式上线

## TL;DR

Mantle Hoodi 测试网现已开放。我们将 sequencer 执行客户端从 op-geth 切换到 Mantle 适配的 reth，基于 Arsia 升级版本。这为 Hoodi 带来了生产就绪、模块化的 Rust 执行基座，也与 OP Stack 生态的演进方向保持一致。现在就连接、部署合约，告诉我们哪里出了问题。

## 为什么是 Hoodi

我们推出 Hoodi 是为了在更广泛部署前，在真实网络环境中验证 Mantle 基于 reth 的执行栈。三个目标驱动了这个决定：

1. **验证 reth 迁移。** Hoodi 运行在 Mantle 适配的 reth 上——与 op-reth、Base 的 base-reth-node、BNB Chain 的 Reth-BSC 同属一个 Rust 执行客户端家族。Optimism 已宣布 op-geth 的 EOL 为 2026-05-31。Hoodi 让我们在主网之前完成 reth 集成的验证。

2. **还原主网执行环境。** 开发者需要一个能真实反映主网运行情况的测试网。Hoodi 的 reth 执行栈就是这个环境。

3. **收集早期信号。** 集成反馈、bug 报告、工具兼容性数据——在更大范围部署之前，这些都是我们需要的。Hoodi 就是为此设计的低风险环境。

Hoodi 专门用于 reth 执行行为的验证，与面向应用和工具开发的 Sepolia 形成互补。

## 网络信息

| 参数 | 值 |
|------|---|
| 网络名称 | Mantle Hoodi Testnet |
| Chain ID | *[待确认——发布前填写]* |
| RPC 端点 | *[待确认]* |
| WebSocket | *[待确认]* |
| 区块浏览器 | *[待确认]* |
| Faucet | *[待确认]* |
| 跨链桥 | *[待确认]* |
| 状态页面 | *[待确认]* |
| 文档入口 | *[待确认]* |

> **发布团队注意：** 发布前请填写所有"待确认"项，不要带占位符上线。

## 可用功能

**执行客户端。** Sequencer 运行在 Mantle 适配的 reth 上。reth 是 Paradigm 开发的 Rust 编写、模块化 Ethereum 执行客户端。其 staged sync pipeline、MDBX 存储层、REVM 集成和 ExEx 扩展点为 Hoodi 提供了生产就绪的执行基础，也为后续性能迭代和长期维护留下了清晰的路径。

**EVM 兼容性。** Hoodi 支持与 Mantle 主网相同的 EVM 行为。现有合约和开发工具——Hardhat、Foundry、ethers.js、viem——无需修改即可使用。标准 RPC 方法均受支持。

**Arsia 基线。** Hoodi 的 reth 集成基于 Arsia 升级版本。Arsia 带来的执行改进在 Hoodi 上同样可用，加上 reth 的可运维性和存储特性。

**暂未提供的功能。** 这是一个测试网——没有 SLA 保证，没有基于 Hoodi 自身工作负载的确认性能基准。公开的 reth 基准（如 Base 的 archive benchmark：存储减少约 83%、provisioning 速度提升约 5 倍）反映的是 Base 的特定工作负载，不是我们的。我们会在收集数据后单独发布 Hoodi 的性能结果。

## 不同用户的行动指引

| 用户类型 | 建议行动 |
|---------|---------|
| **智能合约开发者** | 连接 Hoodi RPC，部署合约，测试 EVM 行为。报告任何兼容性问题或异常的 RPC 响应。 |
| **节点运营者** | 使用基于 reth 的客户端包搭建 Hoodi 节点。查看文档了解配置要求和版本锁定规范。 |
| **跨链桥和工具团队** | 针对 Hoodi 跨链桥端点测试跨链集成，验证工具对新执行客户端的兼容性。 |
| **普通测试用户** | 通过 Faucet 获取测试 ETH，发送交易，与已部署合约交互。报告任何异常行为。 |

## 已知限制

- **非生产环境。** 不要将 Hoodi 用于生产负载、金融结算或任何需要可用性保障的场景。
- **可能重置。** 测试期间我们可能重置链状态，不一定提前通知。不要依赖链上持久化数据。
- **Faucet 有速率限制。** 遇到限制时，查看 Discord 获取替代方案。
- **性能数据待发布。** 我们不会把外部项目的 benchmark 数字作为 Hoodi 的性能承诺。Hoodi 自身的工作负载基准会单独发布。
- **部分网络参数待确认。** 见网络信息表格——所有值在上线前会确认填写。

## 反馈与支持

- **Bug 报告**：[GitHub Issues——待确认]
- **开发者讨论**：[Discord——待确认]
- **论坛**：[待确认]
- **状态与故障通知**：[状态页面——待确认]

遇到问题就报告。这正是 Hoodi 存在的意义。

## 下一步计划

- **[日期待定]**：Hoodi 稳定窗口。任何计划中的链重置会提前通知。
- **[日期待定]**：发布基于 Hoodi 自身工作负载的性能基准。
- **[日期待定]**：主网 reth 迁移时间表更新。

关注 [Discord / 博客 / 文档——待确认] 获取最新动态。

## 摘要

- Mantle Hoodi 测试网已上线。Sequencer 运行在 Mantle 适配的 reth 上——Rust 编写的模块化执行客户端。
- 这与 OP Stack 生态的走向一致：Optimism 将于 2026-05-31 停止 op-geth 支持；Base 和 BNB Chain 已经完成向 reth-based 栈的迁移。
- 通过 Hoodi RPC 连接，部署合约，在与主网目标方向一致的执行环境中测试。
- 这是测试网：无 SLA 保证，可能重置链状态，Faucet 有速率限制。
- 在 [GitHub / Discord] 报告问题。我们需要你的反馈来完成主网前的验证。
