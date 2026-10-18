"""Create an empty project record, never claim that scaffolding is software."""
import argparse
import json
from pathlib import Path
import re

def initialize(parent, name):
    base = Path(parent).expanduser().resolve(strict=True)
    if (not name or name in {'.', '..'} or re.search(r'[\\/<>:"|?*\x00-\x1f]', name)
            or name.endswith((' ', '.')) or re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', name)):
        raise ValueError('Use a single valid new directory name')
    target = base / name
    target.mkdir()  # Never merge with an existing project.
    for folder in ['流程记录', '设计文档', 'src', 'tests', '软件著作权申请资料/草稿',
                   '软件著作权申请资料/截图原始', '软件著作权申请资料/审查记录']:
        (target / folder).mkdir(parents=True, exist_ok=True)
    state = {'schema': 1, 'stage': '需求与选题', 'software_name': None, 'registration_version': None,
             'confirmed_decisions': [], 'evidence': [], 'current_materials': [],
             'open_issues': ['尚未选题、设计、实现或生成申请资料'], 'next_action': '了解真实事务与数据来源'}
    (target / '流程记录/当前状态.json').write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for name, text in {
        '确认记录.md': '# 当前项目确认记录\n\n仅记录真实用户决定、来源和适用范围。暂无确认事实。\n',
        '功能证据对应表.md': '# 功能证据对应表\n\n| 业务承诺 | 实现文件 | 验收证据 | 页面/截图 | 手册章节 | 状态 |\n| --- | --- | --- | --- | --- | --- |\n',
        '问题与修订记录.md': '# 问题与修订\n\n| ID | 证据/原因 | 影响范围 | 修改 | 复验 | 状态 |\n| --- | --- | --- | --- | --- | --- |\n'
    }.items():
        (target / '流程记录' / name).write_text(text, encoding='utf-8')
    return {'project': str(target), 'stage': state['stage'], 'software_implemented': False}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent', required=True); p.add_argument('--name', required=True); a=p.parse_args()
    try: print(json.dumps(initialize(a.parent, a.name), ensure_ascii=False))
    except (OSError, ValueError) as e: p.exit(1, f'Project creation stopped: {e}\n')

if __name__ == '__main__': main()
