# Mantle 企业级权限与准入层设计方案

> **Issue**: WHI-352 | **Milestone**: M3: Mantle 企业级改造可行性设计
> **Date**: 2026-05-07
> **Dependencies**: WHI-350 (Gap Analysis), WHI-341 (Mantle V2 架构基线)
> **Reference Sources**: WHI-344 (准入控制对比), WHI-337 (Prividium 参考), WHI-340 (Tempo/Zones 参考)

---

## 执行摘要

本设计方案为 Mantle V2 制定完整的企业级权限控制和准入机制，覆盖从网络层到数据层的五层纵深防御架构。方案的核心设计理念是**利用 Mantle 中心化 Sequencer 作为天然准入控制点**——这一在公链语境中被视为"中心化缺陷"的架构特征，在企业语境中恰恰是零成本的合规资产。

**核心设计决策**：

1. **Phase 1 采用“四层准入防线”**：RPC 认证网关（企业 IAM 入口）→ Sequencer 策略引擎（交易级过滤）→ L1 Bridge 白名单（封堵强制交易旁路）→ Predeploy 身份/策略注册表（链上权威状态与受管合约兜底）。其中真正的链级强制发生在 RPC、Sequencer、L1 Bridge 三层；Predeploy 在 Phase 1 主要承担策略状态和受管合约集成，不宣称对所有任意 EVM 合约做全局拦截。

2. **Predeploy 优先原则**：所有链上扩展优先使用 Predeploy 合约而非 Precompile 或 opcode 修改。Predeploy 通过代理模式升级，不需要修改 EVM 指令语义——这是满足 WHI-350 中 R1（EVM 兼容性）与 R2（分叉维护负担）约束的关键。

3. **双轨身份模型**：Phase 1 采用“地址白名单 + SSO 联邦”双轨——链上通过 Identity Registry Predeploy 维护已认证地址列表（策略执行层），链下通过 OIDC/JWT 实现 RPC 层认证（用户体验层）。两条路径互补，SSO 提供企业用户体验，白名单提供链上策略执行能力。

4. **多租户先做逻辑隔离，不承诺独立执行环境**：Phase 1 的多租户能力是租户级身份空间、策略覆盖、速率限制和审计分区；真正的“每租户独立执行环境 / 独立隐私域”属于 WHI-350 定义的长期目标，需要在 Phase 2/3 结合隐私层或 Zone 架构实现。

5. **最小侵入原则**：优先中间件层和合约层方案，控制对 OP Stack 核心代码的修改量；对无法在不改核心前提下全局强制的能力（如任意 ERC-20 转账合规、任意内部 CREATE/CREATE2 禁止），明确收敛为“受管资产模板/受管工厂模式”。

**预估总工作量**：Phase 1 准入 MVP 约 8-12 人月，2-3 名全栈工程师 + 1 名合约工程师，3-4 个月内完成。

### 执行审查结论：与 WHI-350 的覆盖关系

| WHI-350 Gap / 约束 | 本文设计响应 | 覆盖结论 |
|---|---|---|
| 准入控制需覆盖网络/交易/合约/数据层 | Layer 0/1/2/3/4 分层方案；P2P 作为网络侧硬化 | **已覆盖** |
| L1→L2 强制交易可绕过 RPC | Layer 0 `OptimismPortal` + L1Allowlist 单独封堵 | **已覆盖** |
| 身份管理需支持 KYC + 企业 IAM | Identity Registry + OIDC/JWT + KYC Oracle | **已覆盖** |
| 多租户支持 | Phase 1 提供逻辑租户隔离；独立执行环境延后到 Phase 2/3 | **已覆盖，但分阶段收敛** |
| 最小侵入 / EVM 兼容 | Predeploy + 中间件优先；避免 precompile / opcode 级改动 | **已覆盖** |
| 数据层准入与隐私协同 | Phase 1 仅做企业 RPC 端点访问控制；真实保密依赖 WHI-351 | **已覆盖，但边界已明确** |
| 工程估算与代码改动点 | 第五章和第六章给出改动清单、阶段与验收项 | **已覆盖** |

---

## 第一章：多层准入控制架构设计

### 1.1 架构总览

