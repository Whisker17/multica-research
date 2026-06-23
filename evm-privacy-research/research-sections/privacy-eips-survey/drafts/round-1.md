---
topic: "Privacy 相关 EIP 全景梳理（含检索方法论）"
project_slug: "evm-privacy-research"
topic_slug: "privacy-eips-survey"
github_repo: "Whisker17/multica-research"
round: 1
status: draft

artifact_paths:
  outline: "evm-privacy-research/outlines/privacy-eips-survey.md"
  draft: "evm-privacy-research/research-sections/privacy-eips-survey/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/privacy-eips-survey/final.md"

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23"
  outline_round: 2
  outline_commit: "233397184b2564748cb238a9cbbe8c4b27a062aa"
  items_covered: ["item-1", "item-2", "item-3", "item-4", "item-5", "item-6", "item-7"]
  fields_investigated: ["eip_number", "eip_status", "privacy_primitive", "deployment_layer", "whi254_requirement_map", "capability_boundary", "mantle_relevance", "crypto_primitive", "verification_url", "source_confidence", "companion_eips"]
  diagrams_produced: ["diagram-1", "diagram-2", "diagram-3", "diagram-4", "diagram-5"]
  source_requirement_coverage: "EIP/ERC status verified against ethereum/EIPs and ethereum/ERCs master + eips.ethereum.org rendered pages; Ethereum Magicians and ethresear.ch searched via search.json API with recorded query strings and result counts; WHI-254 framework referenced from final.md"
  verification_snapshot:
    eips_repo_master_sha: "a8862ae6653a12a2989b64a50eca5334cfe8b3cb"
    eips_repo_master_date: "2026-06-22T09:11:00Z"
    ercs_repo_master_sha: "56c2308c8d69e75e417bc2d2d551ff6f463ec18d"
    ercs_repo_master_date: "2026-06-22T22:03:44Z"
    access_date: "2026-06-23"

multica_issue_id: "3f53d683-eefb-4af0-ae59-8ee77f02c537"
report_issue_id: "68d01fa3-fdaa-4b11-b9e4-e449dfafe39c"
branch_name: "research/evm-privacy-research/privacy-eips-survey"
base_commit: "233397184b2564748cb238a9cbbe8c4b27a062aa"
language: "中文"
research_depth: "survey"
mode: "squad"

dependencies:
  - project_slug: "evm-privacy-research"
    topic_slug: "privacy-landscape-framework"
    multica_issue_id: "51a89bf9-8955-4ae4-914e-cc6920ffea9a"
    status: "done"
    usage: "引用 WHI-254 框架的 8 需求体系、6 技术家族、7 项被保护数据维度、5 轴 rubric、选择性披露 6 维向量、轻量级判定标准作为评估口径"
---

# Privacy 相关 EIP 全景梳理（含检索方法论）

> 本 section 为「Mantle 轻量级机构隐私方案」pre-research 系列的标准层版图文档。系统梳理 **ERC-7984 / ERC-7945 / VOSA 之外**所有与 privacy 相关的活跃/重要 EIP 与论坛草案，建立可复现的检索方法论，按隐私原语 × 层级 × 状态分类，并映射到 WHI-254 框架（`evm-privacy-research/research-sections/privacy-landscape-framework/final.md`）。

## 关于「URL + 访问日期 + commit SHA」溯源约定

本 section 所有 EIP/ERC 状态结论均按以下三元组溯源（验收标准 5）：

1. **URL**：`eips.ethereum.org` 渲染页面 + `github.com/ethereum/{EIPs|ERCs}` 源文件链接。
2. **访问日期**：统一为 **2026-06-23 (UTC)**，即检索截止日期。
3. **commit SHA**：状态核验快照锚定到核验时两个上游仓库的 master HEAD：
   - `ethereum/EIPs` master = `a8862ae6653a12a2989b64a50eca5334cfe8b3cb`（committer date 2026-06-22T09:11:00Z）
   - `ethereum/ERCs` master = `56c2308c8d69e75e417bc2d2d551ff6f463ec18d`（committer date 2026-06-22T22:03:44Z）
   - 已合并 EIP/ERC 的 frontmatter 状态以上述两个 master SHA 为准；**未合并的 open PR**（如 ERC-8302）以 PR head SHA 为准，逐条标注。

这意味着任何复核者可 `git checkout` 上述 master SHA，在 `EIPS/eip-{n}.md` / `ERCS/erc-{n}.md` 中验证本文引用的每条 `status` 字段。本 section 自身的 commit SHA 在 Artifact Ready 提交后由 Orchestrator 记录。

---

## Executive Summary

本 section 对以太坊隐私相关标准层进行了系统梳理，核心交付为：(1) 可复现的六通道检索方法论（含 Ethereum Magicians / ethresear.ch 逐查询结果数执行记录表）；(2) 候选/排除清单（截止 2026-06-23）；(3) EIP 分类表（原语 × 层级 × 状态 × Mantle 相关性）；(4) stealth address 双密钥能力边界深析；(5) EIP-8182 协议层 shielded pool 定位；(6) 隐私赋能基础设施与 EIP-8105 定性；(7) WHI-254 框架映射总表与 Mantle 相关性综合评估。

核心发现：

1. **隐私标准层呈三层结构**：协议层（Core，需硬分叉）以 EIP-8182（统一 shielded pool）为代表；应用层（ERC，合约即可部署）以 ERC-5564/6538（stealth）、ERC-8065（ZK wrapper）、ERC-8302/pERC-20（native private token, **Open ERC PR**）为代表；论坛/研究阶段以 EIP-8093、Privacy Pools 等为代表。

2. **能力边界必须显式标注，避免 capability-washing**：
   - **ERC-5564/6538 stealth addresses 仅提供收款方匿名（R3），不提供金额隐私（R1）或余额隐私（R2）**——金额与发送方在链上完全公开。这是本 section 反复强调的关键边界。
   - **EIP-8105 Encrypted Mempool 不是隐私提案**——其目标是抗 MEV/抗审查（R8），交易最终被公开解密，作者在 Motivation 中明确声明不改善用户隐私。归类为「相关但非隐私」。

3. **EIP-8141 Frame Transaction 是原生账户抽象（AA）提案，不是隐私提案**。Round 1 outline 曾误标为「Privacy Pool Withdrawal Fees」，已核验纠正。其 paymaster 功能对隐私池场景的 gas 代付有**间接赋能潜力**，但这是 AA 通用能力的一个推断性应用场景，**非 EIP-8141 的设计目标**——本文所有相关表述均保持推断语气并附直接源核验。

4. **Mantle 相关性三档分布**：High（纯合约 bolt-on：ERC-5564、ERC-6538、ERC-8065、Privacy Pools）；Medium（需自研适配或为 Open PR：EIP-8182 参考架构、ERC-8302/pERC-20）；Low（L1 协议层/硬分叉专属：EIP-7503、EIP-8141、EIP-8250、EIP-8105）。

5. **生态空白**：无任何已发现 EIP 覆盖 R4（业务逻辑/合约状态隐私）——该维度依赖 Aztec/TEE 等非标准方案；亦缺乏统一的 EIP 级合规-隐私桥接标准（R6+R7 标准化）。

---

## item-1: 检索方法论与候选/排除清单

### 1.1 检索数据来源（六通道）

