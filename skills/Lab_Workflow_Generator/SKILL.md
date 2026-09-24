---
name: Lab_Workflow_Generator
description: >-
  基于文件目录的半自动化物理实验报告工作区引擎：当用户输入 /build_lab、要求“把实验做成工作区”“扫描实验目录并生成
  全套预习/实验报告+PDF”，或按指定目录结构放入讲义与数据后需要自动生成报告时使用。生成 LaTeX 源文件并调用
  advanced_lab_report_gen 的文本生成能力与 XeLaTeX 编译，产出预习报告、实验报告、可复现数据处理脚本和 PDF。
---

# Lab Workflow Generator —— 实验报告工程化工作区

> 当被触发时，你的角色是**工作区自动化引擎**：把“对话式生成报告”升级为“目录驱动、可复现、可编译”的实验报告工作区。

## 1. 核心指令

1. 当用户输入 `/build_lab [实验名称]`（或自然语言指定实验/工作区路径）时启动；
2. 首先检查或创建第 3 节定义的目录结构；
3. 然后按第 5 节顺序执行自动化流程：扫描实验目录 → 调用 `advanced_lab_report_gen` 的核心文本生成能力（实验识别、数据处理、章节撰写，而非重新走其完整对话流程）→ 生成 LaTeX 源文件与 Python 脚本 → 执行 XeLaTeX 编译；
4. 全部产物生成后，向用户汇报文件清单、编译日志摘要与“建议人工复核项”；
5. 本 Skill 只做工程化封装，不改变既有真实性规则：**不编造数据、现象或结论**，缺失项写“待补充”。

## 2. 元数据与触发

```yaml
name: Lab_Workflow_Generator
version: 1.27
trigger_command: /build_lab [--force]
依赖:
  - advanced_lab_report_gen v3.1（文本核心）
  - lab-assist（LaTeX 工程约定）
  - xelatex / python3（numpy、scipy、matplotlib、pandas）
```

`--force` 参数：忽略讲义状态检查，强制重新生成 .tex 正文、重跑数据处理脚本并重新编译 PDF（适用于用户手动修改 .tex 后刷新或想强制重建全部产物）。

常用触发示例：

```text
/build_lab 塞曼效应
/build_lab --workspace ./my_lab_ws --experiment 高温超导材料的特性与表征
/build_lab --workspace ./my_lab_ws --experiment 塞曼效应 --force
```

## 3. 工作区目录结构

默认工作区根目录 = 用户指定的 workspace（未指定时 = 当前工作目录）。首次运行时若根目录缺少规范文件，从本 Skill 的 `references/` 复制：

```text
workspace_root/
├── AGENTS.md                    # 工作区操作约定（复制自 references/agents.md）
├── README.md                    # 说明如何“填入数据”并“生成全套报告”
├── preview.md                   # 预习报告规范（复制自 references/preview.md）
├── report.md                    # 实验报告规范（复制自 references/report.md）
├── .gitignore                   # 忽略 LaTeX 中间产物与 build/、tmp/（复制自 assets/workspace_scaffold/.gitignore）
├── 校徽.webp                     # 首页校徽素材（复制自 assets/branding/校徽.webp）
├── bnu_logo.png                 # 校徽 PNG（graphicx 可直接引用；复制自 assets/branding/bnu_logo.png）
├── 清华近物实验报告模板/          # 默认模板（复制自 assets/thu_template/：thuemp.cls、README、TempExample.*、image/）
├── 物理学报模板_Acta_Physica_Sinica_/   # 备选模板（复制自 assets/aps_template/，含 .sty/.bst/.dbj/bibfile.bib/figures）
└── [实验标题]/                  # 实验目录位于工作区根，名为讲义内部标题，如：塞曼效应
    ├── [实验标题].pdf           # 实验讲义（用户放入；缺失则警告）
    ├── preview_report/          # 预习报告（含 .gitkeep）
    │   ├── preview_report.tex
    │   └── preview_report.pdf
    └── lab_report/              # 实验报告（含 .gitkeep）
        ├── data/                # 原始数据 (CSV/Excel) 与 data/README.md 数据说明
        ├── figures/             # 生成图表 (PDF/PNG)
        ├── scripts/
        │   ├── generate_plots.py
        │   └── make_data_tables.py   # 随 Skill 提供：data/*.csv -> tables/*.tex
        ├── tables/              # 程序化生成的 LaTeX 表片段（附录用）
        ├── build/               # LaTeX 编译临时文件
        ├── lab_report.tex
        ├── lab_report_thu.tex   # 清华模板版（默认）；两种模板可并存以便对比
        ├── lab_report.pdf
        ├── refs.bib             # 参考文献（gbt7714-numerical，BibTeX）
        ├── thuemp.cls           # 默认模板类（随脚手架复制）
        ├── report_preamble.tex  # 备选：物理学报/ctexart 版导言区
        ├── report_frontmatter_thu.tex  # 默认：清华模板前置区骨架
        └── README.md            # 本实验数据来源、结构与再生说明
```

