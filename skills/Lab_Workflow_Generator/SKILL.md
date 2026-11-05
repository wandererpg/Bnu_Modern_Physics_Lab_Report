---
name: Lab_Workflow_Generator
description: >-
  根据实验讲义和真实记录建立预习与实验报告工作区，使用统一最小 LaTeX 模板生成源文件、处理数据并编译 PDF；也用于维护报告或迁移旧模板。
---

# 实验报告工作流

当前入口为统一 `minimal` 模板。新报告不再按六套样板或期刊别名选版；历史资源只用于维护已有报告。具体内容以工作区 `preview.md`、`report.md` 为准；缺失时读取 `references/` 对应副本。任务权限、资料与 Git 范围遵循工作区 `agents.md`，不扩大授权。

## 模板与编辑入口

- 正式实验模板为 `assets/report_templates/template_minimal.tex`，安装后主文件为 `<实验标题>/lab_report/lab_report.tex`。基本信息、摘要、正文和参考文献直接在主文件填写，不要求 metadata/body 分片或自定义文档类。
- 基础为 XeLaTeX、`iftex`、标准 `ctexart[UTF8,fontset=fandol,scheme=plain]`、Fandol 和 Latin Modern；不依赖宋体、微软雅黑或 Times New Roman 等系统字体名称。
- 页面采用 A4 单栏、11pt、25mm 页边距和约 1.5 倍行距；标准 `\section`、`\subsection` 生成 `1`、`1.1`，不重定义章节命令，不手写章节数字。
- 保留两行基本信息、首页校徽、100—200 字中文摘要、3—5 个中文关键词、五个正文顶层章节与上角标顺序引用；英文摘要和对应关键词在参考文献后。校徽缺失标注待补充，正式交付前补齐。
- 骨架中的待补充提示不是实验内容。不能因编译成功称正式报告完成。

使用与兼容说明见 [模板说明](assets/report_templates/README.md)。只有需要查旧报告来源时才读历史来源与版式文档。

## 工作区与内容保护

每份讲义按内部标题建立 `<实验标题>/`，讲义位于 `<实验标题>/<实验标题>.pdf`，分别使用 `preview_report/` 与 `lab_report/`。两份报告均编写为 LaTeX 并生成 PDF，辅助文件集中在各自 `build/`。数据、图片、处理脚本和表格保存在实验目录，不进入通用模板仓库。

新报告选择记录使用 `minimal`；现有主文件、旧选择记录及手动编辑不触发自动换版。迁移前保留原稿并核对正文、信息、文献、数据与手动修改。不得以空骨架替换旧报告；`--force` 也不绕过覆盖保护。

## 按任务执行

1. 读取规范、讲义、原始记录、照片与已有报告，确认实验标题、真实操作和完成条件。扫描讲义不可读时使用可用 OCR；不能用模板常识代替讲义事实。
2. 新报告部署统一骨架；已有报告按实际源文件维护。讲义更新时记录变更，审查需要更新的正文，保留用户手改内容。
3. 按 `preview.md` 写预习报告，按 `report.md` 写实验报告。原始值、计算值、理论值和估计值明确区分，缺失内容写待补充。正文按“设定→结果→解释”组织，必要条件和定义集中说明一次，因果推测就近用“可能”。
4. 依据真实记录生成可复现的数据处理、拟合、绘图脚本及必要正文表。保留异常值及处理依据；原始记录与完整计算表单独保存，不生成实验数据附录。
5. 运行与改动匹配的检查与编译，核对最终 PDF。说明路径、实测结果、未完成项和验证范围。

## 命令与阶段

从工作区根目录执行；`--workspace` 也可传绝对路径：

```powershell
python skills/Lab_Workflow_Generator/scripts/select_report_template.py --list-templates
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage scaffold --template minimal
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage status
# 在完成真实正文后：
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage check
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage compile
```

其他阶段为 `ocr`、`plots`、`tables`；`all` 按脚本执行整个工程流程，但不会代替 AI 阅读材料和完成报告内容。按需使用 `init_workspace.py` 初始化目录；具体参数以 `--help` 为准。正文所需的三线表由 `make_data_tables.py` 从数据生成，引用 `tables/` 片段；图题、表题和正文引用统一中文。绘图字体与 LaTeX 字体分别检查。

## 编译与故障定位

正常编译使用 XeLaTeX 两遍；仅实际使用外部 `.bib` 时增加 BibTeX，再用 XeLaTeX 两遍。最小模板可用真实 `thebibliography` 条目，无外部文献库时不要求 BibTeX。按课程要求著录参考文献，正文必须实际引用；没有文献时标记待补充，不塞虚构占位文献。

编译脚本在报告目录工作，新建 `build/run-<唯一标识>/`，逐次检查退出码和日志，确认非空 PDF 后再更新成品。失败保留源码和日志，说明本轮失败，不交付旧 PDF 冒充新结果。不得自动退回 pdfLaTeX。

如不能生成 PDF，先运行独立诊断：

```powershell
& .\skills\Lab_Workflow_Generator\assets\minimal_latex\build.ps1 -Verify
```

依次检查英文引擎与 PDF 输出、中文文档类与字体、章节及交叉引用。详见 [诊断说明](assets/minimal_latex/README.md)。字体找不到时检查发行版包；编号异常时检查星号章节、编号深度、旧类与章节重定义；输出异常时检查当前目录、主文件、可写输出目录、退出码与最终 PDF 路径。

