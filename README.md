# software-skill

从有实际意义的软件方向出发，完成算法设计、软件实现与验证，再生成和审查中文软件著作权申请材料。

当前版本 **2.0.0**，是独立技能：从0了解需求 → 选题 → 方案设计 → 实现与验证 → 软著撰写 → 审核 → 修改润色。规则、写作指南、源码提取、Word/TXT生成和审查脚本均在本仓库内，不再要求安装或调用其他skill。

保留台账参考样式：独立封面、实际页码目录、流程与模块图、真实页面说明、默认无附录；代码9磅、页内1—50编号。参数见 [format-profile.json](references/format-profile.json)。这是用户交付偏好，不是法定唯一模板。阶段完成条件见[阶段交付](references/stage-deliverables.md)。

## 调用与兼容

| 平台 | 接入方式 | 调用 |
| --- | --- | --- |
| Codex | 原生Agent Skills目录、`agents/openai.yaml` | `$software-skill` |
| DeepSeek Harness | 原生SKILL.md目录；启用registry、filesystem、tool-skill插件 | `/software-skill` 或自然语言指定 |
| WorkBuddy / CodeBuddy | 项目`.codebuddy/skills/`；另提供带WorkBuddy元数据的ZIP | 选择技能或“使用software-skill” |
| DeepSeek网页聊天 / 纯API | 按阶段导出并加载提示词/消息JSON | 以所提供指令工作；本地执行须另外接工具 |

本仓库提供包结构与加载验证，不承诺任意客户端版本、模型配置或权限环境下都能完成本机开发。纯聊天不能仅凭提示词获得文件、浏览器或Word执行能力。具体步骤和官方依据见[平台兼容说明](references/platform-compatibility.md)。

## 安装

需要Python 3.10+。先取得本仓库；私有仓库下载或克隆需要你的GitHub账号访问权。使用当前环境能运行的Python解释器；Windows也可将`python`换成`py -3`。

```text
python scripts/install.py --platform codex --scope user
python scripts/install.py --platform deepseek --scope user
python scripts/install.py --platform workbuddy --scope project --project "你的软件项目目录"
```

默认分别安装到`~/.agents/skills/software-skill`、`~/.dsh/skills/software-skill`、`<项目>/.codebuddy/skills/software-skill`。Codex实际使用其他技能根时用`--skills-dir`明确指定，避免重复同名安装。已有目录须加`--replace`，脚本先精确备份再替换；`--dry-run`无写入。不修改客户端配置、安装运行时或读取API密钥。

WorkBuddy也可在技能页面选择“添加技能→上传技能”，导入下面构建出的`software-skill-workbuddy.zip`。这只是安装本地技能包，不是将技能提交到公共市场。

## DeepSeek聊天与API

```text
python scripts/export_prompt.py --stage direction --task "为行政办公提出三个有实际用途的软件方向" --out prompt.md
python scripts/export_prompt.py --stage audit --task "检查当前项目材料" --format messages --out messages.json
python scripts/export_prompt.py --stage implementation --task "按已确认设计实现" --format request --model "你实际可用的模型ID" --out request.json
```

第一种可粘贴到聊天窗口；后两种由你的API客户端读取。API模型ID由调用者明确提供，脚本不猜测最新模型，不发送网络请求、不收费、不执行生成的命令。导出只包含技能及当前阶段引用，不自动附加软件源码、业务表或身份材料。

## 独立生成材料

本技能自带`materials.py`生成申请信息TXT、源码TXT/DOCX、手册Markdown/DOCX、行映射和哈希，并从实际Word回读核验。示例输入在`assets/material-input.example.json`；具体字段、图片与运行方法见[独立工具指南](references/materials-toolkit.md)。示例不是已实现软件，不能原样作为正式材料。

```text
python scripts/check_environment.py
python scripts/init_project.py --parent <父目录> --name <新项目目录名>
python scripts/materials.py build --input <实际材料JSON> --out <新输出目录>
python scripts/materials.py audit --bundle <输出目录>
```

Word写入使用普通库python-docx，PDF工具使用pypdf、pypdfium2和Pillow，依赖在`requirements.txt`。安装需遵守实际环境权限，建议虚拟环境。无需OfficeCLI，不扫描其他skill。Windows自带`render_word.ps1`用已安装Word在副本刷新目录、实测分页并导出PDF；其他系统可用已安装LibreOffice。`pdf_evidence.py`渲染全部页，`export_deposit.py`从完整实测PDF连续取前后页。

源码文字与图片静态校验不替代真实分页、业务真实性和当前受理规则核查。默认保留待补录、缺图源和未验证项，不凭估算写实际页数。操作手册正文由代理基于真实项目撰写，工具只负责编排、生成和可自动检查部分，不把一键模板当完整成品。

跨平台重新核对设备、软件环境、主体、日期和工具版本；不将历史电脑配置或旧项目权属套用到新软件。材料内部检查通过不等于登记批准。

## 验证和打包

```text
python scripts/test_source_evidence.py
python -m unittest discover -s tests -v
python scripts/build_packages.py --out dist
```

构建产生标准技能ZIP、WorkBuddy元数据适配ZIP及SHA256清单；归档只含技能资源，不含本机项目源码、登记证件或日志。标准ZIP与WorkBuddy ZIP都以一个`software-skill/`目录为顶层。请上传对应技能ZIP，而不是直接把GitHub整库源码ZIP当成WorkBuddy安装包。

入口：[SKILL.md](SKILL.md)。引用采用相对路径；安装、快照和阶段导出仅需标准库，文档工具依赖见上述说明。验证覆盖范围见[测试说明](tests/README.md)。历史来源与第三方工具许可边界见[NOTICE.md](NOTICE.md)。