```
                        ┌─────────────────────────────────────────────────┐
                        │               ETHEREUM L1                       │
                        │  ┌─────────────────────────────────────────┐   │
                        │  │  OptimismPortal / L1Allowlist (修改)      │   │
                        │  │  + isAllowed(msg.sender) 白名单修饰符     │   │
                        │  │  + tenant/tag 映射供审计与路由关联        │   │
                        │  └──────────────────────┬──────────────────┘   │
                        └─────────────────────────│─────────────────────-┘
                                                  │ L1→L2 Deposits
                                                  ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │  MANTLE ENTERPRISE L2                                                     │
  │                                                                           │
  │  Layer 1: RPC 认证网关 (中间件层)                                          │
  │  ┌─────────────────────────────────────────────────────────────────────┐  │
  │  │  Nginx/Envoy Reverse Proxy                                         │  │
  │  │  ┌──────────┐  ┌─────────────┐  ┌────────────────────────────┐    │  │
  │  │  │ OIDC/JWT │  │ Rate Limiter│  │ Audit Logger               │    │  │
  │  │  │ Verifier │  │ (per-tenant)│  │ (structured event stream)  │    │  │
  │  │  └────┬─────┘  └──────┬──────┘  └──────────┬─────────────────┘    │  │
  │  │       │ SSO Token     │ Throttle            │ Audit Event          │  │
  │  └───────│───────────────│─────────────────────│──────────────────────┘  │
  │          ▼               ▼                     ▼                         │
  │  Layer 2: Sequencer 策略引擎 (交易层)                                     │
  │  ┌─────────────────────────────────────────────────────────────────────┐  │
  │  │  op-node/rollup/sequencing/sequencer.go                            │  │
  │  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │  │
  │  │  │ Admission Filter │  │ Policy Evaluator │  │ Compliance Check │ │  │
  │  │  │ (whitelist cache)│  │ (rule engine)    │  │ (AML/sanctions)  │ │  │
  │  │  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘ │  │
  │  │           │ Accept/Reject       │ Policy Result        │ Compliant  │  │
  │  └───────────│─────────────────────│──────────────────────│───────────┘  │
  │              ▼                     ▼                      ▼              │
  │  Layer 3: Predeploy 策略注册表 (合约层/链上权威状态)                      │
  │  ┌─────────────────────────────────────────────────────────────────────┐  │
  │  │  EVM Execution                                                      │  │
  │  │  ┌─────────────────────┐  ┌──────────────────────────────────────┐ │  │
  │  │  │ Identity Registry   │  │ Policy Registry Predeploy            │ │  │
  │  │  │ Predeploy           │  │ (准入策略 + 受管合约策略查询)         │ │  │
  │  │  │ 0x4200...0030       │  │ 0x4200...0031                        │ │  │
  │  │  └─────────────────────┘  └──────────────────────────────────────┘ │  │
  │  └─────────────────────────────────────────────────────────────────────┘  │
  │                                                                           │
  │  Layer 4: 数据层准入 (与 WHI-351 隐私层协同)                               │
  │  ┌─────────────────────────────────────────────────────────────────────┐  │
  │  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │  │
  │  │  │ RPC Query Filter │  │ Event Visibility │  │ Private DA Access│ │  │
  │  │  │ (per-role data)  │  │ Control          │  │ (Phase 2)        │ │  │
  │  │  └──────────────────┘  └──────────────────┘  └──────────────────┘ │  │
  │  └─────────────────────────────────────────────────────────────────────┘  │
  └───────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Layer 1: RPC 认证网关

#### 1.2.1 设计目标

RPC 认证网关是企业用户与 Mantle 链交互的**唯一公开入口**，实现企业 IAM 系统（Okta/Azure AD/Google Workspace）与区块链准入的桥接。参考 Prividium Proxy RPC 三步验证模型（WHI-337 §3.4.2），但针对 Mantle 架构特点做了以下调整：

- 不修改 op-geth 核心代码——纯中间件层部署
- 支持多租户隔离（不同企业客户独立配置）
- 与 Sequencer 策略引擎双向联动

#### 1.2.2 认证流程

```
┌──────────┐     ┌──────────────────────────────────────────────────┐
│  Client  │     │  RPC Authentication Gateway                      │
│ (dApp /  │     │                                                  │
│  Script) │     │  Step 1: Token Verification                      │
│          │────►│  ┌─────────────────────────────────────────────┐ │
│  Bearer: │     │  │ Verify JWT signature (RS256/ES256)          │ │
│  JWT     │     │  │ Check token expiry, issuer, audience        │ │
│          │     │  │ Extract: subject_id, roles[], tenant_id     │ │
│          │     │  └──────────────────────┬──────────────────────┘ │
│          │     │                         ▼                        │
│          │     │  Step 2: Address Binding Verification             │
│          │     │  ┌─────────────────────────────────────────────┐ │
│          │     │  │ Match tx.from → registered wallet addresses │ │
│          │     │  │ Lookup: user_id → [addr1, addr2, ...]       │ │
│          │     │  │ Reject if address not bound to this user    │ │
│          │     │  └──────────────────────┬──────────────────────┘ │
│          │     │                         ▼                        │
│          │     │  Step 3: Permission Check                        │
│          │     │  ┌─────────────────────────────────────────────┐ │
│          │     │  │ Check: role has permission for target       │ │
│          │     │  │  contract + function selector               │ │
│          │     │  │ Optional: argument-level restrictions       │ │
│          │     │  └──────────────────────┬──────────────────────┘ │
│          │     │                         ▼                        │
│          │     │  Step 4: Forward to op-geth RPC                  │
│          │     │  ┌─────────────────────────────────────────────┐ │
│          │     │  │ Inject: X-Enterprise-User, X-Tenant-ID      │ │
│          │     │  │ Emit: audit log event (structured JSON)     │ │
│          │     │  │ Forward: eth_sendRawTransaction → op-geth   │ │
│          │     │  └─────────────────────────────────────────────┘ │
│          │     └──────────────────────────────────────────────────┘
└──────────┘
```

#### 1.2.3 技术实现

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| **反向代理** | Envoy Proxy + ext_authz filter | Envoy 的 ext_authz 允许将认证决策委托给外部服务，不需修改 Envoy 核心 |
| **认证服务** | Go 微服务 (独立进程) | 实现 Envoy ext_authz gRPC 接口；处理 JWT 验证、地址绑定、权限检查 |
| **OIDC 集成** | 标准 OIDC Discovery + JWKS | 自动发现 IdP 端点和签名密钥，支持密钥轮换 |
| **地址绑定存储** | PostgreSQL + Redis 缓存 | 用户-地址映射在 PostgreSQL 中持久化，Redis LRU 缓存热数据 |
| **权限配置** | YAML 配置文件 + Admin API | 静态配置支持快速启动，Admin API 支持运行时动态更新 |
| **审计日志** | 结构化 JSON → Kafka/NATS 事件流 | 每个请求生成审计事件，供合规系统消费 |
| **监控** | Prometheus metrics + Grafana | 请求延迟 (P50/P99)、认证通过/拒绝率、各租户 QPS |

#### 1.2.4 双 RPC 端点

参考 Prividium 的双端点设计（WHI-337 §3.4.2），支持两种接入方式：

| 端点 | 认证方式 | 适用场景 |
|------|---------|---------|
| `POST /rpc` | HTTP Header: `Authorization: Bearer <JWT>` | 后端服务、脚本 (ethers.js, viem) |
| `POST /wallet/{session_token}` | Token 嵌入 URL | 浏览器钱包 (MetaMask Custom RPC) |

`/wallet/{session_token}` 端点通过短期 session token（15 分钟 TTL）避免在 MetaMask 配置中暴露长期凭证。Session token 通过 OAuth2 授权码流程获取，绑定到特定的钱包地址。

#### 1.2.5 安全加固

1. **op-geth RPC 不对外暴露**：通过防火墙规则确保 op-geth 的 JSON-RPC 端口仅允许来自 RPC 网关的流量
2. **TLS 终止**：在 Envoy 层终止 TLS，后端通信使用 mTLS
3. **限流**：per-tenant 令牌桶限流，防止单一租户耗尽资源
4. **Multicall 阻止**：检测并拒绝 Multicall 模式（参考 Prividium 的安全策略，WHI-337 §3.4.3），因其可能绕过函数级权限检查

**预估工作量**：2-4 周，1 名后端工程师

### 1.3 Layer 2: Sequencer 策略引擎

#### 1.3.1 设计目标

Sequencer 策略引擎是准入控制的**核心层**。WHI-350 §2.4A 明确指出：Mantle 的中心化 Sequencer 是**最低成本高价值**的企业适配点——改造不引入新的信任假设（Mantle 已是中心化 Sequencer），只需叠加策略引擎。

Sequencer 策略引擎拦截以下来源的交易：
- 通过 RPC 网关提交的交易（已经过 Layer 1 认证）
- P2P 网络传播的交易（如果启用了 P2P 节点加入）
- 其他非预期路径的交易

#### 1.3.2 方案选型与论证

| 方案 | 描述 | 不可绕过性 | 侵入性 | 推荐 |
|------|------|----------|--------|------|
| **A: Sequencer 前置 API 网关** | 在 Sequencer 前部署网关过滤交易 | 低（L1 强制 TX 绕过；P2P 传播绕过） | 零核心代码修改 | 否（仅作为 Layer 1 的补充） |
| **B: Sequencer 内部 mempool 过滤** | 在 `sequencer.go` 交易处理流程中注入策略检查 | 中（覆盖 Sequencer 处理的所有交易） | 低-中（注入回调/接口） | **推荐（Phase 1 核心）** |
| **C: EVM Precompile 联合** | 通过 EVM precompile 在执行层强制检查 | 最高（EVM 执行级） | 高（需硬分叉） | 否（使用 Predeploy 替代） |

**选择方案 B 的理由**：
1. 方案 A 的 L1 强制交易绕过问题是致命缺陷（WHI-344 §1.2.2）
2. 方案 C 的 precompile 需要硬分叉升级，违反最小侵入原则（WHI-350 R2）；WHI-344 §4.3 明确建议 Mantle 采用 predeploy 而非 precompile
3. 方案 B + Layer 3 Predeploy 策略注册表组合，兼具方案 B 的灵活性和方案 C 的执行级强制力

#### 1.3.3 策略引擎架构

```
op-node/rollup/sequencing/sequencer.go
                │
                ▼
    ┌───────────────────────────────────────┐
    │  Transaction Processing Pipeline       │
    │                                        │
    │  1. Receive TX (from RPC/P2P)          │
    │       │                                │
    │       ▼                                │
    │  ┌─────────────────────────────────┐   │
    │  │ ★ AdmissionFilter.Check(tx)     │   │ ◄─── 新增注入点
    │  │   - whitelist lookup (LRU cache) │   │
    │  │   - policy evaluation            │   │
    │  │   → Accept / Reject / Defer      │   │
    │  └────────────┬────────────────────┘   │
    │               │                        │
    │       ┌───────▼───────┐                │
    │       │  Accept?      │                │
    │       │  Yes → continue│                │
    │       │  No  → drop    │                │
    │       └───────┬───────┘                │
    │               ▼                        │
    │  2. Order TX (existing logic)          │
    │       │                                │
    │       ▼                                │
    │  ┌─────────────────────────────────┐   │
    │  │ ★ ComplianceCheck.Verify(batch) │   │ ◄─── 新增注入点
    │  │   - batch-level policy check     │   │
    │  │   - sanctions screening          │   │
    │  │   → Pass / Flag / Reject         │   │
    │  └────────────┬────────────────────┘   │
    │               ▼                        │
    │  3. Build Block (existing logic)       │
    │       │                                │
    │       ▼                                │
    │  ┌─────────────────────────────────┐   │
    │  │ ★ AuditEmitter.Emit(block)      │   │ ◄─── 新增注入点
    │  │   - structured audit event       │   │
    │  │   - compliance report            │   │
    │  └─────────────────────────────────┘   │
    │                                        │
    └───────────────────────────────────────┘
```

#### 1.3.4 Go 接口定义

```go
// enterprise/admission/admission.go

package admission

import (
    "context"
    "github.com/ethereum/go-ethereum/core/types"
    "github.com/ethereum/go-ethereum/common"
)

// AdmissionResult represents the result of an admission check
type AdmissionResult int

const (
    Accept  AdmissionResult = iota
    Reject                          // 明确拒绝，记录审计日志
    Defer                           // 延迟到 Predeploy 层检查
)

// AdmissionFilter is the primary interface for transaction admission control.
// Implementations MUST be safe for concurrent use.
type AdmissionFilter interface {
    // Check evaluates whether a transaction should be admitted.
    // Called on the hot path — implementations MUST return within 5ms.
    Check(ctx context.Context, tx *types.Transaction) (AdmissionResult, error)

    // Reload refreshes the filter's internal state (e.g., whitelist cache).
    // Called when on-chain Identity Registry emits update events.
    Reload(ctx context.Context) error
}

// PolicyEvaluator evaluates configurable policies against transactions.
type PolicyEvaluator interface {
    // Evaluate runs all active policies against the transaction.
    Evaluate(ctx context.Context, tx *types.Transaction) (PolicyResult, error)
}