## 验收与通用包

- 检查摘要、章节、实际数据、单位、有效数字、不确定度、文献和附录范围；正文要求见 `report.md`，预习内容见 `preview.md`。
- 编译后检查引用、缺字、字体替换、溢出及最终 PDF 页面，必要时使用 `check_report_tex.py`、`check_pdf_geometry.py`、`check_float_distance.py`、`check_inline_distance.py`。判断与页宽/栏宽相关的告警时结合实际模板，不能把历史双栏参数机械套在新单栏上。
- 输出源文件、PDF、可复现脚本及必要数据说明；记录讲义来源/变更、执行动作、编译链与缺失项。正式交付须内容与版面都完成，资料不足只交付草稿。
- 变更通用规范后同步 `references/`，运行 `scripts/export_agent_bundle.py` 并核对 `agent_report_bundle/manifest.json`。通用包不放实验材料、报告成品与缓存。

以下版本记录用于解释旧工作区，不覆盖上述当前规则。

## 历史版本记录（仅供追溯）

以下版本记录保存当时的实现和规则。生成新报告时，以本 Skill 前面的现行流程、工作区根目录 `report.md` 和当前教师要求为准；与现行规范冲突的历史内容不再适用。

用户反馈"报告算得出结果，却无法展示原始数据"，复盘出四条硬规则（已写入 `references/report.md` 与内容核心 `advanced_lab_report_gen`）：

1. **原始与派生分表**：`原始数据` 表只放原始读数（如数字电流表的读数矩阵）；均值、标准差、四方程解、拟合参数等派生量各成表，并在表题注明来历。**同一列名不得在不同批次数据里代表不同物理量**——旧实现把两次课熔进一张 10 列表，`重复次数` 列在第一次课是"4 次重复"、第二次课填的却是"4 个共振判读状态"，`标准差` 列同理。
2. **矩阵形态**：同一条件的多次重复横向排成"第 1 次/第 2 次/…"，多个状态横向排成"状态 1/状态 2/…"，而不是每个读数摊成一行（旧表 16 个读数排成 16 行 + 8 行空行）。
3. **测量条件入表**：方向符号约定、射频频率、重复次数、判读方式、缺测标注必须出现在表内或表题里，否则原始读数无法被理解或复现（旧表第二次课的 16 个读数从未写出对应的射频频率）。
4. **按列统一小数位**：电流一律 3 位、换算系数一律 4 位；长小数（如 19 位）会把列撑爆并连带把表挤出纸面。

配套工具改动：`make_data_tables.py` 新增 **陈旧生成物清理**（CSV 改名/删除后自动删除对应的 `tables/*.tex`，只删带自动生成标记的文件，手写表不动）与 **`--` 连字保护**（TeX 会把 ASCII `--` 连字成 `–`，使数据里的方向组合 `--` 显示成单个短横线与 `-` 无法区分；现插入空组阻断）。

## 更新日志（历史记录，不作为当前入口）

### v1.27（2026-09-18）

**新增硬规则：行文不得出现括号**（用户要求：括号式旁注不符合人类行文逻辑）。

- **`check_report_tex.py` 新增行文括号检查**：扫描 `.tex`（含 `\input` 的表片段）中被掩码后剩余的
  `（…）`/`(…)`，告警给出行号与片段。掩码范围＝LaTeX 注释、`lstlisting`/`verbatim` 代码、
  数学环境与行内 `$…$`（公式分组括号如 `(B_h^{+−}-B_h^{−+})/2` 属数学语法）、
  `\eqref`（渲染成编号括号）、`\texttt{}` 与 `\verb||`（文件名/标识符）。
  掩码按字符替换为空格并**保留换行**，否则告警行号会整体前移（本次踩到并修掉）。
- **改写口径**（写进 `references/report.md` §写作风格 与内容核心 §2.5）：旁注并入句子；
  图表引用写“见表 3”；公式引用写“第 2 式”；枚举写“第一，…；第二，…”；小节标题写“一、二、”；
  单位提示写“单位为 m”或表头“…… / A”；不确定度写“标准不确定度为 …”而不是“(1.2345±0.0012) G”；
  **表题与表内文字同样适用**（表题在 `table_captions.json` / 数据准备脚本里改）。
- **数据脚本的两处配合**（实验工程侧，非通用脚本）：`prepare_real_data.py` 写出的表题映射必须
  覆盖 `data/` 下**全部** CSV，否则重跑会覆盖手工补的表题；`generate_plots.py` 只应**补缺失**表题、
  不得 `update` 覆盖已有条目——否则脚本内置的旧表题会把已改好的文本改回去（本次实测踩到）。
- 实测：光泵磁共振实验报告（12 页）与预习报告改完后，行文括号 0 处，
  `check` 两文件均 0 error / 0 warning，`pdf-geo` FATAL 0/WARN 0，`float-dist` OK，`inline` OK。

### v1.26（2026-09-18）

**打包分享前的自查修复**：随包附带可跑 demo（`examples/demo-单摆法测重力加速度`）后，
用它在"干净环境"里端到端跑通，暴露出 1 处模板 bug + 3 处判据缺陷，全部修掉。

