# Creator Distiller

## 项目与范围

本仓库提供可移植的创作者知识蒸馏 Skill，以及无网络、仅用 Python 标准库的归档辅助工具。在线采集与 ASR 不在内置能力内。

## 文件

- `creator-distiller/SKILL.md`：技能入口。
- `creator-distiller/references/` 与 `templates/`：工作说明与产物结构。
- `creator-distiller/scripts/archive.py`：离线归档工具，要求 Python 3.9+。
- `tests/`：离线行为测试。
- `examples/`：仅含虚构样例；真实用户语料放仓库之外。
- `evals/`：未自动执行的 Agent 行为评估用例，不冒充通过结果。

## 验证

在仓库根目录执行 `python -m unittest discover -s tests -v`。涉及兼容性时核对 GitHub Actions 的对应提交。结构检查不能证明原文支持结论或平台资料全量。

## 数据约束

保留原始资料，只重建生成文件；不按文件大小判断总结完成。不提交 Cookie、Token、真实语料、私人路径或平台会话文件。不要引入固定用户行业、固定 Agent 工具或操作系统依赖。
