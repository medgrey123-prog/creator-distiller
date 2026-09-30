# 示例成品包：causal-check-thinking（思考型）

这是共脑用仓库内 3 条**虚构**材料（mini-archive）生成的一个完整思考型能力包，用来展示“成品包长什么样”。内容只展示结构，不代表真实人物或研究结论。

- 入口文件在这里命名为 `SKILL.example.md`，避免 Agent 把示例误识别为一个已安装的技能。真实生成时，入口必须叫 `SKILL.md`。
- 生成真实包时，按同样的文件分工填入真实底库的内容；篇幅随材料增长，不要照抄这里的简短程度。
- `knowledge/evidence/` 中携带原文，所以把整个文件夹移动到别处也能核对依据。

```text
causal-check-thinking/
├── SKILL.example.md      入口：何时用、输入、流程、读哪些知识、输出、缺口处理
├── knowledge/
│   ├── index.md          问题 → 卡片的导航
│   ├── concepts.md       C 卡（概念与判断前提）
│   ├── methods.md        M 卡（判断框架）
│   ├── conflicts.md      来源冲突与未解决问题
│   ├── sources.md        来源 ID → 标题、类型、定位、正文状态
│   ├── provenance.md     底库版本、输入指纹、覆盖范围与缺口
│   └── evidence/         随包携带的原文
└── trial.md              试运行记录
```
