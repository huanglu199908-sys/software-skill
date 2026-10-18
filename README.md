# software-skill

从有实际意义的软件方向出发，完成算法设计、软件实现与验证，再生成和审查中文软件著作权申请材料。

当前版本 **2.0.0**，是独立技能：从0了解需求 → 选题 → 方案设计 → 实现与验证 → 软著撰写 → 审核 → 修改润色。规则、写作指南、源码提取、Word/TXT生成和审查脚本均在本仓库内，不再要求安装或调用其他skill。

保留台账参考样式：独立封面、实际页码目录、流程与模块图、真实页面说明、默认无附录；代码9磅、页内1—50编号。参数见 [format-profile.json](references/format-profile.json)。这是用户交付偏好，不是法定唯一模板。阶段完成条件见[阶段交付](references/stage-deliverables.md)。

## 第一次使用

这是供具备文件与命令工具的AI代理加载的技能，不是双击运行的软件。最方便的用法是安装后，在代理中打开准备存放软件的项目目录，再用自然语言说明目标。无需手工执行每一个生成脚本；代理会读取本技能并按当前阶段组织工作。

从零开始时，可直接发送：

```text
使用 software-skill，从0开始帮我做一个有实际意义的软件著作权项目。
使用场景：高校教务或日常办公。
先结合我的电脑、可用数据和实际业务，提出3个可比较的方向；
每个方向说明痛点、输入输出、算法改进机制、验证方法及实现成本。
等我选定方向后，继续设计、实现和验证软件，再撰写申请材料、审核并修改润色。
```

Codex中可将开头写成`使用 $software-skill`；DeepSeek Harness通过其技能加载器调用`/software-skill`，WorkBuddy先选择本技能再发送任务。场景、候选数量和算法目标均可按实际需要修改。

如果已经确定要做的软件，直接提供方向及现有文件，不必重新选题：

```text
使用 software-skill。我的方向是“这里填写软件方向”，项目位于“这里填写实际目录”。
请先检查现有文件和进度，补齐可实施方案，实现完整软件并验证；
随后根据实际程序编写软著资料，审核并修正问题。
```

## 全流程怎样推进

| 阶段 | 你提供或决定什么 | 技能完成什么 |
| --- | --- | --- |
| 0 需求与环境 | 使用者、反复处理的事务、可用数据、时间及资源约束 | 核对实际环境、已有文件和缺失信息，建立项目记录 |
| 1 选题 | 从候选中选择；已选方向直接沿用 | 比较业务价值、数据来源、独立性、改进空间与开发成本 |
| 2 方案设计 | 明确关键业务取舍和范围 | 设计业务闭环、数据模型、模块、界面、算法基线与改进、回退和验收标准 |
| 3 实现与验证 | 提供必要业务样例；没有真实数据时可明确使用合成样例 | 实现源码、启动入口、输入输出与异常反馈，先验证正确性再开展算法比较 |
| 4 软著撰写 | 确认名称、版本、权属、完成日期等本项目事实 | 提取真实源码，撰写申请信息与操作手册，取得真实截图并生成Word/TXT |
| 5 审核 | 提供参考格式或补充真实业务事实 | 核对实现、源码回读、截图、登记字段、目录、实际分页和图文布局 |
| 6 修改润色 | 指明审核报告或希望修改的范围 | 修复事实与完整性问题、压缩重复文字、调整格式并重新核验 |

名称、日期和权属等事实不能由技能猜测。证件号可以按约定留待本地补录；身份信息不要写进公开示例或技能仓库。用户已确认且仍适用的决定会复用，例行测试、排版和已要求的修订不重复审批。仅有设计或原型时，不能直接写成“软件已全部实现”。

## 只做其中一步或继续已有项目

按实际需求复制并修改下面的任务即可：