- **模板 bug（`assets/scaffold_template/report_frontmatter_thu.tex`）**：数据说明框原先写成
  `\newcommand{\databox}[1]{...}` 并放在 `\twocolumn[...]` 的**可选参数内部**——`[1]` 里的 `]`
  会提前结束该可选参数，编译直接报 `Argument of \@newcommand has an extra }`。
  改为按真实报告的可行写法：直接用 `\fcolorbox{black!35}{gray!8}{\parbox{\textwidth}{...}}`
  并保留 `\vspace{4.2em}`（抵消 `empAbstract` 自带的 `\vspace{-3em}`）。模板注释里写明了这个坑。
- **`check_pdf_geometry.py`：分式碎片被误报成"两行文字重叠"**。`\frac` 的分子/分母会被 fitz
  拆成两个"行"，它们纵向叠得很深（实测 dy=10pt）而横向只交 9.8–16.8pt，原判据
  （横向 ≥ 0.5×较窄行宽）挡不住，于是**任何含分式的报告都会被误报**。
  新增横向下限 `OVERLAP_DX = 20pt`：真实碰撞（如数据说明框压住摘要首行）横向重叠都在几十 pt 以上。
- **`check_report_tex.py` 对 thuemp 模板的三处误报/漏报**：
  - 「摘要/关键词」原先要求 `.tex` 里出现这两个汉字，而 thuemp 的版面文字由 `empAbstract`
    环境与 `\Keyword` 宏生成 → 改为按宏名一并识别；
  - 「参考文献」原先只查章节标题与前 4000 字符，而 thuemp 用 `\bibliography` 输出（标题走
    `\refname`）且排在正文之后 → 改为同时识别 `\bibliography{}`/`thebibliography`/`\refname`；
  - 题注长度判据用 `[^}]*` 取参数，题注含 `$T^{2}$`、`\textbf{}` 时被第一个 `}` 截断而误判"题注过短"
    → 改用新增的 `brace_arg()` 做花括号配对解析。
- **新增 `examples/demo-单摆法测重力加速度`**：完整的最小可跑工程（讲义 PDF + `data/` + 绘图脚本 +
  报告），一条命令产出 3 页 PDF；四个 checker 全绿，可作为"装完即可验证"的冒烟测试。
  真实项目（11 页）在 v1.26 下复核仍为 `check` 0/0、`pdf-geo` FATAL 0/WARN 0、`float-dist` OK、`inline` OK。

### v1.25（2026-09-18）

**两处"度量口径"缺陷修正**（真实报告里 3 处"图表离引用句太远"的告警，查证后全是判据的锅，不是版式的锅）。

- **`check_inline_distance.py` 改为量"内容上沿"**：`figure[H]` 的题注在图**下方**，原先量"引用行→题注"
  会把图高（约 140pt）算成间距，把"紧贴"误报成"相距 177pt"。现在取题注上沿与图片/绘图 bbox 上沿中
  更靠上者。注意 matplotlib 出的 PDF 是 **Form XObject 矢量**嵌入，`get_image_info()` 取不到，
  必须同时看 `get_drawings()`；表格题注在上、框线在题注下方，被 y 区间条件排除，口径不变。
- **编号正则加护栏**：正文里的"仪表 $0.1\ \mathrm{A}$"断行后行首会出现"表 0.1 A …"，被
  `(表|图)\s*(\d+)` 当成"表 0"的题注（`check_float_distance.py` 因此报出
  "表0 题注 p5 首次引用 p9 相距 -4 页"的幽灵条目）。两脚本统一改为
  `(?<!仪)(表|图)\s*(\d+)(?![\d.])`。
- **教训**：浮动体的"间距"必须量**内容上沿**；判据实现本身要先用真实 PDF 验证一次，
  否则会拿一个假的 177pt 去改本来是 22pt 的版式（本报告 12 页 → 11 页，10 个图表全部 22–27pt）。

### v1.24（2026-09-17）

**版式定稿：双栏 + 半栏宽“就地图表”**（用户要求：保持双栏；提到“图1”后图1 立刻紧贴该句）。

- **`make_data_tables.py` 新增 `--column`**：`table[H]` + `\scriptsize` + `tabcolsep=3pt` + `tabular*{\columnwidth}`，
  半栏紧凑表；p 列宽度基准改为 `\columnwidth`，可用宽度按 `\scriptsize` 折算（21em@10.5pt ≈ 29.5em@7.5pt）。
  runner 在非单栏文档下自动传 `--column`。
- **新增 `check_inline_distance.py`**：量“引用行 → 该图/表题注”的**同栏垂直距离**（用户核心诉求的量化口径），
  runner 的 compile 阶段自动运行。
- **规则（`references/report.md`）**：浮动体声明必须紧跟首次 `\ref` 所在句子的句末（否则段跨栏时会落到邻栏）；
  图表按半栏最终尺寸出图（figsize 宽 = `\columnwidth`，字号 8–8.5pt）；
  表压到 4–6 列、表头缩写、说明入表题；并记录 6 类失败尝试及其实测后果。
- 实测验收（光泵磁共振报告）：11 页；表1/表2/表3/表5 距引用句 **25–55pt**；`check` 0 error 0 warning；
  `[pdf-geo]` FATAL 0 / WARN 0；`[float-dist]` 全部 ≤1 页；Overfull 仅 1 处 6.8pt。

### v1.23（2026-09-17）

**版式定稿：正文单栏 + 表格统一宽度。** 起因：用户指出"表大小不一""大片空白""一页挤四五张图表""正文与表不在同一位置"。

