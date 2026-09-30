# 共脑V1.0

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**完整理解一个人的知识、思维与表达，再把它变成能帮助你思考、表达或持续解决问题的能力。**

版本：共脑V1.0；技能标识 `gongnao`，版本 `1.0.0`。

[下载 Skill 安装包](https://github.com/medgrey123-prog/creator-distiller/releases/download/gongnao-v1.0.0/gongnao-v1.0.0-skill.zip) · [完整源码与发布说明](https://github.com/medgrey123-prog/creator-distiller/releases/tag/gongnao-v1.0.0)

共脑先保留原始材料，逐条详细提炼，再按照你的选择生成新的 Skill 或服务助手包。三项可以单选、多选或全选：

| 选择 | 你拿来做什么 | 最终交付 |
|---|---|---|
| **思维方式** | 借用他的概念、底层前提与判断方法，分析自己的新问题 | 独立思考型 Skill + 对应详细知识库 |
| **表达型** | 借用他的组织与论证逻辑，表达自己的内容 | 独立表达型 Skill + 表达结构及必要知识 |
| **持续服务者** | 以明确的专业服务角色，了解你的情况、交付方案并持续跟进 | 服务 Skill + 身份定义 + 服务流程 + 启动指令 + 私人状态记录模板 |

**选项决定怎么用，不决定提炼有多深。** 即使只选思考型，原始资料、逐条详解、概念、方法与判断、表达与论证仍完整保留；不会用一页概览替代详细底库。需要补做另一种能力时，从原底库继续生成。

## 导航

- [适合什么对象](#适合什么对象)
- [快速开始与首次问询](#快速开始与首次问询)
- [在不同 Agent 中安装和使用](#在不同-agent-中安装和使用)
- [准备什么材料](#准备什么材料)
- [直接复制的使用指令](#直接复制的使用指令)
- [会得到怎样的结果](#会得到怎样的结果)
- [持续服务助手怎么使用](#持续服务助手怎么使用)
- [运行仓库里的小样例](#运行仓库里的小样例)
- [常见问题](#常见问题)
- [验证范围与项目文件](#验证范围与项目文件)

## 适合什么对象

法律、医学、科学、工程、教育、人文、商业和日常经验等领域都可以处理。对象可以是专家、老师、创作者、普通人或多位发言人；不要求是博主，也不默认用于账号运营或内容营销。

支持文章、课程、演讲、访谈、讨论、音视频转录等可读材料。多位讲述者的观点分别归属；单篇也可分析，但不能凭单篇宣称掌握一个人的稳定风格或完整思想。

### 核心流程

```text
问清对象、材料范围与所选用途
              ↓
保留原文，按段落/时间范围逐条详解
              ↓
形成完整底库：概念 + 方法与判断 + 表达与论证
              ↓
回查证据，保留案例、条件、反例、冲突与缺口
              ↓
仅生成所选能力包，并放入对应详细资料
              ↓
用具体任务试运行，交付使用方法与实际验证状态
```

这是供 Agent 执行的 Skill 和离线辅助工具。本包不内置模型、浏览器、下载器、语音转录或 PDF 引擎。文字材料可以直接开始；使用归档脚本才需要 Python 3.9+，不需额外 Python 包。

## 快速开始与首次问询

### 1. 一键安装（macOS / Linux / Windows 通用）

先从上方链接下载安装包并解压，或从仓库的 Code → Download ZIP 获取源码。安装器需要 Python 3.9+，离线执行，不装额外依赖。在仓库根目录（或解压后的安装包目录）执行：

```sh
python3 gongnao/scripts/install.py
```

Windows 把 `python3` 换成 `py -3` 或 `python`。

默认装到两个位置，供下表列出的 Agent 发现；是否启用仍以宿主设置与权限为准：

| 位置 | 被谁读取 |
|---|---|
| `~/.agents/skills/gongnao/` | Codex、Gemini CLI、Cursor、VS Code / GitHub Copilot |
| `~/.claude/skills/gongnao/` | Claude Code |

在终端运行时，安装器会先列出位置，让你回车确认或改选；加 `--yes` 则直接执行（给 Agent 代跑时使用）。其他常用参数：

| 参数 | 作用 |
|---|---|
| `--target claude` | 只装某一个位置，可重复；可选 `agents` `claude` `cursor` `gemini` `copilot` `github` `all` |
| `--project <项目目录>` | 装到项目级目录（如 `<项目>/.agents/skills/`）而不是用户目录 |
| `--dry-run` | 只显示将要做什么 |
| `--force` | 已有不同版本时，先备份到 `~/.gongnao-backups/` 再替换 |
| `--uninstall` | 卸载；旧文件移到 `~/.gongnao-backups/`，不直接删除 |

`github` 目标只用于 `--project`；`copilot` 目标只用于用户级安装。`--target all` 会跳过与当前范围不兼容的目录；通常只选自己使用的位置，避免重复发现。

重复运行是安全的：内容相同显示 `already up to date`；内容不同且没加 `--force` 时不会覆盖你的修改。安装完成后，重启或新开 Agent 会话。

想手动安装也可以：把完整的 `gongnao/` 文件夹复制到下文对应的技能目录。安装后应当是 `技能父目录/gongnao/SKILL.md`，不能多嵌套一层。

```text
gongnao/
├── SKILL.md
├── LICENSE
├── agents/
├── examples/      成品能力包示例
├── references/
├── scripts/       archive.py 归档工具、install.py 安装器
└── templates/
```

### 2. 提供材料并选择用途

```text
使用 gongnao。
对象：[是谁，主要讲什么]。
材料：[文件夹、附件或可访问来源]。
范围：[例如仅这 12 篇文章]。
我选择：思维方式、表达型。
请保持完整细粒度提炼，再生成两个独立可用的 Skill。
试运行任务：[一个我希望用它完成的具体问题；暂时没有可以说明]。
输出到：[新工作目录]。
```

安装本身不会自动问话。**首次调用时**，Agent 会从已提供的信息出发，补问对象、材料范围及三项用途中的缺口。你已经说明的内容不重问；可以选一项，也可以三项都选。

### 3. 得到能力包后使用

把生成包的整个文件夹安装到相应 Agent 技能目录，调用其自己的技能名称，并给出你的实际问题。它会读取包内相关详细知识，而不是每次要求重新处理原始材料。

能力包由 Agent 根据你的资料实际生成；安装共脑不会预装某位人物的知识。没有安装入口的环境也可直接读取生成包的 `SKILL.md` 及其资料。持续服务者另按 `START.md` 启动。

## 在不同 Agent 中安装和使用

一键安装器已经覆盖下表路径；本节供手动安装或排查时参考。以下路径和命令依据官方文档核对于 **2026-09-30**。它们是安装适配说明，**不等于已经在每个 Agent 中端到端实测**。

`~` 表示运行 Agent 的用户主目录；Windows 原生环境通常是 `%USERPROFILE%`，PowerShell 可用 `$HOME`。项目级路径相对于你让 Agent 打开的项目根目录。若 Agent 运行在 WSL、远程服务器或容器里，应安装到**该运行环境**，本机目录不会自动同步过去。

| Agent | 当前项目安装位置（完整文件夹） | 使用方式 |
|---|---|---|
| Codex | `.agents/skills/gongnao/` | `$gongnao` 后接任务 |
| Claude Code | `.claude/skills/gongnao/` | `/gongnao` 后接任务 |
| Cursor | `.cursor/skills/gongnao/` | 在 Agent 对话中明确要求使用 `gongnao` |
| Gemini CLI | `.agents/skills/gongnao/` 或 `.gemini/skills/gongnao/`，也可用下方命令 | `/skills list` 确认后，以自然语言要求使用 |
| VS Code / GitHub Copilot | `.github/skills/gongnao/` | 在 Agent 聊天中选择 `/gongnao` |
| 其他 Agent / 普通聊天界面 | 提供文件或附件 | 明确让它读取技能入口与相关参考文件 |

### Codex

把本地完整 `gongnao/` 文件夹复制到项目的 `.agents/skills/`，或用户级 `~/.agents/skills/`。随后输入：

```text
$gongnao 处理这些文章，完整提炼后生成思考型和表达型两个 Skill。
```

没有出现时重新启动或新开会话，检查是否重复安装了同名 Skill。[Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)

### Claude Code

把文件夹放入当前项目的 `.claude/skills/`；希望本机各项目都能用，则放入 `~/.claude/skills/`。在 Claude Code 对话中输入：

```text
/gongnao 处理这些材料，保留完整知识底库，并生成持续服务助手包。
```

本机用户目录安装不等于已同步到 Cowork 或云端会话；使用这些环境时按其技能管理方式配置。[Claude Code 官方说明](https://code.claude.com/docs/en/skills)

### Cursor

把文件夹放进项目的 `.cursor/skills/`，或个人的 `~/.cursor/skills/`。在 Customize → Skills 中检查是否发现，再在 Agent 对话中发出上面的首次请求。

Cursor 也识别 `.agents/skills/`，已在同一项目为 Codex 安装时可复用，不必重复复制。使用 Cloud Agent 时需处理同步或改用云端能读取的项目级文件，不能默认读取本机技能。[Cursor 官方说明](https://cursor.com/docs/skills)

### Gemini CLI

Gemini CLI 同样读取 `~/.agents/skills/`（优先于 `~/.gemini/skills/`），一键安装器装好后就能用，不必重复安装。也可以在**本地源码根目录的终端**使用它自带的命令：

```sh
gemini skills install ./gongnao --scope user
```

只在当前项目使用时，将 `--scope user` 改为 `--scope workspace`。按 CLI 提示完成安装确认。在 Gemini 会话中执行 `/skills reload`、`/skills list`，确认存在后发送：

```text
使用 gongnao，完整提炼这些材料，并生成思考型 Skill，说明证据覆盖与试运行状态。
```

这里的 `/skills` 是管理命令，不把其他产品的 `$gongnao` 调用语法套进来。[Gemini CLI 官方说明](https://geminicli.com/docs/cli/skills/)

### VS Code / GitHub Copilot

把文件夹放进项目的 `.github/skills/`。打开该项目，在 Agent 聊天中输入 `/` 并选择 `gongnao`，也可通过 `/skills` 查看技能配置。

用户级目录可用 `~/.copilot/skills/`；项目里的 `.agents/skills/` 也受支持。是否允许读文件或运行命令仍取决于你当前的 Agent 工具权限。[VS Code 官方说明](https://code.visualstudio.com/docs/agent-customization/agent-skills)

### 其他 Agent 或没有 Skill 安装入口的聊天界面

无需猜测安装路径。让能读文件的 Agent 打开解压后的 `gongnao/SKILL.md`，并允许它按链接读取 `references/`、`templates/`；只能上传附件时，提供入口与本次任务用到的参考文件。

可发送：

```text
请读取我提供的 gongnao/SKILL.md，按其中的方法处理材料；
按任务需要继续读取相关参考和模板。若附件无法读取，请明确列出缺失文件。
没有执行工具时直接在对话中交付分析，不声称已运行 Python 或写入本地文件。
```

下载了 ZIP 不代表每个聊天产品都会自动安装或解压它。本地交付的是 Skill 文件夹，不是已上架所有产品商店的插件。

<details>
<summary><strong>手动复制命令：macOS/Linux 与 Windows</strong>（可选，不会自动下载）</summary>

先进入**完整仓库根目录**，确认这里有 `gongnao/SKILL.md`。下列以 Codex/共享用户级目录为例；其他产品替换为上面指定的 Skills 父目录。目标已存在时先检查或备份旧版，别混合两个版本。

macOS / Linux：

```sh
mkdir -p "$HOME/.agents/skills"
if [ -e "$HOME/.agents/skills/gongnao" ]; then
  echo "目标已存在，请先检查旧版。"
else
  cp -R ./gongnao "$HOME/.agents/skills/gongnao"
fi
```

Windows PowerShell：

```powershell
$skillRoot = Join-Path $HOME '.agents/skills'
$skillTarget = Join-Path $skillRoot 'gongnao'
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
if (Test-Path $skillTarget) {
  Write-Host '目标已存在，请先检查旧版。'
} else {
  Copy-Item -Recurse -Path '.\gongnao' -Destination $skillTarget
}
```

安装完成后应有 `技能父目录/gongnao/SKILL.md`，不能多嵌套一层 `gongnao/gongnao/`。

</details>

## 各领域需要保留的条件

| 内容领域 | 重点记录 |
|---|---|
| 法律 | 适用地区、时间、规范与案例事实，区别个人解读和有效规则 |
| 医学与健康 | 人群、证据类型、适用条件，区别科普、个人经验和个体诊疗建议 |
| 科学与工程 | 假设、单位、版本、实验条件、误差和可复现性 |
| 人文与哲学 | 定义、前提、价值立场与反对意见，不强行统一分歧 |
| 其他领域 | 按主张性质确定证据与适用边界，不套固定行业模板 |

理解一个人的观点不等于证明观点正确。需要现实应用时再核对相应领域的现行依据；材料不足保留未知。完整规则见 [领域与证据边界](gongnao/references/domain-boundaries.md)。

## 准备什么材料

| 你已有的材料 | 怎么开始 | 需要注意 |
|---|---|---|
| 文章、Markdown、TXT | 直接交给 Agent 阅读 | 保留标题、来源链接或文件名，每篇能单独定位 |
| 音视频逐字稿 | 提供转录及对应作品信息 | 尽量带时间戳；标注机器转录及未校对术语 |
| 只有音视频文件 | 使用 Agent 已有的转录能力，或先取得转录 | 安装本 Skill 不会自动获得语音识别引擎 |
| 只有讲述者主页或作品 URL | 先让 Agent 检查是否具备访问、采集能力 | 记录实际取得的内容和缺口，不能把页面简介当全文 |
| PDF、截图、图片 | 先用现有提取/OCR/视觉工具取得可读材料 | 说明文本来自何处，保留页码和无法识别部分 |

最少提供：**是谁的内容、材料在哪里、要处理哪一部分、想拿结果做什么**。如果只学习其体系，不需要先填个人业务问卷。

首次使用不必自己编写 JSON。有文件工具的 Agent 可以按 [数据约定](gongnao/references/local-workflow.md) 建立 `sources.json`，保存原文副本并执行辅助脚本。真实归档放到你选择的工作目录，建议位于这个公开仓库之外。

## 直接复制的使用指令

替换方括号中的内容。特定 Agent 可在开头使用自己的调用语法。

### 生成思考型和表达型

```text
使用 gongnao。材料在：[位置]；范围：仅本批材料。
选择思维方式和表达型。原始材料与详细知识底库完整保留，不压缩成概览。
生成两个各自带对应资料库、可独立使用的 Skill。
思考型试运行：[我的问题]；表达型试运行：[我的事实、受众和表达目的]。
没有原文依据的推导单独标注；冲突、条件和反例保留。
```

### 生成持续服务者

```text
使用 gongnao，处理这位讲述者的资料：[材料与范围]。
只选择持续服务者。我希望它作为：[服务角色]，持续帮助我：[服务任务]。
请先完整提炼，再交付独立服务 Skill、角色定义、服务流程、启动指令及状态模板。
本次只生成本地包，不创建对话、不配置后台运行。
首个实际任务：[我的问题；没有就标记待试运行]。
```

### 只有主页，先检查资料能否取得

```text
使用 gongnao。对象：[主页 URL]；范围：[时间或作品数量]。
我选择：[思维方式/表达型/持续服务者，可多选]。
核对身份与当前访问、下载、转录能力，能取得的内容继续处理。
无法取得的条目和原因保留，不用标题冒充转录，不宣称取得全部历史作品。
按实际覆盖范围生成所选能力，明确缺口是否影响使用。
```

### 后续增加一种能力

```text
基于已有完整共脑归档：[目录]，再生成表达型 Skill。
请读取底库的表达与论证资料、相关概念和原文，不只读取已有思考型入口。
保留现有包；新包放入独立目录，并记录使用的底库版本。
试运行内容：[我自己的事实、受众、目的]。
```

### 原文更新与能力同步

```text
在已有归档中加入或更新：[资料位置]。
保留原文件与用户修改，回查已过期的详解、知识卡和受影响的能力包。
说明新增观点、反例与冲突，生成更新包并重新检查相关试运行任务。
不要仅刷新指纹或日期来通过检查，也不要覆盖私人服务记录。
```

明确只想阅读知识库时，也可以说“本次只交付完整知识底库，不生成能力包”。普通简短摘要请求无需运行整套流程。

## 会得到怎样的结果

产物分为完整底库和选定能力包，放在独立工作目录：

```text
my-archive/
├── request.md            已选用途、范围、任务与待补信息
├── sources.json          来源清单与正文状态
├── raw/                  原文或转录副本
├── bundles/              单条证据包
├── summaries/            每条材料的详细解析与覆盖记录
├── 00_index.md           资料索引
├── all_summaries.md       详解合集
├── insights/
│   ├── 01_concepts.md    概念、前提、推理链、关系、案例与反例
│   ├── 02_methods.md     方法步骤或判断框架、条件与失败信号
│   └── 03_expression.md  表达和论证顺序、作用、变化与反例
├── deliverables/         仅创建已选类型
│   ├── subject-thinking/
│   ├── subject-expression/
│   └── subject-service/
└── delivery.md           包位置、启动方式、验证状态与缺口
```

文件数量由实际资料规模和选择决定；长资料可分主题文件并建立索引，详细内容不会因此省略。不是要求你逐一阅读所有文件：底库保留供回查，实际使用从对应 Skill 或服务入口开始。

一个思考型/表达型包通常包含：

```text
subject-thinking/
├── SKILL.md              如何使用知识处理新任务
├── knowledge/
│   ├── index.md          问题到详细资料的导航
│   ├── sources.md        来源 ID 与定位
│   ├── provenance.md     底库版本、资料范围与缺口
│   ├── evidence/         必要证据
│   └── ...               对应的完整知识卡、案例和限制
└── trial.md              实际试运行或待运行记录
```

`subject` 是生成时替换的人物/体系标识。包内使用相对路径，必要资料随包带走，不偷偷依赖原电脑目录。底库变更后应同步检查各包；它们不会自动实时同步。

三个示例对照看：

- [流程示意](examples/walkthrough.md)：三种能力怎样使用同一份底库（虚构材料）。
- [成品包示例 causal-check-thinking](gongnao/examples/causal-check-thinking/README.md)：一个完整的思考型能力包，包括入口、知识、来源、指纹和试运行记录（虚构材料）。
- [真实产出节选：姜胡说](examples/real-excerpt-jianghushuo/README.md)：旧版对 100 条抖音作品真实提炼的节选，展示历史卡片的颗粒度；其中统计与归属未经本次复核，不代表当前版本验收结果。

## 持续服务助手怎么使用

服务包在上述结构之外还包含：

| 文件 | 内容 |
|---|---|
| `ROLE.md` | 服务身份、思考原则、沟通方式、能力边界 |
| `SERVICE.md` | 了解情况、判断、交付、收集反馈和修订的流程 |
| `START.md` | 当前环境怎么载入、可复制的启动指令、文件访问检查 |
| `workspace-template/` | 空白用户背景、当前状态、服务记录模板 |

你可以在新对话、专属项目或支持的 Agent 中启动。**新的聊天窗口不会自动继承知识和记忆**：必须让它读到整个包及实际的私人工作目录。共脑会给出这套启动说明；只有你要求且工具支持时才代为创建和配置。

每次服务将目标、事实、已做决定、待办与反馈保存在私人工作目录；下一次先读取状态再继续。公共能力包不保存个人服务记录。没有持久文件工具时，助手交付可保存的状态文本，下次需要你一起提供。

“持续”默认表示再次调用时能衔接，不意味着自动后台工作、提醒或跨平台同步。这些功能需要另外指定，并由宿主提供能力。

角色从材料与服务目标建立，不冒充原作者本人，也不继承其职业资格。法律、医学等实际应用还须检查相应的现行依据、地区、人群和个体条件。

## 运行仓库里的小样例

这条路线用于验证本地工具链。需要 **完整仓库 + Python 3.9+**；仅下载独立 Skill ZIP 时，请再取得完整仓库中的 `examples/`。

在完整仓库根目录打开终端。下文使用 `python3`；Windows 换成 `py -3` 或 `python`。自己的真实材料可以先放进 `<归档>/raw/`，再用 `archive.py init <归档>` 自动生成初始 `sources.json`。

### 第一步：复制样例并生成证据包

```sh
python3 -c "import shutil; shutil.copytree('examples/mini-archive', 'demo-work')"
python3 gongnao/scripts/archive.py bundle demo-work
python3 gongnao/scripts/archive.py split demo-work --groups 2
```

应看到 `Bundles written: 3`、`COVERAGE OK: 3 sources; 2 groups` 以及 `STRUCTURE PASS`。如果某条来源在 `sources.json` 里登记为 `missing`，会显示 `GAP:` 与 `STRUCTURE PASS WITH GAPS`：其余材料照常继续，但结果不能称为全量。若 `demo-work` 已存在，请换一个新的目录名，并同步修改后续命令；不要覆盖已有练习。

### 第二步：让 Agent 完成分析

把下面的话发给可读写该目录的 Agent：

```text
读取 gongnao/SKILL.md，处理 demo-work 中的 3 条虚构素材。
本次明确只做知识底库演练，不生成能力包。
按 gongnao/templates/summarize_brief.md 为每条生成详细解析，并保留对应 bundle 指纹。
再按 gongnao/templates/knowledge_briefs.md 生成三份 insights 文件。
这些是测试材料，只展示有证据的归纳，保留第三条与前两条的论证冲突，不声称效果已验证。
```

这里的两个模板位于 `gongnao/templates/`。**分析由 Agent 完成，Python 脚本不会自行生成总结或三件套。**

### 第三步：生成索引并核验

```sh
python3 gongnao/scripts/archive.py index demo-work
python3 gongnao/scripts/archive.py validate demo-work --stage insights
```

成功时显示 `STRUCTURE PASS`，退出码为 0；缺文件、引用异常或总结指纹过期时退出码为 2。未执行第二步就直接核验，失败是预期结果。

机械检查确认来源 ID、文件覆盖与输入指纹等结构；是否忠于原文仍需按 [质量检查](gongnao/references/quality-gates.md) 回查。命令参数、清单字段和重跑行为见 [本地工具文档](gongnao/references/local-workflow.md)。

## 常见问题

**为什么知识文件仍然详细，不按选择删减？**

选择决定最终要生成的能力。完整底库让你能回查证据、理解条件，并在以后增加其他类型；索引与按需加载解决使用时的信息量，不靠减少提炼细度。

**是不是还要另做一个系统把知识转成 Skills？**

共脑已经包含生成与试运行阶段。思考型、表达型是独立 Skills；持续服务者在 Skill 外增加角色、流程、启动和状态机制，无需另装一个转换系统。

**写好了文件就代表可以用了？**

先检查文件与资料是否完整，再使用具体任务试运行。没有实际任务时会标为“已生成、待试运行”。模板、格式检查、样例运行、真实使用与用户验收分别记录。

**装好后没有出现这个 Skill？**

先重启或新开会话，再用 `python3 gongnao/scripts/install.py --dry-run` 查看安装位置。检查完整文件夹是否放在当前 Agent 实际扫描的目录、是否多嵌套一层，以及当前会话是否处于对应项目。刷新技能列表或重启会话；远程/WSL 环境要检查运行环境内的目录。仍未识别时直接让 Agent 读取入口文件，不用反复安装同名副本。

**能只给一个人的名字，就取得他的所有内容吗？**

先需要可明确识别的来源范围；只有当前环境具备相应访问、采集与转录能力时，Agent 才能尝试完整流程。这个包本身不提供这些引擎。私密、删除或无法访问的作品必须留作缺口；抖音接入见 [平台说明](gongnao/references/douyin-pipeline.md)。

**一定要提供几十或上百篇吗？**

没有固定篇数。少量材料也能分析，但应把结论标为样本内观察；跨题材、跨时期反复出现的模式才更有依据。大批材料可以分组处理，不能读不完却宣称已覆盖全部。

**需要 API Key、GPU 或额外付费吗？**

本地辅助脚本不需要 API Key、GPU 或第三方 Python 包。Agent 模型、浏览/转录服务的费用和硬件要求由你选择的工具决定，不包含在这个仓库中。

**提示 `malformed source citation`？**

引用只接受 `[source:ID]`，定位写在方括号外面，例如 `[source:dy_123] 02:15`。多个来源分别写方括号。

**提示 `Not UTF-8 text`？**

报错里的原文文件不是 UTF-8（常见于 Windows 的 GBK 文本）。用编辑器另存为 UTF-8 后重跑。

**提示 `summary input fingerprint missing or stale`？**

原文或来源元数据可能已变化，或总结没有记录输入指纹。重新生成 bundle，核对总结与新材料是否一致后再更新指纹。已有三件套也应审阅，不能仅改注释绕过检查。

**能直接放进 Obsidian 或其他知识库吗？**

默认产物是 Markdown，可以阅读或导入。自动写入已有知识库需要匹配它的目录、引用规则与授权；见 [知识库集成说明](gongnao/references/knowledge-integration.md)。

**怎样更新或卸载？**

用新版本仓库运行 `python3 gongnao/scripts/install.py --force` 更新（旧版自动备份到 `~/.gongnao-backups/`），`--uninstall` 卸载。手动安装时，先备份自行修改过的技能目录，再用新版本的完整目录替换它；卸载时只移除这一个 Skill 文件夹。用户归档不要存进技能安装目录。Gemini CLI 安装可用其 `gemini skills uninstall gongnao --scope user` 命令卸载，再按上文安装所需版本。

## 验证范围与项目文件

- 离线归档工具与安装器使用 Python 3.9+ 标准库；本次实际检查结果见 [VERIFICATION.json](VERIFICATION.json) 与 [修改记录](REVIEW.md)。
- `archive.py validate` 只检查底库结构，不能证明提炼完整、结论正确或生成包可用。
- 三类交付规则及行为评估用例已更新；各 Agent 实际加载与真实专业服务尚未逐一实测。离线脚本的系统矩阵结果请查看 [当前提交的 Actions](https://github.com/medgrey123-prog/creator-distiller/actions/workflows/test.yml)，以实际运行结果为准。安装器的目录约定依据官方文档，测试在临时目录中模拟完成，不等于已在每个 Agent 里确认加载。安装说明与运行验证分开看待。
- 在线获取、转录、文件持久化和服务运行由当前环境提供。跨平台可移植不等于所有产品自动安装并具备同样权限。

本地工具测试：

```sh
python3 -m unittest discover -s tests -v
```

| 文件 | 作用 |
|---|---|
| [SKILL.md](gongnao/SKILL.md) | 完整工作流入口 |
| [需求问询](gongnao/references/intake.md) | 多选用途与必要信息 |
| [能力交付](gongnao/references/capability-delivery.md) | 独立包、知识映射与可移植性 |
| [服务助手](gongnao/references/service-assistant.md) | 角色、流程、状态及启动 |
| [templates/](gongnao/templates/) | 详细提炼、思考/表达生成要求与试运行记录 |
| [archive.py](gongnao/scripts/archive.py) | 初始化清单、证据包、分组、索引与底库结构检查 |
| [install.py](gongnao/scripts/install.py) | 跨平台一键安装、更新与卸载 |
| [gongnao/examples/](gongnao/examples/) | 随安装包分发的成品能力包示例 |
| [examples/](examples/) | 虚构材料、流程演示与真实产出节选 |
| [tests/](tests/) | 离线工具测试 |
| [evals/](evals/) | 待执行的 Agent 行为评估任务 |

## 许可

采用 [MIT License](LICENSE)，允许使用、修改、分发和商业使用，须保留许可及版权声明。许可覆盖本仓库的自有代码、文档、模板和虚构样例，不包含第三方讲述者的作品授权；`examples/real-excerpt-jianghushuo/` 的权利说明见该目录 README。真实语料、账号凭据和私人服务记录不要提交到公开仓库。
