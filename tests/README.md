# 验证范围

`test_portability.py`使用隔离的临时目录验证真实安装、备份、归档和提示词导出行为，不触碰真实用户配置，不请求API，也不创建远程仓库。

源码证据工具的独立测试仍为`scripts/test_source_evidence.py`。运行：

```text
python scripts/test_source_evidence.py
python -m unittest discover -s tests -v
```

结构与客户端官方文档适配不等于在DeepSeek、WorkBuddy或Codex每个版本中完成了完整软件开发。测试记录如实区分本地格式验证和真实平台端到端验证。