规则：

- 实验目录位于工作区根目录、以讲义内部标题命名：`<实验标题>/`；讲义重命名为 `<实验标题>/<实验标题>.pdf`；
- 预习报告源文件为 `<实验标题>/preview_report/preview_report.tex`（旧名 `preview.tex` 仍兼容）；实验报告为 `<实验标题>/lab_report/lab_report.tex`；
- `preview_report/`、`lab_report/` 与 `lab_report/{data,figures,scripts,tables,build}` 由脚手架自动创建，并放置 `.gitkeep`；
- 旧版 `<workspace>/experiments/<实验标题>/` 布局**仍兼容**（runner 会自动识别），新工作区一律采用根级布局；
- 编译辅助文件只放 `build/`，最终 PDF 与 `.tex` 放报告目录；不得把 `.aux/.log/.out` 散落在源文件目录；
- **默认使用清华模板**（`thuemp.cls`，双栏）：脚手架会把 `thuemp.cls` 与 `report_frontmatter_thu.tex` 复制到 `lab_report/`；物理学报模板（`report_preamble.tex`）为备选，仅在被明确要求时使用；
- 遇到结构歧义时做最小假设，并在报告 README 中标明待确认项。
### 3.1 精简工作区（推荐给日常使用）

面向"每个实验一个文件夹、只放讲义/数据/两个报告"的使用方式，工作区根目录**只保留实验文件夹**，规范与模板全部由本 Skill 自带、生成时自动带入：

```text
<workspace>/
└── [实验标题]/                 # 讲义内部标题
    ├── [实验标题].pdf          # 讲义（用户提供）
    ├── data/                   # ← 用户把数据丢这里（CSV/Excel/图片）；运行时会自动镜像到 lab_report/data
    ├── preview_report/         # 预习报告（纯内容，便于手抄）
    └── lab_report/             # 实验报告；初始含 thuemp.cls / report_frontmatter_thu.tex / report_preamble.tex
        ├── figures/ scripts/ tables/ build/    # 生成时由脚手架创建
        └── lab_report.tex / lab_report.pdf / refs.bib / generation_log.md
```

- 初始化（批量把讲义变成实验文件夹）：`python init_workspace.py --workspace <WS> --lectures <讲义目录>`
  - 自动读取讲义首页标题作为文件夹名；**扫描件无文本层**时退回文件名并给出警告，可用 `--title-map {"文件.pdf":"正确标题"}` 指定；
  - 也可只给实验名：`--experiments "塞曼效应,液晶物性"`；
- 生成（在该实验文件夹内直接执行，无需 `--experiment`）：
  `python run_lab_workflow.py --workspace . --stage all`
