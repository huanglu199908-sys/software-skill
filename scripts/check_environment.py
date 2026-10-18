"""Report local skill/runtime capabilities without installing or changing anything."""
import argparse
import json
import importlib.metadata
from pathlib import Path
import shutil
import sys

def inspect(project=None):
    project = Path(project).resolve() if project else Path.cwd()
    packages = {}
    for name in ['python-docx','pypdf','pypdfium2','Pillow']:
        try: packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name]=None
    word=False
    if sys.platform=='win32':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'Word.Application\CLSID'): word=True
        except OSError: pass
    return {"python_version": sys.version.split()[0], "python_supported": sys.version_info >= (3, 10),
            "project_directory_exists": project.is_dir(), "packages":packages,
            "word_com_registered":word,"libreoffice":shutil.which('soffice'),
            "execution_policy": "Capabilities of the actual agent host must still be verified; no installations performed",
            "docx_generation_ready": bool(packages['python-docx']),
            "pagination_readiness": "Word registration or executable discovery is not a successful render; run the actual engine on a copy"}

def main():
    p = argparse.ArgumentParser(description=__doc__);p.add_argument("--project");a=p.parse_args()
    print(json.dumps(inspect(a.project), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
