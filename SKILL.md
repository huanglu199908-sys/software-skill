---
name: software-skill
description: >-
  独立完成中文软著项目：真实需求选题、方案与算法设计、软件实现验证、申请信息及真实源码和操作手册撰写、
  Word/TXT生成、审查和修改润色。也用于现有项目续做、材料编制与格式修订，不依赖或转交其他skill。
metadata:
  short-description: 从零选题到成品、软著撰写、审核与修订的独立技能
  version: "2.0.0"
---

# 软件开发与软著全流程

本技能自身提供流程规则、写作规范、登记字段规范、源码证据工具、Word/TXT生成及审查工具。执行本流程不要求查找、安装、读取或调用其他skill，也不从其他skill目录导入代码。常规程序库、浏览器、Word或LibreOffice属于执行工具，其使用遵守实际环境权限和当前用户授权。[工具指南](references/materials-toolkit.md)说明依赖与运行。

Codex使用`$software-skill`，DeepSeek Harness按其加载器使用`/software-skill`，WorkBuddy选择本技能。普通聊天/API使用阶段提示词导出，不能仅凭提示词取得本地执行能力。见[平台适配](references/platform-compatibility.md)。

目标是有真实用途、可运行、可验证的软件与材料。算法贡献、文档内部检查和登记受理获批分别判断，不保证登记批准，也不把算法工程改进当作专利新颖性证明。

## 从当前进度开始

先读项目实际文件、最新验证与用户已确认事项，定位最早尚未完成的阶段。收到“继续”时恢复现有任务；只改材料时不重新开发软件。按需读取引用，不一次载入全部资料。

| 阶段 | 行动及完成证据 |
| --- | --- |
| 0 需求与环境 | 核对用户、输入输出、数据来源、电脑资源与约束；`check_environment.py`只读检查；可用`init_project.py`创建独立目录与状态 |
| 1 选题 | [选题与设计](references/direction-design.md)：比较业务价值、数据可得性、算法空间和验收成本；已选方向直接沿用 |
| 2 方案设计 | 明确业务闭环、数据模型、模块、界面、算法不变量、基线与改进、反例和回退、验收；见[阶段交付](references/stage-deliverables.md) |
| 3 方案实行 | [开发验证](references/implementation-verification.md)：实现真实输入到输出的闭环，先正确性和失败路径，再公平比较算法；保留运行证据 |
| 4 软著撰写 | [独立材料编写](references/materials-integration.md)、[登记字段](references/registration-fields.md)、[默认写法](references/reference-format.md)：按实际项目生成申请信息、源码和手册Word/TXT |
| 5 审核 | [审查与修订](references/audit-revision.md)、[规则依据](references/registration-rules.md)：分别审事实、源码、操作、截图、实际分页及图文，列出失败与未验证 |
| 6 修改润色 | [修订与润色](references/revision-polishing.md)：先事实与完整性，再业务文字与版式；回读、刷新目录、全页复验直到本次问题闭环或明确缺口 |

开始时简短说明阶段、证据和下一步。用[阶段交付](references/stage-deliverables.md)判断完成，不用文件名、空表格或勾选代替真实成果。

## 全程规则

- 先说明谁反复遇到什么事务、输入来自哪里、输出如何使用。名称变化不等于独立新软件。可用合成数据验证机制，但不能据此宣称真实业务收益。
- 开发可以新增有用途的程序；材料只能提取真实落盘、可追溯的程序。不为页数制造重复模块、空壳函数、无关测试或第三方库代码。
- 用户偏好可测算法改进，设计合理基线、独立正确性参照与实测指标；这不是所有登记项目的法定门槛。性能无改善时改机制或结论，不改实验事实。
- 当前项目登记数据是名称、版本、主体与日期的单一口径。旧项目的硬件、人员、协议和截图不能自动套用，开发者与著作权人分开记录。
- 区分全登记范围程序量、选材物理行、非空行、展示行与实际页数。保留缩进、字符串空白及尾部符号，冻结源码、行映射与实际DOCX回读绑定哈希；见[源码证据](references/source-evidence.md)。
- 真实界面来自实际运行的软件及对应输入、版本；原型、解释图和测试图片不能冒充截图。按[截图规范](references/screenshots.md)记录来源与章节映射。
- DOCX存在、XML可解析、逻辑50行分组不证明真实分页合格。刷新字段，用排版引擎输出PDF并全页检查，再同步页数。缺引擎就保留“真实分页待核”。

## 默认交付格式

沿用用户指定的台账参考写法，参数见[format-profile.json](references/format-profile.json)。手册为独立封面、实际页码目录、概述、说明、特点、环境、业务流程与模块图、真实操作章节、典型流程、问答及术语表；默认无附录或设计测试文件索引。正文连续讲解业务操作，不机械套字段标题。

代码默认9磅Consolas、中文宋体、页内1—50编号，无生成的文件路径标记，边界在支撑映射保存。源码忠实优先，不能为了50行删改字符串、用空行填充或把折行当成新增代码量。这是用户样式偏好，与登记规则分层核对；新参考优先，实际读取后迁移格式，不复制旧软件事实。

## 自带工具

路径相对于本技能；执行前查看对应工具`--help`。

```text
python scripts/check_environment.py --project <项目>
python scripts/init_project.py --parent <存放目录> --name <新目录名>
python scripts/source_evidence.py snapshot --project <项目> --selection <有序文件JSON> --out <新快照JSON>
python scripts/materials.py build --input <材料输入JSON> --out <不存在的新输出目录>
python scripts/materials.py audit --bundle <生成目录>
```

`materials.py`自主生成申请表信息TXT、代码TXT/DOCX、手册Markdown/DOCX及映射、哈希和审查JSON。申请信息不是官网申请表，不伪造签章或身份证明。默认交付可编辑材料，字段、截图及分页缺失时明确待核。

Windows有Word时用`render_word.ps1`在副本上刷新目录并输出PDF；其他环境按[工具指南](references/materials-toolkit.md)使用LibreOffice。`pdf_evidence.py`输出全部页预览、文本与哈希；`export_deposit.py`从完整实测PDF连续取交存页。依赖在`requirements.txt`，没有其他skill依赖。缺少运行工具时继续独立可做的工作，不伪报已生成、截图或测试。

## 确认、恢复与交付

在`流程记录/`记录阶段、事实来源、确认范围、有效文件及哈希、问题与下一步，见[状态与证据](references/state-evidence.md)。方向取舍、新权属/日期等事实及冲突由用户决定；已授权实现、测试和修订自主完成，不固定重复多轮审批。具体草稿未产生前不声称用户已审阅，已有明确的一并生成授权应复用。

修订前备份精确文件。事实或功能变化复查相关实现、截图与材料；仅文字排版修改不重跑无关算法。最终提供实际项目、启动方式、主要验证、唯一当前正式文件、修订结果及待补录/未验证事项。使用普通第三方程序库保留许可与来源，不能声称第三方技术为原创。

用户只要求某阶段就完成该阶段和必要检查。不自动提交登记、付费、发送消息、部署公网或扩大外部发布范围。需要复用历史项目经验时按需阅读[案例复盘](references/case-lessons.md)，不将案例事实写成新项目默认值。