| # | 数据来源 | 检索方式 | URL | 访问日期 |
|---|---------|---------|-----|---------|
| S1 | eips.ethereum.org | 关键词全文检索：`confidential` / `private` / `privacy` / `stealth` / `shielded` / `encrypt` / `zero-knowledge` / `zk` / `anonymous` / `obfuscate` / `hiding` | https://eips.ethereum.org | 2026-06-23 |
| S2 | ethereum/EIPs GitHub | Open PR 搜索 + master frontmatter 扫描 | https://github.com/ethereum/EIPs | 2026-06-23 |
| S3 | ethereum/ERCs GitHub | Open PR 搜索 + master frontmatter 扫描 | https://github.com/ethereum/ERCs | 2026-06-23 |
| S4 | Ethereum Magicians 论坛 | `search.json?q=` 关键词检索（见 1.2 执行记录） | https://ethereum-magicians.org | 2026-06-23 |
| S5 | ethresear.ch | `search.json?q=` 关键词检索（见 1.2 执行记录） | https://ethresear.ch | 2026-06-23 |
| S6 | EEA Privacy Working Group Report §06b | 报告引用的以太坊隐私标准列表 | https://entethalliance.github.io/wg-privacy/privacy-report.html | 2026-06-23 |

### 1.2 检索执行记录（截止日期 2026-06-23）

#### S2 — ethereum/EIPs GitHub open PR 搜索

| 查询字符串 | 结果数 | 隐私相关命中 |
|-----------|:------:|------------|
| `privacy repo:ethereum/EIPs is:open is:pr` | 5 | #11762 (Privacy-Native Fungible Tokens 早期编号轨迹) |
| `shielded OR encrypt repo:ethereum/EIPs is:open is:pr` | 1 | #11518 (Counterfactual Transaction — 非隐私) |

#### S3 — ethereum/ERCs GitHub open PR 搜索

| 查询字符串 | 结果数 | 隐私相关命中 |
|-----------|:------:|------------|
| `privacy OR private repo:ethereum/ERCs is:open is:pr` | 21 | **#1817 (ERC-8302 Private Fungible Tokens)**, #1373 (Privacy Address Format), #1680 (Encrypted Token), #1379 (Private ERC-20), #1681 (Cryptographic Amnesia) |
| `confidential repo:ethereum/ERCs is:open is:pr` | 3 | #1143 (Encrypted Data), #1361 (Encrypted Hashed Arguments) |
| `stealth repo:ethereum/ERCs is:open is:pr` | 0 | — |
| `zero-knowledge OR zk repo:ethereum/ERCs is:open is:pr` | 15 | #1747 (ZK Compliance Oracle), #1062 (Oracle-Permissioned ERC-20 w/ ZK), #1234 (MultiTrustCredential ZK), #1238 (ZK Proof Verification for Smart Accounts) |

#### S4 — Ethereum Magicians 论坛搜索（`search.json` API）

> **检索方式说明**：通过 `https://ethereum-magicians.org/search.json?q={query}` 获取结构化结果，结果数取 `grouped_search_result.post_ids` 长度。`topic:` 为论坛主题 ID，可拼接为 `https://ethereum-magicians.org/t/-/{topic_id}` 访问。

| 查询字符串 | 结果数 | 主要隐私相关命中（topic ID → 主题） |
|-----------|:------:|-----------------------------------|
| `privacy category:erc` | **0** | 类别限定查询返回空 —— Discourse 的 `category:` slug 与预期不符，关键词查询为有效通道（见下） |
| `confidential token` | **19** | 24735（confidential fungible tokens, pointer-based ≈ ERC-7984 讨论）、25694（ERC-7984 / EIP-8037 落地分析）、28214（FHE Fungible Token 新 ERC 提案）、26592（ERC-8085, PR #1359）、27832（VOSA-20 — 范围外）、17007（ERC-7551 Crypto 扩展） |
| `zero knowledge token` | **49** | 26006（ZWToken, ERC-8065 参考实现 zk.walletaa.com）、27277（Stealth Addresses for ZK Token Wrappers, ERC-8065 扩展）、26763（**EIP-8093 Private ERC-20 — ZK Burns**）、24180（Ant International ERC-20 ZK 扩展）、26452（INTMAX 隐私） |
| `stealth address` | **27** | 12888（Stealth Meta-Address Registry → ERC-6538）、28787（stealth-address writeup / ERC-6538 生产钱包）、15456（ERC-5564 gas funding 问题）、10614（PR #5566 stealth）、27277（ZK Token Wrapper stealth 扩展）、27540 / 27809（Stealth Address + Sub-Account） |
| `private transfer EIP` | **50** | **27889（A canonical private transfer system: one shared pool for ETH and ERC-20 → EIP-8182 讨论帖）**、28702 / 28796（Cyimon ERC-8287/pERC-20）、26452（INTMAX） |
| `shielded pool OR encrypted mempool` | **2** | 28168（EXEC_TX hook-based execution）、28702（Cyimon ERC Draft） |

#### S5 — ethresear.ch 搜索（`search.json` API）

> **检索方式说明**：通过 `https://ethresear.ch/search.json?q={query}` 获取结构化结果。结果数为 `grouped_search_result.post_ids` 长度（Discourse 默认上限 50，标注「50」者表示命中已达分页上限，实际可能更多）。

| 查询字符串 | 结果数 | 主要隐私相关命中（topic ID → 帖子） |
|-----------|:------:|-----------------------------------|
| `private token` | **50**（达上限） | 25200（**pERC20 草案** https://ethresear.ch/t/perc20-private-token-standard-draft/25200）、7754（private smart contracts）、5965（早期 Ethereum 隐私综述） |
| `privacy EIP` | **50**（达上限） | 25089（**EIP-8287/pERC-20 原始帖** https://ethresear.ch/t/eip8287-privacy-native-fungible-token-standard-draft/25089）、18664（**EIP-7503 RFC Private Transfers** https://ethresear.ch/t/rfc-eip7503-private-transfers/18664）、24566（EIP-7503 problem statement）、18875（Nobitex EIP-7503 PoC） |
| `encrypted mempool` | **50**（达上限） | 22129（anti-collusion threshold encrypted mempools）、21717（distributed encrypted mempool）、21834（smart account encrypted mempools）、24327（GhostPool admission metadata） |
| `shielded pool` | **33** | 23624（tracing bad funds through shielded pools）、25200（pERC20 引用 EIP-8182）、16297（meta-keypair 多地址） |
| `stealth address` | **33** | 20897（Curvy protocol — pairing-based stealth）、15437（post-quantum stealth addresses）、16213（Ethereum Fellows stealth 研究）、16774（Stealth Address AA Plugin） |

**Magicians/ethresear.ch 检索小结**：关键词检索为有效通道；类别限定查询（`category:erc`）在 Magicians 上返回空，已记录为方法论限制。命中确认了本 survey 的全部正式 EIP（8182/8065/8302/7503/8141/8250/8105/5564/6538），并新发现一个论坛阶段提案 **EIP-8093（Private ERC-20 ZK Burns）** 及若干范围外/早期提案（VOSA-20、Curvy、INTMAX、cWETH 等）。

### 1.3 候选清单（通过所有排除规则）

| 编号 | 标题 | 状态 | 类别 | 分类标签 |
|------|------|------|------|---------|
| ERC-5564 | Stealth Addresses | Final | ERC | recipient-anonymity |
| ERC-6538 | Stealth Meta-Address Registry | Final | ERC | recipient-anonymity (registry) |
| EIP-8182 | Private ETH and ERC-20 Transfers | Draft | Core | value-confidentiality + graph-unlinkability |
| EIP-7503 | Zero-Knowledge Wormholes | Stagnant | Core | graph-unlinkability |
| ERC-8065 | Zero Knowledge Token Wrapper | Draft | ERC | value-confidentiality + graph-unlinkability |
| ERC-8302 (pERC-20) | Private Fungible Tokens | **Open ERC PR #1817** | ERC | value-confidentiality |
| EIP-8093 | Private ERC-20 — ZK Burns | 论坛草案（Magicians topic 26763） | ERC（拟） | graph-unlinkability |
| Privacy Pools (0xBow) | Compliance-gated privacy pool | 非正式（无 EIP 编号） | 应用层 | compliance-gated |
| EIP-8250 | Keyed Nonces for Frame Transactions | Draft | Core | privacy-enabling-infrastructure |
| EIP-8141 | Frame Transaction (native AA) | Draft | Core | **related-non-privacy**（间接赋能） |
| EIP-8105 | Universal Enshrined Encrypted Mempool | Draft | Core | **related-non-privacy**（抗 MEV） |