- 用户视角只需四样东西：**讲义、data/、preview_report/、lab_report/**；根目录不放 `preview.md`/`report.md`/模板目录（如需，仍可按 §3 的完整布局放置作为覆盖）。

## 4. 模板与规范

### 4.1 两份规范文件（完整内容已打包在本 Skill）

- 预习报告规范：本 Skill `references/preview.md`（内容同步工作区根 `preview.md`）：预习报告必须含实验目的、物理/实验/仪器三层次原理、实验方法、实验内容、第一次课后问题与思考题；正文 2–3 页；不得伪造未做实验的数据。
- 实验报告规范：本 Skill `references/report.md`（内容同步工作区根 `report.md`）：报告顺序固定为 基本信息行（作者/学号；指导老师/时间，不列班级）→ 摘要(100–200字，含关键数值) → 关键词(3–5) → 一、引言 → 二、原理 → 三、实验 → 四、结果与分析讨论 → 五、结论和建议 → 六、参考文献 → 附录。

生成正文前，先读取对应 reference 全文并按其“提交前检查清单”执行。

### 4.2 LaTeX 模板（默认：清华 thuemp；备选：物理学报）

**默认 —— 清华近代物理实验报告模板（`thuemp.cls`，本 Skill `assets/thu_template/`，v1.1 非官方）**

- `ctexart` 派生的 **A4 双栏**类，自带「北京师范大学普通物理实验」页眉与首页结构；主文件头部：

```latex
% !TEX program = xelatex
\documentclass{thuemp}
\usepackage{xcolor}                                        % 数据说明灰框
\sisetup{detect-all,per-mode=symbol,separate-uncertainty=true}
\ctexset{section={name={,、},number=\chinese{section}}}     % 一、二、三
```

- 前置区按 `report_frontmatter_thu.tex`（脚手架已复制）：`\emptitle` → `\empauthor{姓名}{指导教师}` → `\twocolumn[…\maketitle… empAbstract/\Keyword… 英文块… \empfirstfoot{实验时间}{报告时间}{学号}{E-mail}…]` → `\wuhao` → 正文；
- 图题**单语中文**「图N：描述」，正文 `图~\ref{}`（该类基于 `ccaption`，**无 `\bicaption`**）；表题「表N：描述」；公式统一编号并以“式（x）”/`\eqref` 引用；
- 宽幅图/表用 `table*`/`figure*`；首面必要时在正文第一节内加 `\enlargethispage{-3.3cm}`；
- 参考文献按 GB/T 7714—2015：`\bibliographystyle{gbt7714-numerical}` + `\bibliography{./refs}`，正文 `\cite{}`；
- 编译链：`xelatex → bibtex → xelatex → xelatex`（含参考文献必须跑 bibtex）。

**备选 —— 物理学报模板（`assets/aps_template/` + `report_preamble.tex`）**

- `\documentclass[UTF8,a4paper,10pt]{ctexart}` + `\input{report_preamble}`，单栏；仅在被明确要求时使用；
- 双语图题 `\bicaption{中文}{English}`、正文 `Fig.~\ref{}`；校徽 `\bnulogo`（7 cm、相对正文左页边距左移 2 cm、仅首页、overlay 不占流）。

## 5. 核心工作流

对 `experiments/[实验名称]/` 执行以下流程：

### 步骤1：扫描与识别

1. 列出实验目录文件：讲义 PDF、`lab_report/data/` 下所有数据文件、已有 `figures/scripts/*.tex/*.pdf`；
2. 用 `advanced_lab_report_gen` 的实验映射（关键词/公式）识别实验；输出标准实验名与置信度；
3. 无讲义且无数据时停止并提示缺失；只有讲义时仍可生成预习报告与实验报告框架（数据部分“待补充”）。

#### 讲义变更检测（SHA-256）

在执行任何生成操作前执行以下检测：

1. 读取源讲义路径：优先 `<实验标题>/[实验名称].pdf`，其次 `refer/[实验名称].pdf`（或用户指定的源路径）；**若讲义无文本层（扫描件），先运行 `ocr_lecture.py`（或 `--stage ocr`）生成 `lab_report/lecture_ocr.txt`，再据此绑定事实**；
2. 计算源讲义的 SHA-256；
3. 读取工作区副本：`experiments/[实验名称]/[实验名称].pdf`；
4. 若工作区副本不存在 → `lecture_status = "MISSING"`，提示用户先复制讲义，且禁止继续文本生成；
5. 若副本存在：
   - 计算副本 SHA-256；
   - 与源讲义比对：一致 → `"UNCHANGED"`；不一致 → `"CHANGED"`，并自动从源路径复制覆盖工作区副本；
6. 记录到 `lab_report/generation_log.md`：源讲义路径、源/副本 SHA-256、比对结果（UNCHANGED/CHANGED/MISSING）、讲义页数、文本字符数、文本层状态（可提取/需OCR/不可提取）。

`--force` 时跳过比对，直接视为 CHANGED 处理。

### 步骤2：调用文本生成核心

调用 `advanced_lab_report_gen` 的**核心生成逻辑**（§2 全局配置、§3 步骤1–5 的检查规则），而非其完整对话界面：

- 讲义变更/首次运行/`--force` 时，使用同一份讲义全文（如 13,704 字符）同时重写 `preview_report/preview.tex` 与 `lab_report/lab_report.tex`；preview.tex 必须包含讲义中的真实参数（如 Kastler、Zeeman、a₈₇=3417.34 MHz、缓冲气体类型等），不得仅基于 `preview.md` 模板填空；
- 实验报告按 `report.md` 生成 → 写入 `lab_report/lab_report.tex` 的正文部分（摘要、引言、原理、实验、结果与分析讨论、结论、参考文献）；
- 保留该 Skill 的硬性规则：摘要含数值、原理不照抄、讨论四步、图/表/公式规范、封面信息“待补充”清单；
- 文本按 advanced_lab_report_gen v3.1 规则生成：默认应用老师小论文格式组织章节（与 references/report.md 一致），撰写语言与论证参考《大学物理》期刊学术风格锚点（§2.7），不对特定作者加权。

#### 强制文本重生成条件

满足以下任一条件时，必须重新调用 `advanced_lab_report_gen` 生成 .tex 正文：

1. `lecture_status = "CHANGED"`（讲义已更新）；
2. `lecture_status = "MISSING"`（讲义缺失，需提示且不得生成）；
3. 目标 `.tex` 文件不存在（首次运行）；
4. 用户明确指定 `--force`。

当 `lecture_status = "UNCHANGED"` 且目标 `.tex` 已存在时，可跳过文本生成，直接进入数据处理与编译。

禁止行为：讲义已变更却复用旧 .tex；讲义缺失仍继续生成。

### 步骤3：生成数据处理脚本

在 `lab_report/scripts/generate_plots.py` 生成可复现脚本（规范见第 6 节），并运行一次验证输出：

```powershell
py lab_report\scripts\generate_plots.py
```

### 步骤3.5：生成附录数据表（程序化，不手抄）

把 `lab_report/data/*.csv` 渲染为 `lab_report/tables/*.tex`（booktabs 三线表；自动转义、数值列右对齐），报告用 `\input{tables/<name>}` 引入：

```powershell
py <Skill>\scripts\make_data_tables.py --combined     # cwd = lab_report/
# 或由 runner 统一执行：python run_lab_workflow.py --experiment <实验名> --stage tables
```

改数据后重跑即可同步表格；正文与附录不再手抄数字（上游工作区是手抄的，改 CSV 不会更新报告）。

### 步骤4：自动编译 PDF

对预习报告与实验报告分别执行：

```text
# 预习报告（无参考文献，两遍即可）
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build preview_report.tex   （两遍）
# 实验报告：默认清华模板含参考文献 → xelatex → bibtex → xelatex → xelatex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build lab_report.tex
bibtex build/lab_report
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build lab_report.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build lab_report.tex
```

把 `build/*.pdf` 复制到对应报告目录；无 `.bib` 时跳过 bibtex。上述流程已由 `run_lab_workflow.py` 自动化：检测到 `\bibliography{}/\bibreference`（或 `\cite` 且同目录有 `.bib`）即按 `xelatex→bibtex→xelatex→xelatex` 执行，并为 bibtex 设置 `BSTINPUTS/BIBINPUTS/TEXINPUTS` 以定位工作区模板目录。编译失败时保留源文件、输出完整错误日志并说明阻塞原因。

### 步骤5：生成说明文件

生成 `experiments/[实验名称]/README.md`，包含：

- 数据来源与数据声明（实测 / 模拟 / 混合）；
- 目录结构与各文件用途；
- 重新生成命令（脚本 + 两次编译）；
- 待补充项与已知限制。

## 6. 数据与脚本规范

`generate_plots.py` 必须满足：

1. 文件头注释：实验名称、作者占位、数据文件、依赖、固定随机种子；
2. `import numpy as np` 后立即设置 `np.random.seed(42)`（如需随机数据），保证结果可复现；
3. 明确函数结构：`load_data()`、`process_data()`（计算/拟合/误差）、`make_figures()`、`main()`；
4. 从 `../data/` 读取（相对路径以脚本所在目录为基准），图表输出到 `../figures/`（PDF 优先）；
5. 输出数值汇总到 `../data/processed_results.csv`（若适用）并在终端打印关键结果（R²、斜率、误差等）；
6. 禁止硬编码绝对路径；禁止修改原始数据文件；
7. 输出 CSV 应各有独立内容：**不要生成内容重复的两个汇总文件**（否则附录会重复成表）；文件命名建议"中文名 英文名.csv"并在报告附录中按其真实文件名引用。

`make_data_tables.py`（随 Skill 提供，位于本 Skill `scripts/`）：

- 从 `data/*.csv` 生成 `tables/*.tex`（`booktabs` 三线表；表题取文件名；`\label{tab:<slug>}`）；
- 自动转义 `_ % & # $ { } ~ ^`；数值列右对齐、文本列左对齐；超长表默认截断（`--max-rows`，默认 30）并加表注；
- **列宽自适应到版心（`--fit`，默认开）**：自然宽度超版心时改用 `p{\dimexpr f\textwidth-8pt\relax}` 列（每列减去的 `2\tabcolsep` 与列间距相消，故表格总宽恰为 `Σf·\textwidth`，与模板无关）。判据用 em 估算（CJK 1em、ASCII 0.5em，`--fit-em` 默认通栏 45 / 单栏 21）；放不下时报 `FAIL` 并列出「最小宽度 > 可用宽度」，提示必须拆表；`--no-fit` 可退回旧的 `l/r` 自然宽度；
- `--array`：数值列居中、文本列左对齐（需 `\usepackage{array}`）；runner 检测到文档加载 array 时自动开启，否则退化为普通 `p` 列（仍能放进版心）；
- 未四舍五入的长小数（>7 位）会告警，建议在数据准备脚本里取 3–5 位有效数字；
- `--combined` 额外生成 `tables/all_tables.tex`（`\input` 全部表），供附录一次性引入；
- 输出为**生成物**：不要手工编辑；改数据后重跑脚本。

`check_report_tex.py`（随 Skill 提供，位于本 Skill `scripts/`）——把 `report.md` 的文字规则变成可执行检查：

- **每图每表必须有题注**（缺 `\caption`/`\bicaption` 报错）；
- **引用必须可解析**：`\ref/\eqref` 指向不存在的 label 报错；label 从未被引用给警告；
- **必需章节齐全**（实验报告：引言/原理/实验/结果与分析讨论/结论/参考文献；预习：目的/原理/仪器/方法/内容）；
- **摘要长度提示**（实验报告 100–200 字）；
- **可读性/几何检查**：`\resizebox/\scalebox`、插图宽度 <0.85 倍版心、题注 <10 字、表格 >20 行、**表格列数 >7**、**自然宽度估算超版心**（会排到纸外而编译不报错）、**表格里 ≥8 位长小数**；
- 用法：`python check_report_tex.py <file.tex>`、`--dir <目录>`、`--kind lab|preview`、`--strict`（警告也算错误）。

`check_pdf_geometry.py`（随 Skill 提供，位于本 Skill `scripts/`）——**编译后**直接量成品 PDF：

- 为什么必需：LaTeX 对「表格比版心宽」不报错，只把它排到纸外（实测一张 10 列表的横线右端到 x1=1025.6pt，而 A4 纸宽 595.3pt，约 15cm 内容读者看不到），日志里只有一条 Overfull hbox；
- `FATAL` 元素越出纸面；`WARN` 越出版心（出血）、通栏长行重叠（如首页「数据说明」框压住摘要首行）、**横线/框线从字形中穿过**（区分「图内图例压线条」与「版面间距不足」两种根因）、图内文字过小（<8pt 小字成簇且带图形笔画——矢量图被缩小后字号一起缩）、位图有效分辨率 <150dpi；
- 版心边界由文字行的众数边界自动估计，无需知道模板 geometry；
- 用法：`python check_pdf_geometry.py lab_report.pdf [--strict] [--json out.json]`；runner 的 `compile` 阶段会自动执行（缺 PyMuPDF 时跳过，不阻断）。


`init_workspace.py`（随 Skill 提供，位于本 Skill `scripts/`）：

- 批量把讲义 PDF 目录变成**精简工作区**：每份讲义建一个 `<实验标题>/`，内含 `<实验标题>.pdf`、`data/`、`preview_report/`、`lab_report/`（随附 `thuemp.cls`、`report_frontmatter_thu.tex`、`report_preamble.tex`、`data/README.md`）；
- 自动从讲义首页（必要时到第 3 页）提取标题作为文件夹名；无文本层的扫描件退回文件名并警告，可用 `--title-map` 修正；
- 幂等：重复运行不覆盖既有文件（`--force` 可覆盖讲义）。


`ocr_lecture.py`（随 Skill 提供，位于本 Skill `scripts/`）：

- 逐页判断：文本层字符数 **≥50** 直接用文本层，否则**渲染该页为图像并 OCR**（`rapidocr-onnxruntime` + `PyMuPDF`）；
- 输出 `<<<PAGE n>>>` 标记的文本文件；`--experiment <实验目录>` 时默认写入 `<实验>/lab_report/lecture_ocr.txt`；
- 供正文/预习报告绑定讲义事实（尤其扫描件），也便于人复核 OCR 质量；
- runner 的 `all`/`ocr` 阶段会**自动判断**：若讲义是扫描件且尚无 `lecture_ocr.txt`，自动执行本脚本。

工作区根命令：

```powershell
python run_lab_workflow.py --experiment 塞曼效应            # 打印/执行工作流
python run_lab_workflow.py --experiment 塞曼效应 --stage plots
python run_lab_workflow.py --experiment 塞曼效应 --stage tables
python run_lab_workflow.py --experiment 塞曼效应 --stage check
python run_lab_workflow.py --experiment 塞曼效应 --stage compile
```

文本正文（`.tex` 的 prose）必须由本 Skill/`advanced_lab_report_gen` 生成；`run_lab_workflow.py` 只负责目录检查、数据清单、脚本执行与编译等确定性步骤。

## 7. 验收与输出

### generation_log.md 规范（每次运行必生成/更新）

每次运行 `/build_lab`，在 `lab_report/` 下生成或更新 `generation_log.md`：

```markdown
# 生成日志
- 生成时间：[ISO 8601 时间戳]
- Skill版本：Lab_Workflow_Generator v1.19
- 文本生成核心：advanced_lab_report_gen v3.1
- 实验名称：[标准实验名]

## 讲义状态
- 源讲义路径：[路径]
- 源讲义 SHA-256：[哈希值]
- 工作区副本 SHA-256：[哈希值]
- 比对结果：UNCHANGED / CHANGED / MISSING
- 讲义页数：[页数]
- 讲义文本字符数：[字符数]
- 文本层状态：可提取 / 需OCR / 不可提取

## 生成动作
- 文本重生成：YES / NO（原因：CHANGED / 首次运行 / 强制 / 跳过）
- preview.tex SHA-256：[哈希值]
- preview_text_regenerated：YES / NO（原因：CHANGED / 首次运行 / 强制 / 跳过）
- lab_report.tex SHA-256：[哈希值]
- 数据处理脚本：已执行 / 已跳过
- PDF编译（预习）：成功 / 失败
- PDF编译（实验）：成功 / 失败

## 异常与警告
- [列出本次运行中出现的任何异常或警告]
```

完成后汇报：

```text
✅ 工作区产物
- preview_report/preview.pdf
- lab_report/lab_report.pdf
- lab_report/lab_report.tex
- lab_report/scripts/generate_plots.py
- lab_report/figures/（图表）
- experiments/[实验名称]/README.md
```

并给出：

- 编译日志摘要（成功/错误）；
- 数据声明（真实/模拟/混合）；
- 建议人工复核项（封面信息、实测数据替换、原理重写、讨论误差、参考文献、教师签名原始记录）。

## 8. 错误处理

| 异常 | 处理 |
| --- | --- |
| 目录/数据缺失 | 创建骨架并列出缺失项，不编造内容 |
| 识别失败 | 手动指定实验名，或从 `advanced_lab_report_gen` 映射表人工核对 |
| 脚本运行失败 | 自动重试 1 次并输出 traceback；标注待修复 |
| XeLaTeX 编译失败 | 输出完整日志，保留 `.tex`，给出修复建议 |
| 规范文件缺失 | 从本 Skill `references/` 重新复制 |

## 9. 关联 Skill 使用方式

- 文本生成：读取并调用 `advanced_lab_report_gen` 的 §2 全局配置与 §3 步骤1–5 规则（其安装路径：`~/.codex/skills/advanced_lab_report_gen/SKILL.md`）；
- LaTeX 工程约定：参考 `lab-assist`（`~/.codex/skills/lab-assist/SKILL.md`）的目录与编译约定；
- 本 Skill 的 `references/`、`assets/aps_template/`、`scripts/` 是打包资源，工作区初始化时复制使用，不在生成报告后改动。

---

## 数据表组织规范（v1.20 新增，由真实运行反馈驱动）

用户反馈"报告算得出结果，却无法展示原始数据"，复盘出四条硬规则（已写入 `references/report.md` 与内容核心 `advanced_lab_report_gen`）：

1. **原始与派生分表**：`原始数据` 表只放原始读数（如数字电流表的读数矩阵）；均值、标准差、四方程解、拟合参数等派生量各成表，并在表题注明来历。**同一列名不得在不同批次数据里代表不同物理量**——旧实现把两次课熔进一张 10 列表，`重复次数` 列在第一次课是"4 次重复"、第二次课填的却是"4 个共振判读状态"，`标准差` 列同理。
2. **矩阵形态**：同一条件的多次重复横向排成"第 1 次/第 2 次/…"，多个状态横向排成"状态 1/状态 2/…"，而不是每个读数摊成一行（旧表 16 个读数排成 16 行 + 8 行空行）。
3. **测量条件入表**：方向符号约定、射频频率、重复次数、判读方式、缺测标注必须出现在表内或表题里，否则原始读数无法被理解或复现（旧表第二次课的 16 个读数从未写出对应的射频频率）。
4. **按列统一小数位**：电流一律 3 位、换算系数一律 4 位；长小数（如 19 位）会把列撑爆并连带把表挤出纸面。

配套工具改动：`make_data_tables.py` 新增 **陈旧生成物清理**（CSV 改名/删除后自动删除对应的 `tables/*.tex`，只删带自动生成标记的文件，手写表不动）与 **`--` 连字保护**（TeX 会把 ASCII `--` 连字成 `–`，使数据里的方向组合 `--` 显示成单个短横线与 `-` 无法区分；现插入空组阻断）。

## 更新日志

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

- **正文表改“就地通栏表”**：`make_data_tables.py` 新增 **`--strip` / `--strip-csv`**，生成 `cuted` 的 `strip` + `table[H]`（全宽、不浮动）。实测效果：4 张正文表的**题注页 = 首次引用页**，表格横线跨度 481.9pt 恰等于版心。runner 检测到文档加载 `cuted` 时，**只对正文用到的表**（`仪器参数与换算 instrument-params.csv`）传 `--strip-csv`；附录原始数据表保持浮动。
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

- **修正 `make_data_tables.py` 的 slug 冲突（由首次真实运行发现）**：文件名若几乎全为中文，slug 会被剥成空并回退为 `table`，导致**多个 CSV 生成同一个 `table.tex` 互相覆盖、附录静默丢表**。现改为：ASCII 部分为空时用 `tNN`（按排序序号），并对任何重名自动加后缀；已有 ASCII slug 保持不变（旧报告的 `\input` 路径不受影响）。
- **新增 `--caption-map`**：以 JSON 指定每个 CSV 的表题，生成器据此写 `\caption{}`（缺省仍用文件名）；runner 在 `tables` 阶段自动传入 `lab_report/table_captions.json`（存在时）。
- 数据脚本规范补充：建议数据文件命名为「中文名 英文名.csv」以便 slug 可读。

### v1.16（2026-09-16）

- 依据「干涉滤光片的镀制」回归发现的一处质量问题补规则：附录表**不得重复列出同一份数据**（该次生成中 `计算结果汇总 processed_results.csv` 与 `滤光片参数 filter metrics.csv` 内容完全相同，附录 A 因而把同一张表列了两遍）。
  - `references/report.md` 附录条目新增"附录表与数据文件一一对应、不得重复"要求；
  - `SKILL.md` §6 数据脚本规范新增第 7 条：输出 CSV 应各有独立内容，不要生成内容重复的汇总文件；并建议按"中文名 英文名.csv"命名、附录引用真实文件名。

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

- **排版范式固化**：新增随 Skill 提供的、经编译验证的导言区片段 `assets/scaffold_template/report_preamble.tex`（A4/2cm/1.5 倍行距、`\ctexset` 一级标题中文编号「一、」、`siunitx` 不确定度 `\SI{438.5(17)}{\mega\hertz}`、双语图题 `\bicaption`、`\blankfield` 封面留空横线、`\bnulogo` 校徽 overlay 7.0cm/左移 2cm/仅首页）。
- 脚手架新增：把 `bnu_logo.png` 与 `report_preamble.tex` 复制到 `<实验标题>/lab_report/`（`assets/bnu_logo.png`），并创建 `lab_report/assets/`。
- `references/report.md` 新增「排版实现片段」小节，指向该片段与用法。
- 验证：用该片段写成的测试报告（校徽/封面/摘要/双语子图+双语图题/三线表/siunitx）xelatex **编译 exit 0**、产出 PDF、日志**零错误**。

### v1.5（2026-09-10）

- 新增 **程序化附录数据表**：Skill 自带 `scripts/make_data_tables.py`，把 `lab_report/data/*.csv` 渲染为 `lab_report/tables/*.tex`（booktabs 三线表、自动转义、数值列右对齐、超长截断加表注、`--combined` 汇总）。报告以 `\input{tables/<name>}` 引入，**改数据后重跑即同步**，不再手抄（上游工作区为手抄，改 CSV 不更新报告）。
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
