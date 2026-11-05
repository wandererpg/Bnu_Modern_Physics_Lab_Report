# 统一最小实验报告模板

当前唯一注册模板为 `minimal`，源文件 `template_minimal.tex`。它将已验证的最小 LaTeX 基础与实验报告内容要求结合，不依赖六套旧版式、自定义文档类或 metadata/body 分片。

## 部署与填写

```powershell
python skills/Lab_Workflow_Generator/scripts/select_report_template.py --list-templates
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage scaffold --template minimal
```

省略 `--template` 时，新报告默认 minimal。也可直接运行选择脚本安装实验报告骨架；预习报告由 Agent 按 `preview.md` 完成。正文、信息、摘要和参考文献直接编辑 `<实验标题>/lab_report/lab_report.tex`；校徽位于 `assets/bnu_logo.png`，缺失时有待补充提示。生成的 `template_selection.json` 记录来源与主文件摘要，用于覆盖保护，不是报告内容验收记录。

## 内容与版式

以根目录 `report.md` 为准：A4单栏、11pt、25mm页边距、约1.5倍行距；两行基本信息、首页校徽、100—200字中文摘要、3—5个中文关键词、引言/原理/结果与分析讨论/实验总结/参考文献五个顶层章节。英文摘要和对应关键词紧接参考文献。附录只按需包含程序、推导等非实验数据材料，原始数据独立保存在本地。

模板固定 XeLaTeX，使用标准 ctexart、Fandol 和 Latin Modern 字体；标准章节命令产生 `1`、`1.1` 编号。编辑器提示不代替实际引擎设置。缺少发行版字体包时安装相应包，不猜测系统字体名。

## 编译与检查

```powershell
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage check
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage compile
```

两遍 XeLaTeX 解析编号和引用；只有实际使用外部文献库时才增加 BibTeX。真实文献可直接使用主文件的 thebibliography，引用保持上角标顺序编号；待补充文献不能编成虚构条目。编译使用新 `build/run-<唯一标识>/`，全部成功后更新报告目录 PDF，失败保留日志。

模板只保证骨架可编译，不保证报告内容完成；填完后按 `report.md` 检查数据、摘要、讨论、文献并查看最终 PDF。字体、编号或输出异常时，先运行[独立分项诊断](../minimal_latex/README.md)。

## 旧报告兼容

原六套样板不再注册为新报告入口；资产保留供既有报告维护，历史设计来源见 [SOURCES.md](SOURCES.md)。已有正文、元信息、数据、文献和手改主文件均保留。旧选择记录不自动迁移；显式迁移须先完成内容对照与副本保存，不以空骨架替换旧文件。

通用模板与说明可进入 Git。实验讲义、数据、报告、图片、脚本及编译成果仅本地保存。