- **依据**：本课程同学报告样本（6 份抽检）中 4 份为单栏；双栏下 `table*` 只能排页顶、宽表必然排队。
- **实现**：正文 `\onecolumn`；表格 `table[htbp]` + `tabular*{\textwidth}{@{\extracolsep{\fill}}…}`（`make_data_tables.py --single`，runner 检测 `\onecolumn` 时自动启用）。实测：14 页、所有表横线跨度统一 482pt、表/图与首次引用相距 1–2 页、无大片空白、无堆积。
- **负面结论**（已写入 `references/report.md`，勿重蹈）：`\FloatBarrier`+`flafter`+`dblfloatfix` → 16 页 4 处大空白；浮动体交错排布 → 末页孤行；双栏 `strip` 就地表 → 放不下即整页留洞（156pt）；数据图就地 → 两处 208pt 空白；单栏 `table[H]` 就地 → 4 处留洞（最大 494pt），改 `[htbp]` 即消失。
- 工具：`make_data_tables.py` 新增 `--single`；`run_lab_workflow.py` 新增 `has_onecolumn()` 自动判定；修正 `--strip-csv` 赋值位置错误（曾导致工具崩溃、表文件不更新）。

### v1.22（2026-09-17）

用户要求「表出现在正文提及它的地方」后的一轮版式实验与定稿方案：

- **正文表改“就地通栏表”**：`make_data_tables.py` 新增 **`--strip` / `--strip-csv`**，生成 `cuted` 的 `strip` + `table[H]`（全宽、不浮动）。实测效果：4 张正文表的**题注页 = 首次引用页**，表格横线跨度 481.9pt 恰等于版心。runner 检测到文档加载 `cuted` 时，**只对正文用到的表**（`仪器参数与换算 instrument-params.csv`）传 `--strip-csv`；完整原始数据表仅在本地留存，不放入报告附录。
- **`thuemp` 无 `\captionof`**（它用 `ccaption`，与 `caption` 宏包冲突），因此就地表必须走 `table[H] + \caption`，已在验证文档中确认编号与 `\ref` 正常。
- **实测负面结论（勿重蹈）**：① `\FloatBarrier` + `flafter` + `dblfloatfix` → 页数 13→16、4 处大空白（最大 438pt）；② 浮动体“交错”到引用段之后 → 末页只剩一行（空白 723pt）；③ 4 张数据图改成 `strip + figure[H]` 就地图 → 14 页、两处约 208pt 空白。三者均已回退，原因写入 `references/report.md`。
- **`check_report_tex.py` 认识 strip**：strip 区间内的表按通栏宽度判断（原先按单栏 21em 预算 → 误报 8 条“自然宽度超版心”）；strip 内的 `l/r` 表不再做文本估算（真实宽度由 PDF 侧守卫实测）。

### v1.21（2026-09-17）

由用户反馈「正文和它提到的表格相距太远」「仍有少量文本重叠」触发的版式修复（承接 v1.20）：

- **新增 `scripts/check_float_distance.py`**：量成品 PDF，报告每个表/图与其**首次正文引用**相隔多少页（行首且较长者判为题注，行中者判为引用；附录内的浮动体自动豁免）。基线实测：13 页报告里 15 个通栏浮动体，表 5 相隔 3 页、图 4 相隔 3 页——**通栏浮动体每页最多排一两个，数量一多必然排队**。runner 的 `compile` 阶段自动运行它。
- **`make_data_tables.py` 新增 `--place`（默认 `!t`）**：浮动体位置参数由硬编码 `htbp` 改为页顶优先。
- **`check_pdf_geometry.py` 判据修正（重要）**：① 新增**栏溢出**判定——左栏内容越过栏界**且真的压到右栏文字上**才算（通栏题注/页眉也越过栏界但不与右栏文字重叠，故不误报）；实测抓到一条宽 327pt 的显示公式捅进右栏 88pt、压住正文 8.4pt。② "两行相撞"改为**部分纵向重叠**判据（dy ≥ 5.5pt 且 < 行高的 85%）：fitz 把同一视觉行按字体拆成的碎片会纵向几乎完全重合、公式分子/分母碎片 dy 仅约 3pt，两类均不再误报。③ 版心估计改为"逐页取众数、左界取最小、右界取最大"。④ 浅色细线（matplotlib 网格线）不计入"横线穿字"。
- **规则层**：`references/report.md` 新增「浮动体位置」规范（表/图与引用 ≤1 页；原始数据表集中放附录；每节末尾 `\FloatBarrier`；导言区 `flafter` + `dblfloatfix`；位置参数 `[!t]`）；内容核心三副本新增结构口径——**数据处理与结果获得归入「三、实验」，「四、结果与分析讨论」只做分析、不再陈列数据表**。

### v1.20（2026-09-17）

由用户反馈「报告里的图、表完全看不懂」触发的**版式根因修复**。实测发现：那张 10 列汇总表的横线右端量到 **x1=1025.6pt，而 A4 纸宽只有 595.3pt**——约 430pt（15cm）内容被排到纸外、读者完全看不到；同页矢量图被缩小后**图内文字只剩 6.0–7.9pt**（正文 10.5pt）；首页「数据说明」灰框下边框 y=257.9 从摘要首行**74 个字形**中穿过。三种毛病编译全部 exit=0——LaTeX 对「表格比版心宽」不报错，只在日志里留一条 Overfull hbox。由此新增/修正：

