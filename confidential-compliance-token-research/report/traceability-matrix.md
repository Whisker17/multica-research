# Confidential Compliance Token Traceability Matrix

> **Project slug**: `confidential-compliance-token-research`
> **Report issue**: `7b29e4a8-01eb-4cbf-9b59-8e363f9a40e4`
> **Final report**: `confidential-compliance-token-research/report/final-report.md`
> **Source index**: `confidential-compliance-token-research/research-sections/_index.md` @ `cd5ba23`
> **上游 web/doc 来源的访问日期**：继承自各 final 章节；大多数外部来源的访问日期为 2026-06-24。

## Source Section Register

| Code | Topic | Issue | Main merge commit | Final path |
|---|---|---|---|---|
| S1 | requirements-framework | `7d7fa951-8160-4b03-a7ae-8ff1a6a9664c` | `9eb29a1` | `confidential-compliance-token-research/research-sections/requirements-framework/final.md` |
| S2 | zama-confidential-rwa | `22741382-2866-4221-8b39-17551f5f400e` | `1a9fad0` | `confidential-compliance-token-research/research-sections/zama-confidential-rwa/final.md` |
| S3 | pse-private-transfers-constraints | `687a44f7-c9b1-42a3-b435-99ea6fd09a29` | `b54e21b` | `confidential-compliance-token-research/research-sections/pse-private-transfers-constraints/final.md` |
| S4 | compliance-token-private-extension | `18fbd577-47e2-47f6-bfbf-a7519114df13` | `bb27379` | `confidential-compliance-token-research/research-sections/compliance-token-private-extension/final.md` |
| S5 | confidential-rwa-candidates | `84e8d44a-f970-4531-a351-f9d801da4947` | `29269d9` | `confidential-compliance-token-research/research-sections/confidential-rwa-candidates/final.md` |
| S6 | route-comparison | `d44834f3-e3f7-4174-9200-395052956c18` | `1728cac` | `confidential-compliance-token-research/research-sections/route-comparison/final.md` |
| S7 | mantle-protocol-design | `dfd8a3e5-1841-4eac-8050-daaecfff89dd` | `0a058bd` | `confidential-compliance-token-research/research-sections/mantle-protocol-design/final.md` |
| S8 | integration-roadmap | `cf06b8fa-ed51-4b1e-8f3f-bfcd2f76197a` | `0d11f05` | `confidential-compliance-token-research/research-sections/integration-roadmap/final.md` |

## Key Claim Traceability