### 1.4 排除清单

| 编号/方案 | 排除规则 | 原因 |
|----------|---------|------|
| ERC-7984 (Confidential Fungible Token) | EX-3 | 由独立 issue 覆盖（本 survey 范围外） |
| ERC-7945 (Confidential Transactions Supported Token) | EX-3 | 由独立 issue 覆盖 |
| VOSA / VOSA-20 (Magicians topic 27832) | EX-3 | 由独立 issue 覆盖；ERC-5564/6538 为其基础原语，本文在 item-3 说明关系边界 |
| Tornado Cash 类 mixer | EX-4 | 纯消费者混币器，无合规准入 |
| Monero / Zcash 主链 | EX-5 | 非 EVM 生态（Zcash viewing-key 概念影响在 item-3 提及但主链本身排除） |
| ERC-3643 (T-REX) | 部分纳入 item-5/item-7 作为隐私相邻参照 | 非隐私 EIP；仅通过 KYC 准入提供访问控制，非密码学隐私 |

### 1.5 排除标准定义

| 规则 | 说明 |
|------|------|
| EX-1: 已 Withdrawn | 状态为 Withdrawn 的 EIP/ERC 排除 |
| EX-2: 明确非隐私目标 | 主要目标非用户/交易隐私（如 EIP-8105），单列「相关但非隐私」而非完全排除 |
| EX-3: 范围内其他 issue 已覆盖 | ERC-7984、ERC-7945、VOSA |
| EX-4: 纯消费者隐私/混币器 | 无合规准入的纯混币器 |
| EX-5: 非 EVM 生态 | 与 EVM 无交互的纯非 EVM 隐私方案 |

### 1.6 不可核验提案处理

- **EIP-8093（Private ERC-20 — ZK Burns）**：仅在 Ethereum Magicians（topic 26763）以讨论帖形式存在，**截至 2026-06-23 未在 `ethereum/EIPs` master（SHA `a8862ae6`）找到对应 `eip-8093.md` 文件**，eips.ethereum.org 亦无渲染页面。状态标注为「论坛草案，正式 EIP 状态不可核验」。尝试的核验方式：(1) GitHub 仓库路径 `EIPS/eip-8093.md` 检索；(2) eips.ethereum.org/EIPS/eip-8093 访问；(3) Magicians 帖文 frontmatter 阅读。`[unverified: attempted via github master tree + eips.ethereum.org + magicians thread frontmatter, 2026-06-23]`
- **EIP-8250 URL**：`eips.ethereum.org/EIPS/eip-8250` 渲染页面可访问性在本轮以 GitHub master 源文件为主核验通道；若官方渲染页缺失，以 `EIPS/eip-8250.md`（master SHA `a8862ae6`）frontmatter 为准。
- **Privacy Pools / cWETH**：无正式 EIP 编号，按论坛/研究阶段方案处理，状态标注「非正式提案」。

- **Priority**: high · **Dependencies**: none

---

## item-2: EIP 分类表 — 隐私原语 × 层级 × 状态 × Mantle 相关性

### 2.1 主分类表

> 状态核验锚点：`ethereum/EIPs` master `a8862ae6653a12a2989b64a50eca5334cfe8b3cb`，`ethereum/ERCs` master `56c2308c8d69e75e417bc2d2d551ff6f463ec18d`，访问日期 2026-06-23。

| EIP 编号 | 标题 | 状态 | 类别 | 隐私原语 | 部署层级 | WHI-254 映射 | Mantle 相关性 | 能力边界摘要 |
|---------|------|------|------|---------|---------|------------|:------------:|------------|
| **ERC-5564** | Stealth Addresses | Final | ERC | 收款方匿名 | 应用层 | R3 ✅, R5 ⚠️ | **High** | **仅收款方匿名；不隐藏金额(R1)/余额(R2)/发送方** |
| **ERC-6538** | Stealth Meta-Address Registry | Final | ERC | 地址发现（registry） | 应用层 | 补充 R3 | **High** | 仅为 stealth meta-address 发布注册表，本身无隐私计算 |
| **EIP-8182** | Private ETH and ERC-20 Transfers | Draft | Core | 值级隐私 + 图解耦 | 协议层 | R1✅ R2✅ R3✅ R5✅ R4❌ | **Medium** | 全链统一匿名集；值级隐私；不支持通用合约隐私执行 |
| **EIP-7503** | Zero-Knowledge Wormholes | **Stagnant** | Core | 图解耦（burn-and-mint） | 协议层 | R5✅ R3⚠️ | **Low** | 依赖 L1 burn-and-mint 语义；Stagnant；需 EIP-7708 |
| **ERC-8065** | Zero Knowledge Token Wrapper | Draft | ERC | 值级隐私 + 图解耦 | 应用层 | R1✅ R2⚠️ R5✅ | **High** | wrapper 模式，每合约独立匿名集；收款方匿名取决于实现 |
| **ERC-8302** (pERC-20) | Private Fungible Tokens | **Open ERC PR #1817** | ERC | 值级隐私 | 应用层 | R1✅ R2✅ R5⚠️ | **Medium** | 全新接口替代 ERC-20；内置 blacklist；总供应量公开；**未合并标准** |
| **EIP-8093** | Private ERC-20 — ZK Burns | 论坛草案（不可核验） | ERC（拟） | 图解耦 | 应用层 | R5✅ | **Medium** | ZK proof-of-burn 扩展；正式 EIP 状态不可核验 |
| **Privacy Pools** | 0xBow 合规隐私池 | 非正式 | 应用层 | 合规门控隐私 | 应用层 | R5✅ R6✅ R7⚠️ | **High** | Association Sets 合规证明；纯合约部署 |
| **EIP-8250** | Keyed Nonces for Frame TX | Draft | Core | 隐私赋能基础设施 | 协议层 | 间接 R5/R3 | **Low** | EIP-8141 配套；keyed nonce 防发送方侧交易关联 |
| **EIP-8141** | Frame Transaction (native AA) | Draft | Core | **相关但非隐私** | 协议层 | 间接 R5（推断） | **Low** | 原生 AA；paymaster **可能**间接赋能隐私池 gas 代付（推断，非设计目标） |
| **EIP-8105** | Universal Enshrined Encrypted Mempool | Draft | Core | **相关但非隐私** | 协议层 | R8✅，R1-R5❌ | **Low** | 抗 MEV/抗审查；交易最终公开解密；**非隐私提案** |

### 2.2 关键标注（验收标准 3）

1. **ERC-5564/6538 能力边界**：stealth addresses **仅提供收款方匿名（R3），不提供金额隐私（R1）或余额隐私（R2）**。原因见 item-3：ECDH 仅混淆收款*地址*，转账金额与发送方地址在链上明文可见。
2. **EIP-8105 分类**：**相关但非隐私**——目标为抗 MEV/抗审查（R8），交易仅在 pre-confirmation 阶段临时加密，入块后公开解密。作者在 Motivation 明确声明不改善用户隐私（见 item-6）。
3. **EIP-8141 分类**：**相关但非隐私**——核心为原生账户抽象。其隐私关联为推断性间接赋能，非设计目标（见 item-6）。
4. **EIP-8182 定位**：唯一的协议层统一匿名集方案，与应用层碎片化匿名集形成分工（见 item-4）。

- **Priority**: high · **Dependencies**: item-1

---

## item-3: Stealth Address 双密钥机制深度解析与能力边界