- **`make_data_tables.py` 列宽自适应（`--fit`，默认开）**：自然宽度超版心时改发 `p{\dimexpr f\textwidth-8pt\relax}`；每列减去的 `2\tabcolsep` 与列间距相消，故总宽恰为 `(Σf)·\textwidth`，与模板 `\textwidth` 无关。宽度分配用「先保下限、再按余量分摊」；**列宽下限 3em**（首版曾把「分析项目」压成 13pt 宽、一字一行，表高 2362pt 被顶出纸面——已修）。放不下时报 `FAIL` 并给出预计超出百分比。`--no-fit` 可退回旧的 `l/r` 自然宽度。
- **`make_data_tables.py --array`**：数值列 `>{\centering\arraybackslash}p{}`、文本列 `>{\raggedright\arraybackslash}p{}`；runner 检测文档是否加载 `array` 后自动开启（thuemp 经 siunitx 间接加载），未加载时退化为普通 `p` 列。
- **未四舍五入告警**：小数位 >7 位即提示取 3–5 位有效数字。实测 19 位小数会把该列撑到 10em，仅「四舍五入」一项就能把 10 列表从 44em 压到 32em、由溢出转为放得下。
- **`check_report_tex.py` 表格几何守卫**：列数 >7、自然宽度估算超版心（会排到纸外而编译不报错）、表中 ≥8 位长小数。列宽估算与 `make_data_tables.py` 共用同一套 em 口径；表体测量从 `\begin{tabular}` 之后开始（此前把环境前缀并入第一列，49em 被算成 99em）。
- **新增 `check_pdf_geometry.py`（编译后量成品 PDF）**：`FATAL` 越出纸面（区分上/下/左/右哪条边）、`WARN` 越出版心、通栏长行重叠（首页灰框撞摘要，2105pt²）、**横线从字形中穿过**（用 rawdict 字形框判定，要求线在字形内 ≥1.5pt，并区分「图内图例压线条」与「版面间距不足」）、图内文字过小（<8pt 小字行成簇且带图形笔画）、位图 <150dpi。版心边界由文字行众数自动估计，无需知道模板 geometry。
- **runner**：新增 `pdf_geometry()`（`compile` 阶段编译后自动执行，FATAL 计入退出码）；`log_summary()` 汇总日志里的 `Overfull \hbox` 与 **`Float too large for page`**（浮动体放不进一页＝内容必被挤出纸外）；`data_tables()` 自动探测 `array`。
- **脚手架 `report_frontmatter_thu.tex` 增加 `\usepackage{array}`**（供自适应列宽使用）。

### v1.19（2026-09-17）

- **图表可读性（由首次真实运行的反馈发现）**：真实报告里 4 张插图只给了 0.62–0.78 倍栏宽，而绘图脚本按 6.0–6.6 英寸出图 → PDF 实测插图仅 7.8 cm 宽，图内 8–10 pt 的字被压成 4–5 pt；表格则被 `format_tables.py` 统一套上 `resizebox{\textwidth}{!}`（最宽的表 10 列），同样被压小。据此：
  - `make_data_tables.py` 新增 **`--header-map`**（表头改为“物理量 / 单位”，去掉 ASCII 下划线）与 **`--star`**（输出 `table*` 通栏、**不再 resizebox**）；runner 的 `tables` 阶段自动传 `table*` 与 `lab_report/table_headers.json`，并对“列数>7”“行数>20”给出告警。
  - `check_report_tex.py` 新增**可读性检查**：`\resizebox/\scalebox` 告警、插图宽度 <0.85 倍栏宽告警（记录照片除外）、题注 <10 字告警、表格 >20 行告警。
  - `references/report.md` 与内容核心 §2.5 增加“**按最终尺寸出图**、坐标轴写‘物理量 / 单位’、多序列必配图例、**图题/表题必须自足**、表头写‘物理量 / 单位’、列数 ≤7、行数 >20 拆分、禁止 resizebox 缩放表格”等要求。
  - `report_frontmatter_thu.tex` 新增 **`\databox{}` 宏**：thuemp 的 `empAbstract` 自带 `\vspace{-3em}`，此前直接放裸 `\fcolorbox` 导致灰框底线与摘要首行**重叠**（PDF 实测重叠 209 pt²）；现在宏内补偿 4.2em 并留出间距。

### v1.18（2026-09-17）

- **守卫新增**：即使**找不到源讲义**，也仍然执行 .tex 过期检查（此前会整体提前返回，导致正文哈希校验被连带跳过——fail-open）。
- 守卫读哈希前先规范化 Markdown 装饰（去掉反引号与星号），因此 `lab_report.tex` SHA-256：`hash`、**hash** 等写法都能识别；正向测试已确认"改过正文但未更新日志"会被拒绝编译（exit 1）。

