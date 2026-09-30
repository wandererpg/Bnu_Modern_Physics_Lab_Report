# 其他 Agent 使用入口

将整个 `agent_report_bundle/` 复制到目标工作区，保留内部路径。这个文件夹可作为新工作区根目录；也可存放在已有工作区内，运行脚本时用 `--workspace` 指定目标工作区。模板仅提供排版和待填写骨架，实验内容由 Agent 根据真实材料撰写。

## 阅读与执行顺序

1. 先读 [agents.md](agents.md) 和 [AGENT.md](AGENT.md)，确认目录、真实性和历史保留要求。包内涉及原工作区的 Git 提交/推送约定，在其他工作区应结合该用户的授权与远程配置执行。
2. 写预习报告时读 [preview.md](preview.md)；写实验报告时读 [report.md](report.md)、讲义、原始记录和已有报告。确认实验标题、教师要求及缺失信息后再写作。
3. 从 [模板注册表](skills/Lab_Workflow_Generator/assets/report_templates/registry.json) 解析编号或别名。选择顺序：课程明确要求 → 用户指定 → 已有 `template_selection.json` → 新报告默认01。样式对照及限制见 [模板说明](skills/Lab_Workflow_Generator/assets/report_templates/README.md)。
4. 用下面的选择命令部署到 `<实验标题>/lab_report/`。成功标准是主文件、元数据、正文、文献和所选样式依赖齐全，且记录的编号正确。已有手改主文件应先备份、迁移并核对内容，保留原始数据及历史版本。
5. 填写 `report_template/metadata.tex`、`body.tex` 和 `references.bib`。缺测内容标记“待补充”；保留六个主体章节、双语摘要和关键词、基本信息、校徽及按需附录。按 `report.md` 核对数据处理依据、单位、有效数字、图表和引用。
6. 保存 LaTeX 源文件，使用支持中文的引擎编译成 PDF；运行源文件与PDF检查，人工查看渲染页面。交付时提供源文件、PDF及缺失项。只有内容核对和编译、版面检查都完成，才称正式报告完成。

## 直接调用

Python 3.10+ 可直接选择模板，无需安装本包为 Codex Skill。从包根目录执行：

```powershell
python skills/Lab_Workflow_Generator/scripts/select_report_template.py --list-templates
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage scaffold --template 06
# Agent根据真实材料填写内容后：
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage check
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage compile
```

已有工作区可从包根目录将 `--workspace .` 改为目标工作区的绝对路径。若只安装实验报告骨架，使用 `select_report_template.py --workspace <目标工作区> --experiment "实验标题" --template 06`；预习报告由 Agent 按 `preview.md` 单独撰写。

优先在宿主提供的 LaTeX 编辑器中打开、编译报告。使用上述本地编译命令时，需要 PATH 中有 XeLaTeX、BibTeX 及所需宏包；PDF自动测量需要 PyMuPDF。缺少引擎、宏包或字体时保留源码并报告具体原因；缺少PDF检查库时应明确自动检查未执行，继续人工版面检查。

01—05使用 Fandol 字体；06通过 ctex 自动选择中文字体，本机为宋体/黑体。在其他平台需检查中文字体与提取结果。03使用 `multicol` 混合布局，双栏内图表用 `[H]`，附录恢复单栏；长表或复杂通栏浮动体按模板说明处理。

## 包内文件与维护

- 根目录五份 Markdown 是源工作区规范的当前副本，保留最新 `preview.md`；[README.md](README.md) 提供原工作区介绍。
- `skills/Lab_Workflow_Generator/assets/report_templates/` 保存01—06入口、共用版式、内容骨架、注册表和正式说明。
- `assets/branding/bnu_logo.png`、`assets/thu_template/thuemp.cls` 及 `assets/scaffold_template/` 提供脚手架依赖；这些路径相对于 `skills/Lab_Workflow_Generator/`。
- [工具说明](skills/README.md) 列出选择、编译及内容/版面检查工具；工具负责确定性步骤，正文由 Agent 撰写。
- `manifest.json` 记录每个文件的源路径、大小和 SHA-256，可用于核对复制完整性。包中保留正式模板源码，设计样例、预览PDF和实验资料不随包分发。

源工作区更新规范或模板后，运行 `python skills/Lab_Workflow_Generator/scripts/export_agent_bundle.py` 重新同步。本包是可移植副本，导出工具由源工作区维护；若手工修改副本，先将需要保留的修改合并回来源，再导出。目标工作区后续新增的实验资料应保存于独立实验目录。
