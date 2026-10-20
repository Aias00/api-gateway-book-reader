"""Audit GitHub chapter coverage, source fidelity and repository-local links."""
from pathlib import Path
import re, json, subprocess
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parent.parent
chapters=sorted((ROOT/'chapters').glob('*.md'))
assert len(chapters)==27
assert len(list((ROOT/'chapters').glob('ch[0-9][0-9].md')))==20
assert len(list((ROOT/'chapters').glob('appendix-*.md')))==5
links=0
for path in [ROOT/'README.md', *chapters]:
    text=path.read_text()
    # Exclude fenced code from link extraction.
    prose=re.sub(r'```.*?```','',text,flags=re.S)
    for target in re.findall(r'\]\(([^)]+)\)',prose):
        url=urlsplit(target)
        if url.scheme or url.netloc or not url.path:continue
        file=(path.parent/unquote(url.path)).resolve()
        assert file.is_file(),(path,target)
        if url.fragment:
            assert url.fragment=='全书目录' and '## 全书目录' in file.read_text(),(path,target)
        links+=1
    if path.parent.name=='chapters':
        assert text.count('[全书目录](../README.md#全书目录)')==2
        assert len(re.findall(r'^# ',prose,re.M))==1
# Ensure conversion preserves every paragraph and code block from the source.
def parsed(file,format):
    return json.loads(subprocess.run(['pandoc',str(file),'-f',format,'-t','json'],capture_output=True,text=True,check=True).stdout)
def payload(node):
    out=[]
    if isinstance(node,dict):
        if node.get('t')=='CodeBlock':out.append(('code',node['c'][1]))
        if node.get('t')=='Para':
            # GFM may render a source figure as a plain paragraph; compare other prose.
            inline=node['c']
            if not any(n.get('t')=='Image' for n in inline):
                out.append(('para',json.dumps(inline,sort_keys=True,ensure_ascii=False)))
        for value in node.values():out.extend(payload(value))
    elif isinstance(node,list):
        for value in node:out.extend(payload(value))
    return out
source=payload(parsed(ROOT/'dist/完整书稿.md','markdown-implicit_figures')['blocks'])
from collections import Counter
combined=Counter()
for file in chapters:combined.update(payload(parsed(file,'gfm')['blocks']))
missing=Counter(source)-combined
assert not missing, list(missing)[:3]
assert (ROOT/'.github/workflows/pages.yml').is_file()
assert (ROOT/'site/.nojekyll').is_file()
report={'sections':27,'body_chapters':20,'appendices':5,'local_links_verified':links,'source_paragraphs_and_code_blocks':len(source),'source_fidelity':'passed','github_navigation':'passed','pages_workflow':'present; live deployment requires a target repository'}
(ROOT/'research/github-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
