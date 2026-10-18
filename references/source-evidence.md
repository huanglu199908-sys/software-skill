# 源码证据脚本用法与边界

`scripts/source_evidence.py` 使用 Python 3.10+ 标准库，只读取明确选择的项目文件，生成本地 JSON 并比较字符。它不读取整个硬盘、不调用网络、不修改项目、不直接读写 DOCX 包。

## 1. 冻结实际选材

准备有序 JSON 数组，例如 `["app.py", "package/engine.py"]`。该数组是人工/模型已研判的完整文件列表，不是本脚本自动发现或批准的列表。源文件按严格指定编码读取；默认 UTF-8（兼容BOM），其他编码显式提供 `--encoding`。

```text
python scripts/source_evidence.py snapshot --project PROJECT --selection selection.json --out snapshot.json
python scripts/source_evidence.py check --manifest snapshot.json --report drift-check.json
```

命令中的 PROJECT 等替换为真实路径；脚本路径相对于本技能。实际使用中文或含空格路径时按所在 shell 规则引用，不把示例占位符原样执行。

快照记录文件顺序、SHA256、物理行、非空行和全部正文行。只规范化 CRLF/CR 换行；保留缩进、空白行、注释、说明字符串和字符串内部空格。源文件原始字节哈希还可发现换行或编码变化。

快照仅统计**所选文件**。它不等于整个登记软件程序量，除非所选范围经确认就是整个范围。不要把材料选材统计直接填到全软件源程序量字段。

相对路径必须位于项目内，拒绝越界、重复文件和二进制NUL；未知源码扩展名不受限制。默认每文件10MiB保护上限，可用 `--max-file-bytes` 调整。输出文件已存在时拒绝覆盖，使用修订号产生新证据。

## 2. 从最终文档独立回读并映射

用 OfficeCLI 读取最终 DOCX 内容，按实际导出顺序和生成时保存的行映射，建立下列 JSON。不能把快照中的原文复制过去再称已经检查了 Word。

```json
{
  "snapshot_sha256": "快照文件的实际SHA256",
  "document": {"path": "最终DOCX的绝对路径", "sha256": "该DOCX的实际SHA256"},
  "scope": "all-selected-source-lines",
  "tab_expansion": 0,
  "rows": [
    {"file": "app.py", "line": 1, "segments": ["print(", "'hello')"]},
    {"file": "app.py", "line": 2, "segments": [""]}
  ]
}
```

`segments` 是同一源码行在文档中实际出现的连续片段，已根据明确规则去除显示行号，但保留一切源码字符。不要随意 trim、删除空白或使用宽泛正则去掉数字。制表符确实转换为空格时指定实际 `tab_expansion`，默认0表示原样比较。

```text
python scripts/source_evidence.py compare --manifest snapshot.json --rendered actual-doc-lines.json --report source-comparison.json
```

脚本检查当前源码仍与快照一致，快照/文档哈希绑定一致，映射行数量、顺序和逐字符内容一致。新文档若保留空行，应映射空行；旧材料省略空行且无法无歧义回溯时，不得伪造空行是从Word提取的。记录检查限制并做补充检查，或经授权重新生成可追溯材料。

**当前 compare 只支持全部所选源码。** 前后30页模式可用 snapshot/check 冻结来源与检测漂移，但需另外核验分页范围、连续性和实际选定行映射，不能拿本脚本的完整比较结果冒充取页合规。

退出码：0检查通过，1发现差异，2输入/文件/编码不支持。报告不输出源行正文，避免把源码内容或业务信息带进终端。快照本身包含完整源码，应作为项目本地证据，不默认加入公开分享包。

## 3. 脚本不能证明什么

它不能证明导出 JSON 确实来自 DOCX、不能识别代码业务语义、不能验证用户确认、图文排版或法律要求。调用者须保留真实 OfficeCLI 回读命令和原始输出，以支撑映射来源；正文检查后仍须检查实际页数、有效行数与全页预览。

源码变了时冻结新修订并复验受影响的软件/材料，不直接改旧快照哈希掩盖漂移。项目移位但内容相同时可对 check/compare 提供新的 `--project`。
