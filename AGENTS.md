# 共脑V1.0

## 项目与范围

本仓库提供可移植的跨领域人物知识提炼与能力生成 Skill，以及无网络、仅用 Python 标准库的归档辅助工具。在线采集与 ASR 不在内置能力内。

## 文件

- `gongnao/SKILL.md`：技能入口。
- `gongnao/references/` 与 `templates/`：工作说明与产物结构。
- `gongnao/scripts/archive.py`：离线归档工具，要求 Python 3.9+。
- `gongnao/scripts/install.py`：跨平台安装器，默认装到 `~/.agents/skills` 与 `~/.claude/skills`。
- `gongnao/examples/`：随安装包分发的成品能力包示例；入口命名为 `SKILL.example.md`，避免被当成第二个技能加载。
- `tests/`：离线行为测试。
- `examples/`：虚构样例，以及经标注的真实产出节选（`real-excerpt-jianghushuo/`，只保留少量节选、不含原文与转录）。其他真实用户语料放仓库之外。
- `evals/`：未自动执行的 Agent 行为评估用例，不冒充通过结果。

## 验证

在仓库根目录执行 `python3 -m unittest discover -s tests -v`（Windows 用 `py -3`）。没有用户明确发布指令时不要推送远端。不得沿用其他版本的 CI 成绩证明本版兼容性。结构检查不能证明原文支持结论或平台资料全量。

## 数据约束

保留原始资料，只重建生成文件；不按文件大小判断总结完成。不提交 Cookie、Token、真实语料、私人路径或平台会话文件。不要引入固定用户行业、固定 Agent 工具或操作系统依赖。

## 产品约束

- 先问清对象与用途；thinking/expression/service 可多选。只生成所选能力，已给答案不重问。
- 主底库保留原文和细粒度详解、三类完整知识；能力选择不能降低提炼细度。
- 所选能力必须生成带资料的实际包，不能在知识文件交付后提前结束。
- 服务包包含角色、流程、启动与独立的私人状态机制；不能承诺宿主不具备的记忆或后台能力。
- 文件生成、结构检查、实际试运行、跨会话恢复与用户验收分别报告。模板或合成示例不冒充真实使用。
