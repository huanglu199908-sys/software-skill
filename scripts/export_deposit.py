"""Export contiguous front/back pages from an already paginated complete PDF."""
import argparse
import hashlib
import json
from pathlib import Path

def export(source, output, mode='auto'):
    from pypdf import PdfReader, PdfWriter
    source=Path(source).resolve(strict=True);output=Path(output).resolve()
    if output.exists() or output==source or output.with_suffix(output.suffix+'.pages.json').exists():
        raise FileExistsError('Use new output filenames')
    if mode not in {'auto','all','front-back'}: raise ValueError('Unknown deposit mode')
    reader=PdfReader(str(source));total=len(reader.pages)
    if not total: raise ValueError('Empty PDF')
    selected=list(range(total)) if mode=='all' or total<=60 else list(range(30))+list(range(total-30,total))
    writer=PdfWriter()
    for i in selected:writer.add_page(reader.pages[i])
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb') as stream:writer.write(stream)
    report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_actual_pages':total,
            'source_pages_1based':[i+1 for i in selected],'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'mode':'all' if len(selected)==total else 'continuous-front30-back30','acceptance_status':'requires current filing rules and prior whole-document audit'}
    output.with_suffix(output.suffix+'.pages.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf',required=True);p.add_argument('--out',required=True);p.add_argument('--mode',choices=['auto','all','front-back'],default='auto');a=p.parse_args()
    print(json.dumps(export(a.pdf,a.out,a.mode),ensure_ascii=False))

if __name__=='__main__':main()
