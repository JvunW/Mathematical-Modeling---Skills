---
name: mathmodel-workflow
description: "启动并协调完整数学建模任务。用于从赛题和附件开始，确认交付路线、建立可恢复工作区，并按分析、编码、图示、论文和验收阶段推进。"
---

# 数学建模完整工作流

本 Skill 是流程协调入口，不替代各阶段的专业 Skill。它负责确认用户偏好、创建可移植工作区、维护阶段状态、调用下游 Skill，并阻止无证据的阶段跳转。

## 使用边界

- 用户只需要分析、写作或验收等单一阶段时，直接使用对应 Skill。
- 完整赛题、多阶段任务、需要中断恢复或多种交付格式时使用本 Skill。
- 所有状态和产物只写入用户指定的 `<WORK_ROOT>`；未指定时使用当前工作目录。
- Gate 是质量检查，不扩大任务范围。非安全性阻断允许用户显式豁免，但必须记录原因和影响。

## 开始前确认

用户上传题目后，完成附件可读性检查，随后立即调用 `$mathmodel-analysis-grill` 的“用户思路十问”。不要另起一套启动问卷；把下列工作流信息结合具体题目纳入那 10 个问题，尤其是第 10 题：

- 最终交付路线：Typst/PDF、LaTeX/PDF 或 Word/DOCX；
- 比赛或模板类型，以及是否提供官方模板；
- 论文语言、截止时间和团队工具约束；
- 是否允许联网检索文献。

必须展示恰好 10 个问题并等待用户逐题回答。在回答齐全前，不初始化建模方案、不调用分析、编码或写作阶段，也不得由 Agent 自行填入默认偏好。

Word/DOCX 路线使用 Markdown 作为论文源文件，由 `$export-math-docx` 导出 Word 原生 OMML 公式；不得从 Typst 直接转换为 DOCX。

## 初始化工作区

创建或更新：

```text
.
├── plan.md
├── todo.md
├── state/
│   ├── workflow_state.json
│   ├── artifact_registry.json
│   ├── gate_history.jsonl
│   └── stale_report.json
├── reports/
│   ├── model_manifest.json
│   ├── paper_evidence_map.json
│   └── verification.json
├── code/
├── results/
│   └── results_manifest.json
├── figures/
└── paper/
    ├── main.typ              # Typst/PDF 路线
    ├── main.tex              # LaTeX/PDF 路线
    ├── paper.md              # Word/DOCX 路线
    ├── template.docx         # 可选：官方模板副本
    └── output/
```

使用 `scripts/runtime/state_manager.py` 初始化状态。运行时契约、状态枚举和豁免规则见 [references/runtime-contract.md](references/runtime-contract.md)。

## `plan.md` 必需字段

```markdown
# 数学建模任务计划

- 工作区：<绝对路径>
- 排版与交付路线：<Typst/PDF | LaTeX/PDF | Markdown→Pandoc→DOCX>
- 官方模板：<无 | 文件路径>
- 论文语言：<中文 | 英文>
- 比赛类型：<CUMCM | MCM/ICM | 其他>
- 公式策略：<Typst 原生 | LaTeX 原生 | Word 原生 OMML>
- 最终验收：<PDF 视觉验收 | DOCX 结构、OMML 与页面视觉验收>
- 外部检索：<允许 | 禁止 | 仅指定来源>
```

## 阶段与 Gate

```text
G0 ENVIRONMENT_READY
G1 PROBLEM_PARSED
G2 METHOD_VALIDATED
G3 IMPLEMENTATION_VERIFIED
G4 RESULTS_FROZEN
G5 PAPER_EVIDENCE_COMPLETE
G6 DELIVERY_VERIFIED
```

