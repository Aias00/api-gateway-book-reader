"""Check packaged content, navigation targets and required scope."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from collections import Counter
import zipfile, xml.etree.ElementTree as ET, posixpath, re, json
root=Path(__file__).resolve().parent.parent
p=root/'dist/API网关设计与实现.epub'
with zipfile.ZipFile(p) as z:
    assert z.infolist()[0].filename=='mimetype'
    assert z.infolist()[0].compress_type==zipfile.ZIP_STORED
    assert z.read('mimetype')==b'application/epub+zip'
    names=set(z.namelist()); docs={}
    for name in names:
        if name.endswith(('.xhtml','.opf','.xml','.svg','.ncx')):
            docs[name]=ET.fromstring(z.read(name))
    for name,doc in docs.items():
        for el in doc.iter():
            for attr in ('href','src'):
                ref=el.get(attr)
                if not ref: continue
                u=urlsplit(ref)
                if u.scheme or u.netloc:continue
                target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(u.path))) if u.path else name
                assert target in names,(name,ref)
                if u.fragment and target in docs:
                    assert any(e.get('id')==unquote(u.fragment) for e in docs[target].iter()),(name,ref)
    ns={'h':'http://www.w3.org/1999/xhtml'}
    headings=[h.text or '' for doc in docs.values() for h in doc.findall('.//h:h1',ns)]
    chapters=[h for h in headings if re.match(r'第\s*\d+\s*章',h)]
    assert len(chapters)==20,chapters
    content=''.join(''.join(d.itertext()) for d in docs.values())
    for term in ('ShenYu','Spring Cloud Gateway','Kong','APISIX','Higress','Envoy Gateway','限流','熔断','动态配置','插件链','路由匹配'):
        assert term in content,term
    nav=[n for n in names if n.endswith('nav.xhtml')]
    assert len(nav)==1
    imgs=[n for n in names if n.endswith('.svg')]
    assert len(imgs)==4,imgs
report={'epub':p.name,'chapters':len(chapters),'svg_assets':len(imgs),'xml_and_internal_links':'passed','scope_terms':'passed','bytes':p.stat().st_size,'manuscript_characters':len((root/'dist/完整书稿.md').read_text())}
(root/'research/content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
