# Numeric claims and evidence

## Evidence map

每个关键主张在 `reports/paper_evidence_map.json` 中绑定 `claim_id`、正文位置、`artifact_id`、`version`、`content_hash` 和证据定位。相同主张在摘要、正文、表格和结论中复用同一来源。

## 写入规则

- 从结构化结果或最终表格读取数字，不手工回忆或重新计算。
- 写入前检查 Artifact 为 `frozen` 且 `fresh`。
- 保留必要精度，统一单位和小数位；不制造超出计算精度的有效数字。
- 每个结果段先给结论，再给证据和解释；同时说明基线、误差、敏感性或边界。

上游代码、数据、配置、环境或随机性记录改变后，相关结果、图表、证据映射和正文主张都应标为 `stale`，直到重新计算和核对。
