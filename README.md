# 蒸馏大王 · Creator Distiller

把创作者的多篇内容，变成有来源、可核查、可应用的 **概念体系 + 方法论地图 + 表达 DNA**。

核心流程：明确范围 → 保存原始证据 → 逐条总结 → 跨篇归纳 → 回查原文 → 交付三件套。进一步用于实际工作时，结合用户信息和真实数据反馈；不冒充原作者。

## 支持范围

| 环境 | 可用能力 | 条件与边界 |
|---|---|---|
| 支持 Agent Skills 的 Agent | 安装并加载 SKILL.md | 安装位置由各宿主决定，无统一全平台目录 |
| 普通文本 Agent | 按入口和相关参考文件分析已提供材料 | 不自动安装；需要实际提供所引用文件 |
| Windows / macOS / Linux + Python 3.9+ | 本地证据包、分组、索引、结构校验 | 仅标准库；不依赖 Bash、固定盘符或个人环境 |
| 无文件或代码执行能力 | 在回复中交付分析 | 不能声称已写文件或运行检查 |
| 在线采集、音视频转录 | 使用用户环境中另外具备的能力 | 本包不捆绑爬虫、浏览器、ASR、模型或 PDF 引擎 |

“跨 Agent / 跨系统”是可移植的核心规则与本地工具，不是任何 Agent 在任何设备上都能零配置完成所有外部操作。资源很小的设备、无 Python 的环境和平台访问限制仍有各自边界。

## 使用

1. 从 [GitHub 仓库](https://github.com/medgrey123-prog/creator-distiller) 下载源码，或从 [Releases](https://github.com/medgrey123-prog/creator-distiller/releases) 下载独立 Skill ZIP。把完整的 `creator-distiller/` 文件夹放入宿主文档指定的 Skills 目录，或通过宿主安装入口选取该目录。
2. 不支持 Skills 的 Agent：提供 [SKILL.md](creator-distiller/SKILL.md) 和它按任务需要引用的参考/模板文件，作为用户选择的工作说明。
3. 给出创作者身份或已有材料、希望覆盖的范围、实际用途。无需提供私人登录凭据。

示例请求：

> 使用 creator-distiller，处理我提供的这位创作者的 20 篇内容，提炼概念、方法与表达结构。保留来源与冲突，材料缺失请单列，不要把这 20 篇说成他的全部作品。

本地操作详见 [数据约定与命令](creator-distiller/references/local-workflow.md)。支持中文和带空格的目录；下面 `python` 可按环境替换为 `python3` 或 `py -3`。

## 离线小样例

[examples/mini-archive](examples/mini-archive) 包含 3 条**为本项目新写的虚构文本**，不对应任何真实创作者；用于演示来源、条件差异与反例，不是蒸馏成果证明。没有放真实博主作品或私人业务资料。

在仓库根目录运行，复制到新的工作目录（若 `demo-work` 已存在，请换名称）：

```text
python -c "import shutil; shutil.copytree('examples/mini-archive', 'demo-work')"
python creator-distiller/scripts/archive.py bundle demo-work
python creator-distiller/scripts/archive.py split demo-work --groups 2
```

接下来让 Agent 按模板写总结与三件套，再运行：

```text
python creator-distiller/scripts/archive.py index demo-work
python creator-distiller/scripts/archive.py validate demo-work --stage distilled
```

未写总结或三件套时检查失败是预期行为。包内脚本不会生成分析结论；[样例说明](examples/README.md) 解释应如何读证据。

## 质量与状态

- 引用存在、文本完整、结论受到支持是三种不同检查。
- 包含离线行为测试，执行 `python -m unittest discover -s tests -v`。
- 已配置 GitHub Actions 在 Windows、macOS、Linux 上测试 Python 3.9 和 3.13。**配置存在不代表远端测试已通过**；本次本地结果见 [审查记录](REVIEW.md)。
- OpenAI 可选 UI 元数据放 `agents/openai.yaml`；其他 Agent 可忽略。没有把自定义 manifest 或关键词阈值当成所有宿主都会执行的配置。
- [行为评估用例](evals/behavior_cases.json) 是人工/Agent 回归用例，不是已通过的跨 Agent 实测结果。

## 公开发布与许可

本地发布草稿采用 MIT：允许使用、修改、分发和商业使用，并要求保留许可与版权声明。许可只适用于本仓库自有代码、说明、模板和虚构样例，不授权分发第三方原文、音视频或凭据。请把真实归档保存在仓库外；`.gitignore` 仅防常见误提交，不能替代检查暂存区。

依据：[Agent Skills 格式规范](https://agentskills.io/specification)、[GitHub 仓库许可说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)。原 1.x 包中的私有路径、非通用工具依赖和个人案例已去除；迁移与改动见 [REVIEW.md](REVIEW.md)。
