# Runtime Contract

只在完整工作流、中断恢复、结果冻结或失效传播任务中读取本文件。

## 安装边界

Runtime 位于 `mathmodel-workflow/scripts/runtime/`，随本 Skill 一起安装。Coder 和 Writer Skill 不跨插件导入这些模块，只通过工作区中的版本化 JSON 契约交换状态。

## 状态模型

Artifact 使用两个相互独立的状态维度：

- `lifecycle`: `draft | frozen | superseded`
- `validity`: `fresh | stale | missing | blocked`

稳定 `artifact_id` 不包含版本。具体版本由 `version` 和 `content_hash` 标识；依赖项使用结构化对象，不解析拼接字符串。

## 写入安全

- JSON 状态通过同目录临时文件写入、flush/fsync 后使用原子替换。
- 写入前获取 `.lock` 文件；锁超时后失败，不覆盖并发写入。
- 每次 Gate 变化附带 `transaction_id`、actor 和时间。
- JSONL 历史允许末尾不完整记录被忽略，但不得静默忽略中间损坏。

## Gate 结果

```json
{
  "gate_id": "G4_RESULTS_FROZEN",
  "status": "pass",
  "validator": "gate_runner:2.0",
  "actor": "mathmodel-workflow",
  "evidence": ["Q1.results.main@2"],
  "warnings": [],
  "errors": [],
  "transaction_id": "...",
  "checked_at": "..."
}
```

Gate validator 必须幂等，相同输入产生相同结论。`pass_criteria` 使用可执行检查 ID，而不是无法解析的自然语言。

## 豁免

安全性、真实性和最终文件完整性检查不得豁免。其他阻断项可由用户显式豁免，并记录 Gate、检查项、actor、原因、范围和剩余风险。