### 3.1 核心机制（ERC-5564 + ERC-6538）

- **来源**：ERC-5564 https://eips.ethereum.org/EIPS/eip-5564 ；ERC-6538 https://eips.ethereum.org/EIPS/eip-6538 。状态 Final，核验锚点 `ethereum/ERCs` master `56c2308c`，访问日期 2026-06-23。Vitalik Buterin 为 ERC-5564 共同作者。
- **双密钥结构**：每个接收者持有 **spending key（花费密钥）** 与 **viewing key（查看密钥）**。
- **Stealth Meta-Address**：由 spending public key + viewing public key 编码，通过 ERC-6538 registry（部署于 `0x6538...6538` 单例地址）发布。
- **地址派生（SECP256k1 ECDH）**：发送方用接收方的 stealth meta-address + 一次性临时密钥，经 ECDH 派生出一次性 stealth address，并通过 ERC-5564 单例合约（`0x5564...5564`）的 `Announcement` 事件广播 ephemeral pubkey + view tag。
- **接收方扫描**：接收方用 viewing key 扫描所有 `Announcement` 事件（view tag 加速过滤），识别属于自己的交易；用 spending key 控制花费。

### 3.2 能力边界（CRITICAL，验收标准 3）

| 维度 | 是否保护 | 说明 |
|------|:-------:|------|
| 收款方身份 (R3) | ✅ 保护 | 每笔交易生成新 stealth address，外部观察者无法将多笔收款关联到同一接收者 |
| 转账金额 (R1) | ❌ **不保护** | 转账金额在链上**完全公开可见** |
| 账户余额 (R2) | ❌ **不保护** | 余额虽分散到多个 stealth address，但每个地址余额公开可查 |
| 发送方身份 | ❌ **不保护** | 发送方地址完全公开 |
| 交易图 (R5) | ⚠️ 部分 | 观察者无法确认收款方身份，但 from→stealth address 的流向可见；deposit/扫描行为可能泄露元数据 |

**根因**：stealth address 是**地址层匿名**而非**值层加密**。ECDH 解决的是「如何让发送方在不暴露接收方公开地址的前提下完成定向支付」，它不涉及对金额的承诺/加密。因此 stealth 与值级隐私（EIP-8182/ERC-8065）是**正交且可组合**的两类原语。

### 3.3 WHI-254 框架映射

- **技术家族**：ZKP 类（基于 SECP256k1 ECDH 的密码学隐私原语，非 ZK-SNARK proof）。
- **选择性披露 6 维向量**（对齐 WHI-254 item-4）：`(authority=key-holder, trigger=viewing-key-share, payload=identity, scope=per-tx, revocability=one-time, leakage=graph+amount+existence)`。
- **轻量级判定**（对齐 WHI-254 item-5）：纯合约部署，无新链/新桥/全节点/硬分叉 → **通过全部一票否决，属轻量级 bolt-on**。

### 3.4 调查要点与生态信号

- **gas funding 问题**：Magicians topic 15456 讨论 ERC-5564 接收者在 stealth address 上无 gas 的难题——这是 stealth 落地的已知摩擦点，也是后文 EIP-8141 paymaster「间接赋能」推断的来源语境之一。
- **扫描性能**：接收者需扫描全部 `Announcement` 事件，view tag 将平均解密尝试降至约 1/256，但仍是 L2 大规模部署的性能考量。
- **后续演进**：post-quantum stealth（ethresear.ch topic 15437）、Curvy pairing-based stealth（topic 20897）、Stealth Address AA Plugin（topic 16774）显示活跃演进。
- **与 VOSA 的边界**（范围外）：ERC-5564/6538 提供基础 stealth 原语；VOSA（Verifiable Obfuscated Stealth Addresses，Magicians topic 27832 的 VOSA-20 为其 token 形态）在此之上添加可验证混淆，由独立 issue 覆盖。

**Mantle 相关性：High**——可直接在 Mantle L2 部署 ERC-5564/6538 合约（沿用主网单例地址范式），零协议层修改。

- **Priority**: high · **Dependencies**: item-1, item-2

---

## item-4: EIP-8182 协议层 Shielded Pool 定位与架构分析

### 4.1 核心定位

- **来源**：https://eips.ethereum.org/EIPS/eip-8182 ；`ethereum/EIPs` master `a8862ae6`，`EIPS/eip-8182.md`，访问日期 2026-06-23。Magicians 讨论帖：topic 27889（"A canonical private transfer system for Ethereum: one shared pool for ETH and ERC-20 tokens"）。
- **状态**：Draft（Core）。作者 Tom Lehman（@RogerPodacter, Facet）。
- **定位**：以太坊**协议层**（Core EIP）的 shielded pool 提案，通过硬分叉引入系统合约，为 ETH 与任意 ERC-20 提供原生隐私转账。与应用层方案的核心差异：**全链统一匿名集**（所有用户共享同一 shielded pool），而非应用层碎片化匿名集。

### 4.2 技术架构

| 架构要素 | EIP-8182 设计 |
|---------|-------------|
| 模型 | UTXO（note-based，非 account-based） |
| 证明系统 | Groth16 on BN254 |
| 部署方式 | 系统合约（system contract），硬分叉激活 |
| 管理密钥 | 无 admin key，无 proxy，不可升级 |
| 目标升级 | Hegota 硬分叉（计划 H2 2026） |
| 支持资产 | ETH + 任意 ERC-20 |
| 防双花 | Nullifier 机制 |

### 4.3 隐私能力映射（WHI-254 维度）

| WHI-254 维度 | 保护级别 | 机制 |
|-------------|:-------:|------|
| R1 金额隐私 | ✅ 完全 | commitment 隐藏金额 |
| R2 余额隐私 | ✅ 完全 | UTXO 模型，余额分散在加密 notes |
| R3 对手方身份 | ✅ 完全 | 统一匿名集，接收者不可识别 |
| R5 交易图 | ✅ 完全 | nullifier 防双花同时保持不可链接性 |
| R4 业务逻辑/状态 | ❌ 不保护 | 仅值级隐私，不支持通用合约隐私执行 |
| R6 合规 | ⚠️ 待定 | 提案提及 Privacy Pools 兼容性，具体机制待确认 |

### 4.4 隐私赋能基础设施（推断性间接关系，非 EIP-8182 专属配套）

> **重要措辞约束（验收标准 + outline caveat）**：以下两个 EIP 是**原生账户抽象提案**，不是隐私提案，也不是 EIP-8182 的官方配套。它们对隐私池的助益属于**推断性间接赋能**，不得表述为其设计目标。

- **EIP-8141: Frame Transaction**（Draft, Core）——Vitalik Buterin 等提出的原生 AA 提案，引入 frame-based 交易执行模型（VERIFY + EXECUTE frames）、新交易类型与 paymaster 机制。**非隐私提案**。*推断性*隐私关联：paymaster 允许第三方代付 gas，则隐私池用户**可能**无需从公开地址给 stealth/shielded 地址充值 gas（缓解 item-3 §3.4 的 gas funding 问题，从而减少 funding-link 暴露）。此为 AA 通用能力的一个推断应用场景，**非 EIP-8141 设计目标**。`[verified: github.com/ethereum/EIPs/blob/master/EIPS/eip-8141.md @ a8862ae6; eips.ethereum.org/EIPS/eip-8141, 2026-06-23]`
- **EIP-8250: Keyed Nonces for Frame Transactions**（Draft, Core）——Thomas Thiery, Toni Wahrstätter, Lightclient, Vitalik Buterin 提出。将 EIP-8141 frame transaction 的单一 sender nonce 替换为 `(nonce_key, nonce_seq)` 双部分系统。*隐私赋能效果*：不同 key 下交易相互独立，观察者无法通过连续递增 nonce 关联同一发送方的多笔交易——对隐私池共享 sender 场景尤其有用。是 **EIP-8141 的配套（非 EIP-8182 的配套）**。`[verified: github.com/ethereum/EIPs/blob/master/EIPS/eip-8250.md @ a8862ae6, 2026-06-23]`

