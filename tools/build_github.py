"""Generate GitHub-rendered chapters from the same complete book as the EPUB."""
from pathlib import Path
import json, subprocess, re
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'chapters'
OUT.mkdir(exist_ok=True)
source = ROOT / 'dist/完整书稿.md'
if not source.exists():
    raise SystemExit('Run python3 tools/build.py first')
ast = json.loads(subprocess.run(['pandoc', str(source), '--from=markdown-implicit_figures', '-t', 'json'],capture_output=True,text=True,check=True).stdout)
sections=[]
for block in ast['blocks']:
    if block['t'] == 'Header' and block['c'][0] == 1:
        sections.append([])
    if sections:
        sections[-1].append(block)
def stringify(inlines):
    text=[]
    for node in inlines:
        if node['t'] in ('Str', 'Code'): text.append(node['c'] if node['t']=='Str' else node['c'][1])
        elif node['t'] in ('Space','SoftBreak','LineBreak'):text.append(' ')
        elif node['t'] in ('Emph','Strong'):text.append(stringify(node['c']))
    return ''.join(text)
def rewrite_images(node):
    if isinstance(node,dict):
        if node.get('t')=='Image' and node['c'][2][0].startswith('assets/'):
            node['c'][2][0]='../'+node['c'][2][0]
        for value in node.values(): rewrite_images(value)
    elif isinstance(node,list):
        for value in node: rewrite_images(value)
entries=[]
for section in sections:
    title=stringify(section[0]['c'][2])
    number=re.match(r'第\s*(\d+)\s*章',title)
    appendix=re.match(r'附录\s*([A-E])',title)
    filename=f'ch{int(number[1]):02d}.md' if number else f'appendix-{appendix[1].lower()}.md' if appendix else '00-preface.md' if title.startswith('前言') else '99-afterword.md'
    entries.append((title,filename,section))
assert len(entries)==27
assert len([e for e in entries if re.match(r'ch\d',e[1])])==20
assert len({e[1] for e in entries})==27
for i,(title,filename,blocks) in enumerate(entries):
    rewrite_images(blocks)
    doc={**ast,'meta':{},'blocks':blocks}
    result=subprocess.run(['pandoc','-f','json','-t','gfm','--wrap=none'],input=json.dumps(doc),capture_output=True,text=True,check=True).stdout
    prev=f'[← {entries[i-1][0]}]({entries[i-1][1]})' if i else ''
    nxt=f'[{entries[i+1][0]} →]({entries[i+1][1]})' if i+1<len(entries) else ''
    nav=' · '.join(x for x in (prev,'[全书目录](../README.md#全书目录)',nxt) if x)
    (OUT/filename).write_text(nav+'\n\n---\n\n'+result+'\n---\n\n'+nav+'\n')
# Stable markers preserve hand-written README instructions.
readme=ROOT/'README.md'
text=readme.read_text()
start='<!-- BOOK_TOC_START -->'; end='<!-- BOOK_TOC_END -->'
toc=start+'\n## 全书目录\n\n'+''.join(f'- [{title}](chapters/{filename})\n' for title,filename,_ in entries)+end
if start in text:
    text=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:toc,text,flags=re.S)
else:
    title,rest=text.split('\n',1)
    text=title+'\n\n在 GitHub 中点击下方章节即可直接阅读，无需下载或启动服务。\n\n[开始阅读](chapters/00-preface.md) · [下载 EPUB](dist/API网关设计与实现.epub)\n\n'+toc+'\n'+rest
readme.write_text(text)
# GitHub Pages serves an Actions artifact; all paths remain relative.
(ROOT/'site/.nojekyll').touch()
print(f'Generated {len(entries)} GitHub Markdown chapters and README contents')