| 目标 | 示例任务 |
| --- | --- |
| 只做选题 | 使用software-skill，为采购台账工作提出3个有实际价值、数据可得、算法改进可验证的软件方向，先不开发。 |
| 只做设计 | 使用software-skill，按我选定的方向完成业务、算法和模块设计，给出可验证的验收标准，暂不实现。 |
| 设计后实现 | 使用software-skill，根据当前项目已确认方案实现完整软件，跑通关键流程与异常路径，保留验证证据。 |
| 已有软件生成材料 | 使用software-skill，检查这个项目的实际功能与完成程度，按真实源码和运行页面编写软著资料，待补字段明确列出。 |
| 审核现有材料 | 使用software-skill，对照当前程序及我提供的参考文件，审核代码材料和操作手册，逐项列出证据、问题和未验证项。 |
| 根据报告修改 | 使用software-skill，按照这份审核报告逐项修正并润色材料，保留旧版备份，对最终文件重新回读和检查分页。 |
| 跨会话继续 | 使用software-skill，读取这个项目的流程记录和实际文件，从尚未完成的阶段继续，不重做已完成工作。 |

新会话中应明确项目目录，并提供上次的记录或报告路径；只有一句“继续”且没有项目上下文时，代理可能无法判断要继续哪个软件。默认记录见[状态与证据](references/state-evidence.md)。

## 会得到哪些文件

每个软件放独立项目目录，尊重已有布局。常见交付如下，具体数量由实际软件决定：

```text
你的软件项目/
  实际源码、依赖说明和启动入口
  设计文档/、tests/、必要的实验记录
  流程记录/                 当前状态、确认记录、功能证据、问题与修订
  软件著作权申请资料/
    草稿/                   业务理解、登记信息、源码选材、手册及材料输入JSON
    截图原始/、截图/         当前软件的真实运行图及来源清单
    审查记录/               哈希、回读结果、分页与预览、问题和复验
    正式资料/               本轮核验后的当前有效Word/TXT及需要的PDF
```

生成器首次输出是可编辑材料，完成审核后才列入当前正式交付。缺截图、身份信息或真实分页时会明确标为待补录/未验证。申请表信息TXT供填写官网，不代替官网申请表、身份证明、协议和签章；技能不自动提交登记。内部检查通过不表示登记获批。

## 调用与兼容

| 平台 | 接入方式 | 调用 |
| --- | --- | --- |
| Codex | 原生Agent Skills目录、`agents/openai.yaml` | `$software-skill` |
| DeepSeek Harness | 原生SKILL.md目录；启用registry、filesystem、tool-skill插件 | `/software-skill` 或自然语言指定 |
| WorkBuddy / CodeBuddy | 项目`.codebuddy/skills/`；另提供带WorkBuddy元数据的ZIP | 选择技能或“使用software-skill” |
| DeepSeek网页聊天 / 纯API | 按阶段导出并加载提示词/消息JSON | 以所提供指令工作；本地执行须另外接工具 |

本仓库提供包结构与加载验证，不承诺任意客户端版本、模型配置或权限环境下都能完成本机开发。纯聊天不能仅凭提示词获得文件、浏览器或Word执行能力。具体步骤和官方依据见[平台兼容说明](references/platform-compatibility.md)。

## 安装

需要Python 3.10+。先取得本仓库；私有仓库下载或克隆需要你的GitHub账号访问权。下面的命令均在下载或解压后的`software-skill`目录执行；尖括号中的内容是待替换的路径，不要原样复制执行。使用当前环境能运行的Python解释器；Windows也可将`python`换成`py -3`。

```text
python scripts/install.py --platform codex --scope user
python scripts/install.py --platform deepseek --scope user
python scripts/install.py --platform workbuddy --scope project --project "你的软件项目目录"
```

默认分别安装到`~/.agents/skills/software-skill`、`~/.dsh/skills/software-skill`、`<项目>/.codebuddy/skills/software-skill`。Codex实际使用其他技能根时用`--skills-dir`明确指定，避免重复同名安装。已有目录须加`--replace`，脚本先精确备份再替换；`--dry-run`无写入。不修改客户端配置、安装运行时或读取API密钥。

