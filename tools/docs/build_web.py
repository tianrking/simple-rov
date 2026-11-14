"""Generate assembly Markdown and local HTML reading pages from project sources."""
from pathlib import Path
import re,posixpath
import markdown
from content import PAGES
R=Path(__file__).resolve().parents[2]
lines=['# SimpleROV-4 V5 详细组装说明','','V5-01 · 工程试装版。 [PDF](assembly.pdf) · [装配验收](acceptance.md) · [实机路线](build-plan.md)','']
for page in PAGES:
    lines+=['## '+page['title'],'',page['subtitle'],'']
    for b in page['blocks']:
        if b[0]=='p':lines +=[b[1],'']
        elif b[0]=='note':lines +=['> '+b[1],'']
        elif b[0]=='image':lines+=['!['+b[2]+']('+posixpath.relpath(b[1],'docs')+')','',b[2],'']
        elif b[0]=='table':
            lines+=['|'+'|'.join(map(str,b[1]))+'|','|'+'|'.join(['---']*len(b[1]))+'|']
            lines+=['|'+'|'.join(map(str,row))+'|' for row in b[2]];lines+=['']
lines+=['## 原厂资料','','[压力舱装配指南](https://bluerobotics.com/learn/watertight-enclosure-wte-assembly-new/) · [真空验漏指南](https://bluerobotics.com/learn/using-the-vacuum-test-plug/)','']
(R/'docs/assembly.md').write_text('\n'.join(lines))
css='body{font-family:system-ui,sans-serif;max-width:1050px;margin:36px auto;padding:0 24px;color:#173d46;line-height:1.8;background:#f5f9fa}main{background:#fff;padding:30px;border-radius:12px}h1,h2{line-height:1.4}h2{border-top:2px solid #e0ecee;padding-top:22px;margin-top:36px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #cbdade;padding:8px;text-align:left}th{background:#e8f1f3}pre{overflow:auto;padding:18px;background:#173d46;color:#effbff;border-radius:8px}img,video{display:block;max-width:100%;max-height:700px;margin:auto}blockquote{background:#fff0da;padding:10px 16px;border-left:4px solid #df8b31}a{color:#006980} @media print{body,main{margin:0;padding:0}h2{break-before:page}nav{display:none}}'
for source in [R/'README.md',*sorted((R/'docs').glob('*.md'))]:
    target=R/'docs/index.html' if source==R/'README.md' else source.with_suffix('.html')
    text=source.read_text()
    if source==R/'README.md':
        def rebase(m):
            url=m.group(2)
            if not url.startswith(('http:','https:','#','mailto:')):url='../'+url
            return '['+m.group(1)+']('+url+')'
        text=re.sub(r'\[([^\]]*)\]\(([^)]+)\)',rebase,text)
    for md in (R/'docs').glob('*.md'):
        text=text.replace(md.name,md.with_suffix('.html').name)
    body=markdown.markdown(text,extensions=['tables','fenced_code'])
    target.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SimpleROV工程资料</title><style>'+css+'</style><main><nav><a href="index.html">工程入口</a> · <a href="assembly.html">装配</a> · <a href="simulation.html">仿真</a> · <a href="build-plan.html">实机</a></nav>'+body+'</main></html>')
print('Generated assembly Markdown and HTML reading pages')