### 4.5 协议层 vs 应用层方案对比

| 维度 | EIP-8182（协议层） | ERC-8065（应用层 wrapper） | ERC-8302/pERC-20（应用层 native, Open PR） |
|------|-------------------|-------------------------|------------------------|
| 匿名集 | 全以太坊统一 | 每个 wrapper 合约独立 | 每个 pERC-20 token 独立 |
| 部署条件 | 以太坊硬分叉 | 合约部署即可 | 合约部署即可（标准未合并） |
| 支持资产 | ETH + 任意 ERC-20 | ERC-20/721/1155/6909 | 仅 fungible token（替代 ERC-20） |
| 隐私层级 | 值级（R1+R2+R3+R5） | 值级 | 值级 |
| 合规机制 | Privacy Pools 兼容（待确认） | 继承底层 token 合规 | 内置 blacklist，总供应量公开 |

### 4.6 调查要点

- Hegota 硬分叉时间线与 EIP-8182 inclusion 状态待持续跟踪（ethresear.ch topic 25200 显示 pERC-20 已引用 EIP-8182 作为协议层方向）。
- Groth16 BN254 的 gas 成本与 prover 时间需后续基准测试。
- Privacy Pools 合规层与 EIP-8182 的集成细节待确认。

**Mantle 相关性：Medium**——EIP-8182 设计为 L1 硬分叉，Mantle L2 无法直接受益；但其 UTXO + Groth16 + nullifier 架构可作为 Mantle 自建 shielded pool 的参考设计。

- **Priority**: high · **Dependencies**: item-1, item-2

---

## item-5: 应用层隐私 Token 标准 — ERC-8065, ERC-8302/pERC-20 及其他

### 5.1 ERC-8065: Zero Knowledge Token Wrapper

| 属性 | 值 |
|------|------|
| 状态 | Draft（ERC） |
| 来源 | https://eips.ethereum.org/EIPS/eip-8065 ；`ethereum/ERCs` master `56c2308c`，访问日期 2026-06-23 |
| 创建日期 | 2025-10-18 |
| 作者 | Jiahui Cui (@doublespending), 0xZPL |
| 核心机制 | EIP-7503 风格 burn-and-remint，ZK proof 证明 burn 有效后 remint 等值 token |
| 支持资产 | ERC-20 / ERC-721 / ERC-1155 / ERC-6909 |
| 隐私能力 | 打破链上可追踪性（R5），金额可隐藏（R1）；收款方匿名取决于实现 |
| 合规机制 | 继承底层 token 合规逻辑 |
| 生态信号 | 参考实现 ZWToken（Magicians topic 26006, zk.walletaa.com）；stealth 扩展提案（topic 27277） |

**Mantle 相关性：High**——纯合约部署，可直接在 Mantle L2 落地。

### 5.2 ERC-8302 / pERC-20: Private Fungible Tokens

| 属性 | 值 |
|------|------|
| 状态 | **Open ERC PR #1817**（非已合并 Draft）——`ethereum/ERCs` PR #1817，文件 `ERCS/erc-8302.md`，PR head SHA `ffaa99334cec`，state=open |
| 来源 | https://github.com/ethereum/ERCs/pull/1817 （访问日期 2026-06-23）；ethresear.ch topic 25200 / 25089 |
| 类别 | ERC（应用层） |
| 创建日期 | 2026-06-03 ~ 2026-06-09（ethresear.ch 原始帖） |
| 作者 | Cyimon (@Cyimon) |
| PR 历史 | PR #1796（`erc-8287.md`, "Privacy-Native Fungible Tokens"）→ **已关闭**；PR #1817（`erc-8302.md`, "Private Fungible Tokens"）→ **当前 open** |
| 核心机制 | UTXO/note-based + Groth16 + Poseidon hash commitments，**完全替代 ERC-20 接口**（无 balanceOf/approve/allowance）；扩展版新增 ZIP-32 subaccount-based approve/allowance/transferFrom |
| 隐私能力 | R1 金额 + R2 余额；R5 部分（依实现） |
| 合规机制 | 内置 blacklist，总供应量公开可见 |
| 特殊说明 | 非 wrapper，而是全新接口——token 自创建即具隐私属性；与 ERC-20 capability-complete 但 ABI 不兼容 |
| source_confidence | GitHub PR #1817 直接核验（state=open, head `ffaa9933`）；PR #1796 关闭确认 |

**Mantle 相关性：Medium**——纯合约可部署，但作为**未合并标准**（Open PR），接口仍可能变动；新发 privacy-first token 适用，存量 ERC-20 迁移成本高。

### 5.3 其他候选

- **EIP-7503: Zero-Knowledge Wormholes**——**Stagnant**（Core）。来源 https://eips.ethereum.org/EIPS/eip-7503 ；`ethereum/EIPs` master `a8862ae6`。burn-and-mint + ZK proof 的原始提案，ERC-8065 引用其设计模式。依赖 EIP-7708。ethresear.ch RFC topic 18664、Nobitex PoC topic 18875。**Mantle 相关性：Low**（Core EIP，依赖 L1 burn 语义）。
- **EIP-8093: Private ERC-20 — ZK Burns**——论坛草案（Magicians topic 26763）。扩展 ZK proof-of-burn 实现 token 隐私。**正式 EIP 状态不可核验**（master 树无 `eip-8093.md`，见 item-1 §1.6）。**Mantle 相关性：Medium**（若标准化，纯合约可部署）。
- **Privacy Pools (0xBow)**——非正式 EIP，应用层。Association Sets 实现合规门控隐私（R6+R5）。Vitalik 背书。**Mantle 相关性：High**（纯合约部署）。
- **ERC-3643 (T-REX)**——非隐私 EIP，通过 KYC/合规准入提供访问控制（非密码学隐私），作为隐私相邻参照纳入。**Mantle 相关性：High**。

### 5.4 定位分工

| 方案 | 设计哲学 | 适用场景 | Mantle 相关性 |
|------|---------|---------|:------------:|
| ERC-8065 | Wrapper——为现有 token 加隐私 | 存量 ERC-20/721 需隐私增强 | High |
| ERC-8302/pERC-20 | Native——token 自创建即隐私（Open PR） | 新发 privacy-first token | Medium |
| EIP-8093 | Burn 扩展（不可核验） | ZK burn 隐私 | Medium |
| Privacy Pools | Compliance——合规门控隐私池 | 需 AML/合规证明场景 | High |

- **Priority**: high · **Dependencies**: item-1, item-2

---

## item-6: 隐私赋能基础设施（EIP-8141, EIP-8250）及 EIP-8105 定性

### 6.1 关键修正说明（Round 1 outline 误标已纠正）

Round 1 outline 曾将 EIP-8141 误标为 "Privacy Pool Withdrawal Fees"（EIP-8182 配套）。经 GitHub 源文件核验（`ethereum/EIPs` master `a8862ae6`, `EIPS/eip-8141.md`；eips.ethereum.org/EIPS/eip-8141, 2026-06-23），EIP-8141 实为 **"Frame Transaction"**——原生账户抽象提案。部分二手媒体（如 Blockonomi）将其 paymaster 在隐私池场景的应用误报为 EIP 本身目标。**目前不存在编号为 EIP-8141 的 privacy-pool-withdrawal-fee 专属提案**；该概念仅作为 EIP-8141 paymaster 的*推断应用场景*被讨论。`[source_confidence: GitHub YAML 核验优先于二手媒体]`

### 6.2 EIP-8141: Frame Transaction（原生账户抽象）