WorkBuddy也可在技能页面选择“添加技能→上传技能”，导入下面构建出的`software-skill-workbuddy.zip`。这只是安装本地技能包，不是将技能提交到公共市场。

仓库已提供[标准安装包](https://github.com/huanglu199908-sys/software-skill/blob/main/packages/software-skill.zip)和[WorkBuddy安装包](https://github.com/huanglu199908-sys/software-skill/blob/main/packages/software-skill-workbuddy.zip)。WorkBuddy导入专用包；GitHub的整库源码ZIP用于获取仓库，不要直接当作技能导入包。安装后若仍未发现技能，先开启新会话，再核对客户端实际扫描的技能目录。

更新已有安装时，对原来的安装命令加`--replace`，例如`python scripts/install.py --platform deepseek --scope user --replace`。Codex使用过`--skills-dir`时，更新也要指向同一实际目录，避免装出两个同名技能。更新会保留旧目录备份。

## 运行工具准备

仅安装、选题、设计或导出提示词不需要文档库。需要实际生成Word、读取PDF和预览时，在允许安装依赖的环境中执行：

```text
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/check_environment.py
```

上例为Windows；macOS/Linux将解释器路径换成`.venv/bin/python`。使用同一个已装依赖的解释器运行后续材料命令；已有可用环境可以复用。初始化虚拟环境不等于安装了Word或LibreOffice。DOCX写入使用Python库，目录刷新、真实分页及PDF输出需要可用的实际排版引擎。

## DeepSeek聊天与API

```text
python scripts/export_prompt.py --stage direction --task "为行政办公提出三个有实际用途的软件方向" --out "../skill-use/prompt.md"
python scripts/export_prompt.py --stage audit --task "检查当前项目材料" --format messages --out "../skill-use/messages.json"
python scripts/export_prompt.py --stage implementation --task "按已确认设计实现" --format request --model "你实际可用的模型ID" --out "../skill-use/request.json"
```

第一种可粘贴到聊天窗口；后两种由你的API客户端读取。API模型ID由调用者明确提供，脚本不猜测最新模型，不发送网络请求、不收费、不执行生成的命令。导出只包含技能及当前阶段引用，不自动附加软件源码、业务表或身份材料。

可用阶段为`direction`（选题）、`design`（设计）、`implementation`（实现）、`materials`（撰写）、`audit`（审核）、`revision`（修改）。导出文件应放在技能目录之外，例如使用`--out "你的项目目录/prompt.md"`，以保护技能资源；同名输出默认不覆盖。普通网页聊天只能根据你实际提供的内容工作，完整本机开发与材料生成仍需具备相应工具的宿主。

## 独立生成材料

本技能自带`materials.py`生成申请信息TXT、源码TXT/DOCX、手册Markdown/DOCX、行映射和哈希，并从实际Word回读核验。示例输入在`assets/material-input.example.json`；具体字段、图片与运行方法见[独立工具指南](references/materials-toolkit.md)。示例不是已实现软件，不能原样作为正式材料。

通常让代理整理输入即可。希望手动运行时，先准备：有序源码文件清单JSON、对应的源码快照、真实登记数据、完整手册章节及图片，再生成到一个不存在的新目录：

```text
python scripts/source_evidence.py snapshot --project <项目根目录> --selection <有序相对路径数组JSON> --out <新源码快照JSON>
python scripts/materials.py build --input <实际材料JSON> --out <新输出目录>
python scripts/materials.py audit --bundle <输出目录>
```

源码清单形如`["app.py", "src/engine.py"]`，路径和顺序必须对应当前项目的实际程序；不要照抄示例文件名。材料输入结构见[JSON示例](assets/material-input.example.json)，填入真实内容后移除`example_only`标记；只删除标记而不替换事实不算完成材料准备。图片路径相对材料输入JSON所在目录，或使用明确绝对路径。

从零创建记录目录可另外运行`python scripts/init_project.py --parent <父目录> --name <新目录名>`。它只建立空项目与记录，不生成产品；已有项目无需重复初始化。

Windows有已安装Word及可运行的PowerShell 7时，可分别处理两份文件的副本：

```text
pwsh -NoProfile -File scripts/render_word.ps1 -Document <代码DOCX> -OutDir <新的代码排版目录>
pwsh -NoProfile -File scripts/render_word.ps1 -Document <手册DOCX> -OutDir <新的手册排版目录>
python scripts/materials.py audit --bundle <原生成目录> --code-docx <刷新后的代码DOCX> --manual-docx <刷新后的手册DOCX> --report <新审查JSON>
python scripts/pdf_evidence.py --pdf <实际PDF> --out <新的全页预览目录>
python scripts/export_deposit.py --pdf <完整核验后的PDF> --out <新的交存PDF> --mode auto
```

代码与手册分别渲染、审查。不要为运行脚本绕过系统策略；其他环境的排版方法见[工具指南](references/materials-toolkit.md)。连续取页前先核验完整文件；`auto`在全文超过60页时提取连续前30和后30页，较短文件保留全部。这里的命令不会自动完成业务真实性判断或全页目视检查。

Word写入使用普通库python-docx，PDF工具使用pypdf、pypdfium2和Pillow，依赖在`requirements.txt`。安装需遵守实际环境权限，建议虚拟环境。无需OfficeCLI，不扫描其他skill。Windows自带`render_word.ps1`用已安装Word在副本刷新目录、实测分页并导出PDF；其他系统可用已安装LibreOffice。`pdf_evidence.py`渲染全部页，`export_deposit.py`从完整实测PDF连续取前后页。

源码文字与图片静态校验不替代真实分页、业务真实性和当前受理规则核查。默认保留待补录、缺图源和未验证项，不凭估算写实际页数。操作手册正文由代理基于真实项目撰写，工具只负责编排、生成和可自动检查部分，不把一键模板当完整成品。

跨平台重新核对设备、软件环境、主体、日期和工具版本；不将历史电脑配置或旧项目权属套用到新软件。材料内部检查通过不等于登记批准。

## 常见情况

| 情况 | 怎样处理 |
| --- | --- |
| 找不到software-skill | 核对安装目标及客户端技能加载器，开启新会话；WorkBuddy云端面板与本地目录分别检查 |
| 提示已有安装目录 | 先确认目标，使用相同安装参数加`--replace`，或先`--dry-run`看计划 |
| Python缺少docx/PDF模块 | 在授权环境安装`requirements.txt`，并使用该环境的解释器运行；无需安装其他skill |
| 提示源码发生漂移 | 核实程序变更、复验受影响功能，再生成新的快照与材料；不改哈希绕过检查 |
| 提示输出目录已存在 | 改用新的修订目录，保留旧版；不要为重试删除整个项目 |
| static_ok为true，仍显示submission_ready为false | 静态检查只覆盖可自动核验部分；继续完成登记事实、真实运行、受理要求、实际分页及全页检查 |
| 没有Word或LibreOffice | 继续设计、实现和可编辑草稿；真实分页保持待核，按权限准备排版工具 |
| 想按自己的参考文件修改 | 提供实际Word及修改范围，要求先提取格式；只迁移写法与版式，软件事实以当前项目为准 |

## 验证和打包

```text
python scripts/test_source_evidence.py
python -m unittest discover -s tests -v
python scripts/build_packages.py --out dist
```

构建产生标准技能ZIP、WorkBuddy元数据适配ZIP及SHA256清单；归档只含技能资源，不含本机项目源码、登记证件或日志。标准ZIP与WorkBuddy ZIP都以一个`software-skill/`目录为顶层。请上传对应技能ZIP，而不是直接把GitHub整库源码ZIP当成WorkBuddy安装包。

入口：[SKILL.md](SKILL.md)。引用采用相对路径；安装、快照和阶段导出仅需标准库，文档工具依赖见上述说明。验证覆盖范围见[测试说明](tests/README.md)。历史来源与第三方工具许可边界见[NOTICE.md](NOTICE.md)。