// PolicyResult contains the evaluation outcome and metadata.
type PolicyResult struct {
    Allowed    bool
    Reason     string              // human-readable reason for reject
    MatchedRules []string          // IDs of matched policy rules
    Metadata   map[string]string   // additional metadata for audit
}

// ComplianceChecker performs batch-level compliance verification.
type ComplianceChecker interface {
    // VerifyBatch checks a batch of transactions for compliance.
    VerifyBatch(ctx context.Context, txs []*types.Transaction) ([]ComplianceResult, error)
}

// ComplianceResult per-transaction compliance check result.
type ComplianceResult struct {
    TxHash   common.Hash
    Compliant bool
    Flags    []string             // e.g., ["SANCTIONS_MATCH", "HIGH_RISK_JURISDICTION"]
}

// AuditEmitter emits structured audit events for compliance reporting.
type AuditEmitter interface {
    // EmitTxEvent emits an audit event for a single transaction.
    EmitTxEvent(ctx context.Context, tx *types.Transaction, result AdmissionResult, policy PolicyResult)

    // EmitBlockEvent emits an audit event for a completed block.
    EmitBlockEvent(ctx context.Context, blockNumber uint64, txCount int, rejectedCount int)
}
```

#### 1.3.5 白名单缓存策略

策略引擎的核心性能要求：**每笔交易的额外延迟不超过 5ms**。

```
                ┌──────────────────────────────────────────┐
                │  Whitelist Cache Architecture              │
                │                                            │
                │  ┌──────────────────────────────────────┐ │
                │  │  L1 Cache: Go sync.Map (in-process)   │ │
                │  │  - Capacity: 100K addresses            │ │
                │  │  - Lookup: ~100ns                      │ │
                │  │  - Miss → L2 Cache                     │ │
                │  └────────────────┬─────────────────────┘ │
                │                   │ Cache Miss              │
                │  ┌────────────────▼─────────────────────┐ │
                │  │  L2 Cache: LRU (bounded memory)       │ │
                │  │  - Capacity: 1M addresses              │ │
                │  │  - Lookup: ~1μs                        │ │
                │  │  - Miss → On-chain Query               │ │
                │  └────────────────┬─────────────────────┘ │
                │                   │ Cache Miss              │
                │  ┌────────────────▼─────────────────────┐ │
                │  │  Identity Registry Predeploy Query    │ │
                │  │  - eth_call to 0x4200...0030          │ │
                │  │  - Lookup: ~1-5ms                     │ │
                │  │  - Result cached in L1+L2             │ │
                │  └──────────────────────────────────────┘ │
                │                                            │
                │  Cache Invalidation:                       │
                │  - Subscribe to IdentityRegistry events    │
                │  - AddressRegistered → add to cache        │
                │  - AddressRevoked → remove from cache      │
                │  - Full reload every 5 minutes (safety)    │
                └──────────────────────────────────────────┘
```

**链上为权威来源，Sequencer 内存缓存为执行层缓存**——两者通过 Identity Registry 合约的事件（`AddressRegistered`, `AddressRevoked`）保持同步。

**预估工作量**：1-2 人月，1 名 Go 工程师

### 1.4 Layer 3: Predeploy 策略注册表 (合约层)

#### 1.4.1 设计目标

Predeploy 策略注册表在 Phase 1 的定位是**链上权威状态源 + 受管合约策略入口**，而不是“自动拦截全网任意 EVM 调用”的全局机制。它承担三类职责：

1. 为 Sequencer、RPC 网关和受管业务合约提供统一的身份/策略查询接口
2. 作为治理和审计可追溯的链上配置源，避免核心策略完全停留在链下数据库
3. 为 Phase 2 的受管资产模板、Transfer Hook、隐私层协同留下兼容扩展点

这一定义与 WHI-350 的“predeploy 优先、最小侵入”原则一致：把可升级的链上状态与策略查询抽出来，但不为了全局强制去修改 EVM opcode、precompile 或执行语义。

#### 1.4.2 合约架构

```
Predeploy Contracts (deployed at genesis or via upgrade deposit tx)
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Identity Registry (0x4200000000000000000000000000000000000030)   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Storage:                                                   │  │
│  │    mapping(address => Identity) identities                  │  │
│  │    mapping(bytes32 => Role) roles                           │  │
│  │    mapping(address => mapping(bytes32 => bool)) hasRole     │  │
│  │    mapping(address => uint256) kycExpiry                    │  │
│  │                                                             │  │
│  │  Functions:                                                 │  │
│  │    registerAddress(addr, kycLevel, expiry) [ADMIN_ROLE]     │  │
│  │    suspendAddress(addr, reason) [ADMIN_ROLE]                │  │
│  │    revokeAddress(addr) [ADMIN_ROLE]                         │  │
│  │    grantRole(addr, role) [ROLE_ADMIN]                       │  │
│  │    revokeRole(addr, role) [ROLE_ADMIN]                      │  │
│  │    isRegistered(addr) → bool [PUBLIC]                       │  │
│  │    isKYCVerified(addr) → bool [PUBLIC]                      │  │
│  │    hasRole(addr, role) → bool [PUBLIC]                      │  │
│  │    getIdentity(addr) → Identity [PUBLIC]                    │  │
│  │                                                             │  │
│  │  Events:                                                    │  │
│  │    AddressRegistered(addr, kycLevel, expiry)                │  │
│  │    AddressSuspended(addr, reason)                           │  │
│  │    AddressRevoked(addr, reason)                             │  │
│  │    RoleGranted(addr, role, grantedBy)                       │  │
│  │    RoleRevoked(addr, role, revokedBy)                       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Policy Registry (0x4200000000000000000000000000000000000031)     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Storage:                                                   │  │
│  │    mapping(address => ContractPolicy) contractPolicies      │  │
│  │    mapping(bytes4 => FunctionPolicy) globalFunctionPolicies │  │
│  │    PolicyRule[] activeRules                                 │  │
│  │    bool deploymentRestricted                                │  │
│  │                                                             │  │
│  │  Functions:                                                 │  │
│  │    setContractPolicy(contract, policy) [POLICY_ADMIN]       │  │
│  │    setFunctionPolicy(selector, policy) [POLICY_ADMIN]       │  │
│  │    setDeploymentRestricted(bool) [POLICY_ADMIN]             │  │
│  │    isTransactionAllowed(from, to, data) → bool [PUBLIC]     │  │
│  │    isDeploymentAllowed(deployer) → bool [PUBLIC]            │  │
│  │                                                             │  │
│  │  Events:                                                    │  │
│  │    PolicyUpdated(contract, selector, oldPolicy, newPolicy)  │  │
│  │    DeploymentRestrictionChanged(restricted)                 │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Transfer Compliance Hook                                        │
│  (0x4200000000000000000000000000000000000032)                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Storage:                                                   │  │
│  │    mapping(address => bool) regulatedTokens                 │  │
│  │    mapping(address => TransferRule) tokenRules               │  │
│  │                                                             │  │
│  │  Functions:                                                 │  │
│  │    checkTransfer(token, from, to, amount) → bool [PUBLIC]   │  │
│  │    registerToken(token, rules) [TOKEN_ADMIN]                │  │
│  │    updateRules(token, rules) [TOKEN_ADMIN]                  │  │
│  │                                                             │  │
│  │  Transfer rules (for managed assets only):                  │  │
│  │    - Both sender and receiver must be KYC verified           │  │
│  │    - Transfer amount within daily/monthly limits             │  │
│  │    - Cross-jurisdiction transfer restrictions                │  │
│  │    - Sanctions screening (address blacklist)                 │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 1.4.2A 强制边界说明

为避免过度承诺，这里明确三类能力边界：

| 能力 | Phase 1 是否可全局强制 | 实现方式 |
|---|---|---|
| 地址是否允许发起交易 | **是** | RPC 网关 + Sequencer + L1 Bridge |
| 受管合约的函数级权限 | **是** | 业务合约/工厂主动查询 `PolicyRegistry` |
| 任意第三方 ERC-20/合约内部调用的统一拦截 | **否** | 需受管资产模板、受管工厂，或更高侵入执行层改造 |
| 任意 CREATE/CREATE2 的链级禁用 | **否，Phase 1 不做全局承诺** | 通过 Sequencer 对外部创建交易过滤 + 受管工厂模式约束 |

因此，本文将“合约部署权限”和“Transfer Hook”都收敛为**受管部署路径/受管资产路径**，这更符合 Mantle 最小侵入约束。

#### 1.4.3 Identity 数据结构

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Identity record stored in the Identity Registry Predeploy.
struct Identity {
    /// @dev Enterprise tenant identifier (e.g., "acme-corp")
    bytes32 tenantId;

    /// @dev KYC verification level (0 = none, 1 = basic, 2 = enhanced, 3 = institutional)
    uint8 kycLevel;

