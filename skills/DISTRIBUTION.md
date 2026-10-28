# 对外分发与安装

## 推荐上传什么

供他人安装这套工作流时，以本仓库的 `skills/` 为完整分发目录，保持内部相对路径。两个 Skill 配合使用，只上传一个 `SKILL.md` 会缺少模板、规范或脚本。

```text
skills/
├── Lab_Workflow_Generator/
│   ├── SKILL.md
│   ├── scripts/                  # 初始化、模板选择、编译、图表与版面检查
│   ├── references/               # 运行、预习和实验报告规范
│   └── assets/                   # 六种注册模板、兼容模板、标识和脚手架
├── advanced_lab_report_gen/
│   ├── SKILL.md
│   ├── training_output/          # 文本核心引用的脱敏规则和知识资源
│   ├── docs/
│   ├── README.md
│   └── LICENSE
├── docs/
├── install.ps1
├── install.sh
├── verify_install.py
├── requirements.txt
├── README.md
├── INSTALL.md
├── DISTRIBUTION.md
├── CHANGELOG.md
├── LICENSE
└── THIRD_PARTY.md
```

GitHub 仓库可保留根目录通用规范与 `agent_report_bundle/`，帮助用户阅读和直接使用。若单独发布安装压缩包，以上 `skills/` 目录即可作为主要内容；解压后从该目录运行安装器。

根目录规范是维护源，修改后先同步 `Lab_Workflow_Generator/references/` 并导出通用包，再打包。`export_agent_bundle.py` 用于本仓库维护，依赖仓库根目录；它不是终端使用者生成报告的必需步骤。

## 两种包的区别

| 分发形式 | 内容与用途 | 安装方式 |
| --- | --- | --- |
| `skills/` 完整套件 | 两个 Skill、完整脚本、规范、模板与安装说明 | 运行套件安装器 |
| `agent_report_bundle/` 通用包 | 通用规范、模板、部分脚本及校验清单 | 让任意 Agent 按 `START_HERE.md` 使用 |

通用包未包含两个完整的 Skill 入口、文本核心、安装器和全部运行脚本，不能作为完整 Skill 安装包。它也包含第三方模板资源，须遵守下述分发条件。

## 使用者需要的环境

- Python 3.11 或更高，与 `verify_install.py` 的最低版本检查一致。
- 安装 `requirements.txt` 中的 Python 库。读取 Excel 时按需安装 `openpyxl`；扫描讲义需要 OCR 时按需安装 `rapidocr-onnxruntime`。
- 另行安装含 XeLaTeX、BibTeX、所需中文及参考文献宏包的 TeX 发行版，并配置中文字体。Python 安装器不会自动提供这些系统组件。
- 使用依赖 Poppler 的文本提取或预览步骤时，安装 `pdftotext`、`pdftoppm` 并加入可执行程序搜索路径。
- `lab-assist` 与 `lab-report-writer` 未随包分发。内置编排脚本不导入其代码，但旧版文本核心仍有调用它们的步骤；如采用那些步骤，需另行安装相应 Skill，或明确改用内置 LaTeX 编排流程。不能承诺任意旧分支均能脱离它们运行。

在解压后的 `skills/` 目录中执行：

```powershell
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\install.ps1
python .\verify_install.py
```

macOS / Linux 使用 `python3` 并运行 `bash ./install.sh`。安装器将两个 Skill 复制到用户的 `~/.codex/skills/`，保留已有目录，覆盖方式见 `INSTALL.md`。安装后新开会话。

当前仓库不附实验示例数据，`--demo` 会提示缺少示例并跳过；环境自检通过不代表已经完成真实报告的端到端验收。

## 不应上传什么

不打包个人实验目录、讲义、原始记录、测量数据、报告与历史版本、实验图片和绘图产物，也不打包 `.git/`、虚拟环境、缓存、`build/`、`tmp/`、日志、凭据或旧版 ZIP。模板本身所需的示例图和参考资料属于模板资产，应与个人实验材料区分。

`training_output/` 是文本核心资源，不是模型权重。现有文件以学生 A/B/C 等化名记录规则与样本来源；发布前仍应检查新增内容的身份信息、原文摘录和再分发权限，不因脱敏就假定获得版权许可。

## 公开分发前需处理的资产

以 [THIRD_PARTY.md](THIRD_PARTY.md) 和各资产自带许可证为准，套件的 MIT 许可证只覆盖自有内容。

- **清华 `thuemp` 模板**：当前未附明确的上游许可证。先核实公开再分发许可，或替换为授权明确的模板。模板 01 和旧报告兼容流程使用它，直接删去可能导致编译失败。
- **物理学报模板**：保留 `assets/aps_template/LICENSE` 与原作者声明；其 MIT 许可不能替代其他资产的授权。
- **学校标识**：版权归所属机构。跨学校使用时替换标识，并复核模板中的引用和版面；不要假定删图后所有模板仍能编译。
- **示例与风格材料**：上游模板中的姓名、学号和邮箱应识别为示例占位信息；检查分发版本，避免用户误认为自己的署名。包含学生报告的原文或衍生材料时，也要核实分享权限。

## 发布检查

1. 核对将上传的文件清单，确认只含通用资源，第三方资产有适用的许可或替代方案。
2. 同步规范副本，运行导出器并核对 `agent_report_bundle/manifest.json` 中的路径、大小与 SHA-256。
3. 在隔离安装目录核对两个 Skill 及资源可定位，再检查实际使用环境。报告生成能力还需用使用者有权提供的讲义和数据验收。
4. GitHub 仓库用于持续更新；如发布 ZIP，使用明确版本号，并附变更说明、许可证和环境要求。
