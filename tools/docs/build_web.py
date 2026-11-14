"""Generate the English assembly guide and multilingual offline HTML entry points."""
from pathlib import Path
import posixpath,re
import markdown
from content import PAGES
R=Path(__file__).resolve().parents[2]
lines=['# SimpleROV illustrated assembly guide','','Standard assembly and optional accessories. [PDF](assembly.pdf) · [Acceptance](acceptance.md) · [Prototype plan](build-plan.md)','']
for page in PAGES:
    lines+=['## '+page['title'],'',page['subtitle'],'']
    for b in page['blocks']:
        if b[0]=='p':lines+=[b[1],'']
        elif b[0]=='note':lines+=['> '+b[1],'']
        elif b[0]=='image':lines+=['!['+b[2]+']('+posixpath.relpath(b[1],'docs')+')','',b[2],'']
        elif b[0]=='table':
            lines+=['|'+'|'.join(map(str,b[1]))+'|','|'+'|'.join(['---']*len(b[1]))+'|']
            lines+=['|'+'|'.join(map(str,row))+'|' for row in b[2]];lines+=['']
lines+=['## Supplier instructions','','[Enclosure assembly](https://bluerobotics.com/learn/watertight-enclosure-wte-assembly-new/) · [Vacuum leak testing](https://bluerobotics.com/learn/using-the-vacuum-test-plug/)','']
(R/'docs/assembly.md').write_text('\n'.join(lines))
css='''
:root{--ink:#183d46;--muted:#5d7480;--line:#dbe6e9;--accent:#176271;--orange:#ed8a24}
*{box-sizing:border-box}body{margin:0;background:#f3f7f8;color:var(--ink);font:16px/1.8 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{background:#fff;border-bottom:1px solid var(--line)}nav{max-width:1100px;margin:auto;padding:18px 28px;display:flex;gap:22px;align-items:center;flex-wrap:wrap}nav strong{margin-right:auto;letter-spacing:-.5px;font-size:22px}nav a{font-size:14px;text-decoration:none}
main{max-width:1100px;margin:32px auto 70px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:42px 48px;box-shadow:0 8px 35px #183d4608}
h1{font-size:42px;letter-spacing:-1.3px;line-height:1.2;margin-top:0}h2{font-size:26px;border-top:1px solid var(--line);padding-top:30px;margin-top:44px;line-height:1.35}h3{font-size:20px;margin-top:30px;line-height:1.4}p{margin:16px 0}a{color:var(--accent);text-underline-offset:3px}img,video{max-width:100%;height:auto;border-radius:8px}p>img{display:block;margin:22px auto}table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}th,td{border:1px solid var(--line);padding:12px 15px;text-align:left;vertical-align:top}th{background:#eaf2f4;font-weight:600}tr:nth-child(even){background:#fafcfc}td img{width:100%}pre{overflow:auto;background:#163843;color:#edf6f8;padding:22px;border-radius:10px;font-size:13px;line-height:1.7}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}p code,td code{background:#edf3f5;padding:2px 5px;border-radius:4px;font-size:.88em}blockquote{margin:20px 0;padding:1px 20px;background:#fff5e7;border-left:3px solid var(--orange)}details{border:1px solid var(--line);border-radius:10px;padding:12px 18px;margin:20px 0}summary{cursor:pointer}footer{color:var(--muted);font-size:12px;text-align:center;margin:35px auto}
@media(max-width:700px){main{margin:12px 8px;padding:24px 18px;border-radius:10px}h1{font-size:34px}h2{font-size:23px}table{font-size:12px}th,td{padding:8px}nav{gap:12px;padding:14px 20px}pre{font-size:11px}}
@media print{body,main{margin:0;padding:0;background:#fff;border:0;box-shadow:none}header,footer{display:none}h2{break-before:page}}
'''
entries={R/'README.md':R/'docs/index.html',R/'README.es.md':R/'docs/index.es.html',R/'README.zh-CN.md':R/'docs/index.zh-CN.html'}
entries.update({p:p.with_suffix('.html') for p in sorted((R/'docs').glob('*.md'))})
for source,target in entries.items():
    raw=source.read_text()
    def resolve(m):
        url=m.group(2)
        if url.startswith(('https:','http:','#','mailto:','data:')):return m.group(0)
        path,sep,fragment=url.partition('#');dest=(source.parent/path).resolve()
        if dest in entries:dest=entries[dest]
        return '['+m.group(1)+']('+posixpath.relpath(dest,target.parent)+(sep+fragment if sep else '')+')'
    raw=re.sub(r'\[([^\]]*)\]\(([^)]+)\)',resolve,raw)
    raw=raw.replace('<div align="center">','<div align="center" markdown="1">').replace('<details>','<details markdown="1">')
    body=markdown.markdown(raw,extensions=['tables','fenced_code','md_in_html'])
    lang='es' if source.name=='README.es.md' else ('zh-CN' if source.name=='README.zh-CN.md' else 'en')
    nav='<header><nav><strong>SimpleROV</strong><a href="index.html">Overview</a><a href="assembly.html">Assembly</a><a href="gallery.html">Gallery</a><a href="simulation.html">Simulation</a><a href="index.es.html">ES</a><a href="index.zh-CN.html">中文</a></nav></header>'
    target.write_text('<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SimpleROV | Project documentation</title><style>'+css+'</style></head><body>'+nav+'<main>'+body+'</main><footer>SimpleROV · Prototype documentation · Original content all rights reserved</footer></body></html>')
print('Generated English assembly guide and',len(entries),'HTML pages')
