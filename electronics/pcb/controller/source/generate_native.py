from pathlib import Path
import argparse,json,csv,shutil,importlib.util,re
import pcbnew as p
def layers(*values):
 result=p.LSET()
 for value in values:result.AddLayer(value)
 return result
parser=argparse.ArgumentParser();parser.add_argument('design');parser.add_argument('--output-dir',required=True);args=parser.parse_args()
cfg=json.loads(Path(args.design).read_text());root=Path(args.output_dir).resolve();distribution=Path(__file__).resolve().parents[1];assert root!=distribution,'Choose a separate output directory';root.mkdir(parents=True,exist_ok=True)
for folder in ['footprints','SimpleROV_HW.pretty','models','third_party']:shutil.copytree(distribution/folder,root/folder,dirs_exist_ok=True)
spec=importlib.util.spec_from_file_location('native_sch',str(Path(__file__).with_name('native_common_sch.py')));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
s.ROOT=root;s.LIB=root/'footprints';s.parts=cfg['parts'];s.POWER_FLAGS=cfg.get('supply_nets',s.POWER_FLAGS)
for d in s.parts:
 d.setdefault('uuid',s.UID());d.setdefault('angle',0);d.setdefault('side','top');d.setdefault('height',1);d.setdefault('url','');d.setdefault('mpn',d['value'])
sch_root=s.schematic(add_supply_markers=cfg.get('power_flags',True), paper=cfg.get('paper','A0'))
stem=cfg['stem']
if stem!='SimpleROV001_control':
 for fn in ['SimpleROV001_control.kicad_sch']:
  f=root/fn;text=f.read_text().replace('SimpleROV001_control',stem).replace('SimpleROV v0.0.1 control interfaces',cfg['title']);f.rename(root/(stem+'.kicad_sch'));(root/(stem+'.kicad_sch')).write_text(text)
b=p.BOARD();b.SetCopperLayerCount(cfg.get('layers',2));ds=b.GetDesignSettings();ds.SetBoardThickness(p.FromMM(cfg['thickness']));ds.SetAuxOrigin(p.VECTOR2I(0,p.FromMM(cfg['size'][1])))
ds.m_MinClearance=p.FromMM(.127);ds.m_TrackMinWidth=p.FromMM(.15);ds.m_ViasMinSize=p.FromMM(.6);ds.m_MinThroughDrill=p.FromMM(.3)
nets={}
for n in sorted({pin[2] for d in s.parts for pin in d['pins'].values() if pin[2]}):net=p.NETINFO_ITEM(b,'/'+n);b.Add(net);nets[n]=net
local=root/'SimpleROV_HW.pretty';local.mkdir(exist_ok=True)
for d in s.parts:
 lib,name=d['fp'].split(':')
 if 'custom' in d:
  f=p.FOOTPRINT(b);f.SetAttributes(p.FP_SMD if d.get('purchased',True) else p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
  for a in d['custom']:
   pad=p.PAD(f);pad.SetNumber(str(a['num']));pad.SetPosition(p.VECTOR2I(*(p.FromMM(v) for v in a.get('xy',[0,0]))));pad.SetSize(p.VECTOR2I(*(p.FromMM(v) for v in a['size'])));pad.SetShape(p.PAD_SHAPE_CIRCLE if a.get('drill') else p.PAD_SHAPE_RECT)
   if a.get('drill'):pad.SetAttribute(p.PAD_ATTRIB_PTH);pad.SetDrillSize(p.VECTOR2I(p.FromMM(a['drill']),p.FromMM(a['drill'])));pad.SetLayerSet(layers(p.F_Cu,p.B_Cu,p.In1_Cu,p.In2_Cu,p.F_Mask,p.B_Mask) if cfg.get("layers",2)==4 else layers(p.F_Cu,p.B_Cu,p.F_Mask,p.B_Mask))
   else:pad.SetAttribute(p.PAD_ATTRIB_SMD);pad.SetLayerSet(layers(*([p.B_Cu,p.B_Mask] if a.get('bottom') else ([p.F_Cu,p.F_Mask,p.F_Paste] if a.get('paste') else [p.F_Cu,p.F_Mask]))))
   f.Add(pad)
  if d.get('courtyard'):
   cw,ch=d['courtyard'];g=p.PCB_SHAPE(f);g.SetShape(p.SHAPE_T_RECT);g.SetStart(p.VECTOR2I(p.FromMM(-cw/2),p.FromMM(-ch/2)));g.SetEnd(p.VECTOR2I(p.FromMM(cw/2),p.FromMM(ch/2)));g.SetLayer(p.F_CrtYd);g.SetWidth(p.FromMM(.05));f.Add(g)
  f.SetFPID(p.LIB_ID(lib,name));p.PCB_IO_KICAD_SEXPR().FootprintSave(str(local),f)
 else:f=p.FootprintLoad(str(root/'SimpleROV_HW.pretty' if lib=='SimpleROV_HW' else s.LIB/(lib+'.pretty')),name)
 assert f,d['fp'];b.Add(f);f.SetReference(d['ref']);f.SetValue(d['value']);f.SetFPID(p.LIB_ID(lib,name));f.SetPath(p.KIID_PATH('/'+sch_root+'/'+d['uuid']));f.SetPosition(p.VECTOR2I(*(p.FromMM(v) for v in d['xy'])));f.SetOrientationDegrees(d['angle'])
 if d['side']=='bottom':f.Flip(f.GetPosition(),False)
 f.Reference().SetVisible(False);f.Value().SetVisible(False)
 if d.get('model'):
  f.Models().clear(); model=p.FP_3DMODEL();model.m_Filename='${KIPRJMOD}/models/'+d['model'];f.Add3DModel(model)
 for field,val in [('MPN',d['mpn']),('Manufacturer',d.get('manufacturer',''))]:
  a=p.PCB_FIELD(f,p.FIELD_T_USER,field);a.SetText(val);a.SetVisible(False);f.Add(a)
 f.GetField(p.FIELD_T_DATASHEET).SetText(d['url'])
 for pad in f.Pads():
  num=pad.GetNumber()
  if num in d['pins'] and d['pins'][num][2]:pad.SetNet(nets[d['pins'][num][2]])
 for g in f.GraphicalItems():
  if isinstance(g,p.PCB_SHAPE) and g.GetLayer() in [p.F_SilkS,p.B_SilkS]:g.SetWidth(max(g.GetWidth(),p.FromMM(.15)))
for i,xy in enumerate(cfg.get('mounts',[]),1):
 f=p.FootprintLoad(str(root/'SimpleROV_HW.pretty'),'MountingHole3.2_M3_Clearance');b.Add(f);f.SetReference('H'+str(i));f.SetAttributes(p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES);f.SetPosition(p.VECTOR2I(*(p.FromMM(v) for v in xy)));f.Reference().SetVisible(False);f.Value().SetVisible(False)
 for pad in f.Pads():pad.SetLocalClearance(p.FromMM(2.1))

w,h=cfg['size']
for a,c in [((0,0),(w,0)),((w,0),(w,h)),((w,h),(0,h)),((0,h),(0,0))]:
 edge=p.PCB_SHAPE();edge.SetShape(p.SHAPE_T_SEGMENT);edge.SetStart(p.VECTOR2I(*(p.FromMM(v) for v in a)));edge.SetEnd(p.VECTOR2I(*(p.FromMM(v) for v in c)));edge.SetLayer(p.Edge_Cuts);edge.SetWidth(p.FromMM(.05));b.Add(edge)
for text,x,y,side,sz in cfg.get('labels',[]):
 t=p.PCB_TEXT(b);t.SetText(text);t.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));t.SetLayer(p.F_SilkS if side=='top' else p.B_SilkS);t.SetMirrored(side!='top');t.SetTextSize(p.VECTOR2I(p.FromMM(sz),p.FromMM(sz)));t.SetTextThickness(p.FromMM(.15));b.Add(t)
