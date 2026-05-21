# Mantle 企业级合规框架与部署运维架构设计

> **Issue**: WHI-353 | **Milestone**: M3: Mantle 企业级改造可行性设计
> **Date**: 2026-05-07
> **Dependencies**: WHI-350 (Gap 分析), WHI-341 (Mantle 架构基线)
> **Input Sources**: WHI-346 (合规对比), WHI-340 (Tempo TIP-403), WHI-338 (Prividium 架构)

---

## 执行摘要

本文档为 Mantle 企业版设计合规与审计框架（Part A）和部署运维架构（Part B），共同定义 Mantle Enterprise 的"可运营性"。

**核心设计原则**：

1. **Sequencer 即合规控制点**：Mantle 中心化 Sequencer 的完全交易可见性是未被开发的天然合规资产（WHI-346 §2.2.5），本设计将其转化为四层合规栈的核心执行引擎。

2. **三阶段渐进式合规**：Phase 1 中间件 MVP（2-3 人月）→ Phase 2 合约层增强（3-4 人月）→ Phase 3 协议层可选升级（6+ 人月），与 WHI-350 改造路径完全对齐。

3. **最小侵入原则**：优先使用 Predeploy 合约和中间件层方案，最小化对 OP Stack 核心协议的修改。Mantle 已有 6 次自定义硬分叉，每次企业改造都增加分叉维护负担（WHI-350 §5.2 R2）。

4. **监管框架感知**：设计参考 MiCA、GDPR、SEC/CFTC、MAS、Basel III/IV 等主要监管框架的具体要求（WHI-346 §3）。

5. **多模式部署**：支持 SaaS 托管、专有云、本地部署和混合模式，满足不同规模企业的数据主权和监管要求。

---

## 目录

