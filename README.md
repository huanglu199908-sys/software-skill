# software-skill

从有实际意义的软件方向出发，完成算法设计、软件实现与验证，再生成和审查中文软件著作权申请材料。

由原 `software-copyright-workflow` 更名，当前版本 **1.2.0**。保留已确定的台账参考样式：手册独立封面、实测页码目录、总体流程与模块图、真实页面说明，默认无附录；代码采用9磅字体、页内1—50编号。参数见 [format-profile.json](references/format-profile.json)。这是可调整的交付样式，不是登记机构唯一格式。

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

默认分别安装到`~/.agents/skills/software-skill`、`~/.dsh/skills/software-skill`、`<项目>/.codebuddy/skills/software-skill`。Codex已有其他实际生效的技能根目录时，用`--skills-dir`明确指定；避免同名技能装在多个发现目录。脚本遇到已有同名目录会停止；`--replace`会先备份精确目标再替换，`--dry-run`仅显示操作计划。它不修改其他客户端配置、不安装上游或运行时、不读取API密钥。

WorkBuddy也可在技能页面选择“添加技能→上传技能”，导入下面构建出的`software-skill-workbuddy.zip`。这只是安装本地技能包，不是将技能提交到公共市场。

## DeepSeek聊天与API

```text
python scripts/export_prompt.py --stage direction --task "为行政办公提出三个有实际用途的软件方向" --out prompt.md
python scripts/export_prompt.py --stage audit --task "检查当前项目材料" --format messages --out messages.json
python scripts/export_prompt.py --stage implementation --task "按已确认设计实现" --format request --model "你实际可用的模型ID" --out request.json
```

第一种可粘贴到聊天窗口；后两种由你的API客户端读取。API模型ID由调用者明确提供，脚本不猜测最新模型，不发送网络请求、不收费、不执行生成的命令。导出只包含技能及当前阶段引用，不自动附加软件源码、业务表或身份材料。

## 材料阶段依赖

正式Word/TXT生成使用 [Fokkyp/SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) 提供的`software-copyright-materials`，以及该技能要求的OfficeCLI版本。本文不捆绑或修改其代码。缺少依赖时仍可推进方向、设计、开发与Markdown草稿；正式Word阶段如实报告能力缺口，按用户授权安装后继续。

运行`python scripts/check_environment.py`可只读定位已安装的材料技能和OfficeCLI；这也允许其他宿主使用本机已有依赖，而不把依赖路径写死为Codex目录。版本是否符合、是否有执行权限，仍按实际技能与宿主核查。

跨平台重新核对设备、软件环境、主体、日期和工具版本；不将历史电脑配置或旧项目权属套用到新软件。材料内部检查通过不等于登记批准。

## 验证和打包

```text
python scripts/test_source_evidence.py
python -m unittest discover -s tests -v
python scripts/build_packages.py --out dist
```

构建产生标准技能ZIP、WorkBuddy元数据适配ZIP及SHA256清单；归档只含技能资源，不含本机项目源码、登记证件或日志。标准ZIP与WorkBuddy ZIP都以一个`software-skill/`目录为顶层。请上传对应技能ZIP，而不是直接把GitHub整库源码ZIP当成WorkBuddy安装包。

入口：[SKILL.md](SKILL.md)。技能中的引用采用相对路径，Python辅助脚本仅依赖标准库。仓库维护与本地验证范围见[测试说明](tests/README.md)。