| 属性 | 值 |
|------|------|
| 状态 | Draft（Core） |
| 来源 | https://eips.ethereum.org/EIPS/eip-8141 ；`EIPS/eip-8141.md` @ master `a8862ae6`，2026-06-23 |
| 创建日期 | 2026-01-29 |
| 作者 | Vitalik Buterin 等 |
| 核心功能 | frame-based 交易（VERIFY + EXECUTE frames）、新交易类型、paymaster 代付 gas |
| **分类** | **相关但非隐私**——核心为原生 AA，非隐私提案 |
| 隐私间接赋能（推断） | paymaster *可能*使隐私池用户免于从公开地址充值 gas（缓解 funding-link 暴露）——AA 通用能力的推断应用，**非设计目标** |
| WHI-254 映射 | 不直接满足 R1-R8；paymaster *推断性*间接赋能 R5 |
| Mantle 相关性 | Low——L1 协议层 AA 变更；Mantle L2 有独立 AA 路径 |

### 6.3 EIP-8250: Keyed Nonces for Frame Transactions

| 属性 | 值 |
|------|------|
| 状态 | Draft（Core） |
| 来源 | `EIPS/eip-8250.md` @ master `a8862ae6`，2026-06-23（若 eips.ethereum.org 渲染页缺失，以 master 源文件为准） |
| 作者 | Thomas Thiery, Toni Wahrstätter, Lightclient, Vitalik Buterin |
| 核心功能 | 单一 sender nonce → `(nonce_key, nonce_seq)` 双部分系统 |
| **分类** | **隐私赋能基础设施**——EIP-8141 的配套（非 EIP-8182 配套），有显著隐私赋能效果 |
| 隐私赋能机制 | 不同 key 下交易 replay-independent，观察者无法通过递增 nonce 关联同一发送方多笔交易；对隐私池共享 sender 场景尤其重要 |
| WHI-254 映射 | 间接赋能 R5（图解耦）、R3（发送方侧不可关联） |
| Mantle 相关性 | Low——依赖 EIP-8141 Frame Transaction（L1 协议层变更） |

### 6.4 EIP-8105: Universal Enshrined Encrypted Mempool — 定性分析

| 属性 | 值 |
|------|------|
| 状态 | Draft（Core） |
| 来源 | https://eips.ethereum.org/EIPS/eip-8105 ；`EIPS/eip-8105.md` @ master `a8862ae6`，2026-06-23 |
| 创建日期 | 2025-12-17 |
| 作者 | Jannik Luhn (@jannikluhn), Shutter Network |
| 核心功能 | 方案无关的加密 mempool——交易入块前保持加密 |
| 支持解密方案 | 阈值加密 / MPC 委员会 / TEE / 延迟加密 / FHE |
| 新增交易类型 | Type 0x05（加密交易）、Type 0x06（解密密钥） |
| 依赖 | EIP-7732 (ePBS) |

**为何分类为「相关但非隐私」（验收标准 3）**：

1. **作者明确声明**：EIP-8105 Motivation 指出目标**不是**改善用户隐私（交易最终被公开揭示）。
2. **临时加密而非永久隐私**：交易仅在 pre-confirmation 阶段加密，入块后公开解密，金额/参与方/逻辑对公众完全可见。
3. **目标是 R8 而非 R1-R5**：保护执行策略（防 MEV/front-running/sandwich），对齐 WHI-254 R8。
4. **生态信号**：ethresear.ch 大量相关研究（topic 22129/21717/21834/24327）聚焦 MEV/抗合谋/admission metadata，均属执行策略保护范畴而非交易数据持久隐私。

**WHI-254 映射**：R8（执行策略保护）。不满足 R1-R5。
**Mantle 相关性：Low**——需 L1 共识层变更（依赖 ePBS）。Mantle L2 sequencer 架构不同于 L1 公共 mempool，MEV 保护需 private sequencing 等不同方案。

- **Priority**: high · **Dependencies**: item-2, item-4

---

## item-7: WHI-254 框架映射总表与 Mantle 相关性综合评估

### 7.1 WHI-254 8 需求覆盖矩阵

> ✅ 完全覆盖 / ⚠️ 部分覆盖 / ❌ 不覆盖。映射依据 WHI-254 final.md 的 R1-R8 定义。

| EIP | R1 金额 | R2 余额 | R3 身份 | R4 逻辑/状态 | R5 图 | R6 合规 | R7 披露 | R8 MEV |
|-----|:------:|:------:|:------:|:-----------:|:----:|:------:|:------:|:------:|
| ERC-5564 | ❌ | ❌ | ✅ | ❌ | ⚠️ | ❌ | ⚠️ viewing-key | ❌ |
| ERC-6538 | ❌ | ❌ | ⚠️ 补充 | ❌ | ❌ | ❌ | ❌ | ❌ |
| EIP-8182 | ✅ | ✅ | ✅ | ❌ | ✅ | ⚠️ | ⚠️ | ❌ |
| EIP-7503 | ⚠️ | ❌ | ⚠️ | ❌ | ✅ | ⚠️ pool | ❌ | ❌ |
| ERC-8065 | ✅ | ⚠️ | ⚠️ | ❌ | ✅ | ❌ | ❌ | ❌ |
| ERC-8302/pERC-20 | ✅ | ✅ | ⚠️ | ❌ | ⚠️ | ⚠️ blacklist | ❌ | ❌ |
| EIP-8093 | ⚠️ | ❌ | ⚠️ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Privacy Pools | ❌ | ❌ | ⚠️ | ❌ | ✅ | ✅ | ⚠️ | ❌ |
| EIP-8250 | ❌ | ❌ | ⚠️ 间接 | ❌ | ⚠️ 间接 | ❌ | ❌ | ❌ |
| EIP-8141 | ❌ | ❌ | ❌ | ❌ | ⚠️ 推断 | ❌ | ❌ | ❌ |
| EIP-8105 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### 7.2 5 轴 Rubric 预填充（对齐 WHI-254 diagram-2）

| EIP | 轴1 密码学路线 | 轴2 数据维度 | 轴3 信任模型 | 轴4 部署形态 | 轴5 合规披露 |
|-----|-------------|------------|------------|------------|------------|
| ERC-5564/6538 | ECDH (SECP256k1) | 仅身份(R3) | Cryptographic | bolt-on 合约（轻量级） | key-holder / viewing-key-share |
| EIP-8182 | Groth16 BN254 + nullifier | 值级全覆盖(R1/R2/R3/R5) | Cryptographic | 协议层硬分叉（重量级） | Privacy Pools 兼容（待确认） |
| ERC-8065 | ZK burn-and-remint | 值级(R1/R5) | Cryptographic | bolt-on 合约（轻量级） | 继承底层 token |
| ERC-8302/pERC-20 | Groth16 + Poseidon | 值级(R1/R2) | Cryptographic | 合约（轻量级，Open PR） | 内置 blacklist |
| EIP-7503 | ZK proof-of-burn | 图(R5) | Cryptographic | 协议层（重量级，Stagnant） | privacy pool 机制 |
| Privacy Pools | ZK + Association Set | 图+合规(R5/R6) | Cryptographic + Org | bolt-on 合约（轻量级） | association-set / compliance-gate |
| EIP-8250 | keyed nonce | 间接 R5/R3 | — (基础设施) | 协议层（重量级） | — |
| EIP-8141 | frame AA + paymaster | 间接 R5（推断） | — (基础设施) | 协议层（重量级） | — |
| EIP-8105 | threshold/MPC/TEE 加密 | 订单流 R8 | 多方案依赖 | 协议层（重量级） | — |

### 7.3 Mantle 相关性综合评估