    /// @dev KYC expiry timestamp (0 = never expires, unix timestamp otherwise)
    uint64 kycExpiry;

    /// @dev Registration timestamp
    uint64 registeredAt;

    /// @dev Status: 0 = inactive, 1 = active, 2 = suspended, 3 = revoked
    uint8 status;

    /// @dev Additional metadata hash (IPFS CID or off-chain reference)
    bytes32 metadataHash;
}

/// @notice Policy configuration for a contract or function.
struct PolicyConfig {
    /// @dev Policy type: 0 = FORBIDDEN, 1 = ALL_REGISTERED, 2 = ROLE_REQUIRED,
    ///      3 = KYC_LEVEL_REQUIRED, 4 = CUSTOM_RULE
    uint8 policyType;

    /// @dev Required role (if policyType == 2)
    bytes32 requiredRole;

    /// @dev Required KYC level (if policyType == 3)
    uint8 requiredKycLevel;

    /// @dev Custom rule contract address (if policyType == 4)
    address customRuleContract;
}
```

#### 1.4.4 合约部署策略

参考 Mantle 已有的 Predeploy 实践（WHI-341 §7.3），使用 Arsia 升级交易模式部署：

1. **创世部署**（新链场景）：在 genesis 配置中预配置 Predeploy 合约代码和初始状态
2. **升级部署**（现有链场景）：通过 deposit transaction 注入，遵循 `arsia_upgrade_transactions.go` 的模式
3. **代理模式**：所有 Predeploy 使用 `TransparentUpgradeableProxy` 模式，允许后续通过 `DELEGATECALL` 升级逻辑合约

**Predeploy 地址分配**：

| 地址 | 合约 | 说明 |
|------|------|------|
| `0x4200000000000000000000000000000000000030` | IdentityRegistry | 身份注册表 |
| `0x4200000000000000000000000000000000000031` | PolicyRegistry | 策略注册表 |
| `0x4200000000000000000000000000000000000032` | TransferComplianceHook | 转账合规钩子 |
| `0x4200000000000000000000000000000000000033` | GovernanceExecutor | 治理执行器 / ProxyAdmin owner |

> **注意**：地址选择避开 Mantle 已有 Predeploy 范围（MNT 代币 `0xdEAD...1111`，L1Block、GasPriceOracle、OperatorFeeVault 在 `0x4250...` 范围）。

**预估工作量**：1-2 人月（Identity Registry），2-3 人月（含 Transfer Hook），1 名合约工程师

### 1.5 Layer 0: L1 Bridge 白名单

#### 1.5.1 设计目标

**封堵 L1→L2 强制交易旁路**——这是整个准入体系的关键安全基线。WHI-344 §1.2.2 明确指出：没有 L1 Bridge 白名单，所有 RPC/Sequencer 层准入控制都可被 L1 强制交易绕过，使整个体系形同虚设。

WHI-350 §2.4C 评分 (V=5, F=4, Score=20)——这是**最高价值**的准入改造项之一。

#### 1.5.2 实现方案

修改 `OptimismPortal.sol` L1 桥接合约，添加白名单检查。这里不直接依赖 L2 `IdentityRegistry` 做同步查询，因为 L1 deposit 的准入判断必须在 L1 本地完成；L2 身份注册表通过链下同步任务或治理流程把允许列表投影到 L1Allowlist：

```solidity
// packages/contracts-bedrock/src/L1/OptimismPortal2.sol (modified)

contract MantleEnterpriseOptimismPortal is OptimismPortal2 {

    /// @notice L1 侧的企业准入白名单合约地址
    IAllowlist public allowlist;

    /// @notice 是否启用企业准入模式
    bool public enterpriseMode;

    /// @notice 白名单修饰符
    modifier onlyAllowed(address _sender) {
        if (enterpriseMode) {
            require(
                allowlist.isAllowed(_sender),
                "MantleEnterprise: sender not in allowlist"
            );
        }
        _;
    }

    /// @notice 覆写 depositTransaction，添加白名单检查
    function depositTransaction(
        address _to,
        uint256 _value,
        uint64 _gasLimit,
        bool _isCreation,
        bytes memory _data
    )
        public
        payable
        override
        metered(_gasLimit)
        onlyAllowed(msg.sender)  // ★ 新增：白名单检查
    {
        super.depositTransaction(_to, _value, _gasLimit, _isCreation, _data);
    }

    /// @notice 设置白名单合约地址 (仅 admin)
    function setAllowlist(IAllowlist _allowlist) external onlyOwner {
        allowlist = _allowlist;
        emit AllowlistUpdated(address(_allowlist));
    }

    /// @notice 切换企业模式 (仅 admin)
    function setEnterpriseMode(bool _enabled) external onlyOwner {
        enterpriseMode = _enabled;
        emit EnterpriseModeChanged(_enabled);
    }
}

/// @notice L1 白名单接口
interface IAllowlist {
    function isAllowed(address account) external view returns (bool);
}
```

#### 1.5.3 L1 白名单合约

```solidity
// packages/contracts-bedrock/src/enterprise/L1Allowlist.sol

contract L1Allowlist is IAllowlist, Ownable2Step {

    mapping(address => bool) private _allowed;
    address[] private _allowedList;

    /// @notice 非白名单地址仅可执行 ETH/MNT 转账（参考 Prividium TransactionFilterer）
    bool public transferOnlyForNonAllowed;

    function isAllowed(address account) external view override returns (bool) {
        return _allowed[account];
    }

    function addToAllowlist(address[] calldata accounts) external onlyOwner {
        for (uint256 i = 0; i < accounts.length; i++) {
            if (!_allowed[accounts[i]]) {
                _allowed[accounts[i]] = true;
                _allowedList.push(accounts[i]);
                emit AddressAllowed(accounts[i]);
            }
        }
    }

    function removeFromAllowlist(address[] calldata accounts) external onlyOwner {
        for (uint256 i = 0; i < accounts.length; i++) {
            if (_allowed[accounts[i]]) {
                _allowed[accounts[i]] = false;
                emit AddressRemoved(accounts[i]);
            }
        }
    }
}
```

#### 1.5.4 L1/L2 状态同步模型

L1 Bridge 白名单与 L2 Identity Registry 的关系是“**双写治理，同步为辅**”，不是运行时跨链查询：

1. **权威来源**：企业管理员在管理平面中完成开户、KYC 通过、冻结/撤销等操作
2. **L2 写入**：管理平面调用 `IdentityRegistry` 更新链上身份状态，供 Sequencer 和业务合约查询
3. **L1 投影**：同一治理动作同时更新 `L1Allowlist`，保证 L1 deposit 判断不依赖跨链消息时延
4. **校验任务**：后台 reconciliation worker 周期性比对 L1Allowlist 与 L2 IdentityRegistry 的允许名单差异，并生成告警

这种做法的优点是：
- 不引入 L1→L2 同步读依赖
- deposit 准入判断稳定、简单、可审计
- 符合 WHI-350 对最小侵入和高可行性的约束

#### 1.5.5 安全设计

参考 Prividium 的 `PrividiumTransactionFilterer`（WHI-337 §3.4.3）和 Tempo 的 ZonePortal 准入检查（WHI-340 §3.5）：

1. **非白名单降级模式**：非白名单地址仅可执行 ETH/MNT 简单转账（value transfer only），不可调用合约函数或部署合约
2. **紧急开关**：`enterpriseMode` 布尔值可由 admin 快速切换，在紧急情况下恢复为无许可模式
3. **多签 admin**：L1 合约的 owner 为多签钱包（Gnosis Safe），防止单点故障

**预估工作量**：2-3 周（含安全审计），1 名合约工程师

### 1.6 Layer 4: 数据层准入

#### 1.6.1 RPC 查询权限控制

在 RPC 认证网关层实现基于角色的数据过滤。这里需要明确边界：**Phase 1 只能保护企业托管 RPC 端点上的“谁能查什么”，不能让已经发布到公共 L1/L2 数据可被真正隐藏**。因此数据层准入的 Phase 1 价值在于企业接入治理和最小暴露面，而不是链级保密。

| 角色 | 可查询数据 | 限制 |
|------|----------|------|
| **Admin** | 全部链上数据 | 无限制 |
| **Auditor** | 全部交易数据 + 审计日志 | 只读，不可提交交易 |
| **Operator** | 自有地址交易 + 受管合约状态 | 仅限自有租户映射地址与受管资源 |
| **Viewer** | 公开合约状态 | 不可查看交易详情 |

实现方式：在 RPC 网关的认证服务中，根据 JWT 中的 `roles[]` 声明，对以下 RPC 方法进行过滤：

- `eth_getTransactionByHash` → Auditor+ 可访问
- `eth_getLogs` → 根据角色过滤 topic 可见性
- `debug_*` → Admin only
- `eth_getBalance`, `eth_call` → 仅对受管地址簿、受管合约和企业 RPC 视图做租户过滤

#### 1.6.2 Event/Log 可见性控制

Phase 1 通过 RPC 层过滤实现，Phase 2 与隐私层（WHI-351）联动实现链级隐私：

- **Phase 1**：RPC 网关在企业专用端点上，对受管合约和审计主题做方法级、地址级和 topic 级过滤
- **Phase 2**：与 Validium 模式协同——敏感 event/log 仅存储在私有 DA 后端，不在公开节点上可见

#### 1.6.3 多租户边界

WHI-350 要求多租户支持，但 Phase 1 不把“每企业独立执行环境”作为当前交付承诺。本文的多租户边界定义如下：

| 能力 | Phase 1 交付 | 非 Phase 1 能力 |
|---|---|---|
| 身份隔离 | 租户 ID、地址绑定、角色作用域 | — |
| 配置隔离 | per-tenant 速率限制、规则覆盖、审计分区 | — |
| 数据隔离 | 企业 RPC 端点对受管资源的访问控制 | 公共链数据本身不可隐藏 |
| 执行隔离 | 不提供独立状态机，只做策略隔离 | 需 Zone / 子链 / 隐私执行域 |

### 1.7 Network Layer: P2P 网络准入

#### 1.7.1 op-geth P2P 白名单

在 op-geth 的 P2P 层实现节点准入：

```go
// op-geth/p2p/enterprise_whitelist.go