- **修正哈希守卫 fail-open（由首次真实运行发现）**：`generation_log.md` 把哈希写在反引号里（`` `3ab6b4…` ``），而守卫正则不容忍反引号/空格 → **记录哈希根本读不到、正文过期检查被静默跳过**。现改为 `SHA-256：\s*`?([0-9a-fA-F]{64})`，对讲义/实验报告/预习报告三处一致。
- **修正 `check_report_tex.py` 的摘要识别**：thuemp 模板的摘要在 `empAbstract` 环境里、`.tex` 中并无“摘要”二字，旧实现因此误报“未识别到摘要段落”。现优先解析 `empAbstract`，并按「CJK + 数字/字母」计数（排除 LaTeX 命令与行内公式）。

### v1.17（2026-09-16）

- **修正 `make_data_tables.py` 的 slug 冲突（由首次真实运行发现）**：文件名若几乎全为中文，slug 会被剥成空并回退为 `table`，导致**多个 CSV 生成同一个 `table.tex` 互相覆盖、生成表片段静默丢失**。现改为：ASCII 部分为空时用 `tNN`（按排序序号），并对任何重名自动加后缀；已有 ASCII slug 保持不变（旧报告的 `\input` 路径不受影响）。
- **新增 `--caption-map`**：以 JSON 指定每个 CSV 的表题，生成器据此写 `\caption{}`（缺省仍用文件名）；runner 在 `tables` 阶段自动传入 `lab_report/table_captions.json`（存在时）。
- 数据脚本规范补充：建议数据文件命名为「中文名 英文名.csv」以便 slug 可读。

### v1.16（2026-09-16）

- 依据「干涉滤光片的镀制」回归发现的一处质量问题补规则：表格**不得重复列出同一份数据**（该次生成中 `计算结果汇总 processed_results.csv` 与 `滤光片参数 filter metrics.csv` 内容完全相同，附录 A 因而把同一张表列了两遍）。
  - `references/report.md` 附录条目新增"附录表与数据文件一一对应、不得重复"要求；
  - `SKILL.md` §6 数据脚本规范新增第 7 条：输出 CSV 应各有独立内容，不要生成内容重复的汇总文件；并建议按"中文名 英文名.csv"命名、本地数据说明记录真实文件名。

### v1.15（2026-09-10）

- **新增 OCR 流程**（面向扫描件讲义）：`scripts/ocr_lecture.py` 逐页判断——文本层 ≥50 字符直接用，否则渲染该页 OCR（rapidocr-onnxruntime + PyMuPDF），输出 `<<<PAGE n>>>` 标记文本；`--experiment` 模式默认写入 `<实验>/lab_report/lecture_ocr.txt`。
- runner 新增 `ocr` 阶段并纳入 `all`：讲义是扫描件且尚无 `lecture_ocr.txt` 时自动执行，否则跳过。
- §5 步骤1 增补"扫描件先 OCR 再绑定事实"。
- 验证：对 `lab_work/干涉滤光片的镀制`（8 页纯扫描、文本层仅 8 字符）OCR → **8/8 页、7239 字符**，正确读出「HLHLHL2HLHLHLH 膜系」「硫化锌（H）/冰晶石（L）」「机械泵/分子泵」「分光光度计」等关键事实。

### v1.14（2026-09-10）

- **修正 bibtex 运行目录**（由清华模板原生生成回归发现）：此前 bibtex 在 `build/` 内运行，无法解析 `\bibliography{./refs}`（带 `./` 的路径不搜索 `BIBINPUTS`），导致必须手工把 `refs.bib` 复制进 `build/`。现改为**在 `.tex` 所在目录运行 `bibtex build/<base>`**：`./refs` 正常解析，`.bbl` 仍写入 `build/`。
- 前置区模板 `report_frontmatter_thu.tex`：`\bibliography{./refs}` → `\bibliography{refs}`（更稳健）。
- runner 新增 `warn_log_version()`：若 `generation_log.md` 的「Skill版本」与本 Skill 不一致，打印告警（本次回归中日志误写 v1.10 而实际 v1.13）。

### v1.13（2026-09-10）

- **新增精简工作区模式**：工作区根目录只保留实验文件夹（`<实验标题>/{讲义.pdf, data/, preview_report/, lab_report/}`），规范/模板由 Skill 自带并在生成时带入。
- 新增随 Skill 提供的 `scripts/init_workspace.py`：从讲义目录（或实验名列表）批量建立精简工作区；自动以讲义首页标题命名，**扫描件无文本层**时退回文件名并警告，支持 `--title-map` 校正。
- runner 支持**在实验文件夹内直接运行**（`--experiment` 可省略，取文件夹名）；新增**实验级 `data/`**：`<实验>/data/*` 会自动镜像到 `lab_report/data/`，下游脚本与表格生成无需改动。
- `references/preview.md` 新增「交付形态：纯内容」：预习报告只要求纯内容（便于手抄到记录本），不要封面/姓名学号栏/校徽/页眉页脚/英文摘要。
- 验证：以 `refer/` 的 9 份讲义建立 `lab_work`（仅实验文件夹，无根级杂物）；在 `塞曼效应/` 内省略 `--experiment` 运行 `--stage status` 正常解析；把 CSV 丢进 `<实验>/data/` 后 `--stage tables` 成功镜像并生成 `tables/*.tex`。

### v1.12（2026-09-10）

- **默认排版模板切换为「清华近代物理实验报告模板」（thuemp.cls，非官方，by Mingyu Li）**，物理学报模板降为备选：
  - 新增资产 `assets/thu_template/`（`thuemp.cls`、`README.md`、`TempExample.tex`、`TempExample.bib`、`image/example.jpg`）与前置区模板 `assets/scaffold_template/report_frontmatter_thu.tex`；
  - 脚手架把 `thuemp.cls` 与 `report_frontmatter_thu.tex` 复制到 `<实验标题>/lab_report/`；
  - 该模板是 `ctexart` 派生的 **twocolumn/twoside/A4** 类，自带「北京师范大学普通物理实验」页眉、`empAbstract`/`\Keyword`、`\emptitle/\empauthor`、`\empfirstfoot`（实验时间/报告时间/学号/E-mail）与 **gbt7714（BibTeX 国标）** 参考文献；
  - 用 `\ctexset{section={name={,、},number=\chinese{section}}}` 保持老师要求的**一级标题中文编号「一、二、三」**；
  - 图题改为**单语中文**「图N：描述」＋ `图~\ref{}` 引用（该类基于 `ccaption`，**不提供 `\bicaption`**）；`\bnulogo`/校徽 overlay 仅用于物理学报备选模式。
- runner：`bibtex_env` 的模板目录匹配由 `物理学报模板*` 放宽为 `*模板*`（兼容 THU 模式）。
- 验证：官方 `TempExample.tex` 三趟 xelatex + bibtex **exit 0**；塞曼实验报告机械迁移到 THU 模板后 **exit 0、6 页 A4、日志无错误**，首面呈现类的页眉、`【摘 要】/【关键词】`、英文标题/摘要，正文自「一、 引言」双栏排版。
- 修正 `needs_bibtex()` 判据（由本轮回归发现）：含**手写 `thebibliography`** 的文档即使同目录存在 `.bib` 也不再触发 BibTeX（否则会因缺少 `\bibdata` 而编译失败）；THU 模式（`\bibliography{./refs}` + gbt7714）仍正确触发。回归验证：手写文献报告 **exit 0/4 趟 xelatex/0 bibtex**；`needs_bibtex` 对两版分别判定 False/True。

### v1.11（2026-09-10）

- 依据**塞曼效应内容级回归**（Codex 生成 7 页实验报告 + 3 页预习报告）补齐规则与工具：
  - `check_report_tex.py`：新增**公式引用顺序**检查——`\eqref{...}` 若先于其 `\label` 出现即告警（图表前向引用属正常写法，不报）；实验报告另增「摘要/关键词」存在性检查（缺失报错）。
  - `assets/scaffold_template/report_preamble.tex`：新增样式宏 `\abstractheading`（居中「摘 要」）与 `\keywordsline{...}`，保证两份报告标题样式一致。
  - 内容核心（advanced_lab_report_gen v3.1）§2.5 增补**引用顺序**条款：编号公式必须先给出后被引用；图表可前向引用但首次引用应紧邻图表。

### v1.10（2026-09-10）

- **修正 `check_report_tex.py` 的 `\input/\include` 盲区**（由端到端回归发现）：校验器此前只读主 `.tex`，导致由 `make_data_tables.py` 生成、以 `\input{tables/...}` 引入的表其 `\label` 被误判为"悬空引用"。现已递归内联 `\input/\include`（深度上限 8、防循环）后再做 label/ref/章节/图表检查。
- 端到端回归（脚手架 → 表生成 → 源校验 → BibTeX 三趟编译）**exit 0**；注入"删掉图题注"缺陷时 `check` 正确 **exit 1**。

### v1.9（2026-09-10）

- 新增随 Skill 提供的报告源校验器 `scripts/check_report_tex.py`（P2-5）：把 `report.md` 的文字规则变成可执行检查——**每图每表必须有题注**、**`\ref/\eqref` 必须可解析**、**label 必须被引用**、**必需章节齐全**、摘要长度提示；支持 `--dir/--kind/--strict`。
- runner 新增 **`check` 阶段**，并在 `all` 中于编译前执行；退出码按结果传播。
- 验证：好文档 exit 0（仅 1 条摘要长度警告）；构造的坏文档报 3 错（图无题注、悬空引用、缺章节）2 警并 exit 1；runner `--stage check` 正确返回 1。

### v1.8（2026-09-10）

- **预习规范去实验专属内容（P2-1）**：`references/preview.md` 移除混入的 He-Ne 专属术语（纵模/横模/双折射/扫描干涉仪/模竞争），改为“本实验涉及的核心术语须结合实验装置与可观察现象解释”的通用表述。
- **新增三层次原理写法指引（P2-4）**：提炼自上游预习样例的“**常识比喻 → 公式 → 判据**”节奏，给出可操作步骤与刻意保持通用的写法示例（避免再次把某实验内容写进通用规范）。
- 保留原“讲义事实绑定要求”，其光泵示例继续**显式标注**为示例。

### v1.7（2026-09-10）

- **数据溯源声明双落点**：新增随 Skill 提供的 `assets/scaffold_template/data_README.md`，脚手架会写入 `<实验标题>/lab_report/data/README.md`（含来源类型、文件清单、提交前替换清单）。
- 内容核心（advanced_lab_report_gen）步骤0.2 增补**双落点强制**：正文封面信息栏下方灰框（`\fcolorbox` + `\parbox` 配方）＋ `data/README.md`，二者须一致；生成日志记录两处是否写入。
- `references/report.md` 增补相应条目。
- 验证：脚手架随附 `data/README.md`；`\fcolorbox` 灰框配方随测试报告 xelatex 编译通过。

### v1.6（2026-09-10）

- **排版范式固化**：新增随 Skill 提供的、经编译验证的导言区片段 `assets/scaffold_template/report_preamble.tex`（A4/2cm/1.5 倍行距、`\ctexset` 一级标题中文编号「一、」、`siunitx` 不确定度 `\SI{438.5(17)}{\mega\hertz}`、中文图题和中文正文引用 `\bicaption`、`\blankfield` 封面留空横线、`\bnulogo` 校徽 overlay 7.0cm/左移 2cm/仅首页）。
- 脚手架新增：把 `bnu_logo.png` 与 `report_preamble.tex` 复制到 `<实验标题>/lab_report/`（`assets/bnu_logo.png`），并创建 `lab_report/assets/`。
- `references/report.md` 新增「排版实现片段」小节，指向该片段与用法。
- 验证：用该片段写成的测试报告（校徽/封面/摘要/双语子图+中文图题和中文正文引用/三线表/siunitx）xelatex **编译 exit 0**、产出 PDF、日志**零错误**。

### v1.5（2026-09-10）

- 历史新增 **程序化数据表**（当前按 `report.md` 仅生成本地表片段、正文按需选用）：Skill 自带 `scripts/make_data_tables.py`，把 `lab_report/data/*.csv` 渲染为 `lab_report/tables/*.tex`（booktabs 三线表、自动转义、数值列右对齐、超长截断加表注、`--combined` 汇总）。报告以 `\input{tables/<name>}` 引入，**改数据后重跑即同步**，不再手抄（上游工作区为手抄，改 CSV 不更新报告）。
- runner 新增 `tables` 阶段并纳入 `all`；脚手架新增 `lab_report/tables/`。
- 验证：合成 CSV（含下划线与文本列）→ 生成 `fsr-calibration.tex`/`note.tex`/`all_tables.tex`；`\input{tables/all_tables}` 的测试文档 xelatex 编译 **exit 0**、产出 PDF、日志无错误。

### v1.4（2026-09-10）

- **目录约定对齐上游课程工作区**：实验目录改为工作区根级 `<实验标题>/`（原 `experiments/<实验标题>/` 仍兼容）；预习报告源文件采用上游命名 `preview_report/preview_report.tex`（旧名 `preview.tex` 兼容）。
- `run_lab_workflow.py` 新增解析器：`experiment_dir()`（根级优先、回退旧布局）、`preview_tex()`（两种文件名）、`lab_tex()`；脚手架自动创建 `preview_report/`、`lab_report/{data,figures,scripts,build}` 并放置 `.gitkeep`。
- 讲义来源解析扩展：优先 `<实验标题>/<实验标题>.pdf`，其次 `refer/<实验标题>.pdf`、旧布局路径。
- 讲义哈希守卫兼容 `preview.tex` 与 `preview_report.tex` 两种记录键。
- 验证：旧布局回归 exit 0（4 趟 xelatex）、根级布局 exit 0（新文件名、产出 PDF）、空工作区脚手架结构正确。

### v1.3（2026-09-10）

- 模板资产补齐：`assets/aps_template/` 增加 `acta_physica_sinica.bst`、`.dbj`、`bibfile.bib`、`LICENSE`、`template.pdf`、`figures/figure1.png`（与上游 Bnu_Modern_Physics_Lab_Report 逐文件 SHA256 一致），补齐后可运行 BibTeX 参考文献流程。
- 新增品牌资产：`assets/branding/校徽.webp` 与 `assets/branding/bnu_logo.png`（报告首页可直接用 graphicx 插入）。
- 新增 `assets/workspace_scaffold/.gitignore`（忽略 LaTeX 中间产物、`build/`、`tmp/`、Python 缓存）；§3 脚手架清单补充 `.gitignore`、`校徽.webp`、`bnu_logo.png`。
- `references/agents.md` 增补 Git 约定：完成改动并检查通过后自动创建本地 commit；**推送须先向用户确认**；不上传 build/tmp 缓存；推送失败不得强推。
- `run_lab_workflow.py`：检测到 `\bibliography{}/\bibreference`（或 `\cite` 且同目录存在 `.bib`）时执行 **xelatex → bibtex → xelatex → xelatex**，并为 bibtex 设置 `BSTINPUTS/BIBINPUTS/TEXINPUTS` 以定位工作区 `物理学报模板*` 目录；所有 xelatex 调用增加 `-halt-on-error`（失败即停）。

### v1.2（2026-09-10）

- 依赖文本核心版本标注更新为 advanced_lab_report_gen v3.1：报告顶层章节回归老师 PPT 小论文格式（合并“四、结果与分析讨论”，摘要 100–200 字，参考文献 3–6 条），与本工作流 references/report.md 一致；本工作流行为无改动。
- 更新全文依赖版本标注与默认生成口径说明。

### v1.1（2026-09-10）

- 新增讲义变更检测（SHA-256）：MISSING / CHANGED / UNCHANGED 状态与自动复制覆盖；
- 新增强制文本重生成机制：讲义变更、缺失、首次运行或 `--force` 时强制重写 .tex；
- 新增 `--force` 参数说明；
- 新增 `generation_log.md` 规范（每次运行记录讲义哈希、页数、文本状态与生成动作）；
- `run_lab_workflow.py` 增加编译前讲义哈希校验（哈希不一致时拒绝编译并提示先运行 /build_lab）；
- 依赖更新：文本生成核心 advanced_lab_report_gen v3.1。