| 相关性 | EIP 列表 | 部署路径 | 预期工作量 |
|--------|---------|---------|-----------|
| **High** | ERC-5564, ERC-6538, ERC-8065, Privacy Pools, ERC-3643 | 纯合约部署，无协议层修改 | 低 |
| **Medium** | EIP-8182（参考架构）, ERC-8302/pERC-20（Open PR）, EIP-8093（不可核验） | Mantle 侧适配或自研 | 中 |
| **Low** | EIP-7503, EIP-8250, EIP-8141, EIP-8105 | L1 硬分叉/协议层专属或架构不兼容 | 高或不适用 |

### 7.4 空白区域分析（WHI-254 视角）

1. **R4（业务逻辑/合约状态隐私）：无任何已发现 EIP 覆盖**。所有候选 EIP 均聚焦值级（R1/R2）或身份/图（R3/R5）隐私。R4 依赖 Aztec private functions、TEE（Silent Data）、ephemeral EVM（Paladin）等**非标准化**方案——这是标准层最显著的空白。
2. **R6+R7 标准化合规-隐私桥接缺失**：仅 ERC-8302（内置 blacklist）、Privacy Pools（association set）、ERC-3643（KYC 准入）提供碎片化合规机制，缺乏统一 EIP 级标准。
3. **R8 与 R1-R5 互斥定位**：EIP-8105 明确不覆盖交易数据持久隐私，订单流保护与值级隐私是两条独立技术线。

### 7.5 对 Mantle 的结论性启示

- **可立即采用（bolt-on）**：ERC-5564/6538（收款方匿名）+ ERC-8065（值级 wrapper）+ Privacy Pools（合规门控）组合，可在不改 Mantle 基础链架构的前提下覆盖 R1/R3/R5/R6，符合 WHI-254「轻量级 bolt-on」偏好。**但须明确：stealth 部分不解决金额/余额隐私，值级隐私须由 ERC-8065/8182 类方案补足。**
- **参考自研**：EIP-8182 的 UTXO + Groth16 + nullifier 协议层架构可作为 Mantle 原生 shielded pool 的设计蓝本（Medium）。
- **暂不适用**：EIP-7503/8141/8250/8105 为 L1 协议层专属，Mantle L2 不直接受益。

- **Priority**: high · **Dependencies**: item-1~item-6

---

## Diagrams

### diagram-1: 隐私相关 EIP 全景分类图（原语 × 层级）

```
              应用层 (ERC, 合约部署)        协议层 (Core, 硬分叉)        论坛/研究阶段
            ┌──────────────────────────┬──────────────────────────┬─────────────────────┐
收款方匿名   │ ERC-5564 [Final]🟢        │                          │                     │
(R3)        │ ERC-6538 [Final]🟢        │                          │                     │
            ├──────────────────────────┼──────────────────────────┼─────────────────────┤
值级隐私     │ ERC-8065 [Draft]🟡        │ EIP-8182 [Draft]🟡        │                     │
(R1/R2)     │ ERC-8302/pERC-20 [PR]🟠  │ (统一匿名集)              │                     │
            ├──────────────────────────┼──────────────────────────┼─────────────────────┤
图解耦       │ ERC-8065 [Draft]🟡        │ EIP-7503 [Stagnant]⚪     │ EIP-8093 [草案/不可核验]│
(R5)        │                          │                          │                     │
            ├──────────────────────────┼──────────────────────────┼─────────────────────┤
合规门控     │                          │                          │ Privacy Pools [非正式]│
(R6/R7)     │                          │                          │ cWETH [研究]         │
            ├──────────────────────────┼──────────────────────────┼─────────────────────┤
隐私赋能     │                          │ EIP-8250 [Draft]🟡        │                     │
基础设施     │                          │ (keyed nonces)           │                     │
            ├──────────────────────────┴──────────────────────────┴─────────────────────┤
相关但非隐私 │ EIP-8141 [Draft]🟡 (Frame TX / native AA — paymaster 推断性间接赋能)         │
            │ EIP-8105 [Draft]🟡 (Encrypted Mempool — 抗 MEV, 交易最终公开解密)            │
            └─────────────────────────────────────────────────────────────────────────┘
  ┌─ 范围外（独立 issue 覆盖，虚线框）: ⌐ ERC-7984 ¬  ⌐ ERC-7945 ¬  ⌐ VOSA / VOSA-20 ¬
状态色: 🟢Final  🔵Review  🟡Draft  🟠Open PR  ⚪Stagnant
```

### diagram-2: 隐私 EIP 生态关系图（以 EIP-8182 为中心）

```
                          ┌─────────────────────────────┐
                          │  EIP-8182 (协议层 shielded   │
                          │  pool, 统一匿名集) [Draft]   │
                          └──────────────┬──────────────┘
            alternative / complements    │
         ┌────────────────┬──────────────┼──────────────┬────────────────┐
         ▼                ▼              │              ▼                ▼
   ERC-8065         ERC-8302/pERC-20    │        Privacy Pools      EIP-7503
   (wrapper)        (native, Open PR)   │        (合规门控)        (burn-and-mint)
   [应用层替代]      [应用层替代]         │        [应用层补充]       [Stagnant 前身]
                                        │
        ┌───── 隐私赋能基础设施 (AA 提案, 非隐私提案) ─────┐
        ▼                                                ▼
   EIP-8141 (Frame TX, native AA) ◄──companion── EIP-8250 (keyed nonces)
   · paymaster ⇢ [推断性间接赋能] privacy pool gas 代付         · [赋能] 发送方侧 nonce 解关联
   · 关系标注: indirect-benefit (非设计目标)                    · EIP-8250 是 EIP-8141 的配套, 非 8182 的配套

        ┌───── 相关但非隐私 ─────┐
        ▼
   EIP-8105 (Encrypted Mempool) — related-non-privacy
   · 目标 R8 抗 MEV; 交易入块后公开解密; 非用户隐私
```

### diagram-3: Stealth Address 双密钥 ECDH 流程图（能力边界标注）

```
发送方 (Sender)                          链上 (Public/Observable)              接收方 (Recipient)
─────────────                          ─────────────────────              ─────────────────
                                                                          持有: spending key (sk_s)
                                                                                viewing key  (sk_v)
1. 读取接收方 stealth meta-address  ◄──── ERC-6538 Registry (0x6538..) ◄──── 发布 meta-address
   (P_spend, P_view)                                                          (P_spend, P_view)

2. 生成一次性 ephemeral key (r)
3. ECDH: shared = r · P_view
   派生 stealth address P_stealth
4. 转账 value 到 P_stealth     ─────►  ┌────────────────────────────┐
   广播 ephemeral pubkey R    ─────►  │ ERC-5564 Announcement 事件   │ ────► 5. 用 sk_v 扫描所有 Announcement
                                       │  (R, view_tag, P_stealth)   │           (view_tag 加速过滤)
                                       └────────────────────────────┘       6. 识别属于自己的交易
   ┌──────────── 外部观察者可见 ────────────┐                                 7. 用 sk_s 控制 P_stealth 花费
   │ ✅ 发送方地址 (明文)                    │
   │ ✅ 转账金额 value (明文)  ◄── R1 不保护 │  ← KEY: stealth 不提供金额/余额隐私
   │ ✅ P_stealth 地址 (但无法关联到接收者身份)│
   │ ❌ 接收者真实身份 (R3 受保护, 不可见)   │  ← KEY: stealth 只提供收款方匿名
   └────────────────────────────────────────┘
```

### diagram-4: WHI-254 需求覆盖热力图