package p2p

import (
    "github.com/ethereum/go-ethereum/p2p/enode"
)

// EnterpriseNodeWhitelist implements P2P node admission control.
type EnterpriseNodeWhitelist struct {
    allowedNodes map[enode.ID]bool
    enabled      bool
}

// IsAllowed checks if a node is authorized to connect.
func (w *EnterpriseNodeWhitelist) IsAllowed(node *enode.Node) bool {
    if !w.enabled {
        return true
    }
    return w.allowedNodes[node.ID()]
}
```

配置方式：
- 静态配置文件：`enterprise.allowed_nodes` 列表
- 动态 API：`admin_addAllowedNode` / `admin_removeAllowedNode` RPC 方法

> **注意**：P2P 白名单是防御层之一，但不是唯一依赖——即使 P2P 层被绕过，Sequencer 策略引擎和 Predeploy 策略注册表仍然生效。

---

## 第二章：身份管理系统设计

### 2.1 身份模型

#### 2.1.1 设计原则

WHI-350 §1.2.3 指出身份管理是准入控制的**基础**——需要先知道"谁"，才能控制"谁能做什么"。推荐 Phase 1 采用"地址白名单 + SSO 联邦"双轨模型。

```
                    Enterprise Identity Model
┌───────────────────────────────────────────────────────────┐
│                                                            │
│  Off-Chain Layer (企业 IAM)                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ Enterprise A│  │ Enterprise B│  │ Enterprise C│  │  │
│  │  │ (Okta)      │  │ (Azure AD)  │  │ (Google WS) │  │  │
│  │  │ Users:      │  │ Users:      │  │ Users:      │  │  │
│  │  │  - Alice    │  │  - Charlie  │  │  - Eve      │  │  │
│  │  │  - Bob      │  │  - David    │  │  - Frank    │  │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │  │
│  │         │ OIDC           │ OIDC           │ OIDC     │  │
│  │         ▼                ▼                ▼          │  │
│  │  ┌───────────────────────────────────────────────┐   │  │
│  │  │  RPC Authentication Gateway                    │   │  │
│  │  │  JWT: { sub, roles[], tenant_id, wallet_addrs }│   │  │
│  │  └──────────────────────┬────────────────────────┘   │  │
│  └─────────────────────────│────────────────────────────┘  │
│                            │                               │
│  On-Chain Layer (身份注册表)│                                │
│  ┌─────────────────────────▼────────────────────────────┐  │
│  │  Identity Registry Predeploy (0x4200...0030)          │  │
│  │                                                       │  │
│  │  Tenant: "enterprise-a"                               │  │
│  │  ┌───────────────────────────────────────────────┐   │  │
│  │  │ 0xAlice1 → { kycLevel: 2, role: TRADER }     │   │  │
│  │  │ 0xAlice2 → { kycLevel: 2, role: TREASURY }   │   │  │
│  │  │ 0xBob1   → { kycLevel: 1, role: VIEWER }     │   │  │
│  │  └───────────────────────────────────────────────┘   │  │
│  │                                                       │  │
│  │  Tenant: "enterprise-b"                               │  │
│  │  ┌───────────────────────────────────────────────┐   │  │
│  │  │ 0xCharlie → { kycLevel: 3, role: ADMIN }     │   │  │
│  │  │ 0xDavid   → { kycLevel: 2, role: OPERATOR }  │   │  │
│  │  └───────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

#### 2.1.2 身份生命周期

```
┌──────────┐    ┌────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Register │───►│  Verify    │───►│  Active  │───►│ Suspend  │───►│  Revoke  │
│          │    │  (KYC)     │    │          │    │          │    │          │
└──────────┘    └────────────┘    └──────────┘    └──────────┘    └──────────┘
     │                                  │              │              │
     │                                  │              │              │
     ▼                                  ▼              ▼              ▼
  Admin 通过                      正常运营          临时冻结        永久撤销
  Admin API                       可提交交易        不可提交交易    不可提交交易
  创建用户记录                     可查询数据        可查询数据      不可查询数据
  + 关联钱包地址                   角色权限生效      角色权限暂停    角色权限移除
```

| 阶段 | 触发条件 | 链上操作 | 链下操作 |
|------|---------|---------|---------|
| **Register** | Admin 通过 Admin API 创建用户 | — | 创建用户记录，关联钱包地址 |
| **Verify (KYC)** | KYC Provider 回调验证通过 | `IdentityRegistry.registerAddress(addr, kycLevel, expiry)` | 更新用户 KYC 状态 |
| **Active** | 注册+验证完成 | — | JWT 中包含有效角色声明 |
| **Suspend** | Admin 操作 / 风控触发 | `IdentityRegistry.suspendAddress(addr)` | 标记用户为 suspended，JWT 刷新时不再包含角色 |
| **Revoke** | Admin 操作 / KYC 过期 | `IdentityRegistry.revokeAddress(addr)` | 删除用户关联，撤销所有 JWT |

### 2.2 企业 IAM 集成

#### 2.2.1 SSO 集成方案

采用标准 OIDC 协议，支持主流企业 IdP：

| IdP | 协议 | 配置方式 |
|-----|------|---------|
| **Okta** | OIDC (Authorization Code + PKCE) | Okta Developer Console 创建 Application |
| **Azure AD** | OIDC (Microsoft Identity Platform) | Azure Portal App Registration |
| **Google Workspace** | OIDC (Google Identity) | Google Cloud Console OAuth2 Client |
| **Generic SAML** | SAML 2.0 → OIDC Bridge | 通过 Keycloak/Auth0 作为 SAML-to-OIDC Bridge |

#### 2.2.2 Token → 交易签名转换流程

```
┌──────────┐    ┌───────────────┐    ┌──────────────┐    ┌──────────────┐
│ User     │    │ Enterprise    │    │ RPC Gateway  │    │ Mantle L2    │
│ (Browser)│    │ IdP (Okta)    │    │              │    │              │
└────┬─────┘    └───────┬───────┘    └──────┬───────┘    └──────┬───────┘
     │                  │                   │                   │
     │ 1. Login via SSO │                   │                   │
     │─────────────────►│                   │                   │
     │                  │                   │                   │
     │ 2. OIDC Token    │                   │                   │
     │◄─────────────────│                   │                   │
     │ (id_token +      │                   │                   │
     │  access_token)   │                   │                   │
     │                  │                   │                   │
     │ 3. Request Session Token             │                   │
     │─────────────────────────────────────►│                   │
     │ (access_token + wallet_address)      │                   │
     │                  │                   │                   │
     │                  │  4. Verify token + │                   │
     │                  │     Check wallet   │                   │
     │                  │     binding        │                   │
     │                  │                   │                   │
     │ 5. Session Token │                   │                   │
     │◄─────────────────────────────────────│                   │
     │ (short-lived, 15min TTL)             │                   │
     │                  │                   │                   │
     │ 6. Sign TX locally (private key)     │                   │
     │ 7. Submit TX with session token      │                   │
     │─────────────────────────────────────►│                   │
     │                  │                   │ 8. Forward TX     │
     │                  │                   │──────────────────►│
     │                  │                   │                   │
     │                  │                   │ 9. TX Receipt     │
     │                  │                   │◄──────────────────│
     │ 10. TX Receipt   │                   │                   │
     │◄─────────────────────────────────────│                   │
```

**关键设计决策**：

