"""Build a complete, no-JavaScript-readable static book for GitHub Pages."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import quote
import subprocess, re, shutil
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'site'; SITE.mkdir(exist_ok=True)
source=ROOT/'dist/完整书稿.md'
if not source.exists():
    raise SystemExit('Run python3 tools/build.py first')
fragment=subprocess.run(['pandoc',str(source),'--to=html5','--section-divs'],capture_output=True,text=True,check=True).stdout
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,value):self.parts.append(value)
chapters=[]
for match in re.finditer(r'<section id="([^"]+)"\s+class="level1">\s*<h1[^>]*>(.*?)</h1>',fragment,re.S):
    title=Text();title.feed(match[2]);chapters.append((match[1],''.join(title.parts)))
assert len(chapters)==27,len(chapters)
toc='\n'.join(f'<a href="#{quote(id)}">{escape(title)}</a>' for id,title in chapters)
template=(ROOT/'web/index.html').read_text()
assert '<!-- BOOK_CONTENT -->' in template and '<!-- BOOK_TOC -->' in template
(SITE/'index.html').write_text(template.replace('<!-- BOOK_TOC -->',toc).replace('<!-- BOOK_CONTENT -->',fragment))
for name in ('reader.css','reader.js'):shutil.copy2(ROOT/'web'/name,SITE/name)
shutil.copytree(ROOT/'assets',SITE/'assets',dirs_exist_ok=True)
shutil.copy2(ROOT/'dist/API网关设计与实现.epub',SITE/'book.epub')
for old in ('book-data.js','API网关设计与实现.epub'):
    (SITE/old).unlink(missing_ok=True)
(SITE/'.nojekyll').touch()
print(f'Built {len(chapters)} sections with full embedded text in {SITE}')