```
        ERC- ERC- EIP- EIP- ERC- ERC- EIP- Priv EIP- EIP- EIP-   │ 覆盖
        5564 6538 8182 7503 8065 8302 8093 Pool 8250 8141 8105   │ EIP 数
       ┌────────────────────────────────────────────────────────┤
R1 金额 │ ❌   ❌   ✅   ⚠️   ✅   ✅   ⚠️   ❌   ❌   ❌   ❌  │  3✅ 2⚠️
R2 余额 │ ❌   ❌   ✅   ❌   ⚠️   ✅   ❌   ❌   ❌   ❌   ❌  │  2✅ 1⚠️
R3 身份 │ ✅   ⚠️   ✅   ⚠️   ⚠️   ⚠️   ⚠️   ⚠️   ⚠️   ❌   ❌  │  2✅ 7⚠️
R4 逻辑 │ ❌   ❌   ❌   ❌   ❌   ❌   ❌   ❌   ❌   ❌   ❌  │  0  ◄ 空白!
R5 图   │ ⚠️   ❌   ✅   ✅   ✅   ⚠️   ✅   ✅   ⚠️   ⚠️   ❌  │  5✅ 4⚠️
R6 合规 │ ❌   ❌   ⚠️   ⚠️   ❌   ⚠️   ❌   ✅   ❌   ❌   ❌  │  1✅ 3⚠️
R7 披露 │ ⚠️   ❌   ⚠️   ❌   ❌   ❌   ❌   ⚠️   ❌   ❌   ❌  │  0✅ 3⚠️
R8 MEV  │ ❌   ❌   ❌   ❌   ❌   ❌   ❌   ❌   ❌   ❌   ✅  │  1✅
       └────────────────────────────────────────────────────────┤
图例: ✅完全 ⚠️部分 ❌不覆盖    高亮: R4 业务逻辑/状态隐私 = 全空白
```

### diagram-5: Mantle 相关性评级与部署路径决策树

```
                  ┌─────────────────────────────────────┐
                  │ Mantle 是否需要此隐私能力?            │
                  └──────────────────┬──────────────────┘
                                     │ 是
                  ┌──────────────────▼──────────────────┐
                  │ 是否需要 L1 协议层修改 / 硬分叉?       │
                  └────────┬───────────────────┬─────────┘
                      是 │                     │ 否
              ┌──────────▼─────────┐  ┌────────▼──────────────────┐
              │ Mantle L2 不直接受益 │  │ 是否可作为纯合约 bolt-on?  │
              │  ⇒ Mantle 相关性 LOW │  └────┬─────────────────┬────┘
              │  EIP-7503            │   是 │                 │ 否(需自研/Open PR)
              │  EIP-8141 (AA)       │ ┌────▼────────┐  ┌─────▼──────────────┐
              │  EIP-8250 (keyed n.) │ │ Mantle 相关性│  │ Mantle 相关性 MEDIUM│
              │  EIP-8105 (mempool)  │ │ HIGH         │  │ EIP-8182 (参考架构) │
              └─────────────────────┘ │ ERC-5564     │  │ ERC-8302/pERC-20(PR)│
                                       │ ERC-6538     │  │ EIP-8093 (不可核验) │
                                       │ ERC-8065     │  └────────────────────┘
                                       │ Privacy Pools│
                                       │ ERC-3643     │
                                       └─────────────┘
```

> **图表交付说明**：以上为 ASCII 结构草图，用于本 draft 阶段表达图表语义与数据。最终 final/report 阶段如需高保真矢量图，由 Technical Writer 使用 `fireworks-tech-graph` 技能生成 SVG/PNG。

---

## Source Coverage

| Source Requirement | 覆盖情况 | 证据 |
|--------------------|---------|------|
| GitHub YAML frontmatter（最高优先级） | ✅ 已覆盖 | 所有已合并 EIP/ERC 状态锚定到 `ethereum/EIPs` master `a8862ae6`（2026-06-22）与 `ethereum/ERCs` master `56c2308c`（2026-06-22）；ERC-8302 锚定 PR #1817 head `ffaa9933`（state=open） |
| eips.ethereum.org 渲染页面 | ✅ 已覆盖 | EIP-5564/6538/8182/7503/8065/8141/8105 渲染页 URL 全部引用，访问日期 2026-06-23 |
| Ethereum Magicians `discussions-to` / 论坛帖 | ✅ 已覆盖 | search.json 检索 6 个查询，结果数与 topic ID 全部记录（item-1 §1.2）；EIP-8182 帖 topic 27889 等 |
| ethresear.ch | ✅ 已覆盖 | search.json 检索 5 个查询，结果数与 topic ID 全部记录；pERC-20 (25200/25089)、EIP-7503 (18664/18875) |
| WHI-254 框架文档 | ✅ 已覆盖 | `privacy-landscape-framework/final.md` 的 R1-R8、6 技术家族、5 轴 rubric、6 维向量、轻量级判定全部引用 |
| EEA Privacy WG Report §06b | ⚠️ 间接覆盖 | 经 WHI-254 final.md §2.3（EEA §06b 4 项标准映射）间接交叉验证；本 survey 未重新直取 EEA 报告原文（gap，见下） |

---

## Gap Analysis

| Gap | 影响 | 处理方式 |
|-----|------|---------|
| **EIP-8093 正式状态不可核验** | 无法确认其 EIP 编号是否正式分配 | 已按「论坛草案/不可核验」标注，记录尝试核验方式（item-1 §1.6, item-5 §5.3），未给出确定性结论 |
| **EIP-8250 eips.ethereum.org 渲染页可访问性未单独确认** | 渲染页可能缺失 | 以 master 源文件 `EIPS/eip-8250.md` @ `a8862ae6` 为核验基准，已标注 fallback |
| **ERC-8302 为 Open PR，接口未最终化** | 标准内容仍可能变动 | 已显式标注「Open ERC PR #1817」「未合并标准」，head SHA `ffaa9933`，与已合并 Final/Draft 区分 |
| **Magicians `category:erc` 查询返回 0** | 类别通道失效 | 已记录为方法论限制；关键词通道为有效替代，命中覆盖全部正式 EIP |
| **ethresear.ch 多查询达 50 条分页上限** | 实际命中可能超过 50 | 已标注「达上限」，主要隐私相关帖已逐一识别；穷尽枚举非本 survey 目标 |
| **EEA 报告原文未在本轮直取** | §06b 交叉验证依赖 WHI-254 转引 | 已通过 WHI-254 final.md 间接覆盖；若需一手 EEA 引用，后续轮次可补 |
| **EIP-8182 Hegota inclusion / EIP-8105 LUCID 走向为动态信息** | 时间线可能变化 | 已标注「计划」「待跟踪」，截止日期 2026-06-23 快照 |
| **各 EIP 精确逐文件 blob SHA 未逐条记录** | 细粒度溯源 | 以仓库 master HEAD SHA 统一锚定（可 checkout 复核），平衡可复现性与篇幅 |

无虚构来源；所有不确定结论均标注 `[unverified]` / `⚠️` / `待确认` / `推断`。

---

## Revision Log

| Round | 日期 | 变更摘要 |
|-------|------|---------|
| 1 | 2026-06-23 | 初始 deep-draft。基于 outline round 2（commit `233397184`）的 7 items + 4 diagrams 扩展为完整 section（含 diagram-5）。新增内容：(1) Ethereum Magicians / ethresear.ch 逐查询结果数执行记录表（item-1 §1.2，落实 outline review carried-forward caveat）；(2) URL+访问日期+commit SHA 三元组溯源约定（验收标准 5），状态锚定 EIPs master `a8862ae6` / ERCs master `56c2308c` / ERC-8302 PR head `ffaa9933`；(3) EIP-8141 paymaster 关联全部以推断语气表述并附直接源核验（落实 outline caveat）；(4) 新发现论坛提案 EIP-8093 按不可核验标注；(5) stealth 不提供金额/余额隐私、EIP-8105 非隐私 在分类表、item-3、item-6、diagram-3 多处显式标注。 |

> 本 draft 待 Adversarial Agent 审查。未 flag 内容在后续修订轮次中保留。
