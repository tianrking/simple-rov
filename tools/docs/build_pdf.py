from pathlib import Path
import sys,re,json
sys.path.insert(0,str(Path(__file__).parent))
from content import PAGES
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
R=Path(__file__).resolve().parents[2];file=R/'docs/assembly.pdf'
import os
font=Path(os.environ.get('SROV_CJK_FONT','/System/Library/Fonts/STHeiti Light.ttc'))
if not font.is_file():font=Path('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
if not font.is_file():raise SystemExit('Set SROV_CJK_FONT to a TrueType CJK font (.ttf/.ttc). See docs/development.md.')
pdfmetrics.registerFont(TTFont('GuideCJK',str(font),subfontIndex=0))
pdfmetrics.registerFont(TTFont('GuideCJKBold',str(font),subfontIndex=0))
ink=colors.HexColor('#183d46');accent=colors.HexColor('#d57820');light=colors.HexColor('#e8f1f3')
styles={
 'title':ParagraphStyle('title',fontName='GuideCJKBold',fontSize=19,leading=25,textColor=ink,spaceAfter=6,wordWrap='CJK'),
 'subtitle':ParagraphStyle('subtitle',fontName='GuideCJK',fontSize=9,leading=14,textColor=colors.HexColor('#537079'),spaceAfter=13,wordWrap='CJK'),
 'p':ParagraphStyle('p',fontName='GuideCJK',fontSize=11,leading=17.5,textColor=ink,spaceAfter=9,wordWrap='CJK'),
 'note':ParagraphStyle('note',fontName='GuideCJK',fontSize=9.4,leading=14.5,textColor=colors.HexColor('#78431b'),backColor=colors.HexColor('#fff1dd'),borderPadding=8,spaceBefore=4,spaceAfter=11,wordWrap='CJK'),
 'caption':ParagraphStyle('caption',fontName='GuideCJK',fontSize=8.2,leading=12,textColor=colors.HexColor('#637981'),spaceAfter=10,wordWrap='CJK'),
 'cell':ParagraphStyle('cell',fontName='GuideCJK',fontSize=9.3,leading=13.6,textColor=ink,wordWrap='CJK'),
 'th':ParagraphStyle('th',fontName='GuideCJKBold',fontSize=9.4,leading=13.6,textColor=ink,wordWrap='CJK')}
def esc(t):return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
W,H=A4; usable=W-76
story=[];heights=[]
for page in PAGES:
 blocks=[Paragraph(esc(page['title']),styles['title']),Paragraph(esc(page['subtitle']),styles['subtitle'])]
 for b in page['blocks']:
  if b[0] in ['p','note']:blocks.append(Paragraph(esc(b[1]),styles[b[0]]))
  elif b[0]=='image':
   from PIL import Image as PI
   p=R/b[1];w,h=PI.open(p).size;scale=min(usable/w,b[3]/h);blocks+=[Image(str(p),width=w*scale,height=h*scale),Spacer(1,5),Paragraph(esc(b[2]),styles['caption'])]
  elif b[0]=='table':
   data=[[Paragraph(esc(x),styles['th']) for x in b[1]]]+[[Paragraph(esc(x),styles['cell']) for x in row] for row in b[2]]
   widths=[usable*x for x in b[3]] if b[3] else [usable/len(b[1])]*len(b[1]);t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),light),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f8f8')]),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#c9d8dc')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));blocks+=[t,Spacer(1,10)]
 ht=sum(x.wrap(usable,H)[1]+getattr(x,'spaceBefore',0)+getattr(x,'spaceAfter',0) for x in blocks);heights.append(round(ht,1));story.extend(blocks);story.append(PageBreak())
story.pop()
def chrome(c,doc):
 c.saveState();c.setFont('GuideCJK',8);c.setFillColor(ink);c.drawString(38,H-24,'SimpleROV  /  图文组装说明');c.setStrokeColor(accent);c.setLineWidth(1.4);c.line(38,H-31,W-38,H-31);c.setFillColor(colors.HexColor('#667e85'));c.drawString(38,22,'工程原型 · 未经实物可靠性与水密验证');c.drawRightString(W-38,22,f'{doc.page} / {len(PAGES)}');c.restoreState()
doc=SimpleDocTemplate(str(file),pagesize=A4,rightMargin=38,leftMargin=38,topMargin=45,bottomMargin=36,title='SimpleROV 图文组装说明',author='SimpleROV 项目文档')
doc.build(story,onFirstPage=chrome,onLaterPages=chrome)
reader=PdfReader(str(file));report={'pages':len(reader.pages),'expected_pages':len(PAGES),'content_height_estimates_pt':heights,'all_pages_text_nonempty':all(len(p.extract_text())>80 for p in reader.pages)};print(json.dumps(report,ensure_ascii=False,indent=2));assert len(reader.pages)==len(PAGES), 'Unexpected overflow pages';assert report['all_pages_text_nonempty'];(R/'validation/assembly_pdf.json').write_text(json.dumps(report,indent=2))
