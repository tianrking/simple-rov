from pathlib import Path
import json,uuid,csv,wx
import pcbnew as p
APP=wx.App(False)
ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'footprints'
UID=lambda:str(uuid.uuid4())
parts=[]
POWER_FLAGS=['PWR_IN','BAT','REGSRC','GND_MON']
def add(ref,value,fp,xy,pins,mpn='',url='',angle=0,height=2):
    # pins: number -> (pin name, electrical type, net or None)
    d=dict(ref=ref,value=value,fp=fp,xy=xy,pins={str(k):v for k,v in pins.items()},mpn=mpn or value,url=url,angle=angle,height=height,uuid=UID())
    parts.append(d);return d

def schematic(add_supply_markers=True, positions_override=None, paper="A0"):
    root=UID(); defs=[]; instances=[]; wires=[]; tags=[]
    # Readable full net-label schematic, single A1 sheet; each pin has named net.
    positions={ 'U1':(68,105)}
    remaining=[d for d in parts if d['ref']!='U1']
    for idx,d in enumerate(remaining):positions[d['ref']]=(160+(idx%12)*80,38+(idx//12)*78)
    if positions_override:positions.update(positions_override)
    for d in parts:
        ref=d['ref'];x,y=[round(v/1.27)*1.27 for v in positions[ref]];pp=list(d['pins'].items());h=max(10,(len(pp)-1)*2.54+8);nm='SimpleROV:'+ref
        st='(symbol "%s" (pin_names (offset 0.6)) (in_bom yes) (on_board yes) (property "Reference" "%s" (at 0 %s 0) (effects (font (size 1.27 1.27)))) (property "Value" "%s" (at 0 %s 0) (effects (font (size 1.0 1.0)))) (symbol "%s_0_1" (rectangle (start -12.7 %s) (end 12.7 %s) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "%s_1_1" '%(nm,ref[0],h/2+3,d['value'],h/2+6,ref,h/2,-h/2,ref)
        for j,(num,(name,typ,net)) in enumerate(pp):
            py=(len(pp)-1)*1.27-j*2.54
            st+='(pin %s line (at -17.78 %s 0) (length 5.08) (name "%s" (effects (font (size 1 1)))) (number "%s" (effects (font (size 1 1))))) '%(typ,py,name,num)
            gx=x-17.78;gy=y-py
            if net:
                wires.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0.1524) (type default)) (uuid "%s"))'%(gx,gy,gx-5.08,gy,UID()))
                tags.append('(label "%s" (at %s %s 0) (effects (font (size 1 1)) (justify right bottom)) (uuid "%s"))'%(net,gx-5.08,gy,UID()))
            else:tags.append('(no_connect (at %s %s) (uuid "%s"))'%(gx,gy,UID()))
        if not d.get('purchased',True):st=st.replace('(in_bom yes)','(in_bom no)')
        defs.append(st+'))')
        props=''
        for key,val,yy,hide in [('Reference',ref,y-h/2-3,False),('Value',d['value'],y-h/2-6,False),('Footprint',d['fp'],y,True),('Datasheet',d['url'],y,True),('MPN',d['mpn'],y,True)]:
            props+='(property "%s" "%s" (at %s %s 0) (effects (font (size 1 1))%s))'%(key,val,x,yy,' (hide yes)' if hide else '')
        instances.append('(symbol (lib_id "%s") (at %s %s 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "%s") %s (instances (project "SimpleROV001_control" (path "/%s" (reference "%s") (unit 1)))))'%(nm,x,y,d['uuid'],props,root,ref))
    for idx,d in enumerate(parts):
        if not d.get('purchased',True):instances[idx]=instances[idx].replace('(in_bom yes)','(in_bom no)')
    # Explicit external supply drive markers; these do not suppress other ERC checks.
    for idx,net in enumerate(POWER_FLAGS if add_supply_markers else []):
        name='SimpleROV:SUPPLY'+str(idx);x=round((45+(idx%2)*50)/1.27)*1.27;y=round((230+(idx//2)*16)/1.27)*1.27
        defs.append('(symbol "%s" (pin_names (offset 0)) (in_bom no) (on_board no) (property "Reference" "#FLG" (at 0 0 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "EXTERNAL_SUPPLY" (at 0 3 0) (effects (font (size 1 1)))) (symbol "%s_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))))'%(name,'SUPPLY'+str(idx)))
        instances.append('(symbol (lib_id "%s") (at %s %s 0) (unit 1) (in_bom no) (on_board no) (uuid "%s") (property "Reference" "#FLG0%d" (at %s %s 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "EXTERNAL_SUPPLY" (at %s %s 0) (effects (font (size 1 1)))) (instances (project "SimpleROV001_control" (path "/%s" (reference "#FLG0%d") (unit 1)))))'%(name,x,y,UID(),idx+1,x,y,x,y-3,root,idx+1))
        tags.append('(label "%s" (at %s %s 0) (effects (font (size 1 1)) (justify right bottom)) (uuid "%s"))'%(net,x,y,UID()))
    (ROOT/'SimpleROV.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "SimpleROV_generator") '+ '\n'.join(defs).replace('SimpleROV:', '') +')')
    (ROOT/'sym-lib-table').write_text('(sym_lib_table (lib (name "SimpleROV") (type "KiCad") (uri "${KIPRJMOD}/SimpleROV.kicad_sym") (options "") (descr "Explicit datasheet pin maps")))')
    header='(kicad_sch (version 20250114) (generator "SimpleROV_generator") (uuid "%s") (paper "A0") (title_block (title "SimpleROV v0.0.1 control interfaces") (date "2026-11-14") (rev "v0.0.1 ENGINEERING CANDIDATE") (comment 1 "Controller, sensors and optocoupled PWM. No motor current.")) (lib_symbols %s)'%(root,'\n'.join(defs))
    header=header.replace('(paper "A0")','(paper "'+paper+'")')
    (ROOT/'SimpleROV001_control.kicad_sch').write_text(header+'\n'+'\n'.join(instances+wires+tags)+'\n(embedded_fonts no))')
    return root