# Ground plane is filled after routing, not a substitute for unconnected checks.
if cfg.get('ground'):
 for layer in [p.F_Cu,p.B_Cu]:
  z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets[cfg['ground']]);z.SetLocalClearance(p.FromMM(.127));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.15));poly=z.Outline();poly.NewOutline()
  for x,y in [(.3,.3),(w-.3,.3),(w-.3,h-.3),(.3,h-.3)]:poly.Append(p.FromMM(x),p.FromMM(y))
  b.Add(z)
for x,y in cfg.get('ground_vias',[]):
 v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[cfg['ground']]);b.Add(v)
for idx,(x0,y0,x1,y1) in enumerate(cfg.get('ground_spokes',[])):
 t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(x0),p.FromMM(y0)));t.SetEnd(p.VECTOR2I(p.FromMM(x1),p.FromMM(y1)));t.SetLayer(p.B_Cu if cfg.get('ground_spoke_layers',[])[idx:idx+1]==['B.Cu'] else p.F_Cu);t.SetWidth(p.FromMM(.2));t.SetNet(nets[cfg['ground']]);b.Add(t)
for seed in cfg.get('locked_escape_seeds',[]):
 a,z=seed['points'];t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(*(p.FromMM(v) for v in a)));t.SetEnd(p.VECTOR2I(*(p.FromMM(v) for v in z)));t.SetLayer(p.F_Cu);t.SetWidth(p.FromMM(.15));t.SetNet(nets[seed['net']]);t.SetLocked(True);b.Add(t)
 v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(*(p.FromMM(vv) for vv in z)));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[seed['net']]);v.SetLocked(True);b.Add(v)
p.SaveBoard(str(root/(stem+'.kicad_pcb')),b)
(root/'source').mkdir(exist_ok=True);p.ExportSpecctraDSN(b,str(root/'source'/('unrouted.dsn')))
dsn=root/'source/unrouted.dsn';dsn.write_text(dsn.read_text().replace('(clearance 200)', '(clearance 140)').replace('(clearance 50 (type smd_smd))','(clearance 140 (type smd_smd))').replace('(circle F.Cu 3700)', '(circle F.Cu 7400)').replace('(circle B.Cu 3700)', '(circle B.Cu 7400)').replace('(circle In1.Cu 3700)', '(circle In1.Cu 7400)').replace('(circle In2.Cu 3700)', '(circle In2.Cu 7400)'))
if cfg.get('route_ground_explicitly'):
 dsn.write_text(re.sub(r'^\s*\(plane .*?\)\n','',dsn.read_text(),flags=re.M))
project={'meta':{'filename':stem+'.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.127,'min_track_width':.1,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_copper_edge_clearance':.25}}},'net_settings':{'classes':[{'name':'Default','clearance':.127,'track_width':.2,'via_diameter':.6,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.2}]}}
shutil.copy2(distribution/(stem+'.kicad_pro'),root/(stem+'.kicad_pro'));shutil.copy2(distribution/(stem+'.kicad_dru'),root/(stem+'.kicad_dru'));shutil.copy2(distribution/'fp-lib-table',root/'fp-lib-table')
(root/'source/design_manifest.json').write_text(json.dumps(s.parts,indent=2))
with (root/'BOM.csv').open('w',newline='') as f:
 writer=csv.writer(f);writer.writerow(['Reference','Value','MPN','Footprint','Datasheet','Qty']);writer.writerows([d['ref'],d['value'],d['mpn'],d['fp'],d['url'],1] for d in s.parts if d.get('purchased',True))
print(stem,len(s.parts),'parts; native generated, routing still required')
