# 自带工具与材料输入

所有生成、提取和审查代码均在本技能`scripts/`，不读取其他skill。Python 3.10+；普通安装、快照和阶段导出只需标准库，Word生成需要python-docx；PDF提取/预览需要pypdf和pypdfium2。`requirements.txt`给出版本范围，不含OfficeCLI、API或其他skill。可复用已有解释器，新增依赖优先放项目虚拟环境，依当前授权安装，不覆盖基础环境。

## 从输入到可编辑稿

1. 用`source_evidence.py snapshot`冻结已审阅的有序文件。选择JSON是相对项目路径的数组；它不是自动全盘扫描。文件编码可明确指定。
2. 复制`assets/material-input.example.json`到项目草稿目录，替换所有示例事实。`application`遵循[登记字段](registration-fields.md)，`source_snapshot`指向实际快照。
3. `manual.chapters`顺序就是手册章节。块类型为`paragraph`（text）、`table`（headers/rows）或`screenshot/diagram`（path、caption、evidence、可选width_cm）。图片路径相对输入JSON目录或明确绝对路径，支持PNG/JPEG；真实来源仍需人工/运行核对。章节不得只有空壳，示例结构不代替完整手册。
4. `python scripts/materials.py build --input <输入JSON> --out <新目录>`。生成目录必须不存在；旧版本保留，失败时保留诊断标记，不清理用户文件。可以通过`--wrap-columns`调整展示宽度，但不能把其当实际分页。

输出含申请表信息TXT、代码全文TXT/DOCX、手册Markdown/DOCX、图片副本、源码快照、登记事实本地副本、完整行映射和产物哈希。含源码与证件的本地材料目录不得混进技能仓库/安装包。

## 回读与审查

`python scripts/materials.py audit --bundle <生成目录> --report <新的审查JSON>`回读真实DOCX，按独立保存的段映射去编号、合并展示折行并逐行与冻结源码比较，检查漂移、文字和图片哈希、页眉主体及附录残留。它不从快照伪造“已提取文本”。变更正文或登记事实后重新生成到新目录。

`static_ok`只表示已定义的静态检查未发现错误；`submission_ready`始终为false，必须由完整审核补齐事实、运行、规则与分页。工具明确列出空白源码行、展示折行、缺身份、图像来源及实际排版待核。空白行原样保留，绝不能当填充的有效代码；若行数不合受理要求，采用经审查、保留字符串语义及完整映射的展示方案再回读，不机械删除。

## 实际排版与全页预览

Windows已安装Word时，在PowerShell执行：

```powershell
pwsh -NoProfile -File scripts/render_word.ps1 -Document '材料/代码材料_全部.docx' -OutDir '材料/代码排版01'
pwsh -NoProfile -File scripts/render_word.ps1 -Document '材料/操作手册.docx' -OutDir '材料/手册排版01'
```

每份文件在独立PowerShell进程中运行，避免旧版Word在关闭最后一份文档后使COM对象失效。脚本创建自己的Word实例、只操作副本、禁用宏，不连接或关闭用户已有文档。刷新目录/字段、重新分页、保存副本、输出PDF与布局JSON，记录实际页数、每页视觉行数、标题页位置及源码行所在页。遇到不可用Word或许可对话框时停止并记录，不结束用户进程，不把超时当成功。

其他环境可用已安装的LibreOffice：`soffice -env:UserInstallation=file:///绝对路径/独立临时配置 --headless --convert-to pdf --outdir <新目录> <明确DOCX>`。确认输出，检查TOC字段是否刷新；必要时在副本中更新目录。PDF转换成功不自动说明目录已正确，按实际章节页号逐项对照。字体环境改变后必须复核布局。

刷新副本后再审查：`materials.py audit --bundle <原生成目录> --code-docx <刷新代码DOCX> --manual-docx <刷新手册DOCX> --report <新JSON>`。副本哈希与原文件不同是预期，工具仍验证原产物证据及副本实际文字图片。

`python scripts/pdf_evidence.py --pdf <实际PDF> --out <新预览目录>`导出每页PNG和文本；检查所有页并在审查记录中逐项判定。工具不会把已渲染自动写成已目视检查。代码普通页计有效行、编号及无二次折行；手册分类核查封面、目录、普通正文、图文和结束页，不能用PDF提取的文本行数冒充视觉行数。

把实测代码/手册页数同步申请信息、登记记录和当前清单，记录依据PDF哈希和排版引擎。工具不自动推断“全部合规”。用户若要求原项目文件名，可在审核后按已确认全称、版本及修订状态重命名，并更新有效清单哈希。

## 连续交存PDF

全文审查通过后运行`python scripts/export_deposit.py --pdf <完整实测PDF> --out <新交存PDF> --mode auto`。不足或等于60页保留全文，超过则提取连续前30和后30，附原页号及前后哈希。程序和手册分别运行；源码全文DOCX及选材连续性证据保留。例外交存与加密遮盖另按当前正式规则办理，不由此工具默认实现。
