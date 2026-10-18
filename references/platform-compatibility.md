# 平台兼容与调用

核对日期：2026-10-18。技能采用[Agent Skills规范](https://agentskills.io/specification)：目录名和`name`为`software-skill`，根目录包含UTF-8的`SKILL.md`，引用为相对路径。不要求Claude专有工具，也不依赖本机用户名或某个模型版本。

## Codex

安装完整技能目录到Codex实际扫描的技能根。当前[官方说明](https://developers.openai.com/codex/skills/)列出用户级`~/.agents/skills`和项目级`.agents/skills`；桌面已有技能可能使用配置或兼容目录，例如本机先前的`~/.codex/skills`。以当前客户端实际发现路径为准，使用安装器`--skills-dir`适配，不同时向多个Codex发现目录复制同名技能。

调用`$software-skill`或以自然语言指定；`agents/openai.yaml`提供可选的界面元数据，其余平台无需读取它。更名后若会话仍显示旧技能，开启新会话；若客户端尚未刷新再重启。不要为重命名修改其他技能或整个Codex配置。

## DeepSeek Harness

[官方filesystem技能提供方](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)支持`<项目>/.dsh/skills`、`<项目>/.agents/skills`、用户`~/.dsh/skills`和`~/.agents/skills`等目录；它只发现技能根下直接的`<name>/SKILL.md`，不递归搜索任意深度目录。

安装器的`deepseek`平台默认选择`.dsh/skills`。宿主还须有registry、filesystem provider和loader consumer；[官方tool-skill说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/tool-skill/README.md)列出的插件组合为：

```yaml
- name: '@deepseek-ai/dsh-skill'
- name: '@deepseek-ai/dsh-skill-filesystem'
- name: '@deepseek-ai/dsh-tool-skill'
```

按所用版本的插件配置结构合并这些条目，不直接把这一片段覆盖到真实配置。宿主启用后可通过`/software-skill`或模型的`skill`工具加载；仅复制文件但没有技能提供方和加载器，不算原生调用成功。不要擅自改变用户API密钥、模型或插件权限。

## WorkBuddy与CodeBuddy

WorkBuddy[项目说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)明确支持`<项目>/.codebuddy/skills/<name>/SKILL.md`；因此项目安装使用该路径，不猜测内部数据库或修改技能索引。`~/.codebuddy/skills`是[CodeBuddy用户级路径](https://www.codebuddy.ai/docs/zh/cli/skills)，WorkBuddy各端的个人技能面板以其上传导入流程为准。

对于WorkBuddy技能页面，用`software-skill-workbuddy.zip`，在“添加技能→上传技能”导入，然后在会话选择该技能。WorkBuddy端的包清单由构建脚本根据同一正文生成；依据[开放平台结构说明](https://open.workbuddy.cn/docs/skill)补入`description_zh`、`description_en`、`version`和`author`等字段。规范版不加入这些宿主专用字段，避免破坏Codex的清单校验。

Web端和客户端个人技能库可能独立；本机文件安装不等于云端技能面板已经导入。需要真实客户端的技能列表、加载结果和本地执行权限，才能进一步做端到端确认。

## DeepSeek普通聊天与API

模型与执行宿主是两件事。[DeepSeek Tool Calls文档](https://api-docs.deepseek.com/guides/tool_calls/)说明，函数调用需由应用执行工具并回传结果。纯API或普通网页聊天不会因仓库里有`SKILL.md`就自动读取本地文件。

`export_prompt.py`可按阶段导出本技能及必要引用，供聊天粘贴或API调用方加载。它只构造指令/消息/请求JSON，不调用网络、不读取密钥，不将指令提升为系统权限。若要完成真实开发、截图和Word生成，宿主必须另外接入相应本地工具、依赖与授权；不能把纯文本指导描述为已执行的软件交付。

## 能验证什么

进入材料阶段可先运行`python scripts/check_environment.py --project <项目目录>`；它会只读查找当前项目和用户级常见技能根中的`software-copyright-materials`及PATH中的OfficeCLI。依赖在自定义位置时加`--materials-dir`。即使依赖未进入宿主技能列表，也可根据返回路径读取真实SKILL.md及引用，按其确认和后端要求执行；不得把“找到了文件”称为已获得工具权限或正式Word生成成功。

本地测试覆盖清单名称、资源引用、两种ZIP布局、WorkBuddy必需字段、安装路径、已有目录保护、备份更新、提示词引用展开与源码证据工具。它们证明包和适配器可被相应格式加载，不证明远程模型质量、客户端所有版本或用户权限设置。真实平台会话未运行时应标为“加载格式已验证，端到端待该宿主确认”。
