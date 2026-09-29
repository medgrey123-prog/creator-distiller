# 本地数据约定与命令

辅助脚本只处理本地文件，不抓取网站、不转录音频、不调用模型、不上传资料。Python 3.9+ 标准库即可，无 pip 依赖。下列命令以 skill 目录为当前目录；按本机环境选择 `python`、`python3` 或 Windows 的 `py -3`。路径带空格或中文时加引号。

## 输入

归档放在发布仓库之外的用户工作目录，结构为：

```text
archive/
  sources.json
  raw/                 原文或转录（只读输入）
  bundles/             脚本生成的单条证据包
  summaries/           Agent 编写的逐条总结
  distilled/           Agent 编写的三件套
```

`sources.json` 示例：

```json
{
  "schema_version": 1,
  "scope": {
    "requested": "用户提供的一份本地文字材料",
    "status": "complete",
    "observed_at": "2026-09-30T00:00:00+08:00",
    "evidence": "逐一核对用户提供的文件清单；不代表该创作者全部作品"
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
python scripts/archive.py bundle "path/to/archive"
python scripts/archive.py split "path/to/archive" --groups 3
python scripts/archive.py shard "path/to/archive" --groups 3
```

`bundle` 生成证据包与输入指纹；缺原文仍生成标记但返回失败。`split` 先以来源清单检查每一条是否齐全、是否过期，然后写 `groups.json`，每组存相对 bundle 路径；单 Agent 也能依组顺序工作。`shard` 按音视频时长尽量均衡写 `shards.json`，未知时长按条数分摊；它只生成任务清单，不运行 ASR。

依据 [逐条模板](../templates/summarize_brief.md) 编写总结，复制 bundle 顶部的指纹注释。然后：

```text
python scripts/archive.py index "path/to/archive"
python scripts/archive.py validate "path/to/archive" --stage summaries
```

`index` 写 `00_index.md` 与 `all_summaries.md`，即使材料不完整也可供排查，但会返回非零退出码。索引按清单顺序排列，不依赖机器本地时区；需要按日期排序时先用明确时区排好清单。

再按 [三件套模板](../templates/distill_briefs.md) 生成三份指定文件：

```text
python scripts/archive.py validate "path/to/archive" --stage distilled
```

退出码 0 只代表该阶段结构检查通过，2 代表参数、输入或结构问题。正文语义、来源归属与范围完整性需另外核对。`scope=partial/unknown` 即使结构通过也不能报成全量。

## 重跑与迁移

`bundle`、`index`、`split`、`shard` 会覆盖各自生成文件，不改 raw、sources.json、summaries 或 distilled。请在单独归档中运行，生成文件不要用作手工笔记。原文或元数据变化会使总结指纹过期，需回查后更新，不要只刷新注释。

当来源范围缩小时，旧 bundle/summary 会被报告为 unexpected，不自动删除；确认无用后由用户或有相应授权的 Agent 归档。AppleDouble 的 `._*` 文件会被忽略。临时文件使用宿主安全临时目录，不依赖 `/tmp`。

旧版 `awemes_full.json` 需按 [抖音接入说明](douyin-pipeline.md) 转换；旧脚本命令不兼容 2.0。三件套与总结是 Agent 的分析工作，Python 不会自动产生可靠结论。