1. **私钥始终在客户端**——RPC 网关不触碰私钥，仅验证身份和权限。交易签名在用户设备（浏览器钱包/HSM）上完成。
2. **Session token 不是签名密钥**——Session token 仅用于 RPC 认证，不参与交易签名。即使 session token 泄露，攻击者没有私钥也无法提交交易。
3. **钱包地址绑定**——每个企业用户的钱包地址在注册时绑定到 SSO 身份。RPC 网关验证 `tx.from` 匹配 session token 中的 `wallet_address`。

### 2.3 KYC 集成

#### 2.3.1 链上 KYC 注册表

KYC 状态存储在 Identity Registry Predeploy 中，作为身份记录的一部分：

```solidity
// KYC Levels
uint8 constant KYC_NONE = 0;         // 未验证
uint8 constant KYC_BASIC = 1;        // 基础 KYC (个人身份验证)
uint8 constant KYC_ENHANCED = 2;     // 增强 KYC (收入/资产证明)
uint8 constant KYC_INSTITUTIONAL = 3; // 机构 KYC (企业注册文件+UBO)
```

#### 2.3.2 KYC Provider 集成接口

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ KYC Provider     │     │ KYC Oracle       │     │ Identity Registry│
│ (Jumio/Onfido/   │────►│ Service          │────►│ Predeploy        │
│  Sumsub 等)      │     │ (off-chain)      │     │ (on-chain)       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
     Webhook callback    Signed TX to update       kycLevel + expiry
     with KYC result     on-chain KYC status       stored on-chain
```

**KYC Oracle Service**：
- 接收 KYC Provider 的 webhook 回调
- 验证回调签名的真实性
- 将 KYC 结果转换为链上交易（调用 `IdentityRegistry.registerAddress()`）
- 使用 HSM 签名交易（复用 Mantle 已有的 GCP KMS 集成，WHI-341 §2.5）

#### 2.3.3 KYC 状态表示

选择 **Registry 合约模式**而非 Soul-Bound Token (SBT)：

| 方案 | 优势 | 劣势 | 推荐 |
|------|------|------|------|
| **Registry 合约** | 查询高效 (`isKYCVerified()` 单次 SLOAD)；Admin 可直接修改；与策略引擎原生集成 | 不可转移（即 SBT 本质）；集中式管理 | **推荐** |
| **Soul-Bound Token** | 符合 ERC-5192 标准；可展示在钱包中；社区生态兼容 | 查询需要 `balanceOf()` + 额外校验；Admin 操作需要 burn/mint | 不推荐 |

选择 Registry 的理由：
1. 准入检查在每笔交易的热路径上，SLOAD 比 ERC-721 `balanceOf()` 更高效
2. Admin 操作（suspend/revoke）在 Registry 模式下是简单的状态更新，无需 token burn
3. Identity Registry 已经作为 Predeploy 存在，KYC 状态是其自然属性

---

## 第三章：治理框架设计

### 3.1 角色层级

```
┌─────────────────────────────────────────────────────────────────┐
│  Governance Role Hierarchy                                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SUPER_ADMIN (多签钱包, 3/5 阈值)                         │   │
│  │  - 升级 Predeploy 合约逻辑                                 │   │
│  │  - 修改 L1 Bridge 白名单合约                               │   │
│  │  - 切换 enterpriseMode 开关                                │   │
│  │  - 添加/移除 ADMIN 角色                                    │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  ADMIN (企业管理员, 每租户独立)                              │   │
│  │  - 注册/撤销用户地址                                        │   │
│  │  - 授予/撤销角色                                            │   │
│  │  - 修改租户级策略配置                                        │   │
│  │  - 查看审计日志                                              │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  POLICY_ADMIN (策略管理员)                                  │   │
│  │  - 更新合约级/函数级策略                                     │   │
│  │  - 注册/更新 Transfer Compliance 规则                       │   │
│  │  - 管理受监管 token 列表                                    │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  OPERATOR / TRADER / VIEWER (业务角色)                      │   │
│  │  - 按角色权限执行业务操作                                    │   │
│  │  - 权限由策略注册表定义                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 多签治理

关键操作需要多方签名，防止单点权限滥用：

| 操作 | 签名阈值 | 时间锁 | 说明 |
|------|---------|--------|------|
| 升级 Predeploy 合约 | 3/5 SUPER_ADMIN | 48h | 合约逻辑变更影响全局 |
| 修改 L1 Bridge 白名单合约 | 3/5 SUPER_ADMIN | 24h | L1 安全边界 |
| 切换 enterpriseMode | 2/5 SUPER_ADMIN | 0 (紧急) | 紧急恢复开关 |
| 批量注册地址 (>100) | 2/3 ADMIN | 6h | 防止误操作 |
| 单个地址注册/撤销 | 1/1 ADMIN | 0 | 日常操作 |
| 策略更新 | 2/3 POLICY_ADMIN | 6h | 策略变更需要审批 |

**实现方式**：Phase 1 更推荐使用 **Gnosis Safe / Safe module + TimelockController** 组合，而不是把完整 Governor 逻辑塞进预编排治理路径。原因是：

1. Safe 更符合企业运维习惯，审批流和签名人管理成熟
2. 准入治理操作偏运维控制面，不需要代币投票式 Governor 模型
3. 可以把治理逻辑保持在独立合约/模块中，减少对 Predeploy 本体的耦合

因此 `0x4200...0033` 更准确的定位是 **GovernanceExecutor / ProxyAdminOwner**，实际可由 L2 Safe 或 L1 Safe 控制。

### 3.3 紧急操作

#### 3.3.1 账户冻结流程

```
紧急冻结 (目标: < 30秒生效)

1. Admin 调用 IdentityRegistry.suspendAddress(target)
   → 链上状态即时更新 (status = SUSPENDED)
   → 事件 AddressSuspended(target, reason)

2. Sequencer 策略引擎接收事件
   → 缓存立即失效 (event-driven invalidation)
   → 后续交易被 AdmissionFilter 拒绝

3. RPC 网关接收事件
   → 相关 JWT session 标记失效
   → 后续 RPC 请求返回 403

生效时间: ~区块时间 (2秒 Mantle 出块) + 事件传播延迟 (< 1秒)
```

#### 3.3.2 紧急关停流程

```
全链紧急关停 (灾难恢复场景)

1. SUPER_ADMIN 多签 (2/5 阈值, 无时间锁)
   → 调用 PolicyRegistry.setGlobalPause(true)
   → Sequencer/RPC 对新交易统一拒绝；受管合约侧进入 pause 模式

2. 或 L1 层操作
   → 调用 OptimismPortal.setEnterpriseMode(false)
   → 恢复为无许可模式（仅在“保资金可达”优先于“准入约束”时使用）
```

### 3.4 升级机制

#### 3.4.1 策略热更新

策略更新通过链上交易执行，无需节点重启：

```
策略更新流程:

1. POLICY_ADMIN 通过 Safe module / GovernanceExecutor 提交策略更新 proposal
   → GovernanceExecutor.propose(PolicyRegistry.setContractPolicy(...))

2. 多签审批 (2/3 POLICY_ADMIN)
   → GovernanceExecutor.approve(proposalId)

3. 时间锁执行 (6h 后)
   → TimelockController.execute(proposalId)
   → PolicyRegistry 状态更新

4. Sequencer 策略引擎自动同步
   → 事件驱动缓存刷新
   → 新策略在下一个区块生效
```

#### 3.4.2 合约升级

Predeploy 合约通过 Transparent Proxy 模式升级：

```
合约升级流程 (SUPER_ADMIN 3/5 多签 + 48h 时间锁):

1. 部署新逻辑合约 (implementation)
2. SUPER_ADMIN 提交升级 proposal
3. 多签审批 (3/5)
4. 48h 时间锁等待期 (社区可审查)
5. TimelockController 执行 proxy.upgradeTo(newImpl)
6. 新逻辑生效, 存储状态保留
```

---

## 第四章：配置模型

### 4.1 完整配置结构

