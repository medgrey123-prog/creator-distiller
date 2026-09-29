# 蒸馏大王 · Creator Distiller

[![Offline tests](https://github.com/medgrey123-prog/creator-distiller/actions/workflows/test.yml/badge.svg)](https://github.com/medgrey123-prog/creator-distiller/actions/workflows/test.yml)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**把一位创作者的多篇内容，整理成有来源、能查证、可用于实际工作的知识体系。**

你提供文章、转录或可访问的作品来源，Agent 按这套 Skill 逐条整理证据，再提炼三件套：

| 产物 | 回答的问题 | 包含什么 |
|---|---|---|
| **概念体系** | 他如何理解问题、作出判断？ | 定义、判断逻辑、适用条件、反例、原文出处 |
| **方法论地图** | 遇到具体问题，该怎么做？ | 输入、步骤、输出、验收指标、失败信号、对应概念 |
| **表达 DNA** | 内容是怎样组织和讲清楚的？ | 开场、论证结构、节奏、句式模板、跨样本规律与反例 |

每条关键结论都能回到来源。素材有缺失、观点有冲突、方法未经验证，会保留说明，不为了凑卡片数量补造内容。

**[下载 Skill 安装包](https://github.com/medgrey123-prog/creator-distiller/releases/download/v2.0.0/creator-distiller-2.0.0-skill.zip)** · **[查看输入输出示例](examples/walkthrough.md)** · **[版本与校验文件](https://github.com/medgrey123-prog/creator-distiller/releases/tag/v2.0.0)**

## 导航

- [适合拿它做什么](#适合拿它做什么)
- [快速开始](#快速开始)
- [在不同 Agent 中安装和使用](#在不同-agent-中安装和使用)
- [准备什么材料](#准备什么材料)
- [直接复制的使用指令](#直接复制的使用指令)
- [会得到怎样的结果](#会得到怎样的结果)
- [运行仓库里的小样例](#运行仓库里的小样例)
- [常见问题](#常见问题)
- [验证范围与项目文件](#验证范围与项目文件)

## 适合拿它做什么

- **系统学习一位创作者**：从多篇作品中找到反复出现的概念、方法与边界，建立可查询的知识资产。
- **提炼可执行的方法**：把“他说得有道理”细化为需要什么输入、按什么步骤做、怎样判断效果。
- **学习内容表达结构**：分析如何开场、举例、解释和收束，产出可迁移的结构模板。
- **结合自己的问题使用**：蒸馏之后补充你的目标、资源与限制，设计最小试运行，再依据实际反馈调整。

适用内容不限于运营或营销，也可以是教学、设计、技术、管理等领域。单篇摘要、整本书总结、冒充创作者本人不属于这个 Skill 的主要用途。

### 核心流程

```text
明确创作者与材料范围
         ↓
保留原文 / 音视频转录 / 图片提取结果
         ↓
逐条总结，并保留来源 ID 与原文定位
         ↓
跨篇提炼：概念 + 方法 + 表达
         ↓
回查证据，保留冲突与缺口
         ↓
交付知识资产；按需结合用户情况实际应用
```

**这是给 Agent 使用的工作方法和本地辅助工具，不是独立的全自动爬虫软件。** 本包不内置模型、浏览器、下载器、语音转录或 PDF 引擎；已有文字材料可以直接开始。只有在执行本地归档脚本时，才需要 Python 3.9+，无需安装额外 Python 包。

## 快速开始

### 1. 获取完整 Skill 文件夹

下载上方 **Skill 安装包**并解压，应该得到：

```text
creator-distiller/
├── SKILL.md
├── LICENSE
├── agents/
├── references/
├── scripts/
└── templates/
```

把**整个 `creator-distiller` 文件夹**安装到下文对应的位置。不要只复制 `SKILL.md`，也不要把整个 GitHub 仓库当作 Skill 文件夹。

若下载的是 GitHub 的 Source code ZIP，打开解压后的仓库，取其中的 **`creator-distiller/` 子目录**。需要自带样例和测试时下载完整仓库，独立 Skill 包不包含仓库级 `examples/`。

### 2. 让 Agent 读取你的材料

先用几篇能直接阅读的文章或转录跑通一次，再处理大批量资料。将材料放入当前 Agent 可读取的文件夹，或作为附件提供。

### 3. 发出第一条请求

安装后，在 Agent 对话里发送（替换方括号内容）：

```text
使用 creator-distiller，蒸馏我提供的这位创作者的内容。

材料：[文件夹、附件或已取得的正文]
范围：[例如：仅处理这 12 篇文章，不代表作者全部作品]
用途：[例如：理解他的教学判断，并提炼可用于备课的方法]
输出位置：[一个新的工作目录；没有文件工具时在对话里输出]

请逐条整理，再交付概念体系、方法论地图和表达 DNA。
关键结论附来源和原文定位；区分原作者观点、你的归纳与待验证推导。
缺失和冲突单列，不凭标题补造正文。不要改动原始文件。
```

它应先核对材料范围，再开始整理。若没有识别到 Skill，使用下面对应产品的显式调用方式或直接指定 `SKILL.md` 路径。

## 在不同 Agent 中安装和使用

以下路径和命令依据官方文档核对于 **2026-09-30**。它们是安装适配说明，**不等于已经在每个 Agent 中端到端实测**。

`~` 表示运行 Agent 的用户主目录；Windows 原生环境通常是 `%USERPROFILE%`，PowerShell 可用 `$HOME`。项目级路径相对于你让 Agent 打开的项目根目录。若 Agent 运行在 WSL、远程服务器或容器里，应安装到**该运行环境**，本机目录不会自动同步过去。

| Agent | 当前项目安装位置（完整文件夹） | 使用方式 |
|---|---|---|
| Codex | `.agents/skills/creator-distiller/` | `$creator-distiller` 后接任务 |
| Claude Code | `.claude/skills/creator-distiller/` | `/creator-distiller` 后接任务 |
| Cursor | `.cursor/skills/creator-distiller/` | 在 Agent 对话中明确要求使用 `creator-distiller` |
| Gemini CLI | 使用下方安装命令 | `/skills list` 确认后，以自然语言要求使用 |
| VS Code / GitHub Copilot | `.github/skills/creator-distiller/` | 在 Agent 聊天中选择 `/creator-distiller` |
| 其他 Agent / 普通聊天界面 | 提供文件或附件 | 明确让它读取技能入口与相关参考文件 |

### Codex

可以直接让内置安装器安装本仓库的子目录，在 **Codex 对话中**发送：

```text
$skill-installer 请安装 https://github.com/medgrey123-prog/creator-distiller
中的 creator-distiller 子目录。
```

若当前环境没有安装器，手动把完整文件夹放进项目的 `.agents/skills/`，或用户级 `~/.agents/skills/`。随后输入：

```text
$creator-distiller 蒸馏我提供的这些文章，保留来源并交付三件套。
```

没有出现时重新启动或新开会话，检查是否重复安装了同名 Skill。[Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)

### Claude Code

把文件夹放入当前项目的 `.claude/skills/`；希望本机各项目都能用，则放入 `~/.claude/skills/`。在 Claude Code 对话中输入：

```text
/creator-distiller 处理我提供的材料，输出概念、方法和表达结构。
```

本机用户目录安装不等于已同步到 Cowork 或云端会话；使用这些环境时按其技能管理方式配置。[Claude Code 官方说明](https://code.claude.com/docs/en/skills)

### Cursor

把文件夹放进项目的 `.cursor/skills/`，或个人的 `~/.cursor/skills/`。在 Customize → Skills 中检查是否发现，再在 Agent 对话中发出上面的首次请求。

Cursor 也识别 `.agents/skills/`，已在同一项目为 Codex 安装时可复用，不必重复复制。使用 Cloud Agent 时需处理同步或改用云端能读取的项目级文件，不能默认读取本机技能。[Cursor 官方说明](https://cursor.com/docs/skills)

### Gemini CLI

在**终端**执行：

```sh
gemini skills install https://github.com/medgrey123-prog/creator-distiller.git --path creator-distiller --scope user
```

只在当前项目使用时，将 `--scope user` 改为 `--scope workspace`。按 CLI 提示完成安装确认。在 Gemini 会话中执行 `/skills reload`、`/skills list`，确认存在后发送：

```text
使用 creator-distiller，蒸馏这些材料，并说明你的证据覆盖范围。
```

这里的 `/skills` 是管理命令，不把其他产品的 `$creator-distiller` 调用语法套进来。[Gemini CLI 官方说明](https://geminicli.com/docs/cli/skills/)

### VS Code / GitHub Copilot

把文件夹放进项目的 `.github/skills/`。打开该项目，在 Agent 聊天中输入 `/` 并选择 `creator-distiller`，也可通过 `/skills` 查看技能配置。

用户级目录可用 `~/.copilot/skills/`；项目里的 `.agents/skills/` 也受支持。是否允许读文件或运行命令仍取决于你当前的 Agent 工具权限。[VS Code 官方说明](https://code.visualstudio.com/docs/agent-customization/agent-skills)

### 其他 Agent 或没有 Skill 安装入口的聊天界面

无需猜测安装路径。让能读文件的 Agent 打开解压后的 `creator-distiller/SKILL.md`，并允许它按链接读取 `references/`、`templates/`；只能上传附件时，提供入口与本次任务用到的参考文件。

可发送：

```text
请读取我提供的 creator-distiller/SKILL.md，按其中的方法处理材料；
按任务需要继续读取相关参考和模板。若附件无法读取，请明确列出缺失文件。
没有执行工具时直接在对话中交付分析，不声称已运行 Python 或写入本地文件。
```

下载了 ZIP 不代表每个聊天产品都会自动安装或解压它。这个仓库发布的是 Skill 文件夹，不是已上架所有产品商店的插件。

<details>
<summary><strong>手动复制命令：macOS/Linux 与 Windows</strong>（可选，不会自动下载）</summary>

先进入**完整仓库根目录**，确认这里有 `creator-distiller/SKILL.md`。下列以 Codex/共享用户级目录为例；其他产品替换为上面指定的 Skills 父目录。目标已存在时先检查或备份旧版，别混合两个版本。

macOS / Linux：

```sh
mkdir -p "$HOME/.agents/skills"
if [ -e "$HOME/.agents/skills/creator-distiller" ]; then
  echo "目标已存在，请先检查旧版。"
else
  cp -R ./creator-distiller "$HOME/.agents/skills/creator-distiller"
fi
```

Windows PowerShell：

```powershell
$skillRoot = Join-Path $HOME '.agents/skills'
$skillTarget = Join-Path $skillRoot 'creator-distiller'
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
if (Test-Path $skillTarget) {
  Write-Host '目标已存在，请先检查旧版。'
} else {
  Copy-Item -Recurse -Path '.\creator-distiller' -Destination $skillTarget
}
```

安装完成后应有 `技能父目录/creator-distiller/SKILL.md`，不能多嵌套一层 `creator-distiller/creator-distiller/`。

</details>

## 准备什么材料

| 你已有的材料 | 怎么开始 | 需要注意 |
|---|---|---|
| 文章、Markdown、TXT | 直接交给 Agent 阅读 | 保留标题、来源链接或文件名，每篇能单独定位 |
| 音视频逐字稿 | 提供转录及对应作品信息 | 尽量带时间戳；标注机器转录及未校对术语 |
| 只有音视频文件 | 使用 Agent 已有的转录能力，或先取得转录 | 安装本 Skill 不会自动获得语音识别引擎 |
| 只有创作者主页或作品 URL | 先让 Agent 检查是否具备访问、采集能力 | 记录实际取得的内容和缺口，不能把页面简介当全文 |
| PDF、截图、图片 | 先用现有提取/OCR/视觉工具取得可读材料 | 说明文本来自何处，保留页码和无法识别部分 |

最少提供：**是谁的内容、材料在哪里、要处理哪一部分、想拿结果做什么**。如果只学习其体系，不需要先填个人业务问卷。

首次使用不必自己编写 JSON。有文件工具的 Agent 可以按 [数据约定](creator-distiller/references/local-workflow.md) 建立 `sources.json`，保存原文副本并执行辅助脚本。真实归档放到你选择的工作目录，建议位于这个公开仓库之外。

## 直接复制的使用指令

下面是任务模板，把方括号内容替换成实际信息；使用特定 Agent 时，可在开头加它的显式调用语法。

### 已有材料：系统提炼知识

```text
使用 creator-distiller。
材料在：[路径或附件]；范围：仅限这批材料。
请先列出来源清单，再逐条整理，最后交付概念体系、方法论地图和表达 DNA。
不要预设概念数量。相互矛盾的表述并列保留，说明哪些是原观点、哪些是你的归纳。
输出到：[新目录]。
```

### 只有主页：先取得可用内容

```text
使用 creator-distiller 处理这位创作者：[主页 URL]。
范围：[例如某个时间段，或最新 20 条可访问作品]。
先核对账号身份并检查当前环境是否能获取正文、下载和转录。
能取得的材料继续处理；无法取得的条目和原因列入缺口，不用标题代替转录。
报告实际覆盖范围，不将本次可见内容称为作者所有历史作品。
```

### 蒸馏之后：用于自己的实际问题

```text
基于刚才的蒸馏结果，帮我解决：[具体问题]。
我的目标：[目标]；已有条件：[资源/经验]；限制：[时间/预算/其他边界]。
只补问会改变关键决定的信息，再设计最小试运行。
每项建议标出所用方法、来源，以及我的哪条情况支持这个选择。
素材没有给出的验收指标可以建议，但必须标注为待验证推导。
```

### 原文更新：检查哪些结论需要重做

```text
在已有归档中加入或更新这些材料：[位置]。
保留原文件与来源映射，检查新增 ID、重复和缺失。
更新证据包后，回查指纹已过期的总结，再审阅受影响的三件套结论。
说明哪些结论新增、修改或出现了新的反例，不只修改指纹让检查通过。
```

## 会得到怎样的结果

有文件写入能力时，推荐把结果放在独立归档目录：

```text
my-archive/
├── sources.json          来源清单、范围与材料状态
├── raw/                  原文或转录副本
├── bundles/              每条来源的证据包
├── summaries/            每条内容的总结
├── 00_index.md           内容总索引
├── all_summaries.md       总结合集
└── distilled/
    ├── 01_concepts.md    概念体系
    ├── 02_methods.md     方法论地图
    └── 03_expression.md  表达 DNA
```

三件套还应说明适用边界、冲突与待验证事项。没有文件能力时，同样的内容可以在对话中交付。PDF 是按需转换的阅读版，不是默认依赖。

### 看一段实际格式

以下基于仓库中 **3 条新写的虚构材料**，只演示产物格式，不代表某位真实创作者的观点或方法效果。

> **C1：投入随证据调整（分析者归纳）**
>
> 探索阶段先低成本尝试，出现较稳定的需求信号后再考虑增加投入。
>
> **依据：** `[source:sample_001]` 正文第 1 段；`[source:sample_002]` 正文第 1 段。
>
> **冲突：** `[source:sample_003]` 又主张任何情况下都要先买齐设备，原文没有解释这一矛盾，因此不能替作者编造统一结论。
>
> **方法入口：** M1，小规模验证；其中具体观察周期与指标需结合使用者情况另行设定。

完整示例继续展示这张卡片如何对应到 **M1 方法卡**与**表达规律**：[原始输入 → 三件套输出](examples/walkthrough.md)。示例中的来源标记用于追踪，不是网页链接；正文定位仍需回查原材料。

## 运行仓库里的小样例

这条路线用于验证本地工具链。需要 **完整仓库 + Python 3.9+**；仅下载独立 Skill ZIP 时，请再取得完整仓库中的 `examples/`。

在完整仓库根目录打开终端。下文使用 `python`；macOS/Linux 若只有 `python3` 就替换为 `python3`，Windows 也可用 `py -3`。

### 第一步：复制样例并生成证据包

```sh
python -c "import shutil; shutil.copytree('examples/mini-archive', 'demo-work')"
python creator-distiller/scripts/archive.py bundle demo-work
python creator-distiller/scripts/archive.py split demo-work --groups 2
```

应看到 `Bundles written: 3`、`COVERAGE OK: 3 sources; 2 groups` 以及 `STRUCTURE PASS`。若 `demo-work` 已存在，请换一个新的目录名，并同步修改后续命令；不要覆盖已有练习。

### 第二步：让 Agent 完成分析

把下面的话发给可读写该目录的 Agent：

```text
读取 creator-distiller/SKILL.md，处理 demo-work 中的 3 条虚构素材。
按 creator-distiller/templates/summarize_brief.md 为每条生成总结，并保留对应 bundle 指纹。
再按 creator-distiller/templates/distill_briefs.md 生成三份 distilled 文件。
这些是测试材料，只展示有证据的归纳，保留第三条与前两条的冲突，不声称效果已验证。
```

这里的两个模板位于 `creator-distiller/templates/`。**分析由 Agent 完成，Python 脚本不会自行生成总结或三件套。**

### 第三步：生成索引并核验

```sh
python creator-distiller/scripts/archive.py index demo-work
python creator-distiller/scripts/archive.py validate demo-work --stage distilled
```

成功时显示 `STRUCTURE PASS`，退出码为 0；缺文件、引用异常或总结指纹过期时退出码为 2。未执行第二步就直接核验，失败是预期结果。

机械检查确认来源 ID、文件覆盖与输入指纹等结构；是否忠于原文仍需按 [质量检查](creator-distiller/references/quality-gates.md) 回查。命令参数、清单字段和重跑行为见 [本地工具文档](creator-distiller/references/local-workflow.md)。

## 常见问题

**装好后没有出现这个 Skill？**

检查完整文件夹是否放在当前 Agent 实际扫描的目录、是否多嵌套一层，以及当前会话是否处于对应项目。刷新技能列表或重启会话；远程/WSL 环境要检查运行环境内的目录。仍未识别时直接让 Agent 读取入口文件，不用反复安装同名副本。

**能一条指令抓完某个博主的所有内容吗？**

只有当前环境具备相应采集与转录能力时，Agent 才能尝试完整流程。这个包本身不提供这些引擎。私密、删除或无法访问的作品必须留作缺口；抖音接入见 [平台说明](creator-distiller/references/douyin-pipeline.md)。

**一定要提供几十或上百篇吗？**

没有固定篇数。少量材料也能分析，但应把结论标为样本内观察；跨题材、跨时期反复出现的模式才更有依据。大批材料可以分组处理，不能读不完却宣称已覆盖全部。

**需要 API Key、GPU 或额外付费吗？**

本地辅助脚本不需要 API Key、GPU 或第三方 Python 包。Agent 模型、浏览/转录服务的费用和硬件要求由你选择的工具决定，不包含在这个仓库中。

**提示 `summary input fingerprint missing or stale`？**

原文或来源元数据可能已变化，或总结没有记录输入指纹。重新生成 bundle，核对总结与新材料是否一致后再更新指纹。已有三件套也应审阅，不能仅改注释绕过检查。

**能直接放进 Obsidian 或其他知识库吗？**

默认产物是 Markdown，可以阅读或导入。自动写入已有知识库需要匹配它的目录、引用规则与授权；见 [知识库集成说明](creator-distiller/references/knowledge-integration.md)。

**怎样更新或卸载？**

手动安装时，先备份自行修改过的技能目录，再用新版本的完整目录替换它；卸载时只移除这一个 Skill 文件夹。用户归档不要存进技能安装目录。Gemini CLI 安装可用其 `gemini skills uninstall creator-distiller --scope user` 命令卸载，再按上文安装所需版本。

## 验证范围与项目文件

- **离线工具已实测：** Windows、macOS、Linux × Python 3.9/3.13，6 个任务各运行 19 项测试并通过。[2.0 发布提交的 CI](https://github.com/medgrey123-prog/creator-distiller/actions/runs/36606124807)
- **安装路径已核对文档：** 上述各 Agent 的官方链接列在对应章节；不把文档适配说成逐个产品的端到端测试。
- **尚未验证：** 所有 Agent 的实际蒸馏效果、在线平台抓取、ASR 和 PDF。能力存在、结构正确与分析结论正确是不同层面的事情。

本地开发验证：

```sh
python -m unittest discover -s tests -v
```

| 文件 | 作用 |
|---|---|
| [SKILL.md](creator-distiller/SKILL.md) | Agent 使用的核心工作规则 |
| [templates/](creator-distiller/templates/) | 总结、三件套和采访提示 |
| [references/](creator-distiller/references/) | 数据约定、核验、采集重建与集成说明 |
| [archive.py](creator-distiller/scripts/archive.py) | 证据包、分组、转录任务分片、索引和结构检查 |
| [examples/](examples/) | 虚构输入及完整产物示意 |
| [tests/](tests/) | 离线工具行为测试 |
| [evals/](evals/) | Agent 行为评估用例，尚未自动运行 |
| [REVIEW.md](REVIEW.md) | 从原始版本到公开版的审查与修改记录 |

## 许可

采用 [MIT License](LICENSE)，允许使用、修改、分发和商业使用，须保留许可及版权声明。许可覆盖本仓库的自有代码、文档、模板和虚构样例，不包含第三方创作者的作品授权。真实语料、账号凭据与私人归档不要提交到公开仓库。
