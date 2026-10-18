"""Independent local DOCX/TXT materials builder and source round-trip auditor.

Input is explicit project data, not instructions or executable code. No networking,
other skills, OfficeCLI, API keys, or global installs. Requires python-docx.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import unicodedata

from source_evidence import check, digest, read_json, write_new

def dependencies():
    try:
        from docx import Document
        return Document
    except ImportError as exc:
        raise RuntimeError('Install requirements.txt in an authorized Python environment; python-docx is missing') from exc

def text(value):
    if value is None: return '待补录'
    if isinstance(value, list): return '、'.join(text(x) for x in value) if value else '待补录'
    return str(value) if str(value).strip() else '待补录'

FIELD_LABELS = {
    'name':'软件全称', 'version':'登记版本', 'abbreviation':'软件简称', 'category':'软件分类',
    'developers':'开发者', 'completion_date':'开发完成日期', 'development_mode':'开发方式',
    'publication_status':'发表状态', 'origin':'原创或修改', 'acquisition':'权利取得方式',
    'rights_scope':'权利范围', 'development_environment':'开发环境', 'runtime_environment':'运行环境',
    'source_total_lines':'整个登记范围的程序量及口径', 'purpose':'开发目的', 'field':'适用领域',
    'functions':'主要功能', 'technical_features':'技术特点'
}

def missing_fields(app):
    required = ['name','version','category','completion_date','development_mode','publication_status',
                'origin','acquisition','rights_scope','development_environment','runtime_environment',
                'source_total_lines','purpose','field','functions','technical_features']
    absent = [k for k in required if text(app.get(k)) == '待补录' or '待补' in text(app.get(k))]
    owners = app.get('owners', [])
    if not owners: absent.append('owners')
    for i, owner in enumerate(owners):
        for k in ['name','type','country','province','city','id_type','id_number']:
            if not owner.get(k) or '待补' in str(owner[k]): absent.append(f'owners[{i}].{k}')
    return absent

def safe_title(value):
    if not isinstance(value,str) or not value.strip() or len(value)>120 or re.search(r'[\\/<>:"|?*\x00-\x1f]', value) or value.endswith((' ','.')):
        raise ValueError('Invalid software name for local artifact filenames')
    return value

def checked_string(value):
    if not isinstance(value, str): raise ValueError('Expected text string')
    if any(ord(c)<32 and c not in '\t\n\r' for c in value):
        raise ValueError('Text contains unsupported XML control characters; preserve original and review representation')
    return value

def wrap_line(line, columns):
    checked_string(line)
    pieces, current, width = [], '', 0
    for c in line:
        size = 4-(width%4) if c=='\t' else (2 if unicodedata.east_asian_width(c) in {'W','F'} else 1)
        if current and width+size>columns:
            pieces.append(current); current=''; width=0
            size=4 if c=='\t' else size
        current+=c; width+=size
    pieces.append(current)
    return pieces

def font(run, name='SimSun', size=12, bold=False):
    from docx.shared import Pt, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    run.font.name=name; run.font.size=Pt(size); run.font.bold=bold
    run.font.color.rgb=RGBColor(0,0,0)
    fonts=run._element.get_or_add_rPr().find(qn('w:rFonts'))
    if fonts is None: fonts=OxmlElement('w:rFonts'); run._element.get_or_add_rPr().append(fonts)
    fonts.set(qn('w:eastAsia'),'SimSun' if name=='Consolas' else name)
    return run

def field(paragraph, instruction, cache='待刷新'):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    for kind, val in [('begin',None), ('instruction',instruction), ('separate',None), ('cache',cache), ('end',None)]:
        run=paragraph.add_run()
        if kind=='instruction':
            node=OxmlElement('w:instrText'); node.set(qn('xml:space'),'preserve'); node.text=' '+val+' '
        elif kind=='cache':
            node=OxmlElement('w:t'); node.text=val
        else:
            node=OxmlElement('w:fldChar'); node.set(qn('w:fldCharType'),kind)
        run._r.append(node); font(run,size=9)

def setup(app, code=False):
    from docx.shared import Cm, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
    doc=dependencies()(); section=doc.sections[0]
    section.page_width=Cm(21); section.page_height=Cm(29.7)
    section.top_margin=section.bottom_margin=Cm(.9 if code else 2.4)
    section.left_margin=section.right_margin=Cm(1 if code else 2.5)
    section.header_distance=section.footer_distance=Cm(.4 if code else 1)
    normal=doc.styles['Normal']; normal.font.name='SimSun'; normal.font.size=Pt(9 if code else 12)
    normal.paragraph_format.space_after=Pt(0 if code else 4)
    normal.paragraph_format.line_spacing=Pt(13.4 if code else 18)
    normal.paragraph_format.widow_control=False
    for level in [1,2]:
        style=doc.styles[f'Heading {level}']; style.font.name='SimHei'; style.font.size=Pt(15 if level==1 else 13)
        style.paragraph_format.keep_with_next=True
    header=section.header.paragraphs[0]
    header.style=doc.styles['Normal']
    header.paragraph_format.tab_stops.clear_all()
    header.paragraph_format.line_spacing=Pt(12)
    header.paragraph_format.tab_stops.add_tab_stop(section.page_width-section.left_margin-section.right_margin,WD_TAB_ALIGNMENT.RIGHT)
    font(header.add_run(app['name']+' '+app['version']),size=9)
    font(header.add_run('\t第 '),size=9); field(header,'PAGE'); font(header.add_run(' 页'),size=9)
    footer=section.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    font(footer.add_run('著作权人：'+'、'.join(o['name'] for o in app['owners'])),size=9)
    return doc

def paragraph(doc, value, style=None, size=12):
    from docx.shared import Pt
    p=doc.add_paragraph(style=style); font(p.add_run(checked_string(value)),name='SimHei' if style else 'SimSun',size=size)
    if style is None: p.paragraph_format.first_line_indent=Pt(24)
    return p

def application_txt(app):
    rows=['软件著作权申请表填报信息（供官网填报，不代替官网申请表）','']
    for k,label in FIELD_LABELS.items(): rows.append(label+'：'+('无' if k=='abbreviation' and not app.get(k) else text(app.get(k))))
    for i, owner in enumerate(app['owners'],1):
        rows.append(f'\n著作权人{i}')
        for k in ['name','type','country','province','city','id_type','id_number']: rows.append(k+'：'+text(owner.get(k)))
    rows+=['','代码页数：待实际排版核实','操作手册页数：待实际排版核实','待补录字段：'+', '.join(missing_fields(app))]
    return '\n'.join(rows)+'\n'

def make_code(app, snapshot, out, columns):
    from docx.shared import Pt
    doc=setup(app,True); mapping=[]; plain=[]; rowno=0
    for item in snapshot['files']:
        for lineno,line in enumerate(item['lines'],1):
            pieces=wrap_line(line,columns); plain.append(line)
            mapping.append({'file':item['path'],'line':lineno,'start':rowno,'segments':len(pieces)})
            for piece in pieces:
                p=doc.add_paragraph()
                if rowno and rowno%50==0: p.paragraph_format.page_break_before=True
                p.paragraph_format.keep_together=True
                p.paragraph_format.space_before=Pt(0); p.paragraph_format.space_after=Pt(0)
                font(p.add_run(f'{rowno%50+1:02d} '),'Consolas',9)
                font(p.add_run(piece),'Consolas',9)
                rowno+=1
    doc.save(out/'代码材料_全部.docx')
    (out/'代码材料_全部.txt').write_text('\n'.join(plain)+'\n',encoding='utf-8')
    return mapping,rowno

def make_manual(app, manual, base, out):
    from docx.shared import Cm, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    doc=setup(app); expected=[]; images=[]
    for index,(title,size) in enumerate([(app['name'],30),('操 作 手 册',36),(app['version'],14),
                       ('开发完成日期：'+text(app.get('completion_date')),14),
                       ('著作权人：'+'、'.join(o['name'] for o in app['owners']),14)]):
        p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;font(p.add_run(title),'SimHei',size)
        p.paragraph_format.line_spacing=1.2
        p.paragraph_format.space_before=Pt(90 if index==0 else 0)
        p.paragraph_format.space_after=Pt(18)
    doc.add_page_break(); p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;font(p.add_run('目  录'),size=18)
    field(doc.add_paragraph(),'TOC \\o "1-2" \\h \\z \\u','目录页码待实际排版引擎刷新')
    doc.add_page_break(); markdown=['# '+app['name']+' 操作手册', '', app['version'], '']; figure=0
    chapters=manual.get('chapters',[])
    if not chapters: raise ValueError('Manual needs actual chapters')
    for chapter in chapters:
        title=checked_string(chapter['title']); paragraph(doc,title,'Heading 1',15);expected.append(title);markdown+=['## '+title,'']
        for block in chapter.get('blocks',[]):
            kind=block['type']
            if kind=='paragraph':
                value=checked_string(block['text']);paragraph(doc,value);expected.append(value);markdown += [value,'']
            elif kind=='table':
                headers=block['headers']; rows=block['rows']
                if not headers or any(len(r)!=len(headers) for r in rows): raise ValueError('Invalid table width')
                table=doc.add_table(rows=1,cols=len(headers));table.style='Table Grid'
                for cell,value in zip(table.rows[0].cells,headers): cell.text=checked_string(value);expected.append(value)
                for row in rows:
                    for cell,value in zip(table.add_row().cells,row): cell.text=checked_string(value);expected.append(value)
                for row in table.rows:
                    for cell in row.cells:
                        for para in cell.paragraphs:
                            for run in para.runs: font(run)
                markdown+=[' | '.join(headers),' | '.join('---' for _ in headers)]+[' | '.join(r) for r in rows]+['']
            elif kind in {'screenshot','diagram'}:
                path=Path(block['path']);path=(base/path).resolve() if not path.is_absolute() else path.resolve()
                if not path.is_file() or path.suffix.lower() not in {'.png','.jpg','.jpeg'}: raise ValueError('Figure must be an existing PNG or JPEG')
                figure+=1; target=out/'图片'/f'{figure:02d}{path.suffix.lower()}';target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target)
                p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
                p.paragraph_format.line_spacing=1.0
                width=float(block.get('width_cm',15))
                if not 1<=width<=16: raise ValueError('Figure width must fit the text column')
                shape=p.add_run().add_picture(str(target),width=Cm(width))
                if shape.height>Cm(20):
                    ratio=Cm(20)/shape.height;shape.width=int(shape.width*ratio);shape.height=Cm(20)
                caption=f'图{figure} '+checked_string(block['caption']);p=paragraph(doc,caption,size=10.5);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_together=True
                p.paragraph_format.first_line_indent=Cm(0)
                images.append({'path':target.relative_to(out).as_posix(),'sha256':digest(target.read_bytes()),'type':kind,
                               'evidence':block.get('evidence'), 'caption':caption})
                expected.append(caption);markdown += ['!['+caption+']('+target.relative_to(out).as_posix()+')',caption,'']
            else: raise ValueError('Unknown manual block type')
    doc.save(out/'操作手册.docx'); (out/'操作手册.md').write_text('\n'.join(markdown),encoding='utf-8')
    return expected,images

def build(input_path, output, columns=90):
    if not 30<=columns<=160: raise ValueError('Wrap columns must be between 30 and 160')
    dependencies(); input_path=Path(input_path).resolve(strict=True); data=read_json(input_path)
    if data.get('schema')!=1: raise ValueError('Unsupported material input schema')
    if data.get('example_only'): raise ValueError('Replace example facts with actual project data and remove the example_only marker')
    app=data['application'];safe_title(app['name']);checked_string(app['version'])
    if not app.get('owners') or any(not o.get('name') for o in app['owners']): raise ValueError('Explicit copyright owner names required')
    base=input_path.parent; source_path=Path(data['source_snapshot']);source_path=(base/source_path).resolve() if not source_path.is_absolute() else source_path.resolve()
    drift=check(source_path)
    if not drift['ok']: raise ValueError('Source drift detected; verify software and freeze again')
    snapshot=read_json(source_path);out=Path(output).resolve()
    if not any(f['lines'] for f in snapshot['files']): raise ValueError('Source snapshot contains no program text')
    if out.exists(): raise FileExistsError('Output must be a new directory; preserve previous revisions')
    # Refuse outputs containing or inside the input project sources.
    project=Path(snapshot['project_root']).resolve()
    if project.is_relative_to(out): raise ValueError('Output must not contain the source project')
    for item in snapshot['files']:
        for line in item['lines']: checked_string(line)
    out.mkdir(parents=True);(out/'证据').mkdir()
    try:
        shutil.copyfile(source_path,out/'证据/源码快照.json')
        write_new(out/'证据/登记信息.json',app)
        (out/'申请表信息.txt').write_text(application_txt(app),encoding='utf-8')
        mapping,rows=make_code(app,snapshot,out,columns)
        expected,images=make_manual(app,data['manual'],base,out)
        info={'schema':1,'generator':'software-skill/2.0.0','application_name':app['name'],'version':app['version'],
              'input_sha256':digest(input_path.read_bytes()),'source_snapshot_sha256':digest(source_path.read_bytes()),
              'source_mapping':mapping,'display_rows':rows,'logical_code_pages':(rows+49)//50,
              'physical_source_lines':sum(f['physical_lines'] for f in snapshot['files']),
              'nonblank_source_lines':sum(f['nonblank_lines'] for f in snapshot['files']),
              'manual_expected_text':expected,'images':images,'missing_fields':missing_fields(app),
              'pagination':'NOT_VERIFIED','files':[]}
        for p in sorted(out.rglob('*')):
            if p.is_file(): info['files'].append({'path':p.relative_to(out).as_posix(),'sha256':digest(p.read_bytes())})
        write_new(out/'生成记录.json',info)
        report=audit(out);write_new(out/'静态审查.json',report)
        return {'output':str(out),'static_ok':report['static_ok'],'pagination':'NOT_VERIFIED','submission_ready':False,
                'display_rows':rows,'logical_code_pages':info['logical_code_pages'],'missing_field_count':len(info['missing_fields'])}
    except Exception:
        # Preserve partial artifacts and error marker for diagnosis; do not delete user paths.
        (out/'生成未完成.txt').write_text('生成中断。此目录不是有效正式交付，请修复输入后生成到新的目录。\n',encoding='utf-8')
        raise

def all_text(doc):
    from docx.text.paragraph import Paragraph
    from docx.table import Table
    from docx.oxml.ns import qn
    values=[]
    for child in doc.element.body:
        if child.tag==qn('w:p'): values.append(Paragraph(child,doc).text)
        elif child.tag==qn('w:tbl'):
            for row in Table(child,doc).rows:
                for cell in row.cells: values += [p.text for p in cell.paragraphs]
    return values

def audit(bundle, code_docx=None, manual_docx=None):
    Document=dependencies();root=Path(bundle).resolve(strict=True);info=read_json(root/'生成记录.json')
    issues=[]; reviews=[]
    if info.get('schema')!=1: raise ValueError('Unsupported build manifest')
    for item in info['files']:
        p=(root/item['path']).resolve()
        if not p.is_relative_to(root): raise ValueError('Manifest path leaves bundle')
        if not p.is_file() or digest(p.read_bytes())!=item['sha256']: issues.append({'kind':'artifact_hash_mismatch','path':item['path']})
    source=root/'证据/源码快照.json';drift=check(source)
    if not drift['ok']: issues.append({'kind':'source_drift','count':len(drift['issues'])})
    if digest(source.read_bytes())!=info['source_snapshot_sha256']: issues.append({'kind':'snapshot_binding_mismatch'})
    snapshot=read_json(source);expected=[(f['path'],i,line) for f in snapshot['files'] for i,line in enumerate(f['lines'],1)]
    codepath=Path(code_docx).resolve(strict=True) if code_docx else root/'代码材料_全部.docx'
    code=Document(codepath); extracted=[];blank=0
    for i,p in enumerate(code.paragraphs):
        prefix=f'{i%50+1:02d} '
        if not p.text.startswith(prefix): issues.append({'kind':'code_numbering_mismatch','row':i+1})
        value=p.text[len(prefix):]; extracted.append(value)
        if not value.strip(): blank+=1
    mapping=info['source_mapping']
    if len(extracted)!=info['display_rows'] or len(expected)!=len(mapping): issues.append({'kind':'code_row_count_mismatch'})
    cursor=0
    for (file,line,value),m in zip(expected,mapping):
        if (file,line,cursor)!=(m['file'],m['line'],m['start']) or m['segments']<1: issues.append({'kind':'source_mapping_invalid','line':line})
        actual=''.join(extracted[m['start']:m['start']+m['segments']])
        if actual!=value: issues.append({'kind':'source_roundtrip_mismatch','file':file,'line':line})
        cursor+=m['segments']
    if cursor!=len(extracted): issues.append({'kind':'unmapped_code_rows'})
    if blank: reviews.append({'kind':'blank_code_rows_not_effective_lines','count':blank})
    if info['display_rows']>len(expected): reviews.append({'kind':'display_wraps_not_additional_source_lines'})
    manualpath=Path(manual_docx).resolve(strict=True) if manual_docx else root/'操作手册.docx'
    manual=Document(manualpath);values=all_text(manual);joined='\n'.join(values)
    if app_name := info.get('application_name'):
        if app_name not in values or info['version'] not in values: issues.append({'kind':'manual_cover_identity_mismatch'})
    position=0
    for index,value in enumerate(info['manual_expected_text']):
        try: position=values.index(value,position)+1
        except ValueError: issues.append({'kind':'manual_text_missing_or_changed','block':index})
    if re.search(r'附录|相关文档|TOC_ENTRY',joined): issues.append({'kind':'appendix_or_placeholder_review_required'})
    if len(manual.inline_shapes)!=len(info['images']): issues.append({'kind':'manual_image_count_mismatch'})
    for i,(shape,item) in enumerate(zip(manual.inline_shapes,info['images'])):
        rel=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
        if digest(manual.part.related_parts[rel].blob)!=item['sha256']: issues.append({'kind':'embedded_image_mismatch','figure':i+1})
        if not item.get('evidence'): reviews.append({'kind':'image_provenance_missing','figure':i+1})
    app=read_json(root/'证据/登记信息.json')
    for doc,kind in [(code,'code'),(manual,'manual')]:
        header='\n'.join(p.text for s in doc.sections for p in s.header.paragraphs)
        footer='\n'.join(p.text for s in doc.sections for p in s.footer.paragraphs)
        if app['name'] not in header or app['version'] not in header: issues.append({'kind':'header_identity_mismatch','document':kind})
        if any(o['name'] not in footer for o in app['owners']): issues.append({'kind':'footer_owners_mismatch','document':kind})
    reviews += [{'kind':'registration_fields_pending','fields':missing_fields(app)},
                {'kind':'actual_pagination_and_toc_NOT_VERIFIED'},
                {'kind':'real_screenshot_and_business_semantics_require_runtime_evidence'},
                {'kind':'ownership_and_current_acceptance_require_human_confirmation'}]
    return {'static_ok':not issues,'issues':issues,'review_required':reviews,'submission_ready':False,
            'code_docx_sha256':digest(codepath.read_bytes()),'manual_docx_sha256':digest(manualpath.read_bytes()),
            'roundtrip_lines_checked':len(expected),'limits':'Static checks only; not legal approval or final pagination verification'}

def main():
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='command',required=True)
    b=subs.add_parser('build');b.add_argument('--input',required=True);b.add_argument('--out',required=True);b.add_argument('--wrap-columns',type=int,default=90)
    a=subs.add_parser('audit');a.add_argument('--bundle',required=True);a.add_argument('--code-docx');a.add_argument('--manual-docx');a.add_argument('--report')
    args=p.parse_args()
    try:
        r=build(args.input,args.out,args.wrap_columns) if args.command=='build' else audit(args.bundle,args.code_docx,args.manual_docx)
        if getattr(args,'report',None): write_new(args.report,r)
        print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r.get('static_ok') else 1
    except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:
        print(json.dumps({'ok':False,'error':type(exc).__name__,'message':'Inspect local input schema, paths, snapshot drift and installed requirements; partial output is not final.'}));return 2

if __name__=='__main__': sys.exit(main())
