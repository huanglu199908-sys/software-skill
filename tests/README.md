# 验证范围

`test_portability.py`使用隔离的临时目录验证真实安装、备份、归档和提示词导出行为，不触碰真实用户配置，不请求API，也不创建远程仓库。

源码证据工具的独立测试仍为`scripts/test_source_evidence.py`。运行：

`test_materials.py`在临时目录中实际生成DOCX/TXT并从Word包回读，验证源码中的空格、空行、Unicode和折行、源码漂移阻断、篡改检出、图片缺失、目录保护、身份页眉、表格内容、连续PDF页范围与空项目初始化。它不查找其他skill，示例输入不允许直接生成项目。

```text
python scripts/test_source_evidence.py
python -m unittest discover -s tests -v
```

结构与客户端官方文档适配不等于在DeepSeek、WorkBuddy或Codex每个版本中完成了完整软件开发。测试记录如实区分本地格式验证和真实平台端到端验证。

v2.0本机还用独立样例完成Word实际字段刷新、代码3页和手册3页PDF输出、6页全部渲染检查及刷新副本源码回读。图片明确为测试夹具，不能作为任何登记软件的真实截图；样例保留待补录和空白行待核，用于证明工具能够发现缺口，不宣称样例可提交。此记录不等于未来项目已审核，其他客户端完整会话和LibreOffice引擎未实测。
