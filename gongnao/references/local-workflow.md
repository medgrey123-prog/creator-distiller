# 本地数据约定与命令

辅助脚本只处理本地文件，不抓取网站、不转录音频、不调用模型、不上传资料。Python 3.9+ 标准库即可，无 pip 依赖。下列命令中的 `<SKILL>` 指本技能目录的**绝对路径**，归档也写绝对路径；不要切到技能目录后用相对路径，否则归档会被解析到技能安装目录里。按本机环境选择 `python3`、`python` 或 Windows 的 `py -3`。路径带空格或中文时加引号。

## 输入

归档放在发布仓库之外的用户工作目录，结构为：

```text
archive/
  request.md           Agent 记录需求选择与任务目标
  sources.json
  raw/                 原文或转录（只读输入）
  bundles/             脚本生成的单条证据包
  summaries/           Agent 编写的逐条总结
  insights/            Agent 编写的三份详细知识资料
  deliverables/        Agent 生成所选能力包
  delivery.md          Agent 记录交付与实际验证状态
```

`sources.json` 示例：

```json
{
  "schema_version": 1,
  "scope": {
    "requested": "用户提供的一份本地文字材料",
    "status": "complete",
    "observed_at": "2026-09-30T00:00:00+08:00",
    "evidence": "逐一核对用户提供的文件清单；不代表该讲述者全部作品"
  },
  "sources": [
    {
      "source_id": "local_001",
      "title": "材料标题",
      "kind": "text",
      "url": "",
      "published_at": "",
      "duration_seconds": 0,
      "status": "complete",
      "text_origin": "provided_text",
      "text_path": "raw/local_001.txt"
    }
  ]
}
```

实际 `sources` 须逐条列出完整清单，不能遗漏范围内的材料。

- `source_id`：稳定文件标识，1–96 个 ASCII 字母/数字/下划线/连字符，以字母或数字开头；不使用 Windows 保留名；不区分大小写也须唯一。原平台 ID 可加平台前缀，如 `dy_123`、`yt_abc`。可另加 `original_id` 保留原标识。
- `kind`：video/audio/article/image/text。不能仅以时长判断类型。
- `status`：complete/partial/missing，表示**当前条目正文**是否完整，不表示它的观点正确。缺失仍登记，不从分母剔除。
- `text_origin`：asr/manual_transcript/article_body/ocr/visual_description/provided_text/page_excerpt/unavailable。音视频标 complete 需 asr 或 manual_transcript；摘要不能标全文。ASR 完整与校对正确是不同概念，另可加 `transcription_review` 说明。
- `text_path`：归档内 `raw/` 下的 UTF-8 文本，相对路径统一用 `/`。missing 可省略。不得使用绝对路径、`..`、跨根目录的软链接、Windows 盘符或反斜线。为能跨系统复制，文件名宜用同一安全 ID，避免系统保留字符。
- `url`：公开 HTTP(S) 链接；本地资料为空。不要存 Cookie、密钥、带凭据或短时签名的下载链接。
- `published_at`：已知时用 ISO 8601，未知为空；`duration_seconds` 是非负秒数，未知可省略。
- `scope.status` 是**请求范围**的 complete/partial/unknown。`requested`、`observed_at`、`evidence` 必填，记录范围、采集时间和完整性证据/限制。脚本不会自动证明此陈述。

## 操作

```text
python3 "<SKILL>/scripts/archive.py" init "/abs/path/to/archive"
python3 "<SKILL>/scripts/archive.py" bundle "/abs/path/to/archive"
python3 "<SKILL>/scripts/archive.py" split "/abs/path/to/archive" --groups 3
python3 "<SKILL>/scripts/archive.py" shard "/abs/path/to/archive" --groups 3
```

`init` 在 `sources.json` 不存在时，按 `raw/` 下的 `.txt`/`.md` 生成初始清单（kind=text、scope.status=unknown），同时提示非 UTF-8 文件；它从不覆盖已有清单，生成后必须核对范围、类型、标题与链接。`bundle` 生成证据包与输入指纹；标为 complete/partial 却没有正文会返回失败。`split` 先以来源清单检查每一条是否齐全、是否过期，然后写 `groups.json`，每组存相对 bundle 路径；单 Agent 也能依组顺序工作。`shard` 按音视频时长尽量均衡写 `shards.json`，未知时长按条数分摊；它只生成任务清单，不运行 ASR。

依据 [逐条模板](../templates/summarize_brief.md) 编写总结，复制 bundle 顶部的指纹注释。然后：

```text
python3 "<SKILL>/scripts/archive.py" index "/abs/path/to/archive"
python3 "<SKILL>/scripts/archive.py" validate "/abs/path/to/archive" --stage summaries
```

`index` 写 `00_index.md` 与 `all_summaries.md`，存在登记缺口时仍可供排查；结构错误或 `--strict` 检查不通过时返回非零退出码。索引按清单顺序排列，不依赖机器本地时区；需要按日期排序时先用明确时区排好清单。

再按 [三件套模板](../templates/knowledge_briefs.md) 生成三份指定文件：

```text
python3 "<SKILL>/scripts/archive.py" validate "/abs/path/to/archive" --stage insights
```

退出码 0 只代表该阶段结构检查通过，2 代表参数、输入或结构问题。

## 缺口与引用格式

- 登记为 `missing` 的来源不需要正文和总结，`partial` 的来源照常总结；两者都以 `GAP:` 行报告，结果为 `STRUCTURE PASS WITH GAPS`，末行给出“有正文来源数/总数”。缺口不阻塞其余材料，但交付必须写明覆盖比例。要求所有来源完整且请求范围已确认时加 `--strict`；它也会拒绝 `scope=partial/unknown`，但无法自动证明采集者的 complete 声明。
- 标为 `complete`/`partial` 却读不到正文，是失败而不是缺口：要么补原文，要么如实改成 `missing`，不能反向把 missing 改成 complete。
- 引用只认 `[source:ID]` 这一种写法，定位写在方括号外：`[source:dy_123] 02:15`、`[source:local_001] 第3段`。`[source:ID 第3段]`、`[source:a, b]` 会被判为格式错误；多个来源写成多个方括号。
- 原文必须是 UTF-8。脚本遇到 GBK 等编码会报出具体文件，转换后再运行。正文语义、来源归属与范围完整性需另外核对。`scope=partial/unknown` 即使结构通过也不能报成全量。

## 重跑与迁移

`bundle`、`index`、`split`、`shard` 会覆盖各自生成文件，不改 raw、sources.json、summaries 或 insights。请在单独归档中运行，生成文件不要用作手工笔记。原文或元数据变化会使总结指纹过期，需回查后更新，不要只刷新注释。

当来源范围缩小时，旧 bundle/summary 会被报告为 unexpected，不自动删除；确认无用后由用户或有相应授权的 Agent 归档。AppleDouble 的 `._*` 文件会被忽略。临时文件使用宿主安全临时目录，不依赖 `/tmp`。

旧版 `awemes_full.json` 需按 [抖音接入说明](douyin-pipeline.md) 转换；旧脚本命令与本版不直接兼容。三件套与总结是 Agent 的分析工作，Python 不会自动产生可靠结论。

## 从底库继续到能力交付

`--stage insights` 通过后，按 [能力交付](capability-delivery.md) 和已选模式生成实际能力包。脚本不会生成、安装或检查这些包，也不创建新对话。`request.md`、`delivery.md` 和包内 `trial.md` 由 Agent 按实际情况填写；用户选择能力输出时，底库结构检查通过不等于整项任务完成。