| ID | Report claim | Source section(s) | Evidence path / URL / version | Commit / access | Confidence and caveat |
|---|---|---|---|---|---|
| C-01 | CCT 的最小边界为：compliance token + 机密记账 + 选择性披露 + 可审计性。 | S1 | `requirements-framework/final.md`，Executive Summary 及第 2 项 | `9eb29a1` | 高；框架定义。 |
| C-02 | Mantle 第一阶段应避免新建链/VM、新建 bridge、运营完整的隐私节点、hardfork 或更换 execution-client。 | S1, S6, S8 | `requirements-framework/final.md`；`route-comparison/final.md`；`integration-roadmap/final.md` | `9eb29a1`, `1728cac`, `0d11f05` | 高；在路线与路线图章节中反复出现。 |
| C-03 | 推荐路线为：ERC-3643 风格的合规底层，叠加可替换后端的 ERC-7984/OZ 机密 overlay。 | S6, S7 | `route-comparison/final.md`，Executive Summary 及 §2.4；`mantle-protocol-design/final.md`，Executive Summary | `1728cac`, `0a058bd` | 高；核心路线决策。 |
| C-04 | Zama/OZ 是首选的后端验证路径，但并非无条件的生产可用主张。 | S2, S6, S7 | `zama-confidential-rwa/final.md`；`route-comparison/final.md`；`mantle-protocol-design/final.md` | `1a9fad0`, `1728cac`, `0a058bd` | 候选地位为高置信；Mantle 支持与 SLA 仍为门控项。 |
| C-05 | ERC-3643 由六个核心 T-REX 合约加上 ONCHAINID 身份层构成。 | S4 | `compliance-token-private-extension/final.md`，final fixes 及第 3 项 | `bb27379` | 高；dispatch 注意事项已明确纳入。 |
| C-06 | 原生 ERC-3643 中依赖金额的模块无法直接消费加密的 ERC-7984 amount/balance handle。 | S2, S4, S7 | `zama-confidential-rwa/final.md` 第 3–4 项；`compliance-token-private-extension/final.md`；`mantle-protocol-design/final.md` | `1a9fad0`, `bb27379`, `0a058bd` | 高；关键技术张力。 |
| C-07 | 加密 amount/balance 谓词不得使用依赖谓词的 revert，因为这会泄露比较结果。 | S7, S8 | `mantle-protocol-design/final.md`，final refinement 及第 3 项；`integration-roadmap/final.md` PoC gates | `0a058bd`, `0d11f05` | 高；生产门控项。 |
| C-08 | B20 提供的是策略/合规词汇，而非当前的机密性。 | S4, S6, S7 | `compliance-token-private-extension/final.md` 第 2、6、7 项；`route-comparison/final.md` §3.2；`mantle-protocol-design/final.md` | `bb27379`, `1728cac`, `0a058bd` | 高；本地/当前状态代码检查仍有边界限制。 |
| C-09 | Base/Mantle 代码观察属于当前状态检查，而非生产事实。 | S4, S8 | `compliance-token-private-extension/final.md` 第 7 项；`integration-roadmap/final.md` 本地 Mantle 代码分析 | `bb27379`, `0d11f05` | 中高；有边界的扫描，不构成对缺失的证明或对路线图的证明。 |
| C-10 | 第一阶段加密余额作为产品需求是强制项，但受后端生产就绪度门控。 | S4, S6, S8 | `compliance-token-private-extension/final.md` Executive Summary 及第 5 项；`route-comparison/final.md`；`integration-roadmap/final.md` | `bb27379`, `1728cac`, `0d11f05` | 高；区分产品需求与生产可用。 |
| C-11 | Inco Lightning 是最强的非 Zama 后端备选，但 Mantle 支持与 TEE 信任仍存在缺口。 | S5, S6 | `confidential-rwa-candidates/final.md` Inco profile；`route-comparison/final.md` backup bucket | `29269d9`, `1728cac` | 中高；除非经独立锚定，Base/mainnet 与审计主张均标注为厂商自述。 |
| C-12 | Inco confidential ERC20 框架仅为未经审计的 PoC，不应作为生产代码复用。 | S1, S5 | `requirements-framework/final.md` 第 5 项；`confidential-rwa-candidates/final.md` Inco PoC 行 | `9eb29a1`, `29269d9` | 高；README 注意事项由源章节继续传递。 |
| C-13 | VOSA-RWA/VOSA-20 是轻量级 PoC 退路，而非生产主路线。 | S5, S6 | `confidential-rwa-candidates/final.md`；`route-comparison/final.md` | `29269d9`, `1728cac` | 中；论坛草案，未经审计，图谱暴露，发行方控制能力存在缺口。 |
| C-14 | Railgun/Privacy Pools 提供资金来源与关联集/披露方面的经验，但不提供发行方代币生命周期。 | S3, S5, S6 | `pse-private-transfers-constraints/final.md`；`confidential-rwa-candidates/final.md`；`route-comparison/final.md` | `b54e21b`, `29269d9`, `1728cac` | 中高；组件分类。 |
| C-15 | Paladin/Pente 是业务流程隐私的补充方案，而非最小化的代币账本路线。 | S5, S6 | `confidential-rwa-candidates/final.md`；`route-comparison/final.md` | `29269d9`, `1728cac` | 中；组件分类。 |
| C-16 | Optalysys 是 FHE 性能/产品化的参考，而非代币标准或 CCT 路线。 | S1, S5, S6 | `requirements-framework/final.md`；`confidential-rwa-candidates/final.md`；`route-comparison/final.md` | `9eb29a1`, `29269d9`, `1728cac` | 中；厂商性能材料未经核实。 |
| C-17 | 对 Mantle CCT 而言，account-based 机密代币在近期是比 note-based 资金池更优的底层。 | S3, S6 | `pse-private-transfers-constraints/final.md` 第 3 项；`route-comparison/final.md` | `b54e21b`, `1728cac` | 中高；产品契合度，而非隐私上限主张。 |
| C-18 | 披露必须按权限、触发条件、载荷、范围、撤销、残余泄露与日志建模。 | S1, S2, S3, S7 | `requirements-framework/final.md`；`zama-confidential-rwa/final.md`；`pse-private-transfers-constraints/final.md`；`mantle-protocol-design/final.md` | `9eb29a1`, `1a9fad0`, `b54e21b`, `0a058bd` | 高；跨章节共识。 |
| C-19 | 全历史 viewing key 或不设限的观察者访问属于反模式。 | S2, S3, S6, S7 | Zama ACL/OZ ObserverAccess 注意事项；PSE 披露反模式；route 披露视角；protocol design | `1a9fad0`, `b54e21b`, `1728cac`, `0a058bd` | 高；后端特定的历史撤销问题仍未解决。 |
| C-20 | 第一阶段 CCT 默认不隐藏地址图谱、事件存在性、时序、mempool/订单流或私有身份。 | S1, S2, S3, S7 | `requirements-framework/final.md`；Zama lifecycle；PSE account vs note model；protocol non-goals | `9eb29a1`, `1a9fad0`, `b54e21b`, `0a058bd` | 高；残余泄露必须明确说明。 |
| C-21 | Bridge/redeem 是有意为之的披露边界，且必须记录日志。 | S1, S2, S6, S7, S8 | requirements bridge/redeem capability；Zama lifecycle；route constraints；protocol flows；roadmap checklist | `9eb29a1`, `1a9fad0`, `1728cac`, `0a058bd`, `0d11f05` | 高；法律结算路径仍因产品而异。 |
| C-22 | 在没有适配器的情况下，不应主张通用 ERC-20 DeFi 兼容性。 | S1, S3, S6 | requirements DeFi caveat；PSE DeFi blockers；route non-goals | `9eb29a1`, `b54e21b`, `1728cac` | 高；适配器相关属于后续工作。 |
| C-23 | BackendAdapter 必须保持公开接口对后端中立。 | S6, S7, S8 | route hybrid shape；protocol backend abstraction；roadmap Phase 0 tasks | `1728cac`, `0a058bd`, `0d11f05` | 高；避免对 Zama/Inco/native 的锁定。 |
| C-24 | 若不存在可信的后端路径，Phase 0 应当停止。 | S8 | `integration-roadmap/final.md`，phase table 及 risk tree | `0d11f05` | 高；路线图门控项。 |
| C-25 | 试点就绪要求在决策前给出实测的 p50/p95/p99、成本以及数值化阈值。 | S8 | `integration-roadmap/final.md`，Executive Summary、第 5 项、第 8 项 checklist C-20 | `0d11f05` | 高；不接受仅凭厂商的 SLA。 |
| C-26 | 原生 B20-like / PolicyRegistry / 加密记账 precompile 仅属于 phase 2。 | S4, S6, S8 | phase boundary table；route verdict；native roadmap | `bb27379`, `1728cac`, `0d11f05` | 高；需要单独的协议提案。 |
| C-27 | 厂商的路线图、性能、合作伙伴及审计主张，除非经独立确认，否则均为未经核实。 | S2, S5, S6, dispatch caveats | Zama T-REX post handling；Inco audit claim；Fhenix status；Optalysys performance material | `1a9fad0`, `29269d9`, `1728cac` | 高；报告保留 unverified 标注。 |
| C-28 | PoC 最小闭环为：KYC/策略 onboarding、机密 mint、机密 transfer、限定范围的审计披露、freeze 或 recovery，以及证据导出。 | S8, S7 | `integration-roadmap/final.md` 第 1 项；`mantle-protocol-design/final.md` flows | `0d11f05`, `0a058bd` | 高；运营验收门控项。 |
| C-29 | [TW inference] Mantle 应将首个项目定位为门控式可行性与 PoC 阶段，而非生产上线。 | S6, S7, S8 | route verdict + protocol gates + integration roadmap | `1728cac`, `0a058bd`, `0d11f05` | 高度综合；融合了已接受的路线、协议与路线图产出。 |
| C-30 | [TW inference] 披露 UX 与审计导出是核心产品界面，而非文档附录。 | S1, S3, S7, S8 | requirements selective-disclosure vector；PSE product constraints；protocol DisclosureRegistry；PoC checklist | `9eb29a1`, `b54e21b`, `0a058bd`, `0d11f05` | 高度综合；跨章节的产品性结论。 |

## External Source Handling

| Source family | Treatment |
|---|---|
| Standards and docs | ERC-3643、ERC-7984、OpenZeppelin Confidential Contracts、Zama docs、Inco docs 均通过各 final 章节引用，除另有说明外访问日期为 2026-06-24。 |
| Vendor claims | 路线图、性能、合作伙伴、审计及 mainnet 支持等主张，除非某源章节锚定了独立代码、审计或观察到的链上证据，否则仍属厂商/自述。 |
| Local code checks | Base 与 Mantle 检查属于有边界的 `current-state-checked` 证据，不构成生产发布承诺。 |
| Soft prior research | 此前的 EVM 隐私章节仅在已接受的 CCT 章节纳入它们、或明确将其标注为软性佐证时才被使用。 |
