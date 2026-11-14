"""Replay the frozen engineering candidate into a separate directory. KiCad Python+wx required."""
from pathlib import Path
import argparse,json,subprocess,sys,shutil,xml.etree.ElementTree as E
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True);ap.add_argument('--kicad-cli',default='kicad-cli');args=ap.parse_args();src=Path(__file__).resolve().parent;distribution=src.parent;out=Path(args.output_dir).resolve();assert out!=distribution,'Choose a separate output directory';subprocess.run([sys.executable,str(src/'generate_native.py'),str(src/'design.json'),'--output-dir',str(out)],check=True)
cli=args.kicad_cli;stem='SimpleROV001_control';subprocess.run([cli,'sch','export','netlist','--format','kicadxml','-o',str(out/'source/netlist.xml'),str(out/(stem+'.kicad_sch'))],check=True)
import wx,pcbnew as p
app=wx.App(False);b=p.LoadBoard(str(out/(stem+'.kicad_pcb')));ds=b.GetDesignSettings();ds.m_MinClearance=p.FromMM(.127);ds.m_TrackMinWidth=p.FromMM(.1);ds.m_CopperEdgeClearance=p.FromMM(.25);ds.m_NetSettings.GetDefaultNetclass().SetClearance(p.FromMM(.127));b.SynchronizeNetsAndNetClasses(False);assert p.ImportSpecctraSES(b,str(src/'route_completed.ses'));ff={f.GetReference():f for f in b.GetFootprints()};cfg=json.loads((src/'design.json').read_text())
for d in cfg['parts']:
 f=ff[d['ref']];f.SetPosition(p.VECTOR2I(*(p.FromMM(v) for v in d['xy'])));f.SetOrientationDegrees(d['angle'])
for n in E.parse(out/'source/netlist.xml').findall('.//nets/net'):
 name=n.get('name');name=name if name.startswith('/') else name.replace('/','{slash}');net=b.FindNet(name)
 if not net:net=p.NETINFO_ITEM(b,name);b.Add(net)
 for node in n.findall('node'):
  for pad in ff[node.get('ref')].Pads():
   if pad.GetNumber()==node.get('pin'):pad.SetNet(net)
pt=p.VECTOR2I(p.FromMM(22.5),p.FromMM(16.4))
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  if abs(p.ToMM(t.GetPosition().x)-22.5)<.001 and abs(p.ToMM(t.GetPosition().y)-16.4)<.001:t.SetPosition(pt)
 else:
  for get,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
   a=get()
   if abs(p.ToMM(a.x)-22.5)<.001 and abs(p.ToMM(a.y)-16.4)<.001:setter(pt)
for g in list(b.GetDrawings()):
 if isinstance(g,p.PCB_TEXT):b.Delete(g)
for d in json.loads((src/'silkscreen.json').read_text()):
 t=p.PCB_TEXT(b);t.SetText(d['text']);t.SetLayer(p.F_SilkS if d['layer']=='top' else p.B_SilkS);t.SetMirrored(d['layer']=='bottom');t.SetPosition(p.VECTOR2I(*(p.FromMM(v) for v in d['xy'])));t.SetTextAngle(p.EDA_ANGLE(d['angle_deg'],p.DEGREES_T));t.SetTextSize(p.VECTOR2I(p.FromMM(d['size_mm']),p.FromMM(d['size_mm'])));t.SetTextThickness(p.FromMM(d['thickness_mm']));b.Add(t)
for z in list(b.Zones()):b.Delete(z)
for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:
 z=p.ZONE(b);z.SetLayer(l);z.SetNet(b.FindNet('/GND'));z.SetLocalClearance(p.FromMM(.51));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.15));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);poly=z.Outline();poly.NewOutline()
 for x,y in [(.3,.3),(79.7,.3),(79.7,31.7),(.3,31.7)]:poly.Append(p.FromMM(x),p.FromMM(y))
 b.Add(z)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/(stem+'.kicad_pcb')),b)
shutil.copy2(distribution/(stem+'.kicad_pro'),out/(stem+'.kicad_pro'))
for kind,extension in [('pcb','pcb'),('sch','sch')]:
 cmd=[cli,kind,'drc' if kind=='pcb' else 'erc','--format','json','-o',str(out/(kind+'_checks.json')),str(out/(stem+'.kicad_'+extension))]
 if kind=='pcb':cmd.insert(3,'--schematic-parity')
 subprocess.run(cmd,check=True)
 dr=json.loads((out/(kind+'_checks.json')).read_text());viol=dr.get('violations',[]);viol+=sum([x.get('violations',[]) for x in dr.get('sheets',[])],[])
 assert not viol and not dr.get('unconnected_items',[]) and not dr.get('schematic_parity',[]),(kind,'check failed; inspect report')
print('Rebuilt frozen candidate: ERC0, DRC0, unconnected0, schematic parity0. Hardware bench qualification remains open.')
