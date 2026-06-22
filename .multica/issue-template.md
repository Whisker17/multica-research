# Multica Issue Template

本仓库（Multica Research Squad）创建 issue 时统一使用本模板，保证 issue 自包含、可执行、可验收。
模板综合自现有 issue 的实际约定（`[Research]` / `[Analysis]` / `[M2-对比]` / `[Config]` 等）。

---

## 标题规范

格式：`[类别] 简短的动宾式标题`

- `[类别]` 必填，方括号开头。常见类别：
  - 研究流水线：`[Research]`（单链/单标准调研）、`[Analysis]`（跨项目 gap/对比分析）、`[M1-分析]` / `[M2-对比]` / `[M2-策略]` / `[M3-报告]`（里程碑式研究阶段）。
  - 工程/运维：`[Config]`、`[Infra]`、`[Observability]`、`[Budget]`、`[Alert]`、`[Reporter]`、`[Calibration]`、`[Impact Checker]`。
  - 周期性：`[Daily]`、`[Weekly]`。
- 新增类别前优先复用现有类别；确需新增时，同步更新本模板与 `AGENTS.md` / `CLAUDE.md` 的 issue 规范。
- 标题主体用一句话说清「做什么、产出什么」，避免泛化（如「优化一下」）。
- 语言：与 issue 正文一致，默认中文。

`priority`：`high` / `medium` / `low` / `none`。`status` 默认 `backlog`。

---

## 描述正文骨架

按以下顺序使用 `##` 二级标题。**必填**章节必须出现；**可选**章节按 issue 类型取舍，但不要新增同义章节。

```markdown
## 目标            （必填 — 一段话说清最终产出与价值，面向谁）
## 背景            （可选 — 为什么现在要做；当前现状/问题/口径约束）
## 范围 / 输入      （按需 — 调研范围表、输入文档清单、对比维度、重点关注）
## 执行步骤         （研究/分析类必填；工程/运维类按需 — Step 1..N，可执行、有先后）
## 交付物          （必填 — 明确输出路径；完成后在本 issue 评论贴交付物链接）
## 验收标准         （必填 — checkbox 列表，逐条可核验）
## Review 要求      （必填 — reviewer 如何抽查验证，验什么）
## 依赖            （必填 — 写明 Blocked By / Blocks，无则写「无」）
```

工程类（有 Epic / 设计文档）issue，可在最前面追加链接区：

```markdown
## Parent          （可选 — 所属 Epic 标题或 ID）
## Spec            （可选 — 设计文档路径 + 章节锚点）
## Blocked By      （可选 — 阻塞本 issue 的 issue，含一句话原因）
## Blocks          （可选 — 本 issue 阻塞的 issue，含一句话原因）
```

---

## 各章节要求

- **目标**：单段落，说清「交付什么 + 给谁用 + 解决什么」。不堆任务清单。
- **背景**：只写影响任务判断的上下文，如现状、问题、口径约束或触发原因；不要复述目标。
- **范围 / 输入**：调研类用表格列 `Repo | 语言 | URL`；分析类用表格列出输入文档及其路径；对比类列出对比维度表。网页或外部文档需记录访问日期或版本号；资源不可访问时，标注「不可访问（权限受限）」并写明尝试方式，**不得**当作缺失结论。
- **执行步骤**：研究/分析类用 `### Step N:` 分段，每步可独立执行。工程/运维类可省略；若保留，允许只写一个 Step。涉及评分/分类时给出 rubric 表（评分维度 × 分档）。
- **交付物**：列出确切产出路径（如 `repo-github-actions/research-sections/<topic>/drafts/round-1.md`、`docs/research/.../*.md`）。固定补一句：「完成后在本 issue 评论中贴交付物链接」。
- **验收标准**：`- [ ]` 复选框，每条客观可核验。研究类必含：「每个结论附带文件路径或 URL，以及调研时的 commit SHA」；外部网页/文档结论还需标注访问日期或版本号。
- **Review 要求**：写清 reviewer 抽查方式。示例：研究类「抽查至少 3 个结论，打开对应源文件验证准确性」；对比类「复核对比矩阵是否覆盖所有输入维度」；工程类「按验收标准执行命令或检查配置生效」。
- **依赖**：显式列出依赖的 issue（WHI-xxx 或 UUID）及原因；可并行则写「无（可与其他 X 并行）」。

---

## 创建命令

正文多行、含中文，统一用 `--description-file` 从文件读取（避免转义与编码问题）：

```bash
multica issue create \
  --title "[Research] <标题>" \
  --priority low \
  --description-file /tmp/issue-body.md
```

可选：`--parent <epic-id>`、`--project <project-id>`、`--assignee <name>`、`--attachment <path>`、`--due-date YYYY-MM-DD`。

---

## 最小骨架（复制即用）

```markdown
## 目标

<一段话：交付什么、给谁、解决什么>

## 执行步骤

### Step 1: <...>
### Step 2: <...>

## 交付物

- `<输出路径>`
- 完成后在本 issue 评论中贴交付物链接

## 验收标准

- [ ] <可核验条目>
- [ ] 每个结论附带文件路径 / URL 及 commit SHA

## Review 要求

- <reviewer 如何抽查验证>

## 依赖

- 无
```
