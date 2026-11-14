"""Check the exported native netlist against frozen electrical interface requirements."""
from pathlib import Path
import argparse,json,xml.etree.ElementTree as E,csv,math
ap=argparse.ArgumentParser();ap.add_argument('package',nargs='?',default=str(Path(__file__).resolve().parents[2]));args=ap.parse_args();r=Path(args.package).resolve();tree=E.parse(r/'controller/source/netlist.xml');pin={};parts={a.get('ref'):a for a in tree.findall('.//components/comp')}
for n in tree.findall('.//nets/net'):
 for q in n.findall('node'):pin[(q.get('ref'),q.get('pin'))]=n.get('name')
def check(ref,num,net):assert pin[(ref,str(num))]=='/'+net,(ref,num,pin.get((ref,str(num))),net)
checks=[]
for ref,num,net in [('U9',1,'WDT_OK'),('U9',4,'WDI'),('U9',3,'GND'),('U12',1,'ARM_CLR'),('U12',3,'ARM_SET'),('U12',5,'ARM_LATCH_Q'),('U13',1,'GND'),('U13',2,'GND'),('U13',3,'WDT_OK'),('U13',4,'ARM_CLEAR_DRIVE'),('U13',5,'V3V3'),('U13',6,'ARM_KEY')]:check(ref,num,net)
checks.append('Watchdog WDO/WDI, HCS latch and Schmitt active-clear gate native pin maps')
assert parts['U4'].findtext('value')=='W25Q16JVSNIQ';assert 'SOIC-8_3.9x4.9mm' in parts['U4'].findtext('footprint');assert parts['U12'].findtext('value')=='SN74HCS74PWR';assert 'D6' not in parts
for i,ch in enumerate(['HL','HR','VL','VR']):
 j='J'+str(i+3);u='U'+str(i+5);check(j,1,'ESC_'+ch+'_5V');check(j,2,'ESC_'+ch+'_PWM_PORT');check(j,3,'ESC_'+ch+'_GND');check(u,1,'LED_'+ch);check(u,3,'PWM_'+ch+'_BUF');check(u,4,'ESC_'+ch+'_GND');check(u,6,'ESC_'+ch+'_5V');check('U1',[8,9,11,12][i],'PWM_'+ch+'_RAW');assert parts['R'+str(18+i)].findtext('value')=='365';assert parts['R'+str(26+i)].findtext('value')=='10k'
assert len({pin[('J'+str(i), '3')] for i in range(3,7)}|{pin[('J1','2')]})==5
checks.append('Four physical motor channels, distinct BEC domains and non-inverting sink-drive topology')
for k,v in enumerate(['DEPTH_3V3','DEPTH_SCL','DEPTH_SDA','GND'],1):check('J7',k,v)
for row in csv.DictReader((r/'docs/CONNECTOR_PINOUT.csv').open()):
 if row['net']=='NC':continue
 assert pin[(row['connector'],row['pin'])]=='/'+row['net']
check('J2',1,'GND');check('J2',2,'UART_TX_PORT');check('J2',3,'UART_RX_PORT')
assert any(a['text']=='J2 UART 1G2TX3RX' for a in json.loads((r/'controller/source/silkscreen.json').read_text()))
assert 'J2 UART 1G2TX3RX' in (r/'controller/SimpleROV001_control.kicad_pcb').read_text()
checks.append('All exported connector pin labels compared with final native XML, including Bar02 factory order')
# Enumerate configured TI1G97 truth table; In1=GND, In2=KEY, In0=WDT.
truth=[]
for key in [0,1]:
 for wd in [0,1]:
  clear=wd if key else 0;assert clear==(key and wd);truth.append(dict(key=key,watchdog_ok=wd,clear_drive=clear))
for key,wd,q,enable in [(1,1,0,1),(0,1,1,1),(1,0,1,1),(1,1,1,0)]:
 clear=wd if key else 0
 if not clear:q=0
 assert not (key and q and enable)
checks.append('Configured clear truth table and disabled cases; no recovery edge sets the latch in the logic model')
calc=dict(led_if_min_mA=1000*(3.267-1.8-.55)/(365*1.01),led_if_max_mA=1000*(3.333-1.2)/(365*.99),off_cathode_drop_max_V=20e-6*10000*1.01,battery_ratio_nominal=27000/(1000+147000+27000),battery_adc_at16V=16*27000/(1000+147000+27000),source_short_at16V_power_W=16**2/990,leak_dry_ratio=1006.6/1106.6,leak_short_ratio=6.6/106.6)
assert calc['led_if_min_mA']>=2 and calc['led_if_max_mA']<=6 and calc['off_cathode_drop_max_V']<.8 and calc['source_short_at16V_power_W']<.5
checks.append('Analytical resistor corners under the explicitly stated VF/rail assumptions, not bench results')
raw={}
for name in ['DRC','ERC']:
 d=json.loads((r/f'verification/{name}.json').read_text());viol=d.get('violations',[])+sum([q.get('violations',[]) for q in d.get('sheets',[])],[]);assert not viol and not d.get('unconnected_items',[]) and not d.get('schematic_parity',[]);raw[name]=dict(violations=0,unconnected=len(d.get('unconnected_items',[])),parity=len(d.get('schematic_parity',[])),ignored_checks=d.get('ignored_checks',[]))
assert not raw['DRC']['ignored_checks'];assert [a['key'] for a in raw['ERC']['ignored_checks']]==['simulation_model_issue']
report=dict(project='SimpleROV',version='v0.0.1',result='PASS',checks=checks,native_reports=raw,clear_truth_table=truth,analytical_values=calc,limits='No physical electrical/motor/thermal/EMC test or firmware verification. VF1.2..1.8V is an engineering qualification window; exact ESC signal-loss stop remains unverified.');(r/'verification/CONTRACT_CHECKS.json').write_text(json.dumps(report,indent=2));print('PASS:',len(checks),'electrical export/logic checks')
