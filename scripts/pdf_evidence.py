"""Extract every actual PDF page and render previews, without another skill."""
import argparse
import hashlib
import json
from pathlib import Path

def inspect_pdf(source, output, scale=1.25):
    from pypdf import PdfReader
    import pypdfium2 as pdfium
    if not .5<=scale<=3: raise ValueError('Preview scale must be between .5 and 3')
    source=Path(source).resolve(strict=True);out=Path(output).resolve()
    out.mkdir(parents=True,exist_ok=False)
    reader=PdfReader(str(source));render=pdfium.PdfDocument(str(source));pages=[]
    try:
        for i,page in enumerate(reader.pages):
            extracted=page.extract_text() or ''
            (out/f'page-{i+1:03d}.txt').write_text(extracted,encoding='utf-8')
            bitmap=render[i].render(scale=scale)
            try: bitmap.to_pil().save(out/f'page-{i+1:03d}.png')
            finally: bitmap.close()
            pages.append({'page':i+1,'text_characters':len(extracted),'nonempty_extracted_lines':sum(bool(x.strip()) for x in extracted.splitlines()),
                          'preview':f'page-{i+1:03d}.png','text':f'page-{i+1:03d}.txt'})
    finally: render.close()
    report={'pdf_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'actual_pages':len(pages),
            'pages':pages,'visual_review':'NOT_PERFORMED','limits':'Extracted text lines are not visual lines; inspect all previews, especially figures and layout.'}
    (out/'PDF证据.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'actual_pages':len(pages),'output':str(out),'visual_review':'NOT_PERFORMED'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf',required=True);p.add_argument('--out',required=True);p.add_argument('--scale',type=float,default=1.25);a=p.parse_args()
    print(json.dumps(inspect_pdf(a.pdf,a.out,a.scale),ensure_ascii=False))

if __name__=='__main__':main()