| Gate | 主责 Skill | 必需证据 |
|---|---|---|
| G0 | `$mathmodel-doctor` 或本 Skill | 环境、附件和输出路径可用 |
| G1 | `$mathmodel-analysis-grill` 与 `$mathmodel-analysis` | 用户十问已完成或显式豁免；`reports/model_manifest.json` 已生成 |
| G2 | `$mathmodel-analysis`，按需配合统计/实验/不确定性 Skill | 方法、假设、约束和验证方案已形成且风险已记录 |
| G3 | `$mathmodel-coding` | 可复现代码、检查结果和运行记录 |
| G4 | Runtime | `results/results_manifest.json` 中的必需结果已冻结且 fresh |
| G5 | `$mathmodel-writing`、两次 `$mathmodel-writing-grill` 用户十问，中文论文在正文起草和成稿润色阶段各调用一次 `$mathmodel-humanizer-zh` | 两个论文门禁各有 10 个用户回答；`reports/paper_evidence_map.json` 完整；中文写作的两种模式均有记录，成稿保护检查通过或记录显式跳过 |
| G6 | `$mathmodel-verification` | `reports/verification.json` 为 pass |

不得仅根据聊天记忆宣称 Gate 已通过。Gate 必须由验证器输出结构化结果，并写入 `gate_history.jsonl`。

## 执行顺序

1. **用户思路采集**：题目上传后先调用 `$mathmodel-analysis-grill`，提出恰好 10 个问题并等待用户逐题回答。
2. **分析**：十问完成后调用 `$mathmodel-analysis`，使用用户回答形成模型清单。
3. **编码**：调用 `$mathmodel-coding`，读取模型清单并输出结果清单。
4. **图示**：图确实服务论证时调用 `$mathmodel-figure-templates`，先冻结 Figure Contract，再在 TikZ、Matplotlib、DrawIO 或 Mermaid 中路由；数据图必须来自编码阶段的真实结果，DrawIO 执行仍交给 `$mathmodel-drawio`。
5. **冻结结果**：记录代码、数据、配置和环境指纹。只有 lifecycle=`frozen` 且 validity=`fresh` 的必需结果才能用于论文。
6. **写作**：调用 `$mathmodel-writing`，关键数字只引用结果清单，关键结论写入证据映射；内容计划形成后由 `$mathmodel-writing-grill` 向用户提出恰好 10 题并等待逐题回答。门禁完成后，中文论文调用 `$mathmodel-humanizer-zh` 的正文起草模式，再生成各章节。
7. **成稿用户十问与中文润色**：完整论文再次调用 `$mathmodel-writing-grill`，向用户提出另一组恰好 10 题并等待全部回答；中文论文随后第二次调用 `$mathmodel-humanizer-zh` 的成稿润色模式。任何门禁不得由 Agent 自问自答或内部通过。
8. **重新生成交付物**：重新编译 Typst/LaTeX；Word/DOCX 路线调用 `$export-math-docx`。
9. **验收**：调用 `$mathmodel-verification`；未通过 G6 不得声称可提交。

每完成一个阶段，同步更新 `todo.md` 和工作流状态。阶段失败时保留诊断证据，不伪造缺失产物。

## 失效传播与恢复

开始任何新阶段或恢复任务前：

1. 读取 `workflow_state.json` 和 Artifact Registry。
2. 重新计算已注册文件的内容 hash。
3. 将变化的上游产物及其下游依赖标记为 stale；只改元数据，不删除用户文件。
4. 从第一个未通过或已失效的 Gate 恢复。
5. 已验证且依赖仍 fresh 的阶段不重复执行。

必需产物为 stale、blocked 或 missing 时不能通过 G6。可选产物缺失只产生 warning。用户豁免必须记录 actor、时间、原因、范围和剩余风险。

## 完成标准

- 三种交付路线贯穿计划、目录、写作和验收。
- 关键模型、结果、图表和论文结论具有稳定 Artifact ID、版本、hash 和依赖。
- 论文数字可以追溯到 frozen/fresh 结果。
- 新会话可仅根据工作区状态恢复。
- 最终交付通过对应格式的结构检查和视觉验收。