```yaml
# mantle-enterprise-config.yaml
# Mantle Enterprise Access Control Configuration
# Version: 1.0.0

enterprise:
  # 全局开关
  enabled: true
  mode: "permissioned"  # permissioned | semi-permissioned | open

  # ============================================================
  # Layer 0: L1 Bridge 白名单
  # ============================================================
  l1_bridge:
    enterprise_mode: true
    allowlist_contract: "0x..."  # L1 Allowlist 合约地址
    non_allowed_transfer_only: true  # 非白名单仅可转账
    admin_multisig: "0x..."  # L1 Gnosis Safe 地址

  # ============================================================
  # Layer 1: RPC 认证网关
  # ============================================================
  rpc_gateway:
    listen_address: "0.0.0.0:8545"
    upstream_rpc: "http://op-geth:8545"  # 内部 op-geth RPC

    authentication:
      providers:
        - name: "okta-enterprise-a"
          type: "oidc"
          issuer: "https://enterprise-a.okta.com/oauth2/default"
          audience: "mantle-enterprise"
          jwks_uri: "https://enterprise-a.okta.com/oauth2/default/v1/keys"
          tenant_id: "enterprise-a"

        - name: "azure-ad-enterprise-b"
          type: "oidc"
          issuer: "https://login.microsoftonline.com/{tenant}/v2.0"
          audience: "api://mantle-enterprise"
          tenant_id: "enterprise-b"

    session:
      token_ttl: "15m"
      max_sessions_per_user: 5
      wallet_binding: true  # 强制 wallet 地址绑定

    rate_limiting:
      global_rps: 10000
      per_tenant_rps: 2000
      per_user_rps: 100
      burst_multiplier: 3

    audit:
      enabled: true
      sink: "kafka://audit-cluster:9092/mantle-audit-events"
      include_tx_data: false  # 不记录交易原始数据 (隐私)
      include_request_metadata: true

  # ============================================================
  # Layer 2: Sequencer 策略引擎
  # ============================================================
  sequencer_policy:
    enabled: true

    admission_filter:
      mode: "whitelist"  # whitelist | blacklist | registry
      # whitelist 模式: 仅允许已注册地址
      # blacklist 模式: 阻止特定地址
      # registry 模式: 查询链上 Identity Registry

      # 静态白名单 (用于快速启动, 生产环境应使用 registry 模式)
      static_whitelist:
        - "0xAdmin1..."
        - "0xAdmin2..."

      # 链上注册表查询 (推荐)
      registry:
        contract: "0x4200000000000000000000000000000000000030"
        cache_size: 100000
        cache_ttl: "5m"
        event_driven_invalidation: true

    policy_rules:
      # 合约部署限制
      deployment:
        mode: "admin_only"  # admin_only | registered | open
        allowed_deployers:
          - role: "CONTRACT_DEPLOYER"
        enforcement_scope: "sequencer_external_create_only"  # 仅约束外部提交的 create/create2 交易

      # 交易金额限制
      value_limits:
        enabled: true
        max_single_tx: "1000000000000000000000"  # 1000 MNT
        max_daily_per_address: "10000000000000000000000"  # 10000 MNT

      # 函数调用限制 (可选)
      function_restrictions:
        enabled: false  # Phase 1 不启用, Phase 2 开启
        # 由 Policy Registry Predeploy 管理

    compliance:
      sanctions_check:
        enabled: false  # Phase 1 使用白名单模式, 无需实时制裁检查
        provider: "chainalysis"  # chainalysis | elliptic | custom
        api_endpoint: "https://api.chainalysis.com/..."
        cache_ttl: "24h"

      audit_emission:
        enabled: true
        sink: "kafka://audit-cluster:9092/sequencer-compliance-events"

  # ============================================================
  # Layer 3: Predeploy 合约配置 (on-chain, 仅列出初始参数)
  # ============================================================
  predeploy:
    identity_registry:
      address: "0x4200000000000000000000000000000000000030"
      initial_admins:
        - "0xSuperAdmin1..."
        - "0xSuperAdmin2..."

    policy_registry:
      address: "0x4200000000000000000000000000000000000031"
      default_contract_policy: "ALL_REGISTERED"  # 默认: 所有已注册用户可调用
      deployment_restricted: true  # 供 Sequencer/受管工厂查询，不代表 EVM 全局禁 deploy

    transfer_compliance:
      address: "0x4200000000000000000000000000000000000032"
      enabled: false  # Phase 2 启用

    governance:
      address: "0x4200000000000000000000000000000000000033"
      super_admin_threshold: 3  # 3/5 多签
      timelock_delay: "48h"

  # ============================================================
  # Layer 4: 数据层准入
  # ============================================================
  data_access:
    rpc_filtering:
      enabled: true
      roles:
        admin:
          allowed_methods: ["*"]
        auditor:
          allowed_methods:
            - "eth_getTransaction*"
            - "eth_getBlock*"
            - "eth_getLogs"
            - "eth_getBalance"
            - "eth_call"
          read_only: true
        operator:
          allowed_methods:
            - "eth_sendRawTransaction"
            - "eth_getTransaction*"
            - "eth_getBalance"
            - "eth_call"
            - "eth_estimateGas"
          tenant_isolated: true
        viewer:
          allowed_methods:
            - "eth_call"
            - "eth_getBalance"
            - "eth_blockNumber"
          read_only: true

  # ============================================================
  # Network Layer: P2P 准入
  # ============================================================
  network:
    p2p_whitelist:
      enabled: true
      allowed_nodes:
        - "enode://abc123...@10.0.1.1:30303"
        - "enode://def456...@10.0.1.2:30303"
      dynamic_management: true  # 允许通过 admin RPC 动态管理
```

### 4.2 多租户配置覆盖

支持租户级配置覆盖，允许不同企业客户有不同的策略：

```yaml
# tenant-overrides/enterprise-a.yaml
tenant_id: "enterprise-a"
overrides:
  sequencer_policy:
    policy_rules:
      value_limits:
        max_single_tx: "5000000000000000000000"  # 5000 MNT (更高限额)
      deployment:
        mode: "registered"  # 允许所有已注册用户发起外部部署交易

  rpc_gateway:
    rate_limiting:
      per_tenant_rps: 5000  # 更高 QPS 限额
```

### 4.3 配置管理 API

```
POST   /api/v1/config/tenants/{tenant_id}       # 创建/更新租户配置
GET    /api/v1/config/tenants/{tenant_id}       # 获取租户配置
DELETE /api/v1/config/tenants/{tenant_id}       # 删除租户配置
POST   /api/v1/config/reload                     # 热重载全局配置
GET    /api/v1/config/validate                   # 配置校验
```

---

## 第五章：代码改动点清单

### 5.1 改动总览

| # | 改动点 | 代码位置 | 改动类型 | 侵入性 | Phase | 预估工作量 |
|---|--------|---------|---------|--------|-------|-----------|
| 1 | RPC 认证网关 | 新增独立服务 | **新增** | 零（中间件） | 1 | 2-4 周 |
| 2 | Sequencer 策略引擎 | `op-node/rollup/sequencing/sequencer.go` | **扩展** | 低 | 1 | 1-2 月 |
| 3 | 交易池策略过滤 | `op-geth/core/txpool/` | **扩展** | 低 | 1 | 2-3 周 |
| 4 | L1 Bridge 白名单 | `OptimismPortal.sol` (L1 合约) | **修改** | 中 | 1 | 2-3 周 |
| 5 | Identity Registry Predeploy | 新增 Predeploy 合约 | **新增** | 低 | 1 | 1-2 月 |
| 6 | Policy Registry Predeploy | 新增 Predeploy 合约 | **新增** | 低 | 1 | 1 月 |
| 7 | Governance Executor / Safe 集成 | 新增治理执行器或 Safe 模块 | **新增** | 低 | 1 | 2 周 |
| 8 | 管理面板 (Admin Dashboard) | 新增 Web 应用 | **新增** | 零 | 1 | 1 月 |
| 9 | P2P 节点白名单 | `op-geth/p2p/` | **扩展** | 低 | 1 | 1 周 |
| 10 | Transfer Compliance Hook（受管资产） | 新增 Predeploy 合约 + 受管资产模板 | **新增** | 低 | 2 | 2-3 月 |
| 11 | KYC Oracle Service | 新增独立服务 | **新增** | 零 | 2 | 1 月 |

### 5.2 逐项详细说明

#### 5.2.1 Sequencer 策略引擎 (#2)

**修改文件**：

```
op-node/rollup/sequencing/sequencer.go
├── 新增: AdmissionFilter 接口调用点
│   - 在 StartBuildingBlock() 前添加 filter.Check(tx) 调用
│   - 在交易排序阶段添加 PolicyEvaluator.Evaluate(tx) 调用
│   - 在区块构建完成后添加 AuditEmitter.EmitBlockEvent() 调用
│   - 对 create/create2 型外部交易执行 deployment policy 检查
│
├── 新增接口注入:
│   - sequencer 构造函数增加 AdmissionFilter, PolicyEvaluator, AuditEmitter 参数
│   - 配置通过 rollup.Config 的 EnterpriseConfig 字段传入
│
op-node/rollup/sequencing/iface.go
├── 不修改现有接口
├── 新增: enterprise 子包
│
enterprise/                          ← 独立目录, 最小化上游分歧
├── admission/
│   ├── admission.go                 # AdmissionFilter 接口定义
│   ├── whitelist_filter.go          # 白名单过滤实现
│   ├── registry_filter.go           # 链上注册表过滤实现
│   └── cache.go                     # LRU 缓存实现
├── policy/
│   ├── evaluator.go                 # PolicyEvaluator 实现
│   ├── rules.go                     # 规则定义 (YAML → Go struct)
│   └── config.go                    # 策略配置加载
├── compliance/
│   ├── checker.go                   # ComplianceChecker 实现
│   └── sanctions.go                 # 制裁名单检查 (Phase 2)
├── audit/
│   ├── emitter.go                   # AuditEmitter 实现
│   └── kafka_sink.go               # Kafka 事件发送
└── config.go                        # EnterpriseConfig 定义
```

