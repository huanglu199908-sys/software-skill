# 登记事实与填报信息

`材料输入.json`的`application`保存当前事实口径，来源与决定放`流程记录/确认记录.md`。申请信息TXT用于官网填写，不制造官网表单、申请号、签字、印章或证明。

| 字段 | 填写与核验 |
| --- | --- |
| name / version | 软件全称和登记版本，统一正文、文件名、页眉与界面；内部版本建立映射 |
| owners | 当前全部著作权人：name、type、country、province、city、id_type、id_number；用户提供或待补录 |
| developers | 实际开发者；未提供时不自动从权利人推定 |
| completion_date | 实际开发完成日期，不是文档生成日期或旧项目日期 |
| development_mode | 单独/合作/委托等实际关系；合同写三方共有不能填写单位单独所有 |
| publication_status | 实际发表情况及必要时间地点；仓库可访问性不自动代替法律发表判断 |
| origin / acquisition / rights_scope | 原创或修改、取得方式与权利范围，有许可/转让/继承时核对应证明 |
| category / abbreviation | 实际软件类别，无简称可空，不能虚构 |
| development_environment / runtime_environment | 实测或明确目标设备、OS、开发工具和运行依赖，分别说明，不自动写入旧电脑 |
| source_total_lines | 整个登记范围的程序量及统计口径，不等于选材或页数乘50 |
| purpose / field / functions / technical_features | 实际用途、领域、已实现功能和技术特点；官网字数限制临填报再核实 |

缺失值用空值或明确待补录；可生成编辑稿但不能称资料齐备。来源冲突先写具体差异，集中询问需要决定的字段。旧项目协议不自动适用于新软件。按申请情况收集身份、合同/任务书、原软件许可或承继转让证明，不替用户制造。

完整证件号只进入用户要求的本地申请信息文件，不进技能包、GitHub、截图演示或公共审查日志。自动工具只报告缺失字段路径及数量，不在诊断中回显证件内容。