- [Part A: 合规与审计框架](#part-a-合规与审计框架)
  - [第一章: 合规栈架构设计](#第一章-合规栈架构设计)
  - [第二章: 链上合规组件设计](#第二章-链上合规组件设计)
  - [第三章: 审计追踪设计](#第三章-审计追踪设计)
  - [第四章: 选择性披露方案](#第四章-选择性披露方案)
- [Part B: 部署与运维架构](#part-b-部署与运维架构)
  - [第五章: 部署模型矩阵](#第五章-部署模型矩阵)
  - [第六章: 运维架构设计](#第六章-运维架构设计)
  - [第七章: 多租户设计](#第七章-多租户设计)
  - [第八章: 安全加固方案](#第八章-安全加固方案)
- [第九章: 代码与基础设施改动清单](#第九章-代码与基础设施改动清单)
- [附录](#附录)

---

# Part A: 合规与审计框架

## 第一章: 合规栈架构设计

### 1.1 四层合规栈架构

Mantle Enterprise 的合规架构采用分层设计，每一层解决不同维度的合规需求：

```
┌─────────────────────────────────────────────────────────────────────┐
│  Layer 4: 外部合规集成层 (External Compliance Integration)          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ KYT Provider │  │ AML/CFT      │  │ OFAC/Sanctions Screening  │ │
│  │ (Chainalysis │  │ (Elliptic,   │  │ (SDN List, EU Sanctions   │ │
│  │  Reactor)    │  │  ComplyAdv.) │  │  OFSI Lists)              │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬────────────────┘ │
│         │                 │                      │                   │
│         └─────────────────┼──────────────────────┘                   │
│                           │ REST API / Webhook                       │
├───────────────────────────┼─────────────────────────────────────────┤
│  Layer 3: 合规中间件层 (Compliance Middleware)                       │
│                           │                                         │
│  ┌────────────────────────┼────────────────────────────────────────┐│
│  │              Compliance API Gateway                             ││
│  │  ┌──────────────┐  ┌──┴───────────┐  ┌────────────────────┐   ││
│  │  │ RPC Auth     │  │ Rules Engine │  │ Audit Event        │   ││
│  │  │ Proxy        │  │ (Policy      │  │ Collector          │   ││
│  │  │ (JWT/OAuth2) │  │  evaluation) │  │ (structured logs)  │   ││
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬───────────┘   ││
│  │         │                 │                    │                ││
│  │  ┌──────┴─────────────────┴────────────────────┴───────────┐   ││
│  │  │          Sequencer Policy Engine                         │   ││
│  │  │  (Transaction filtering, compliance checks, ordering)    │   ││
│  │  └──────────────────────────┬───────────────────────────────┘   ││
│  └─────────────────────────────┼──────────────────────────────────┘│
│                                │                                    │
├────────────────────────────────┼────────────────────────────────────┤
│  Layer 2: 链上合规合约层 (On-chain Compliance Contracts)            │
│                                │                                    │
│  ┌─────────────────────────────┼──────────────────────────────────┐│
│  │  ┌──────────────┐  ┌───────┴──────┐  ┌────────────────────┐   ││
│  │  │ Compliance   │  │ Policy       │  │ Audit Log          │   ││
│  │  │ Registry     │  │ Executor     │  │ Contract           │   ││
│  │  │ (Predeploy)  │  │ (Predeploy)  │  │ (Predeploy)        │   ││
│  │  │              │  │              │  │                    │   ││
│  │  │ - KYC status │  │ - Pre-tx     │  │ - Compliance       │   ││
│  │  │ - Sanctions  │  │   checks     │  │   event records    │   ││
│  │  │ - Geo blocks │  │ - Post-tx    │  │ - Immutable log    │   ││
│  │  │ - Risk tiers │  │   hooks      │  │ - Queryable index  │   ││
│  │  └──────────────┘  └──────────────┘  └────────────────────┘   ││
│  └────────────────────────────────────────────────────────────────┘│
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 1: Mantle 核心协议层 (Mantle Core Protocol)                  │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ op-node      │  │ op-geth      │  │ op-batcher / op-proposer  │ │
│  │ (Sequencer)  │  │ (EVM exec)   │  │ (L1 submission)           │ │
│  └──────────────┘  └──────────────┘  └───────────────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ L1 Bridge    │  │ op-alt-da    │  │ op-conductor (HA)         │ │
│  │ (Portal)     │  │ (pluggable)  │  │                           │ │
│  └──────────────┘  └──────────────┘  └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 各层职责与设计原则

| 层 | 核心职责 | 设计原则 | 改造侵入性 |
|---|---------|---------|-----------|
| **Layer 4: 外部集成** | 对接企业现有 KYT/AML/OFAC 系统 | 标准 API 接口、供应商无关 | 零（纯外部服务） |
| **Layer 3: 中间件** | RPC 认证、策略引擎、审计采集、Sequencer 策略执行 | 独立服务部署、热更新策略 | 低（Sequencer 扩展） |
| **Layer 2: 链上合约** | KYC 注册表、策略执行合约、审计日志合约 | Predeploy 模式、受控升级 | 低（Predeploy 不改 EVM） |
| **Layer 1: 核心协议** | 提供底层交易处理、状态管理、L1 提交 | 最小修改、保持 EVM 兼容 | 最低（仅 L1 边界过滤） |

### 1.3 Layer 3 合规中间件详细设计

Layer 3 是合规执行的核心层，包含四个主要组件：

#### 1.3.1 RPC 认证代理 (Compliance RPC Proxy)

```
外部请求流:

用户/企业应用
    │
    ▼
┌───────────────────────────────────────────────────────┐
│  Compliance RPC Proxy (Nginx/Envoy + Auth Module)     │
│                                                        │
│  Step 1: 认证验证                                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │ • Bearer JWT token 验证 (签名 + 过期 + 签发者)    │ │
│  │ • OIDC 协议支持 (Okta / Azure AD / Google)       │ │
│  │ • API Key 认证 (M2M 服务间调用)                   │ │
│  │ • mTLS 客户端证书 (高安全场景)                     │ │
│  │ → 失败: 401 Unauthorized + 审计日志               │ │
│  └──────────────────────────┬───────────────────────┘ │
│                             │ ✅                       │
│  Step 2: 地址绑定验证                                  │
│  ┌──────────────────────────┼───────────────────────┐ │
│  │ • 提取 tx.from 地址                               │ │
│  │ • 验证地址已关联到认证用户身份                      │ │
│  │ • 防止身份冒用 (SIWE 签名验证可选)                 │ │
│  │ → 失败: 403 Forbidden + 审计日志                  │ │
│  └──────────────────────────┬───────────────────────┘ │
│                             │ ✅                       │
│  Step 3: 合规策略预检                                  │
│  ┌──────────────────────────┼───────────────────────┐ │
│  │ • 查询 Compliance Registry: KYC 有效? 制裁名单?   │ │
│  │ • 金额阈值检查 (可配置 AML 报告阈值)               │ │
│  │ • 地理限制检查 (IP + 用户注册国家)                 │ │
│  │ • 速率限制 (per-user, per-contract)                │ │
│  │ → 失败: 451 Unavailable For Legal Reasons          │ │
│  └──────────────────────────┬───────────────────────┘ │
│                             │ ✅                       │
│  → 转发至 Sequencer RPC                               │
└───────────────────────────────────────────────────────┘
```

**技术选型**：
- **认证协议**: OIDC (OpenID Connect) — 支持 Okta、Azure AD、Google Workspace
- **API 网关**: Envoy Proxy + 自定义 ext_authz filter（Go 实现）
- **JWT 库**: `golang-jwt/jwt` + JWK 集合自动轮换
- **缓存**: Redis — KYC 状态缓存（TTL 5 分钟，事件驱动失效）

**部署架构**：

```
                ┌─────────────────────────────┐
                │  Load Balancer (L4/L7)      │
                │  (TLS termination)          │
                └──────────┬──────────────────┘
                           │
              ┌────────────┼────────────────┐
              ▼            ▼                ▼
        ┌──────────┐ ┌──────────┐    ┌──────────┐
        │ Proxy #1 │ │ Proxy #2 │    │ Proxy #N │
        │ (active) │ │ (active) │    │ (active) │
        └────┬─────┘ └────┬─────┘    └────┬─────┘
             │             │               │
             └─────────────┼───────────────┘
                           ▼
                  ┌────────────────┐
                  │ Sequencer RPC  │
                  │ (op-geth)      │
                  └────────────────┘
```

> **参考方案**: Prividium Proxy RPC 三步验证（WHI-338 §3.2），但 Mantle 版本增加了合规策略预检步骤

#### 1.3.2 Sequencer 策略引擎 (Sequencer Policy Engine)

Sequencer 策略引擎在交易处理流程的三个阶段注入合规检查：

```
交易处理流程:

  RPC 接收交易
       │
       ▼
  ┌─────────────────────────────────────────┐
  │  阶段 1: 交易接收时 (Admission)          │
  │                                         │
  │  PolicyEngine.CheckAdmission(tx):       │
  │  ├─ sender 在白名单中?                   │
  │  │  └─ 查询内存缓存 (LRU, 事件同步)      │
  │  ├─ sender KYC 状态有效?                 │
  │  │  └─ 查询 Compliance Registry 缓存     │
  │  ├─ 交易类型允许?                        │
  │  │  └─ 合约部署是否需要特殊权限           │
  │  └─ 拒绝: 返回错误 + 记录审计事件         │
  └──────────────┬──────────────────────────┘
                 │ ✅ 通过
                 ▼
  ┌─────────────────────────────────────────┐
  │  阶段 2: 交易排序前 (Pre-ordering)       │
  │                                         │
  │  PolicyEngine.CheckCompliance(tx):      │
  │  ├─ AML 金额阈值检查                     │
  │  │  └─ 超过阈值: 标记为可疑 + 生成 SAR   │
  │  ├─ 制裁名单实时检查                     │
  │  │  └─ 查询缓存的 OFAC SDN 列表          │
  │  ├─ 跨地址关联分析                       │
  │  │  └─ 调用 Layer 4 KYT API (异步)       │
  │  └─ 拒绝或标记 + 记录审计事件             │
  └──────────────┬──────────────────────────┘
                 │ ✅ 通过
                 ▼
  ┌─────────────────────────────────────────┐
  │  阶段 3: 交易打包时 (Pre-sealing)        │
  │                                         │
  │  PolicyEngine.CheckPackaging(batch):    │
  │  ├─ DA 路由规则                          │
  │  │  └─ 敏感交易 → 私有 DA 后端 (Phase 2) │
  │  ├─ 批次级合规摘要生成                   │
  │  │  └─ 统计信息 + 合规状态               │
  │  └─ 审计事件批量写入                     │
  └─────────────────────────────────────────┘
```

**实现位置**: `op-node/rollup/sequencing/sequencer.go` — 交易处理流程注入策略检查回调

**策略配置模型** (YAML):

```yaml
# compliance-policy.yaml
admission:
  whitelist:
    enabled: true
    source: "predeploy"          # 从链上 Predeploy 同步
    cache_ttl: 300               # 秒
    sync_mode: "event_driven"    # 通过合约事件同步
  
  kyc_check:
    enabled: true
    required_level: "basic"      # basic | enhanced | full
    
  contract_deployment:
    allowed: "whitelist_only"    # whitelist_only | disabled | open

compliance:
  aml:
    enabled: true
    threshold_usd: 10000         # CTR 报告阈值
    sar_auto_generate: true      # 自动生成可疑活动报告
    
  sanctions:
    enabled: true
    lists: ["ofac_sdn", "eu_consolidated", "un_sanctions"]
    update_interval: 3600        # 秒
    
  kyt:
    enabled: false               # Phase 2 启用
    provider: "chainalysis"
    async: true                  # 异步检查,不阻塞交易

packaging:
  da_routing:
    enabled: false               # Phase 2 启用
  audit_batch:
    enabled: true
    flush_interval: 10           # 秒
```

#### 1.3.3 审计事件采集器 (Audit Event Collector)

```
数据流:

  Sequencer           RPC Proxy          外部系统
     │                    │                  │
     │ tx_admitted        │ auth_success     │ kyc_status_change
     │ tx_rejected        │ auth_failure     │ sanctions_hit
     │ tx_executed        │ rate_limited     │
     │ policy_violation   │                  │
     │                    │                  │
     └────────────────────┼──────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Audit Event Collector │
              │                       │
              │  ┌─────────────────┐ │
              │  │ Event Router    │ │
              │  │ (topic-based)   │ │
              │  └────────┬────────┘ │
              │           │          │
              │  ┌────────┼────────┐ │
              │  ▼        ▼        ▼ │
              │ ┌────┐ ┌────┐ ┌────┐│
              │ │ DB │ │ L2 │ │Kafka││
              │ │    │ │ Tx │ │    ││
              │ └────┘ └────┘ └────┘│
              │  ↑       ↑       ↑   │
              │  链下    链上    流式  │
              │  存储    存储    输出  │
              └───────────────────────┘
```

**审计事件 Schema**:

```json
{
  "event_id": "uuid",
  "timestamp": "2026-05-07T10:30:00Z",
  "event_type": "tx_admitted | tx_rejected | policy_violation | kyc_change | ...",
  "severity": "info | warning | critical",
  "actor": {
    "address": "0x...",
    "identity_id": "user-uuid",
    "kyc_level": "basic | enhanced"
  },
  "transaction": {
    "hash": "0x...",
    "from": "0x...",
    "to": "0x...",
    "value": "1000000",
    "method": "transfer(address,uint256)"
  },
  "policy": {
    "rule_id": "aml_threshold",
    "result": "pass | fail | flagged",
    "details": "Amount exceeds CTR threshold"
  },
  "metadata": {
    "block_number": 12345678,
    "sequencer_timestamp": 1715100600,
    "source": "sequencer | rpc_proxy | external"
  }
}
```

### 1.4 合规栈与 Mantle 架构的集成点

| 集成点 | 现有组件 | 改造内容 | Phase |
|--------|---------|---------|-------|
| RPC 入口 | op-geth JSON-RPC | 前置 Compliance RPC Proxy | 1 |
| 交易池过滤 | `op-geth/core/txpool/` | 添加 PolicyEngine 过滤回调 | 1 |
| Sequencer 排序 | `op-node/rollup/sequencing/sequencer.go` | 注入三阶段策略检查 | 1 |
| L1 边界 | `MantleOptimismPortal` / `MantleL1StandardBridge` | 添加 TransactionFilterer hook 或 allowlist 检查，封堵 forced transaction 绕过 | 1 |
| Predeploy 合约 | L1Block, GasPriceOracle 等已有模式 | 新增 3 个合规 Predeploy | 2 |
| Token Transfer | 企业发行的合规 ERC-20 / wrapper token | Transfer Hook / 合规 token 基类 | 2 |
| DA 路由 | `op-alt-da/daclient.go` + `op-batcher/` | 添加策略驱动的 DA 选择 | 2-3 |

> **Evidence**: WHI-341 §7 (自然插入点); WHI-350 §2.4 (切入点详细分析)

---

## 第二章: 链上合规组件设计

### 2.1 Predeploy 合约架构总览

Mantle 已有成熟的 Predeploy 合约实践（L1Block, GasPriceOracle, OperatorFeeVault），本设计沿用相同模式部署三个合规 Predeploy 合约。

**地址分配（建议保留区间，需在实现前与 Mantle 当前 predeploy map 再确认）**：

| 合约名 | Predeploy 地址 | 用途 | Phase |
|--------|---------------|------|-------|
| ComplianceRegistry | `0x4200000000000000000000000000000000000020` | KYC 状态、制裁名单、地理限制 | 1-2 |
| PolicyExecutor | `0x4200000000000000000000000000000000000021` | 合规策略执行、Transfer Hook | 2 |
| AuditLog | `0x4200000000000000000000000000000000000022` | 不可篡改的合规事件记录 | 2 |

**部署方式**: 通过 Mantle 升级 deposit transaction 或创世配置部署（与 `arsia_upgrade_transactions.go` 相同模式），最终以 Mantle 目标网络的升级机制为准。

> **设计决策**: Predeploy 而非 Precompile。WHI-344 §4.3 和 WHI-350 §4.1 均推荐 Predeploy，理由：(1) 使用 Mantle 已有的 predeploy 升级路径，尽量不新增 EVM 语义；(2) 合约逻辑迭代不必默认绑定到新的 precompile 生命周期；(3) Mantle 已有 Predeploy 实践先例。具体升级实现可采用代理模式，也可采用重新部署 + 系统配置切换，取决于 Mantle 实际 predeploy 管理方式。

### 2.2 ComplianceRegistry (合规注册表合约)

#### 合约接口设计

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ComplianceRegistry
/// @notice Manages KYC status, sanctions lists, and geographic restrictions
/// @dev Deployed as predeploy at 0x4200000000000000000000000000000000000020
interface IComplianceRegistry {
    
    // ============ KYC Status Management ============
    
    /// @notice KYC levels
    enum KYCLevel { NONE, BASIC, ENHANCED, FULL }
    
    /// @notice KYC record for an address
    struct KYCRecord {
        KYCLevel level;
        uint64 issuedAt;        // Unix timestamp
        uint64 expiresAt;       // Unix timestamp (0 = no expiry)
        bytes32 attestationId;  // Hash/pointer to off-chain KYC attestation
        bytes32 jurisdictionCode; // ISO 3166-1 alpha-2 encoded
    }
    
    /// @notice Set KYC status for an address (admin only)
    function setKYCStatus(
        address account,
        KYCLevel level,
        uint64 expiresAt,
        bytes32 attestationId,
        bytes32 jurisdictionCode
    ) external;
    
    /// @notice Batch set KYC status (admin only)
    function batchSetKYCStatus(
        address[] calldata accounts,
        KYCLevel[] calldata levels,
        uint64[] calldata expiresAt
    ) external;
    
    /// @notice Check if address has valid KYC at minimum level
    function isKYCValid(address account, KYCLevel minLevel) 
        external view returns (bool);
    
    /// @notice Get full KYC record
    function getKYCRecord(address account) 
        external view returns (KYCRecord memory);
    
    // ============ Sanctions List Management ============
    
    /// @notice Add addresses to sanctions list (admin only)
    function addToSanctionsList(address[] calldata accounts) external;
    
    /// @notice Remove addresses from sanctions list (admin only)
    function removeFromSanctionsList(address[] calldata accounts) external;
    
    /// @notice Check if address is sanctioned
    function isSanctioned(address account) external view returns (bool);
    
    // ============ Geographic Restrictions ============
    
    /// @notice Set geographic restriction for a jurisdiction
    function setGeoRestriction(
        bytes32 jurisdictionCode, 
        bool restricted
    ) external;
    
    /// @notice Check if jurisdiction is restricted
    function isJurisdictionRestricted(bytes32 jurisdictionCode) 
        external view returns (bool);
    
    // ============ Risk Tier Management ============
    
    /// @notice Risk tiers for graduated compliance
    enum RiskTier { LOW, MEDIUM, HIGH, PROHIBITED }
    
    /// @notice Set risk tier for an address
    function setRiskTier(address account, RiskTier tier) external;
    
    /// @notice Get risk tier
    function getRiskTier(address account) 
        external view returns (RiskTier);
    
    // ============ Admin Management ============
    
    /// @notice Transfer admin role (multisig recommended)
    function transferAdmin(address newAdmin) external;
    
    // ============ Events ============
    
    event KYCStatusUpdated(
        address indexed account, 
        KYCLevel level, 
        uint64 expiresAt
    );
    event SanctionsListUpdated(
        address indexed account, 
        bool sanctioned
    );
    event GeoRestrictionUpdated(
        bytes32 indexed jurisdictionCode, 
        bool restricted
    );
    event RiskTierUpdated(
        address indexed account, 
        RiskTier tier
    );
    event AdminTransferred(
        address indexed oldAdmin, 
        address indexed newAdmin
    );
}
```

#### 存储设计 (Gas 优化)

```
Storage Layout:
  slot 0:    admin / access control root
  slot 1:    total registered addresses (counter)
  
  KYC Records (mapping):
    keccak256(abi.encode(address, 0x10)) => packed KYCRecord
    
    Packed format (1 slot = 32 bytes):
    ┌─────────┬──────────┬──────────┬──────────┬──────────────┐
    │ level(1)│issued(8) │expires(8)│attest(8) │jurisdiction(7)│
    │ byte    │ bytes    │ bytes    │ bytes    │ bytes         │
    └─────────┴──────────┴──────────┴──────────┴──────────────┘
    = 32 bytes total → 1 storage slot per KYC record
    
  Sanctions Bitmap (mapping):
    keccak256(abi.encode(address, 0x20)) => bool (1 slot per check)
    
    优化: 使用 bitmap 模式, 每个 slot 存储 256 个地址的制裁状态
    slot_key = keccak256(abi.encode(address >> 8, 0x20))
    bit_index = address & 0xFF
    → gas 节省: 从 20,000 gas (SSTORE) 降至 ~5,000 gas (bitmap 更新)
    
  Geo Restrictions (bitmap):
    slot 0x30: 256-bit bitmap for first 256 jurisdictions
    → 单个 SLOAD 即可检查任何 jurisdiction
```

**Gas 效率目标**:
- KYC 状态查询: < 2,600 gas (cold SLOAD)
- 制裁名单查询: < 2,600 gas (cold SLOAD, bitmap)
- KYC 状态更新: < 25,000 gas (SSTORE)
- 批量更新 (100 地址): < 500,000 gas

**数据最小化约束**:
- 链上仅保存"是否通过""到期时间""证明引用"等最小状态，不保存姓名、证件号、住址、出生日期等直接 PII。
- `attestationId` 指向链下 KYC 证明或文档包的哈希/引用；链上不承担原始 KYC 文档保管责任。
- 监管披露时由链下审计仓和证明包提供完整材料，链上仅提供状态锚点和完整性证明。

### 2.3 PolicyExecutor (合规策略执行合约)

#### 设计原则

1. **非阻塞原则**: 策略检查失败时 revert 交易，但不阻塞整个区块
2. **可升级性**: 通过 Mantle 现有 predeploy 升级路径支持策略逻辑升级；是否采用 proxy pattern 取决于最终实现
3. **组合性**: 策略可组合——多个检查可串联执行
4. **性能**: 策略检查的 gas 开销应 < 50,000 gas per transaction

#### 合约接口

```solidity
/// @title PolicyExecutor
/// @notice Executes compliance checks as pre/post transaction hooks
/// @dev Deployed as predeploy at 0x4200000000000000000000000000000000000021
interface IPolicyExecutor {
    
    // ============ Policy Types ============
    
    enum PolicyType { 
        WHITELIST,          // 白名单模式 (默认拒绝)
        BLACKLIST,          // 黑名单模式 (默认允许)
        KYC_REQUIRED,       // 要求 KYC
        AMOUNT_LIMIT,       // 金额限制
        COMPOUND            // 组合策略 (TIP-1015 参考)
    }
    
    struct Policy {
        PolicyType policyType;
        bool active;
        bytes32 params;     // 策略参数 (阈值/等级等, 按策略类型解释)
    }
    
    // ============ Transfer Authorization ============
    
    /// @notice Check if a transfer is authorized
    /// @dev Called by Transfer Hook or directly
    function transferAuthorized(
        address token,
        address from,
        address to,
        uint256 amount
    ) external view returns (bool authorized, string memory reason);
    
    /// @notice Check if a transaction is authorized
    function transactionAuthorized(
        address sender,
        address target,
        bytes4 selector,
        uint256 value
    ) external view returns (bool authorized, string memory reason);
    
    // ============ Policy Management ============
    
    /// @notice Register a policy for a token
    function registerPolicy(
        address token, 
        Policy calldata policy
    ) external;
    
    /// @notice Register compound policy (sender + recipient rules)
    function registerCompoundPolicy(
        address token,
        Policy calldata senderPolicy,
        Policy calldata recipientPolicy
    ) external;
    
    /// @notice Deactivate a policy
    function deactivatePolicy(address token) external;
    
    // ============ Events ============
    
    event TransferBlocked(
        address indexed token,
        address indexed from,
        address indexed to,
        uint256 amount,
        string reason
    );
    event PolicyRegistered(
        address indexed token, 
        PolicyType policyType
    );
    event PolicyDeactivated(address indexed token);
}
```

#### Transfer Hook 机制 (Phase 2)

Transfer Hook 在 ERC-20 `transfer` 和 `transferFrom` 执行时自动触发合规检查：

```
ERC-20 Transfer 执行流:

  user calls token.transfer(to, amount)
       │
       ▼
  ERC-20 合约执行 (标准 Solidity)
       │
       ├─ 检查 balance >= amount
       │
       ▼
  Transfer Hook 触发 (Predeploy 调用)
       │
       ├─ PolicyExecutor.transferAuthorized(token, from, to, amount)
       │     │
       │     ├─ ComplianceRegistry.isSanctioned(from)? → revert
       │     ├─ ComplianceRegistry.isSanctioned(to)?   → revert
       │     ├─ ComplianceRegistry.isKYCValid(from)?   → revert
       │     ├─ amount > policy.params.limit?           → revert
       │     └─ return (true, "")
       │
       ├─ ✅ authorized → 继续执行 transfer
       │  or
       └─ ❌ not authorized → revert 整笔交易
```

**实现选项**:

| 方案 | 实现方式 | 不可绕过性 | Gas 开销 | EVM 兼容性 |
|------|---------|-----------|----------|-----------|
| A: 合约级 Hook | Token 合约继承 ComplianceToken 基类，在 `_beforeTokenTransfer` 调用 PolicyExecutor | 仅对合规 token 有效 | ~30,000 gas | 完全兼容 |
| B: 执行层 Hook | 在 state transition 中对受管 token 列表注入 PolicyExecutor 调用 | 对受管 token 不可绕过 | ~40,000 gas | 兼容性需专项验证 |
| C: Precompile 级 | 在 EVM 执行层拦截 CALL 到 ERC-20 `transfer` selector | 最不可绕过 | ~20,000 gas | 需谨慎测试 |

**推荐**: Phase 2 采用 **方案 A**（合规 token 基类 / wrapper token）。这意味着合规强制默认覆盖"企业发行或受管资产"，而不是对 Mantle 上所有历史 ERC-20 一刀切。Phase 3 再评估方案 B 的 ROI，仅在确有"对受管 token 做系统级强制"需求时推进。

> **参考**: Tempo TIP-403 采用 precompile 级方案（WHI-340 §2.4），不可绕过性最高但需修改 EVM。Prividium 采用中间件+合约层混合（WHI-338 §3）。

### 2.4 AuditLog (审计日志合约)

#### 设计目标

- 所有合规相关事件的不可篡改链上记录
- 支持按地址、时间范围、事件类型查询
- Gas 高效：仅存储事件哈希，完整数据存于链下

#### 合约接口

```solidity
/// @title AuditLog
/// @notice Immutable on-chain compliance event log
/// @dev Deployed as predeploy at 0x4200000000000000000000000000000000000022
interface IAuditLog {
    
    /// @notice Audit event categories
    enum EventCategory {
        KYC_STATUS_CHANGE,      // KYC 状态变更
        SANCTIONS_HIT,          // 制裁名单命中
        TRANSFER_BLOCKED,       // Transfer 被阻止
        POLICY_VIOLATION,       // 策略违规
        PERMISSION_CHANGE,      // 权限变更
        CONFIG_CHANGE,          // 配置变更
        SUSPICIOUS_ACTIVITY     // 可疑活动
    }
    
    /// @notice Compact on-chain audit record (1 storage slot)
    struct AuditRecord {
        uint64 timestamp;
        EventCategory category;
        address actor;
        bytes32 dataHash;       // keccak256 of full event data (stored off-chain)
    }
    
    /// @notice Log an audit event (authorized callers only)
    function logEvent(
        EventCategory category,
        address actor,
        bytes32 dataHash
    ) external returns (uint256 eventId);
    
    /// @notice Get audit record by ID
    function getRecord(uint256 eventId) 
        external view returns (AuditRecord memory);
    
    /// @notice Get event count for an address
    function getEventCount(address actor) 
        external view returns (uint256);
    
    /// @notice Get events for address in range
    function getEvents(
        address actor, 
        uint256 fromId, 
        uint256 toId
    ) external view returns (AuditRecord[] memory);
    
    // ============ Events (for off-chain indexing) ============
    
    event AuditEventLogged(
        uint256 indexed eventId,
        EventCategory indexed category,
        address indexed actor,
        bytes32 dataHash,
        uint64 timestamp
    );
}
```

#### 链上 vs 链下审计存储策略

| 数据类型 | 存储位置 | 理由 |
|---------|---------|------|
| **事件哈希 + 最小元数据** | 链上 (AuditLog Predeploy) | 不可篡改性保证；体积小；避免链上保存敏感字段 |
| **完整事件数据** | 链下 (PostgreSQL + S3) | 数据量大；需要复杂查询；GDPR 删除需求 |
| **事件索引** | 链下 (Elasticsearch) | 全文搜索、聚合分析 |
| **合规报告** | 链下 (生成后存 S3) | 格式多样、体积大 |

**成本估算**：
- 链上存储: ~32 bytes per event × 20,000 gas (SSTORE) = 20,000 gas per event
- 以 50 TPS、每笔交易 1 个审计事件计: 50 × 20,000 = 1,000,000 gas/秒 (< Mantle 30M gas limit 的 3.3%)

### 2.5 合规组件的分阶段部署

| Phase | 合规组件 | 部署方式 | 核心功能 |
|-------|---------|---------|---------|
| **Phase 1** | ComplianceRegistry (基础版) | 创世 Predeploy 或升级 deposit tx | 白名单/黑名单、基础 KYC 状态 |
| **Phase 2** | ComplianceRegistry (完整版) | Predeploy 升级路径 | 风险分层、地理限制、批量操作 |
| **Phase 2** | PolicyExecutor | 升级 deposit tx | Transfer Hook、合规策略执行 |
| **Phase 2** | AuditLog | 升级 deposit tx | 链上审计事件记录 |
| **Phase 3** | ZK Compliance Proof (可选) | 新增 Predeploy | ZK 制裁筛查（参考 Prividium） |

### 2.6 治理与职责分离

合规组件不能只有单一 `admin`。最小可运营设计应满足职责分离和紧急处置要求：

| 角色 | 权限范围 | 建议实现 |
|------|---------|---------|
| **Compliance Admin** | KYC 状态录入、风险分层、地理限制配置 | 多签 + 审批流 |
| **Sanctions Operator** | 制裁名单同步、外部名单导入 | 自动任务 + 双人复核 |
| **Security Admin** | 密钥轮换、紧急暂停、访问证书撤销 | 独立多签 |
| **Auditor / Regulator** | 只读审计查询、证明验证 | 只读 API role |

**控制要求**:
- 关键变更采用 `2-of-3` 或更高门槛多签，不接受单 EOA 管理生产合规状态。
- `setKYCStatus`、`addToSanctionsList`、策略阈值修改、L1 Filterer allowlist 修改等操作都必须进入审计流。
- 提供 `break-glass` 紧急暂停能力，但作用域应限于"暂停新准入/暂停特定资产/暂停特定租户"，避免全链一键停摆。

---

## 第三章: 审计追踪设计

### 3.1 审计数据范围

#### 必须记录的审计数据

| 数据类别 | 具体内容 | 记录触发条件 | 监管依据 |
|---------|---------|-------------|---------|
| **交易数据** | 发送方、接收方、金额、合约调用、gas | 所有交易 | MiCA Art. 76, SEC 记录保留规则 |
| **状态变更** | 余额变化、合约状态变更 | 合规相关合约的状态变更 | Basel III 资产跟踪 |
| **权限变更** | KYC 状态变更、白名单增删、角色变更 | 每次变更 | GDPR Art. 30, SOX |
| **配置变更** | 策略更新、阈值调整、系统参数修改 | 每次变更 | ISO 27001, SOC 2 |
| **访问日志** | RPC 认证成功/失败、API 调用记录 | 每次访问 | GDPR Art. 30 |
| **异常事件** | 策略违规、制裁名单命中、可疑活动 | 触发时 | AML/CTF 法规, SAR 报告 |

#### 不应记录的数据 (隐私保护)

| 排除数据 | 理由 |
|---------|------|
| 用户密码/私钥 | 安全最佳实践 |
| 完整 PII (护照号等) | GDPR 数据最小化原则 |
| 内部系统密钥 | 安全合规 |

**保留分层原则**:
- 合规证明所需的交易元数据、策略命中结果、审批记录按监管要求保留 5-7 年。
- 可识别个人的原始 KYC 文档、身份证明附件、人工审核备注采用独立保留策略，到期删除或匿名化。
- 因此"审计可追溯"与"PII 可删除"不是同一份数据集，必须物理和逻辑分层存储。

### 3.2 审计追踪架构

```
完整审计数据流:

┌──────────────────────────────────────────────────────────────────┐
│                     数据源层 (Data Sources)                       │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐│
│  │Sequencer │  │ RPC      │  │ L1 Bridge│  │ Admin Dashboard  ││
│  │Policy Eng│  │ Proxy    │  │ Events   │  │ Operations       ││
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────────────┘│
│       │              │             │              │              │
└───────┼──────────────┼─────────────┼──────────────┼──────────────┘
        │              │             │              │
        └──────────────┼─────────────┼──────────────┘
                       │             │
                       ▼             ▼
┌──────────────────────────────────────────────────────────────────┐
│                   处理层 (Processing Layer)                       │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Audit Event Pipeline                          │  │
│  │                                                            │  │
│  │  ┌────────────┐   ┌─────────────┐   ┌──────────────────┐ │  │
│  │  │ Ingest     │──►│ Enrich      │──►│ Route            │ │  │
│  │  │ (validate, │   │ (add context│   │ (on-chain hash,  │ │  │
│  │  │  normalize)│   │  identity,  │   │  off-chain store,│ │  │
│  │  │            │   │  risk score)│   │  alerts, stream) │ │  │
│  │  └────────────┘   └─────────────┘   └──────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                       │
           ┌───────────┼───────────────────────┐
           ▼           ▼                       ▼
┌────────────┐ ┌──────────────┐    ┌─────────────────────┐
│  链上存储   │ │  链下存储      │    │  实时输出             │
│            │ │              │    │                     │
│ AuditLog   │ │ PostgreSQL   │    │ ┌─────────────────┐│
│ Predeploy  │ │ (结构化数据)  │    │ │ Kafka Stream    ││
│ (event     │ │              │    │ │ → SIEM 集成     ││
│  hashes)   │ │ S3/MinIO     │    │ │ → Alert Engine  ││
│            │ │ (原始数据+    │    │ │ → Dashboard     ││
│            │ │  报告归档)    │    │ └─────────────────┘│
└────────────┘ │              │    │                     │
               │ Elasticsearch│    │ ┌─────────────────┐│
               │ (全文索引)    │    │ │ Webhook/Email   ││
               └──────────────┘    │ │ → Compliance    ││
                                   │ │   Officer Alert ││
                                   │ └─────────────────┘│
                                   └─────────────────────┘
```

### 3.3 审计接口设计 (Regulator Access)

#### 监管方审计 API

```
┌─────────────────────────────────────────────────────────────┐
│               Regulator Audit API (REST + GraphQL)           │
│                                                              │
│  认证: mTLS 客户端证书 + API Key (双因素)                     │
│  授权: 基于角色的数据访问范围                                  │
│                                                              │
│  Endpoints:                                                  │
│                                                              │
│  GET /api/v1/audit/transactions                              │
│    ?from_time=2026-01-01&to_time=2026-06-30                 │
│    &address=0x...                                            │
│    &min_amount=10000                                         │
│    → 返回: 交易列表 + Merkle 证明                            │
│                                                              │
│  GET /api/v1/audit/compliance-events                         │
│    ?category=SANCTIONS_HIT&severity=critical                 │
│    → 返回: 合规事件列表                                      │
│                                                              │
│  GET /api/v1/audit/kyc-status                                │
│    ?address=0x...                                            │
│    → 返回: 当前 KYC 状态 + 历史变更记录                       │
│                                                              │
│  POST /api/v1/audit/reports/generate                         │
│    { "type": "sar", "period": "2026-Q1", "format": "pdf" }  │
│    → 返回: 异步报告生成任务 ID                                │
│                                                              │
│  GET /api/v1/audit/verify                                    │
│    ?event_id=123&proof=0x...                                 │
│    → 返回: 链上 AuditLog 验证结果                             │
│                                                              │
│  GET /api/v1/audit/statistics                                │
│    → 返回: 交易量、活跃地址数、合规事件统计                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 审计报告自动化

| 报告类型 | 生成频率 | 内容 | 格式 | 监管要求 |
|---------|---------|------|------|---------|
| **交易活动报告 (TAR)** | 每日 | 当日所有交易汇总、top 地址、异常检测 | PDF + CSV | MiCA Art. 76 |
| **可疑活动报告 (SAR)** | 触发时 | 可疑交易详情、关联分析、风险评估 | FinCEN BSA 格式 | AML/CTF |
| **货币交易报告 (CTR)** | 触发时 | 超过阈值的交易详情 | FinCEN CTR 格式 | Bank Secrecy Act |
| **合规状态报告** | 每月 | KYC 覆盖率、制裁筛查统计、策略执行统计 | PDF | 内部合规 |
| **季度合规摘要** | 每季度 | 系统运行健康度、合规事件趋势、改进建议 | PDF + Dashboard | 董事会/监管报告 |
| **年度审计包** | 每年 | 完整审计追踪、Merkle 证明包、系统变更记录 | 加密 ZIP + 证明 | SOC 2 / ISO 27001 |

**自动化流程**:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 定时任务      │───►│ 数据聚合     │───►│ 报告生成     │
│ (cron/k8s    │    │ (SQL query + │    │ (template +  │
│  CronJob)    │    │  aggregation)│    │  rendering)  │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                    ┌──────────────────────────┬┘
                    ▼                          ▼
             ┌──────────────┐          ┌──────────────┐
             │ 加密存储      │          │ 通知分发      │
             │ (S3 + KMS    │          │ (Email +     │
             │  encryption) │          │  Dashboard)  │
             └──────────────┘          └──────────────┘
```

---

## 第四章: 选择性披露方案

### 4.1 披露需求矩阵

| 披露场景 | 数据范围 | 访问方 | 粒度 | 频率 |
|---------|---------|--------|------|------|
| 常规监管审计 | 指定时间范围的交易 | 监管机构 | 交易级 | 按需 |
| AML 调查 | 特定地址的完整历史 | 执法机构 | 地址级 | 按需 |
| 税务审计 | 年度交易汇总 | 税务机关 | 地址级/年度 | 年度 |
| 合规证明 | 合规状态声明 | 合作方 | 摘要级 | 按需 |
| 公开透明度 | 链活跃度指标 | 公众 | 聚合级 | 实时 |
| 争议解决 | 特定交易的完整数据 | 仲裁方 | 交易级 | 按需 |

### 4.2 三层选择性披露架构

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: 加密数据包 (Encrypted Audit Packages)                  │
│                                                                  │
│  针对特定监管方加密的审计数据包                                    │
│  • 使用监管方公钥加密 (RSA-OAEP / ECIES)                         │
│  • 数据包含 Merkle 证明 → 可独立验证数据来源于链上                  │
│  • 时间范围限定 → 仅包含授权时段的数据                              │
│  • 签名防篡改 → 运营方签名保证数据完整性                            │
│                                                                  │
│  格式: EncryptedAuditPackage {                                   │
│    header: { recipient_pubkey_hash, time_range, data_scope }     │
│    encrypted_data: AES-256-GCM(audit_records)                    │
│    merkle_proofs: [proof_1, proof_2, ...]                        │
│    operator_signature: ECDSA(header + hash(encrypted_data))      │
│  }                                                               │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: 监管方专用接口 (Regulator API)                          │
│                                                                  │
│  基于角色的 API 访问控制                                          │
│  • mTLS + API Key 双因素认证                                      │
│  • 数据范围由 Scope Token 定义                                    │
│  • 请求/响应全量审计日志                                           │
│  • 支持实时查询 + 批量导出                                        │
│                                                                  │
│  Scope Token: {                                                  │
│    role: "regulator" | "auditor" | "law_enforcement",            │
│    scope: { addresses: [...], time_range: {...}, event_types: }   │
│    expires_at: "2026-12-31",                                     │
│    issuer_signature: "..."                                       │
│  }                                                               │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: 链上可验证证明 (On-chain Verifiable Proofs)             │
│                                                                  │
│  任何披露数据都可通过链上状态验证                                   │
│  • AuditLog Predeploy 存储事件哈希 → Merkle 根                   │
│  • 验证方流程:                                                    │
│    1. 收到审计数据                                                │
│    2. 计算 keccak256(audit_data) → data_hash                     │
│    3. 使用 Merkle 证明验证 data_hash ∈ AuditLog state root       │
│    4. AuditLog state root 包含在 Mantle L2 state root 中          │
│    5. Mantle L2 state root 锚定在以太坊 L1                        │
│  → 信任链: 审计数据 → AuditLog → Mantle L2 → Ethereum L1         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 数据粒度控制

| 粒度级别 | 内容 | 用途 | 隐私保护 |
|---------|------|------|---------|
| **聚合级** | 链活跃度统计（交易量、活跃地址数、TVL） | 公开透明度报告 | 最高（无个体数据） |
| **地址级** | 特定地址的交易历史、余额变化、KYC 状态 | AML 调查、税务审计 | 中等（限特定地址） |
| **交易级** | 单笔交易的完整数据（含合规检查结果） | 争议解决、法律调查 | 较低（但限特定交易） |
| **全量级** | 完整链数据 + 审计日志 | 全面审计（极罕见） | 最低（全数据暴露） |

### 4.4 GDPR 合规考量

| GDPR 条款 | 要求 | Mantle Enterprise 设计 |
|-----------|------|----------------------|
| **Art. 5 数据最小化** | 仅收集必要数据 | 链上仅存事件哈希；完整 PII 存链下且可删除 |
| **Art. 17 被遗忘权** | 数据主体可请求删除 | 链下数据库支持删除/匿名化；链上哈希不含 PII |
| **Art. 25 设计隐私** | 隐私保护融入系统设计 | 选择性披露、加密审计包、范围化访问控制 |
| **Art. 30 处理记录** | 维护数据处理活动记录 | Audit Event Collector 自动记录所有访问 |
| **Art. 44 跨境传输** | 限制向欧盟外传输 | 部署模型支持数据主权（本地部署选项） |

**现实边界说明**:
- Phase 1 仍然基于公开 L2/L1 数据路径，无法让已经公开上链的交易内容满足严格意义上的删除要求。
- 因此 GDPR 的"完全可删"只适用于链下保管的 KYC 文档、审计明文、身份映射等外围数据；链上公开交易历史只能通过最小化上链内容来降低风险。
- 真正接近 GDPR 友好形态的，是 Phase 2 以后引入私有 DA / Validium 后，对敏感明文不上公共 DA 的方案。

**GDPR 删除流程**:

```
用户请求删除个人数据
       │
       ▼
  ┌─────────────────────────────────────┐
  │ Step 1: 标识关联数据                 │
  │ • 链下: PostgreSQL 中的用户记录      │
  │ • 链下: S3 中的审计日志明文          │
  │ • 链上: AuditLog 中的事件哈希        │
  │ • 链上: ComplianceRegistry KYC 记录  │
  └───────────────┬─────────────────────┘
                  │
                  ▼
  ┌─────────────────────────────────────┐
  │ Step 2: 评估法律义务                 │
  │ • 金融数据: MiFID II 要求保留 5-7 年 │
  │ • AML 数据: 保留 5 年 (4AMLD)       │
  │ • 税务数据: 保留 7 年               │
  │                                     │
  │ → 若在保留期内: 标记为"待删除",      │
  │   到期后自动删除                     │
  │ → 若已过保留期: 立即执行删除          │
  └───────────────┬─────────────────────┘
                  │
                  ▼
  ┌─────────────────────────────────────┐
  │ Step 3: 执行删除/匿名化             │
  │ • 链下: 删除 PII 字段 或 匿名化     │
  │ • 链上: 不可删除，但哈希不含 PII     │
  │   → 链上状态对 GDPR 合规无影响       │
  │ • KYC 记录: 设为 NONE + 清除字段    │
  └───────────────┬─────────────────────┘
                  │
                  ▼
  ┌─────────────────────────────────────┐
  │ Step 4: 记录删除操作                 │
  │ • 在审计日志中记录删除事件           │
  │ • 保留删除操作的元数据 (非 PII)      │
  │ • 通知数据主体删除已完成             │
  └─────────────────────────────────────┘
```

> **Evidence**: WHI-346 §3.4 — Prividium 的 Validium 模型被评估为"最 GDPR 友好的 ZK L2 架构"，因其链下 DA 支持数据删除。Mantle 的 Phase 1（公开 DA）无法完全满足 GDPR，但 Phase 2 引入 Validium 模式后可实现类似能力。

---

# Part B: 部署与运维架构

## 第五章: 部署模型矩阵

### 5.1 四种部署模型

```
┌─────────────────────────────────────────────────────────────────────┐
│                    部署模型光谱                                       │
│                                                                     │
│  运维责任                                                            │
│  Mantle 团队 ◄──────────────────────────────────► 企业自身           │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐        │
│  │  Model A │  │  Model B │  │  Model C │  │   Model D    │        │
│  │  SaaS    │  │  专有云   │  │  本地部署 │  │   混合部署    │        │
│  │  托管    │  │  部署    │  │          │  │              │        │
│  │          │  │          │  │          │  │              │        │
│  │ Mantle   │  │ 企业云   │  │ 企业数据  │  │ 核心:本地    │        │
│  │ 基础设施 │  │ 账户     │  │ 中心     │  │ 辅助:云端    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘        │
│                                                                     │
│  数据主权                                                            │
│  Mantle 管理 ◄──────────────────────────────────► 企业完全控制       │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 部署模型详细对比

| 维度 | Model A: SaaS 托管 | Model B: 专有云 | Model C: 本地部署 | Model D: 混合 |
|------|-------------------|----------------|----------------|-------------|
| **运维方** | Mantle 团队 | 共同（Mantle 协助） | 企业 DevOps 团队 | 分层共管 |
| **基础设施** | Mantle 公有云 | 企业 AWS/Azure/GCP | 企业数据中心 | 混合 |
| **数据位置** | Mantle 选择 | 企业选择 Region | 企业机房 | 分层存放 |
| **数据主权** | 低 | 中 | 高 | 高（核心数据） |
| **监管合规** | 依赖 Mantle 合规 | 企业可控 | 完全可控 | 完全可控 |
| **启动成本** | 最低 | 中 | 最高 | 高 |
| **运行成本** | 订阅制 | 云资源 + 支持费 | 硬件 + 人力 | 混合 |
| **扩展性** | 自动 | 云弹性 | 有限 | 灵活 |
| **SLA** | Mantle 承诺 | 共同 SLA | 企业自保 | 分层 SLA |
| **适用客户** | FinTech 创业公司 | 中型金融机构 | 大型银行/央行 | 大多数企业 |
| **启动时间** | 1-2 周 | 2-4 周 | 2-3 月 | 1-2 月 |

### 5.3 推荐部署架构 (Model D: 混合模式)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    企业本地环境 (On-Premises)                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     安全区 (DMZ)                              │   │
│  │  ┌──────────────┐  ┌──────────────┐                         │   │
│  │  │ Load Balancer│  │ WAF / DDoS   │                         │   │
│  │  │ (HAProxy)    │  │ Protection   │                         │   │
│  │  └──────┬───────┘  └──────────────┘                         │   │
│  └─────────┼───────────────────────────────────────────────────┘   │
│            │                                                        │
│  ┌─────────┼───────────────────────────────────────────────────┐   │
│  │         ▼           应用层 (Application Layer)                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐ │   │
│  │  │ Compliance   │  │ Admin        │  │ Audit API          │ │   │
│  │  │ RPC Proxy    │  │ Dashboard    │  │ (Regulator Access) │ │   │
│  │  └──────┬───────┘  └──────────────┘  └────────────────────┘ │   │
│  │         │                                                     │   │
│  │  ┌──────┴───────────────────────────────────────────────────┐│   │
│  │  │              Core Blockchain Layer                        ││   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               ││   │
│  │  │  │ op-node  │  │ op-geth  │  │ op-cond. │               ││   │
│  │  │  │ (Seq.)   │  │ (exec)   │  │ (HA)     │               ││   │
│  │  │  └──────────┘  └──────────┘  └──────────┘               ││   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               ││   │
│  │  │  │op-batcher│  │op-proposer│ │gas-oracle │               ││   │
│  │  │  └──────────┘  └──────────┘  └──────────┘               ││   │
│  │  └──────────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     数据层 (Data Layer)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐ │   │
│  │  │ State DB     │  │ Audit DB     │  │ HSM              │ │   │
│  │  │ (LevelDB/    │  │ (PostgreSQL) │  │ (密钥管理)       │ │   │
│  │  │  MDBX)       │  │              │  │                  │ │   │
│  │  └──────────────┘  └──────────────┘  └────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                           │
                    专线/VPN 连接
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    云端环境 (Cloud — AWS/Azure/GCP)                   │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ Monitoring   │  │ Log          │  │ Backup & DR               │ │
│  │ (Prometheus  │  │ Aggregation  │  │ (State snapshots →        │ │
│  │  + Grafana)  │  │ (ELK/Loki)  │  │  S3 encrypted)            │ │
│  └──────────────┘  └──────────────┘  └───────────────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ L1 Beacon    │  │ Alert        │  │ CI/CD Pipeline            │ │
│  │ Node Access  │  │ Engine       │  │ (升级部署)                 │ │
│  │ (Ethereum)   │  │ (PagerDuty)  │  │                           │ │
│  └──────────────┘  └──────────────┘  └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.4 部署组件清单

| 组件 | 实例数 | 资源需求 (最低) | 高可用配置 |
|------|-------|---------------|-----------|
| **op-node (Sequencer)** | 2 (active + standby) | 8 vCPU, 32GB RAM, 500GB SSD | op-conductor HA |
| **op-geth** | 2 (active + standby) | 16 vCPU, 64GB RAM, 2TB NVMe | 跟随 op-node HA |
| **op-batcher** | 1 (+ hot spare) | 4 vCPU, 16GB RAM | L1 交易管理 |
| **op-proposer** | 1 (+ hot spare) | 4 vCPU, 16GB RAM | L1 状态根提交 |
| **gas-oracle** | 1 | 2 vCPU, 4GB RAM | 定期任务 |
| **Compliance RPC Proxy** | 3+ (behind LB) | 4 vCPU, 8GB RAM each | 水平扩展 |
| **Audit Event Collector** | 2 (active-active) | 4 vCPU, 16GB RAM | 消息队列缓冲 |
| **Admin Dashboard** | 2 (behind LB) | 2 vCPU, 4GB RAM | 无状态 |
| **PostgreSQL (Audit)** | 3 (primary + 2 replica) | 8 vCPU, 64GB RAM, 1TB SSD | 流复制 + PITR |
| **Redis (Cache)** | 3 (sentinel mode) | 4 vCPU, 16GB RAM | Sentinel HA |
| **Elasticsearch** | 3 (cluster) | 8 vCPU, 32GB RAM, 500GB | 3 节点集群 |

---

## 第六章: 运维架构设计

### 6.1 监控体系

```
┌─────────────────────────────────────────────────────────────────┐
│                      监控架构                                     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    指标采集层                                  ││
│  │                                                              ││
│  │  op-node metrics ──┐                                         ││
│  │  op-geth metrics ──┤                                         ││
│  │  batcher metrics ──┼──► Prometheus ──► Grafana Dashboards   ││
│  │  proxy metrics ────┤     (TSDB)        (可视化)              ││
│  │  audit metrics ────┤                                         ││
│  │  system metrics ───┘    15s 采集间隔                          ││
│  │                         90 天保留                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    日志采集层                                  ││
│  │                                                              ││
│  │  Structured JSON logs ──► Promtail/Filebeat ──► Loki/ELK   ││
│  │                                                              ││
│  │  日志级别策略:                                                ││
│  │  • INFO:  交易处理、区块生产、正常操作                         ││
│  │  • WARN:  性能降级、重试、阈值接近                             ││
│  │  • ERROR: 策略执行失败、组件异常、连接中断                     ││
│  │  • FATAL: 系统不可用、数据不一致、安全事件                     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    告警策略                                    ││
│  │                                                              ││
│  │  P0 (立即响应, <5min):                                       ││
│  │  • Sequencer 停止出块 > 30s                                  ││
│  │  • L1 batch 提交失败 > 3 次                                  ││
│  │  • 安全事件 (未授权访问、制裁名单命中)                         ││
│  │  • 数据不一致 (state root 校验失败)                            ││
│  │                                                              ││
│  │  P1 (30min 内响应):                                          ││
│  │  • TPS < SLA 目标的 50%                                      ││
│  │  • P99 延迟 > 5s                                             ││
│  │  • 磁盘使用率 > 80%                                          ││
│  │  • 合规审计系统延迟 > 60s                                     ││
│  │                                                              ││
│  │  P2 (4h 内响应):                                             ││
│  │  • 内存使用率 > 75%                                          ││
│  │  • L1 gas 费用异常                                           ││
│  │  • 证书即将过期 (< 30 天)                                     ││
│  │                                                              ││
│  │  告警通道: PagerDuty → Slack → Email                         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 关键监控指标

| 指标类别 | 具体指标 | SLA 目标 | 告警阈值 |
|---------|---------|---------|---------|
| **链健康** | 区块生产延迟 | < 2s (区块时间) | > 4s 触发 P0 |
| **链健康** | L1 batch 提交延迟 | < 5 min | > 10 min 触发 P1 |
| **链健康** | Sequencer ↔ L1 同步延迟 | < 30s | > 60s 触发 P1 |
| **性能** | TPS (交易吞吐量) | > 50 TPS (基线) | < 25 TPS 触发 P1 |
| **性能** | 交易确认延迟 (P99) | < 3s | > 5s 触发 P1 |
| **性能** | RPC 响应时间 (P99) | < 500ms | > 2s 触发 P1 |
| **合规** | 审计事件处理延迟 | < 10s | > 60s 触发 P1 |
| **合规** | 策略检查延迟 | < 5ms (内存缓存) | > 50ms 触发 P2 |
| **合规** | 制裁名单更新频率 | < 1h | > 4h 触发 P1 |
| **安全** | 认证失败率 | < 1% | > 5% 触发 P1 |
| **安全** | 未授权访问尝试 | 0 | > 0 触发 P0 |
| **资源** | CPU 使用率 | < 70% | > 85% 触发 P2 |
| **资源** | 磁盘使用率 | < 70% | > 80% 触发 P2 |
| **资源** | 内存使用率 | < 75% | > 85% 触发 P2 |

### 6.3 备份与灾难恢复

#### 备份策略

| 数据类型 | 备份方式 | 频率 | 保留期 | 恢复目标 |
|---------|---------|------|--------|---------|
| **链状态 (State DB)** | 全量快照 + 增量 | 每 6 小时 (全量), 每 30 分钟 (增量) | 90 天 | RPO < 30 min |
| **审计数据库（交易/策略/审批）** | PostgreSQL PITR | 连续 WAL 归档 | 5-7 年（按法域配置） | RPO < 1 min |
| **KYC 原始档案/PII 附件** | 加密对象存储 + 生命周期策略 | 实时写入 | 到期删除/匿名化（默认不超过法定保留期） | RPO < 15 min |
| **配置文件** | Git 版本控制 | 每次变更 | 永久 | RPO = 0 |
| **密钥材料** | HSM 自动备份 | 实时 | 永久 | 按 HSM 策略 |
| **L1 交易记录** | 以太坊自身保证 | N/A | 永久 | N/A |

#### 灾难恢复方案

```
灾难恢复场景与策略:

场景 1: 单组件故障 (op-geth 崩溃)
  → RTO: < 5 min
  → 策略: op-conductor 自动切换到 standby 节点
  → 数据: 无丢失 (从 L1 重新推导)

场景 2: 数据中心网络故障
  → RTO: < 30 min
  → 策略: DNS 切换到灾备站点 + 从最新快照恢复
  → 数据: RPO < 30 min (增量备份)

场景 3: 完整数据中心毁坏
  → RTO: < 4 hours（公开 DA 模式）
  → 策略: 在灾备站点从 L1 完全重新推导 L2 状态
  → 数据: 零丢失 (公开 DA 阶段 L1 是权威来源)
  → 审计数据: 从异地备份恢复

场景 3B: Phase 2 私有 DA / Validium 阶段的数据中心毁坏
  → RTO: 4-24 hours（取决于私有 DA 副本健康度）
  → 策略: 从异地私有 DA 副本 + 审计仓恢复；仅凭 L1 证明/commitment 不足以重构明文数据
  → 数据: 取决于私有 DA 复制策略，必须额外建设跨区域副本和定期恢复演练

场景 4: L1 (Ethereum) 临时不可用
  → 策略: Sequencer 继续出块 (软终局)
  → 影响: Batch 提交暂停，恢复后自动追赶
  → RTO: 依赖 L1 恢复时间
```

### 6.4 升级策略

| 升级类型 | 策略 | 停机时间 | 回滚方案 | 适用场景 |
|---------|------|---------|---------|---------|
| **中间件更新** | 滚动更新 (Rolling) | 零停机 | 回滚到前版本 Pod | RPC Proxy、Audit Collector |
| **Predeploy 合约升级** | Deposit Transaction / 受控升级窗口 | 接近零停机 | 预置回滚交易或切回旧实现 | ComplianceRegistry 等 |
| **op-geth 更新** | Blue-Green | < 1 min | 切回 Blue 环境 | 执行层更新 |
| **op-node 更新** | 计划停机 + HA 切换 | < 5 min | op-conductor 切回 | Sequencer 更新 |
| **硬分叉升级** | 协调升级 (所有节点) | 计划窗口 | 回退到前版本 (需共识) | 核心协议变更 |

**升级注意事项**:
- L1 边界过滤若落在 `MantleOptimismPortal` / `MantleL1StandardBridge`，必须把 Mantle 双代币桥接差异一起纳入测试，不可按标准 OP Portal 假设实现。
- 任何涉及 forced transaction 过滤的升级，都要单独验证"白名单地址仍可执行合法紧急强制交易"与"非白名单地址无法旁路"这两条。

**版本管理策略**:

```
版本号格式: MAJOR.MINOR.PATCH-BUILD
  MAJOR: 硬分叉级变更 (不兼容)
  MINOR: 新功能 (向后兼容)
  PATCH: Bug 修复 + 安全补丁
  BUILD: CI 构建号

发布流程:
  开发 → 内部测试 → Testnet (Mantle Sepolia) → Canary (1% 流量)
  → 灰度 (10% → 50% → 100%) → 全量发布

最小灰度周期:
  PATCH: 24 小时
  MINOR: 1 周
  MAJOR: 2 周 (含 testnet 验证)
```

### 6.5 SLA 保证

| SLA 指标 | Bronze | Silver | Gold | Platinum |
|---------|--------|--------|------|---------|
| **可用性** | 99.5% | 99.9% | 99.95% | 99.99% |
| **年停机时间** | 43.8 h | 8.76 h | 4.38 h | 52.6 min |
| **RTO** | < 4h | < 1h | < 15min | < 5min |
| **RPO** | < 1h | < 30min | < 5min | < 1min |
| **TPS 保证** | 50 | 100 | 200 | 500 |
| **P99 延迟** | < 5s | < 3s | < 2s | < 1s |
| **审计延迟** | < 5min | < 1min | < 30s | < 10s |
| **适用部署** | SaaS | 专有云 | 本地/混合 | 定制 |

---

## 第七章: 多租户设计

### 7.1 多租户模型对比

| 维度 | 单链多租户 | 每租户独立链 | 混合模式 |
|------|-----------|------------|---------|
| **架构** | 共享 Sequencer + 逻辑隔离 | 独立 Sequencer 实例 | 共享基础设施 + 独立执行 |
| **数据隔离** | 合约级 + namespace | 物理隔离 (独立 DB) | 可配置 |
| **性能隔离** | 共享 gas limit | 独立 gas limit | 保证最低 + 突发共享 |
| **运维复杂度** | 低 | 高 (N 套系统) | 中 |
| **成本效率** | 最高 | 最低 | 中 |
| **合规隔离** | 逻辑 (RBAC) | 物理 | 可配置 |
| **适用场景** | 低隐私需求 | 银行间/高隐私 | 大多数企业 |

### 7.2 推荐: Phase 1 单链 + Phase 3 Zone 架构

**Phase 1-2**: 单链多租户（逻辑隔离）

```
┌────────────────────────────────────────────────┐
│          单链多租户 (Phase 1-2)                  │
│                                                │
│  ┌─────────────────────────────────────────┐  │
│  │         Mantle Enterprise L2             │  │
│  │                                         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐│  │
│  │  │ Tenant A │ │ Tenant B │ │ Tenant C ││  │
│  │  │ (Bank)   │ │ (Insurer)│ │ (Fund)   ││  │
│  │  │          │ │          │ │          ││  │
│  │  │ Contracts│ │ Contracts│ │ Contracts││  │
│  │  │ + KYC    │ │ + KYC    │ │ + KYC    ││  │
│  │  │ namespace│ │ namespace│ │ namespace││  │
│  │  └──────────┘ └──────────┘ └──────────┘│  │
│  │                                         │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │ Shared: Sequencer, DA, Bridge    │  │  │
│  │  │ Isolated: ComplianceRegistry per │  │  │
│  │  │          tenant namespace        │  │  │
│  │  └──────────────────────────────────┘  │  │
│  └─────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

**Phase 3**: Zone 架构（物理隔离，参考 Tempo Zones）

```
┌────────────────────────────────────────────────┐
│          Zone 架构 (Phase 3)                     │
│                                                │
│  ┌──────────────────────────────────────┐     │
│  │         Mantle Enterprise L2          │     │
│  │         (Settlement Layer)            │     │
│  └──────────┬──────────┬────────────────┘     │
│             │          │                       │
│      ┌──────┴──┐  ┌───┴──────┐  ┌──────────┐ │
│      │ Zone A  │  │ Zone B   │  │ Zone C   │ │
│      │ (Bank X)│  │ (Bank Y) │  │ (Fund Z) │ │
│      │         │  │          │  │          │ │
│      │ 独立    │  │ 独立     │  │ 独立     │ │
│      │ Seq.    │  │ Seq.     │  │ Seq.     │ │
│      │ 独立    │  │ 独立     │  │ 独立     │ │
│      │ State   │  │ State    │  │ State    │ │
│      └─────────┘  └──────────┘  └──────────┘ │
│                                                │
│  每 Zone:                                      │
│  • 独立 Sequencer 实例                          │
│  • 独立状态数据库                                │
│  • 独立合规策略                                  │
│  • 通过 Mantle L2 跨 Zone 通信                   │
└────────────────────────────────────────────────┘
```

> **Evidence**: WHI-340 §3.1 — Tempo Zones 架构验证了"单序列器 Validium"模式可行；WHI-350 §3.1 — Phase 3 推荐 Zone 隔离方案

### 7.3 租户级资源计量

| 计量维度 | 计量方式 | 计费模型 |
|---------|---------|---------|
| **交易量** | 每租户交易计数器 (Sequencer 策略引擎统计) | 按交易数阶梯计费 |
| **存储空间** | 每租户合约 + 状态数据大小 | 按 GB/月 |
| **Gas 消耗** | 每租户 gas 使用量 (标记 tenant ID) | 按 gas 单位 |
| **合规服务** | KYC 查询次数、制裁筛查次数、审计报告数 | 按服务调用 |
| **带宽** | RPC 调用量 + 数据传输量 | 按请求数/GB |

---

## 第八章: 安全加固方案

### 8.1 密钥管理

```
┌─────────────────────────────────────────────────────────────────┐
│                    密钥管理架构                                    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   HSM 层 (最高安全)                           ││
│  │                                                              ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  ││
│  │  │ Sequencer    │  │ Batcher      │  │ Proposer         │  ││
│  │  │ Signing Key  │  │ Signing Key  │  │ Signing Key      │  ││
│  │  │ (ECDSA)      │  │ (ECDSA)      │  │ (ECDSA)          │  ││
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  ││
│  │                                                              ││
│  │  HSM 提供商:                                                 ││
│  │  • Google Cloud KMS (已有集成: op-service/hsm/)              ││
│  │  • AWS CloudHSM                                              ││
│  │  • HashiCorp Vault (本地部署)                                 ││
│  │  • Thales Luna HSM (金融级)                                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   密钥管理策略                                 ││
│  │                                                              ││
│  │  密钥轮换:                                                    ││
│  │  • Sequencer key: 每 90 天 (计划停机窗口)                     ││
│  │  • Batcher/Proposer key: 每 180 天                            ││
│  │  • TLS 证书: 每 365 天 (自动续签)                              ││
│  │  • API keys: 每 90 天 (自动轮换)                               ││
│  │  • JWT signing key: 每 30 天 (JWK 集合自动轮换)                ││
│  │                                                              ││
│  │  密钥泄露应急:                                                 ││
│  │  1. 检测: 异常签名活动监控                                     ││
│  │  2. 隔离: 立即暂停受影响组件                                   ││
│  │  3. 轮换: 生成新密钥, 更新 L1 配置合约                        ││
│  │  4. 审计: 回溯泄露时间窗口内的所有操作                         ││
│  │  5. 通知: 通知受影响方和监管机构                                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

> **Evidence**: WHI-341 §2.5 — Mantle gas-oracle 已有 Google Cloud KMS HSM 签名集成 (`op-service/hsm/hsm_signer.go`)

### 8.2 网络安全

```
┌─────────────────────────────────────────────────────────────────┐
│                    网络安全架构                                    │
│                                                                  │
│  外部网络                                                         │
│  │                                                               │
│  │  ┌────────────────────────────────────────────────────────┐  │
│  │  │  Layer 1: 边界防护                                      │  │
│  │  │                                                        │  │
│  │  │  • TLS 1.3 everywhere (no exceptions)                  │  │
│  │  │  • WAF (Web Application Firewall)                      │  │
│  │  │  • DDoS 防护 (Cloudflare / AWS Shield)                 │  │
│  │  │  • IP 白名单 (管理接口)                                 │  │
│  │  │  • Rate limiting (per-IP, per-user)                     │  │
│  │  └────────────────────────────────────────────────────────┘  │
│  │                                                               │
│  │  ┌────────────────────────────────────────────────────────┐  │
│  │  │  Layer 2: 网络分段                                      │  │
│  │  │                                                        │  │
│  │  │  DMZ (公开): Load Balancer, WAF                        │  │
│  │  │  App Zone:   RPC Proxy, Dashboard, Audit API           │  │
│  │  │  Core Zone:  op-node, op-geth (不可从 DMZ 直接访问)     │  │
│  │  │  Data Zone:  DB, HSM (仅 Core Zone 可访问)             │  │
│  │  │                                                        │  │
│  │  │  Zone 间通信: 通过安全组/防火墙规则严格控制              │  │
│  │  └────────────────────────────────────────────────────────┘  │
│  │                                                               │
│  │  ┌────────────────────────────────────────────────────────┐  │
│  │  │  Layer 3: 传输加密                                      │  │
│  │  │                                                        │  │
│  │  │  外部: TLS 1.3 (HTTPS, WSS)                            │  │
│  │  │  内部: mTLS (组件间通信)                                 │  │
│  │  │  L1 连接: 通过 VPN 或专线访问 Ethereum 节点              │  │
│  │  │  备份: AES-256-GCM 加密传输                             │  │
│  │  └────────────────────────────────────────────────────────┘  │
│  │                                                               │
│  │  ┌────────────────────────────────────────────────────────┐  │
│  │  │  Layer 4: 应用安全                                      │  │
│  │  │                                                        │  │
│  │  │  • 输入验证 (所有 RPC 请求)                              │  │
│  │  │  • SQL 注入防护 (参数化查询)                              │  │
│  │  │  • CSRF/XSS 防护 (Dashboard)                            │  │
│  │  │  • 依赖扫描 (Snyk / Dependabot)                         │  │
│  │  │  • 容器安全扫描 (Trivy)                                  │  │
│  │  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 安全审计流程

| 审计类型 | 频率 | 执行方 | 范围 | 标准 |
|---------|------|--------|------|------|
| **智能合约审计** | 每次部署/升级前 | 第三方审计公司 (Trail of Bits, OpenZeppelin) | ComplianceRegistry, PolicyExecutor, AuditLog | SCSVS |
| **渗透测试** | 每季度 | 第三方安全公司 | 全栈 (网络 + 应用 + API) | OWASP Top 10 |
| **代码安全审查** | 每次 PR | 内部 + 自动化工具 | 所有代码变更 | SAST/DAST |
| **密码学审计** | Phase 2-3 | 密码学专家 | ECIES, ZK 组件 | 专项 |
| **SOC 2 Type II** | 年度 | 认证审计师 | 运维流程 + 安全控制 | AICPA TSC |
| **ISO 27001** | 年度 | 认证机构 | 信息安全管理体系 | ISO/IEC 27001:2022 |

### 8.4 DDoS 防护

| 攻击类型 | 防护措施 | 组件 |
|---------|---------|------|
| **L3/L4 DDoS** | 云端清洗 + BGP 黑洞 | Cloudflare / AWS Shield |
| **L7 DDoS** | WAF 规则 + 速率限制 | Envoy + 自定义规则 |
| **RPC 滥用** | Per-user 速率限制 + 验证码 | Compliance RPC Proxy |
| **Mempool 攻击** | 交易池大小限制 + 策略过滤 | op-geth txpool |
| **L1 Bridge 攻击** | Gas 限制 + allowlist + TransactionFilterer | MantleOptimismPortal / MantleL1StandardBridge |

**安全补充**:
- 管理面板和审计 API 必须强制 MFA、短期凭证、审批流和完整会话审计，不得仅依赖静态 API key。
- 对外部 KYT/AML 供应商调用要设置熔断和降级策略；供应商故障时系统应转入"只允许低风险白名单交易"或"仅告警不放大阻断"的预定义模式，而不是随机失败。

---

## 第九章: 代码与基础设施改动清单

### 9.1 Phase 1: 企业准入 MVP (3-4 个月)

| # | 改动项 | 代码位置 | 改动类型 | 工作量 | 侵入性 |
|---|--------|---------|---------|--------|--------|
| 1.1 | RPC 认证代理 | 新服务 (Go) | **新增** | 2-4 周 | 零 (独立服务) |
| 1.2 | Sequencer 策略引擎 | `op-node/rollup/sequencing/sequencer.go` | **扩展** | 1-2 月 | 低 (hook 注入) |
| 1.3 | 交易池策略过滤 | `op-geth/core/txpool/` | **扩展** | 2-3 周 | 低 (过滤回调) |
| 1.4 | L1 边界 TransactionFilterer / allowlist | `MantleOptimismPortal` / `MantleL1StandardBridge` | **修改** | 2-4 周 | 中 (L1 合约) |
| 1.5 | ComplianceRegistry Predeploy (基础版) | 新 Predeploy 合约 | **新增** | 1-2 月 | 低 (Predeploy) |
| 1.6 | 审计事件采集器 | 新服务 (Go) | **新增** | 1 月 | 零 (独立服务) |
| 1.7 | 管理面板 (白名单 CRUD + 审计查询) | 新 Web 应用 | **新增** | 1 月 | 零 (独立应用) |
| 1.8 | 策略配置文件系统 | `op-node/` config | **扩展** | 1 周 | 低 (配置) |

**Phase 1 团队需求**: 2-3 名全栈 Go 工程师 + 1 名智能合约工程师
**Phase 1 累计工作量**: ~8 人月

### 9.2 Phase 2: 合约层增强 (6-9 个月)

| # | 改动项 | 代码位置 | 改动类型 | 工作量 | 侵入性 |
|---|--------|---------|---------|--------|--------|
| 2.1 | ComplianceRegistry 完整版 | Predeploy 合约升级 | **升级** | 1-2 月 | 低 |
| 2.2 | PolicyExecutor Predeploy | 新 Predeploy 合约 | **新增** | 2-3 月 | 低 |
| 2.3 | Transfer Hook (合规 Token 基类 / wrapper) | ERC-20 扩展合约 | **新增** | 1-2 月 | 低 |
| 2.4 | AuditLog Predeploy | 新 Predeploy 合约 | **新增** | 1 月 | 低 |
| 2.5 | 选择性披露 API | 新服务 (Go) | **新增** | 1-2 月 | 零 |
| 2.6 | 加密审计数据包 | 审计服务扩展 | **扩展** | 1 月 | 零 |
| 2.7 | 自动化合规报告生成 | 新服务 | **新增** | 1-2 月 | 零 |
| 2.8 | 外部合规系统集成 (KYT/AML API) | 中间件扩展 | **扩展** | 1 月 | 零 |

**Phase 2 团队需求**: 3-4 名工程师 + 2 名智能合约工程师
**Phase 2 累计工作量**: ~20 人月

### 9.3 Phase 3: 协议层可选升级 (12-18 个月)

| # | 改动项 | 代码位置 | 改动类型 | 工作量 | 侵入性 |
|---|--------|---------|---------|--------|--------|
| 3.1 | ZK 合规证明 (制裁筛查) | 新 Predeploy + 密码学库 | **新增** | 4-6 月 | 中 |
| 3.2 | Zone 隔离架构 | 全栈新增 | **新增** | 12-18 月 | 高 |
| 3.3 | 私有 DA 后端 | `op-alt-da/daclient.go` | **扩展** | 2-3 月 | 低 |
| 3.4 | 混合 DA 路由 | `op-batcher/` | **修改** | 2-3 月 | 中 |
| 3.5 | 跨 Zone 合规状态共享 | 新增协议 | **新增** | 3-4 月 | 中 |
| 3.6 | Compliance Precompile (可选) | `op-geth/core/vm/` | **修改** | 3-4 月 | 高 |

### 9.4 基础设施改动清单

| # | 改动项 | 涉及基础设施 | Phase | 优先级 |
|---|--------|-------------|-------|--------|
| I.1 | 部署 Load Balancer + TLS | HAProxy/Nginx, 证书管理 | 1 | P0 |
| I.2 | 部署 PostgreSQL (审计 DB) | PostgreSQL 15+, 流复制 | 1 | P0 |
| I.3 | 部署 Redis (缓存) | Redis 7+ Sentinel | 1 | P0 |
| I.4 | 部署 Prometheus + Grafana | 监控栈 | 1 | P0 |
| I.5 | 部署 Elasticsearch / Loki | 日志聚合 | 1 | P1 |
| I.6 | 配置 HSM | Google KMS / AWS CloudHSM / Vault | 1 | P0 |
| I.7 | 配置 VPN/专线 (L1 连接) | WireGuard / AWS Direct Connect | 1 | P1 |
| I.8 | 部署 Kafka / NATS (事件流) | 消息队列 | 2 | P1 |
| I.9 | 配置 S3/MinIO (备份存储) | 对象存储 + KMS 加密 | 1 | P1 |
| I.10 | 配置 CI/CD Pipeline | GitHub Actions / GitLab CI | 1 | P1 |
| I.11 | 部署 WAF + DDoS 防护 | Cloudflare / AWS Shield | 1 | P1 |
| I.12 | 配置 PagerDuty (告警) | 告警管理 | 1 | P1 |

---

## 附录

### 附录 A: 与 M2 横向对比结论的映射

| M2 结论 | 来源 | WHI-353 应用 |
|---------|------|-------------|
| Sequencer 完全可见性是合规资产 | WHI-346 §2.2.5 | Layer 3 Sequencer 策略引擎核心设计理念 |
| 中间件 MVP → 合约层 → 协议层演进 | WHI-346 §5 | Phase 1/2/3 渐进路径 |
| Prividium 四层纵深防御最完整 | WHI-338 §3 | Layer 1-4 四层合规栈设计参考 |
| TIP-403 precompile 级不可绕过 | WHI-340 §2.4 | Phase 3 可选 Compliance Precompile |
| Validium 是最 GDPR 友好架构 | WHI-338 §4.4 | GDPR 合规设计, Phase 2+ Validium 支持 |
| L1 强制交易是关键攻击面 | WHI-344 §1.2.2 | L1 边界 TransactionFilterer / allowlist (Phase 1 P0) |
| Predeploy 优于 Precompile | WHI-344 §4.3 | 所有链上合规组件使用 Predeploy |
| 多链架构支持公开+隐私共存 | WHI-338 §1.3 | Phase 3 Zone 架构 |
| ZK 合规证明是创新方向 | WHI-338 §4.1 | Phase 3 ZK 制裁筛查 |
| Canton Observer 模式是最成熟监管接口 | WHI-346 §2.3 | 选择性披露 API 设计参考 |
| 企业部署需多模式支持 | WHI-350 §3 | 四种部署模型矩阵 |
| EVM 兼容是底线约束 | WHI-350 §5.2 R1 | 所有设计维持完全 EVM 兼容 |

### 附录 B: 监管框架参考

| 监管框架 | 地区 | 对 Mantle Enterprise 的关键要求 | 设计覆盖 |
|---------|------|-------------------------------|---------|
| **MiCA** | 欧盟 | CASP 注册、AML/CTF、客户资产隔离、运营韧性 | Layer 3 合规检查 + Layer 4 AML 集成 + HA 部署 |
| **GDPR** | 欧盟 | 数据最小化、被遗忘权、跨境传输限制 | 选择性披露 + 链下可删除存储 + 本地部署选项 |
| **SEC/CFTC** | 美国 | 证券合规 (Howey Test)、交易报告、SAR | PolicyExecutor (合格投资者) + 自动报告 |
| **MAS** | 新加坡 | Project Guardian 要求、资产代币化标准 | ComplianceRegistry + 审计 API |
| **Basel III/IV** | 全球 | 资本充足率、风险权重 | Transfer Hook (金额限制) + 审计追踪 |
| **4AMLD/5AMLD** | 欧盟 | KYC/CDD、交易监控、可疑报告 | Layer 3 KYT + 自动 SAR 生成 |
| **Bank Secrecy Act** | 美国 | CTR ($10K+)、SAR | 阈值策略 + 自动报告 |

### 附录 C: 术语对照

| 术语 | 英文 | 定义 |
|------|------|------|
| 合规栈 | Compliance Stack | 分层的合规架构，从协议层到外部集成层 |
| 策略引擎 | Policy Engine | 在 Sequencer 层执行合规策略的软件组件 |
| 预部署合约 | Predeploy Contract | 在创世块中预部署的智能合约，可升级 |
| 选择性披露 | Selective Disclosure | 向特定方有条件暴露数据的能力 |
| 审计追踪 | Audit Trail | 不可篡改的操作记录链 |
| 加密审计包 | Encrypted Audit Package | 使用监管方公钥加密的审计数据包 |
| 传输规则 | Travel Rule | 要求金融机构传递交易双方身份信息的规则 |
| 可疑活动报告 | SAR (Suspicious Activity Report) | 向监管机构提交的可疑交易报告 |
| 货币交易报告 | CTR (Currency Transaction Report) | 超过阈值交易的强制报告 |
| 零知识合规证明 | ZK Compliance Proof | 不暴露 PII 的密码学合规验证 |

---

## 数据来源

本文档全部结论均来源于以下文件：

| 来源编号 | 文件 | 主要贡献 |
|---------|------|---------|
| WHI-341 | `m1-research/mantle/mantle-v2-architecture-baseline.md` | Mantle V2 架构基线、HSM 集成、自然插入点、Predeploy 模式 |
| WHI-346 | `m2-comparison/compliance/WHI-346-compliance-comparison.md` | 合规能力矩阵、审计模型对比、Sequencer 合规角色、MVP 方案 |
| WHI-340 | `m1-research/tempo-zones/WHI-340-tempo-code-analysis.md` | TIP-403 策略注册表、Zone 架构、加密桥接、审计数据流 |
| WHI-338 | `m1-research/prividium/WHI-338-prividium-architecture-deep-analysis.md` | 四层纵深防御、Validium DA、RBAC、ZK 合规证明、GDPR 分析 |
| WHI-350 | `m3-design/gap-analysis/WHI-350-gap-analysis.md` | Gap 矩阵、改造切入点、三阶段路径、风险评估 |

---

*本文档基于 2026 年 5 月 7 日完成的 M1/M2 研究成果和 M3 Gap 分析编制。所有设计均可追溯至具体来源文件。*
