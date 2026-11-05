# 六种实验报告模板

制作新报告前，先展示六种样式并询问用户选择。用户已为本份报告明确选择或正在维护已有报告时沿用，不重复询问；没有选择不生成默认骨架。

| 编号 | 名称 | 主要差异 |
| --- | --- | --- |
| 01 | 清华课程双栏 | 居中题头、传统双栏；11pt、1.5 倍行距 |
| 02 | Physical Review 风格 | 紧凑双栏、栏间细线；10pt、1.3 倍行距 |
| 03 | Nature 风格 | 大标题、浅色摘要；引言单栏、原理起双栏、附录单栏 |
| 04 | Applied Physics Letters 风格 | 单栏、浅色题头、无首行缩进、段间留白 |
| 05 | Journal of Physics 风格 | 独立题头摘要页；12pt、较大字号及行距 |
| 06 | He-Ne 原报告单栏 | 黑白单栏、1.5 倍行距、题目页眉、就地图表 |

六种都是课程排版样式。01、02 双栏，03 混排，04—06 单栏；保留各自题头、字号、段落与行距。共同采用 A4、25mm 页边距、XeLaTeX、标准 ctexart、Fandol 与 Latin Modern、自动阿拉伯章节编号，避免旧自定义类和系统字体硬依赖。03、04、06 为 11pt、1.5 倍行距；05 为 12pt、1.5 倍行距。

## 调用和填写

```powershell
python skills/Lab_Workflow_Generator/scripts/select_report_template.py --list-templates
# 用户已选择 03 后：
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage scaffold --template 03
```

也可以在对话中直接说“用 03 Nature 风格制作这份报告”；尚未指定时 Agent 会先询问。CLI 新报告必须显式提供 01—06 之一或注册表中的名称/别名；不在终端里阻塞询问。`minimal` 只用于 [故障诊断](../minimal_latex/README.md)。

安装后的主文件为 `<实验标题>/lab_report/lab_report.tex`；基本信息、摘要、正文和文献在这一个文件中填写。校徽位于 `assets/bnu_logo.png`，缺失时允许草稿编译并提示补充。`template_selection.json` 记录选择与来源，用于内容保护，不代表内容已验收。

03 的双栏正文由 `multicols` 管理，栏内图表使用 `figure[H]`、`table[H]` 就地放置；通栏图表应置于双栏环境之外，再恢复双栏。不要在多栏环境里使用会被延后的普通浮动体。

六种模板都遵守 `report.md` 的实验内容要求：两行信息、100—200 字中文摘要、3—5 个关键词、引言两段、原理三个子标题、结果与分析讨论、总结、上角标文献引用、参考文献后的英文摘要及关键词。缺少数据时标记待补充，不虚构。

## 编译和检查

```powershell
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage check
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage compile
```

普通文档两遍 XeLaTeX，实际使用外部 `.bib` 才运行 BibTeX 并完成后续两遍 XeLaTeX。每轮辅助文件位于独立 `build/run-<唯一标识>/`；全部成功、日志检查通过且最终 PDF 非空后才更新报告目录 PDF，失败保留旧成品。

需要排查引擎、字体和章节编号时使用 `../minimal_latex/build.ps1 -Verify`，该诊断模板不是报告样式选择。

## 已有报告和来源

已有主文件、旧分片结构、记录和手工修改均保留；选择新样式不等于授权用空骨架覆盖旧稿。明确迁移前先保存原稿，核对正文、信息、数据与文献，随后编译并复核版面。

六种当前入口是重构后的自包含版本；旧 `common.tex`、`layout_v2.tex`、`layout_06_he_ne.tex`、`metadata.tex`、`body.tex` 与旧文档类保留供历史报告维护，新六模板不依赖这些旧分片。来源与课程适配边界见 [SOURCES.md](SOURCES.md)，旧 06 实现的设计记录见 [DESIGN_06.md](DESIGN_06.md)。