**关键设计**：
- 企业改造代码放在独立 `enterprise/` 目录，不修改 OP Stack 核心接口
- 通过 Go interface 与核心代码交互，上游合并时只需更新接口适配层
- `AdmissionFilter` 默认实现为 `NoopFilter`（Accept all），不影响非企业部署

#### 5.2.2 交易池策略过滤 (#3)

**修改文件**：

```
op-geth/core/txpool/legacypool/legacypool.go
├── 在 validateTx() 中添加: enterprise filter check
│   if pool.enterpriseFilter != nil {
│       if !pool.enterpriseFilter.IsAllowed(tx.From()) {
│           return ErrEnterpriseNotAllowed
│       }
│   }
│
op-geth/core/txpool/txpool.go
├── 新增: EnterpriseFilter 字段
├── 构造函数增加 optional EnterpriseFilter 参数
```

**修改量**：~50 行代码修改 + enterprise filter 包（~200 行新增）

> **说明**：TxPool/Sequencer 能稳定拦截的是“外部提交交易”。合约内部再创建合约的路径不在 Phase 1 的全局约束范围，需通过受管工厂模式补足。

#### 5.2.3 L1 Bridge 白名单 (#4)

**修改文件**：

```
packages/contracts-bedrock/
├── src/L1/
│   └── MantleEnterpriseOptimismPortal.sol  ← 新增 (继承 OptimismPortal2)
├── src/enterprise/
│   ├── L1Allowlist.sol                      ← 新增
│   └── IAllowlist.sol                       ← 新增
└── test/enterprise/
    ├── L1Allowlist.t.sol                    ← 新增
    └── MantleEnterpriseOptimismPortal.t.sol ← 新增
```

#### 5.2.4 Predeploy 合约 (#5, #6, #7)

**新增文件**：

```
packages/contracts-bedrock/src/enterprise/predeploy/
├── IdentityRegistry.sol          # 身份注册表
├── PolicyRegistry.sol            # 策略注册表
├── TransferComplianceHook.sol    # 转账合规钩子 (Phase 2, 受管资产)
├── GovernanceExecutor.sol        # 治理执行器 / ProxyAdmin owner
├── interfaces/
│   ├── IIdentityRegistry.sol
│   ├── IPolicyRegistry.sol
│   └── ITransferComplianceHook.sol
└── libraries/
    ├── EnterpriseRoles.sol       # 角色常量
    └── EnterpriseErrors.sol      # 自定义 error
```

**创世/升级部署**：

```go
// op-node/rollup/derive/enterprise_upgrade_transactions.go (新增)
// 参考 arsia_upgrade_transactions.go 模式

func EnterpriseUpgradeDepositTxs() ([]hexutil.Bytes, error) {
    // 1. Deploy IdentityRegistry implementation
    // 2. Deploy IdentityRegistry proxy at 0x4200...0030
    // 3. Deploy PolicyRegistry implementation
    // 4. Deploy PolicyRegistry proxy at 0x4200...0031
    // 5. Deploy GovernanceExecutor proxy at 0x4200...0033
    // 6. Initialize contracts with admin addresses
}
```

### 5.3 侵入性评估

| 侵入性等级 | 改动项 | 上游合并影响 |
|-----------|--------|-------------|
| **零侵入** | #1 RPC 网关, #8 管理面板, #11 KYC Oracle | 独立服务，不影响上游合并 |
| **低侵入** | #2 Sequencer 策略 (interface injection), #3 交易池 (filter hook), #5-7 Predeploy/治理执行器, #9 P2P, #10 Transfer Hook | 通过 interface 注入或独立目录，上游合并冲突极低 |
| **中侵入** | #4 L1 Bridge | 修改 OptimismPortal 合约，需要随上游桥接合约升级同步 |

**分叉预算评估**（WHI-350 R2 风险缓解）：
- 核心代码修改行数：~100 行（Sequencer 注入点 + 交易池 hook）
- 新增代码行数：~5000 行（enterprise/ 目录 + Predeploy 合约）
- 合约修改行数：~200 行（L1 Bridge）

---

## 第六章：实施计划与里程碑

### 6.1 Phase 1 并行执行计划

```
月份:    1         2         3         4
        ┌─────────┐
  #1    │ RPC 认证  │
  RPC   │ 网关     │
        └─────────┘
        ┌──────────────────────┐
  #2    │ Sequencer 策略引擎    │
  Seq   │ (接口定义+白名单实现) │
        └──────────────────────┘
        ┌──────────────┐
  #3    │ 交易池过滤   │
  TxP   │              │
        └──────────────┘
        ┌──────────────┐
  #4    │ L1 Bridge    │
  L1    │ 白名单       │
        └──────────────┘
        ┌──────────────────────┐
  #5    │ Identity Registry    │
  IDR   │ Predeploy            │
        └──────────────────────┘
             ┌─────────────────┐
  #6         │ Policy Registry  │
  POL        │ Predeploy        │
             └─────────────────┘
                  ┌────────────┐
  #7              │ Governance │
  GOV             │ Executor   │
                  └────────────┘
                       ┌──────────┐
  #8                   │ Admin    │
  UI                   │ 面板     │
                       └──────────┘
        ┌────┐
  #9    │ P2P│
  P2P   │    │
        └────┘
```

### 6.2 验收标准

| # | 验收项 | 测试方法 |
|---|--------|---------|
| AC-1 | 未认证用户无法通过 RPC 提交交易 | 无 JWT 的 `eth_sendRawTransaction` 返回 401 |
| AC-2 | 未在白名单的地址无法通过 L1 Bridge 发起强制交易 | L1 `depositTransaction()` 对非白名单地址 revert |
| AC-3 | Sequencer 拒绝不在注册表中的地址提交的交易 | 已签名但未注册的交易不被打包 |
| AC-4 | Identity Registry 正确记录和查询身份信息 | `isRegistered()`, `isKYCVerified()`, `hasRole()` 返回正确值 |
| AC-5 | 策略更新通过多签治理流程执行 | 未满足阈值的策略更新 proposal 不执行 |
| AC-6 | 审计日志完整记录所有准入决策 | Kafka 消费者接收到所有 accept/reject 事件 |
| AC-7 | EVM 兼容性测试全部通过 | 以太坊官方测试套件 + Mantle 兼容性测试通过 |
| AC-8 | 性能退化 < 20% | TPS 基准测试结果不低于改造前的 80% |
| AC-9 | 合约部署限制仅作用于外部部署交易且行为可解释 | 外部 CREATE 交易被拒绝；文档与实现不声称拦截合约内部 CREATE2 |
| AC-10 | 多租户访问隔离仅针对企业 RPC 与受管资源生效 | 租户 A 无法经企业 RPC 查询租户 B 的受管对象；公共链数据不作隐藏承诺 |

---

## 数据来源

本设计方案全部结论均来源于以下文件：

| 来源编号 | 文件 | 主要贡献 |
|---------|------|---------|
| WHI-341 | `m1-research/mantle/mantle-v2-architecture-baseline.md` | Mantle V2 架构基线：Sequencer 代码位置、Predeploy 实践、Engine API 边界、HSM 集成、代码修改点清单 |
| WHI-344 | `m2-comparison/access-control/WHI-344-access-control-comparison.md` | 五层准入模型、L1 强制交易风险分析、Predeploy vs Precompile 建议、三层纵深防御推荐 |
| WHI-337 | `m1-research/prividium/WHI-337-prividium-official-docs-research.md` | Proxy RPC 三步验证、SSO/OIDC 集成、RBAC 六种权限类型、PrividiumTransactionFilterer |
| WHI-340 | `m1-research/tempo-zones/WHI-340-tempo-code-analysis.md` | TIP-403 Policy Registry、AccountKeychain、Zone 认证 RPC、事件驱动策略同步 |
| WHI-350 | `m3-design/gap-analysis/WHI-350-gap-analysis.md` | Gap 分析矩阵、切入点优先级、三层纵深方案推荐、风险评估、Phase 1 工作量估算 |

---

*本设计方案基于 2026 年 5 月 7 日的 M1 基线分析、M2 横向对比和 M3 Gap 分析成果编制。所有设计决策均可追溯至具体来源文件和代码位置。*
