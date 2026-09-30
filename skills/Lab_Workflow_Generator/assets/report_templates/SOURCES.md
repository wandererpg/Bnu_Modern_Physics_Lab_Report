# 期刊风格来源与课程适配

以下官方页面于 2026-09-30 核验。它们用于确认出版机构、模板生态及写作特点；中文课程版的标题字体、颜色、栏距、行距等是本项目选择，不是期刊官方规范的逐项复制。

| 模板 | 官方来源 | 核验内容与适配 |
| --- | --- | --- |
| 02 Physical Review | [APS REVTeX](https://journals.aps.org/revtex)、[REVTeX FAQ](https://journals.aps.org/revtex/revtex-faq) | APS 提供 REVTeX。FAQ 区分单栏双倍行距的 `preprint` 与模拟期刊成稿的 `reprint`，并说明 `twocolumn` 选项。这里采用便于课程阅读的双栏、居中题头和紧凑摘要，不加载 REVTeX，不宣称满足 APS 投稿规范。 |
| 03 Nature | [Nature Formatting guide](https://www.nature.com/nature/for-authors/formatting-guide) | 指南强调面向跨学科读者的摘要及短小子标题。这里借鉴清晰题头与视觉层级；课程仍保留100—200字中文摘要、对应英文摘要、编号六章节，不套用期刊的英文词数或文章长度限制。 |
| 04 Applied Physics Letters | [AIP Author instructions](https://publishing.aip.org/resources/researchers/author-instructions/) | AIP 通用指南提供格式说明及官方 Overleaf 模板入口。本项目采用紧凑双栏，但保留课程所需完整结果讨论。APL 专属 [Authors 页面](https://pubs.aip.org/aip/apl/pages/authors) 本次返回HTTP 403，未将未读取内容作为规范依据，也不采用未经核验的篇幅限制。 |
| 05 Journal of Physics | [IOP LaTeX template support](https://publishingsupport.iopscience.iop.org/questions/latex-template/) | IOP 官方支持页面提供 LaTeX 模板说明及模板入口。此处借鉴物理期刊通用题头和公式友好排版，使用中文 `ctexart` 与课程双栏；不宣称全部 Journal of Physics 期刊具有相同版式或此模板可投稿。 |

01 使用仓库已有 `assets/thu_template/thuemp.cls`，保留其来源信息，不宣称是清华大学官方模板。02—05 为本项目独立编写的课程适配源，没有复制期刊标识或标注虚构投稿、接收日期、作者单位、基金及PACS。

无论选择哪套样式，内容、数据、引用、校徽和提交检查均由根目录 `report.md` 决定；明确的课程模板和教师要求优先。样式选择不改变正文职责，不隐藏异常值，不压缩掉误差分析或改进建议。
