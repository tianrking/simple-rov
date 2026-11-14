"""Verify system/PCB interface consistency from published native engineering files.

Run --publish after native KiCad ERC/DRC/netlist export; CI uses --check.
Does not establish electrical function, physical fit, thermal or sealing results.
"""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from project_files import project_files
C = R/'electronics/pcb/controller'
V = R/'electronics/validation'
p = argparse.ArgumentParser()
p.add_argument('--publish', action='store_true')
p.add_argument('--check', action='store_true')
p.add_argument('--controller-dir', type=Path, default=C)
p.add_argument('--pin-table', type=Path, default=R/'electronics/interfaces/CONTROLLER_PINOUT.csv')
p.add_argument('--native-only', action='store_true', help='Check native outline/pins/netlist only, without publishing an integration verdict')
a = p.parse_args()
C = a.controller_dir.resolve()
assert not (a.native_only and (a.publish or a.check)), 'Native-only cannot publish or certify the full integration report'


def read_csv(path):
    with (R/path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sexpr(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    stack = [[]]
    for token in tokens:
        if token == '(':
            node = []
            stack[-1].append(node)
            stack.append(node)
        elif token == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert len(stack) == 1 and len(stack[0]) == 1, 'Invalid PCB s-expression'
    return stack[0][0]


def children(node, name):
    return [x for x in node if isinstance(x, list) and x and x[0] == name]


def child(node, name):
    xs = children(node, name)
    assert len(xs) == 1, (name, len(xs))
    return xs[0]


def normalize_net(name):
    return name.lstrip('/')


allowed = {'SELECTED_REFERENCE','PCB_DEPENDENT','RFQ_HOLD','FIT_HOLD','OPTIONAL','BENCH_ONLY'}
counts = {}
all_ids = []
for name in ['SYSTEM_BOM','HARNESS_BOM','CONSUMABLES_TOOLS','CONTROLLER_HARNESS_PARTS']:
    rows = read_csv('electronics/bom/'+name+'.csv')
    ids = [x['id'] for x in rows]
    assert len(ids) == len(set(ids))
    all_ids += ids
    counts[name] = len(rows)
    for row in rows:
        assert row['status'] in allowed, row
        for key in ['qty','quantity','installed_qty','new_purchase_qty']:
            if key in row:
                value = float(row[key])
                assert math.isfinite(value) and value >= 0, (row['id'],key)
        if row.get('reference_only') == 'true':
            assert float(row['new_purchase_qty']) == 0, 'Duplicate reference purchase'
assert len(all_ids) == len(set(all_ids))
system = {x['id']:x for x in read_csv('electronics/bom/SYSTEM_BOM.csv')}
assert int(system['SYS-001']['installed_qty']) == int(system['SYS-002']['installed_qty']) == 4
assert system['SYS-011']['status'] == 'RFQ_HOLD'

contract = json.loads((R/'electronics/interfaces/MECHANICAL_CONTRACT.json').read_text())
channel = json.loads((R/'electronics/interfaces/SYSTEM_CHANNELS.json').read_text())
act = json.loads((R/'simulation/mujoco/ACTUATOR_MAP.json').read_text())
assert [x['name'] for x in channel['channels']] == [x['name'] for x in act['sites']]
for ch, site in zip(channel['channels'],act['sites']):
    assert ch['positive_thrust_body'] == site['thrust_direction']
    assert ch['position_body_m'] == site['position_m']
assert not channel['power']['motor_current_through_controller']
assert not channel['power']['BEC_positives_parallel']

board = sexpr((C/'SimpleROV001_control.kicad_pcb').read_text())
assert float(child(child(board,'general'),'thickness')[1]) == 1.6
assert len([x for x in child(board,'layers')[1:] if isinstance(x,list) and str(x[1]).endswith('.Cu')]) == 4
parts = {}
mounts = []
for footprint in children(board,'footprint'):
    props = {x[1]:x[2] for x in children(footprint,'property')}
    ref = props.get('Reference')
    assert ref and ref not in parts, ref
    pads = collections.defaultdict(set)
    for pad in children(footprint,'pad'):
        if pad[2] == 'np_thru_hole':
            at = child(footprint,'at')
            local = child(pad,'at')
            assert float(local[1]) == float(local[2]) == 0, 'Unexpected mounting-hole local offset'
            mounts.append([float(at[1]),float(at[2]),float(child(pad,'drill')[1])])
            clearance = float(child(pad,'clearance')[1])
            assert clearance + 1.6 >= contract['board']['mount_hole_copper_keepout_radius_mm'] - 1e-6, 'M3 washer copper keepout too small'
        for net in children(pad,'net'):
            pads[pad[1]].add(normalize_net(net[-1]))
    at = child(footprint,'at')
    parts[ref] = {'value':props.get('Value'),'footprint':footprint[1],'pads':dict(pads),'xy':[float(at[1]),float(at[2])],'angle':float(at[3]) if len(at)>3 else 0}
assert sorted(mounts) == sorted([x+[3.2] for x in contract['board']['mount_holes_local_xy_mm']])
edge_points = []
for name in ['gr_line','gr_rect']:
    for item in children(board,name):
        if child(item,'layer')[1] == 'Edge.Cuts':
            for key in ['start','end']:
                edge_points.append(list(map(float,child(item,key)[1:3])))
assert edge_points
assert [min(x[0] for x in edge_points),max(x[0] for x in edge_points),min(x[1] for x in edge_points),max(x[1] for x in edge_points)] == [0,80,0,32]

with a.pin_table.open(encoding='utf-8-sig',newline='') as f:
    pins = list(csv.DictReader(f))
board_bom = []
with (C/'BOM.csv').open(encoding='utf-8-sig',newline='') as f:
    board_bom = list(csv.DictReader(f))
seen_refs = set()
for item in board_bom:
    refs = [x.strip() for x in item['Reference'].split(',')]
    assert len(refs) == int(item['Qty']), item
    assert item['MPN'].strip(), item
    for ref in refs:
        assert ref not in seen_refs, 'Duplicate PCBA BOM reference'
        seen_refs.add(ref)
        assert parts[ref]['value'] == item['Value'], ('BOM value',ref)
        assert parts[ref]['footprint'] == item['Footprint'], ('BOM footprint',ref)

for pin in pins:
    fp = parts[pin['connector']]
    assert all(abs(x-y)<1e-5 for x,y in zip(json.loads(pin['native_xy_mm']),fp['xy'])), ('Stale connector position',pin['connector'],json.loads(pin['native_xy_mm']),fp['xy'])
    assert abs((float(pin['angle_deg'])-fp['angle'])%360)<1e-5, ('Stale connector angle',pin)
    if pin['net'] == 'NC':
        continue
    assert normalize_net(pin['net']) in parts[pin['connector']]['pads'].get(pin['pin'], set()), pin
expected = {
'J1':{'1':'SYS5V','2':'GND'},
'J2':{'1':'GND','2':'UART_TX_PORT','3':'UART_RX_PORT'},
'J7':{'1':'DEPTH_3V3','2':'DEPTH_SCL','3':'DEPTH_SDA','4':'GND'},
'U9':{'1':'WDT_OK','2':'GND','3':'GND','4':'WDI','5':'V3V3'},
'U12':{'1':'ARM_CLR','2':'V3V3','3':'ARM_SET','4':'V3V3','5':'ARM_LATCH_Q','7':'GND','10':'V3V3','11':'GND','12':'GND','13':'GND','14':'V3V3'},
'U13':{'1':'GND','2':'GND','3':'WDT_OK','4':'ARM_CLEAR_DRIVE','5':'V3V3','6':'ARM_KEY'},
}
for connector, short in zip(['J3','J4','J5','J6'],['HL','HR','VL','VR']):
    expected[connector]={'1':f'ESC_{short}_5V','2':f'ESC_{short}_PWM_PORT','3':f'ESC_{short}_GND'}
for ref, mapping in expected.items():
    for pin, net in mapping.items():
        assert parts[ref]['pads'][pin] == {net}, (ref,pin,parts[ref]['pads'][pin],net)
silk = [x[1] for x in children(board,'gr_text')]
assert 'J2 UART 1G2TX3RX' in silk, 'UART silkscreen must agree with J2 pad numbers'
assert not any('1TX2RX3G' in t for t in silk), 'Stale UART pin legend'
assert parts['U4']['value'] == 'W25Q16JVSNIQ'
assert parts['U4']['footprint'].endswith('SOIC-8_3.9x4.9mm_P1.27mm')
assert parts['U12']['value'] == 'SN74HCS74PWR'
assert 'D6' not in parts
for ref in ['R18','R19','R20','R21']:
    assert parts[ref]['value'] == '365'
for ref in ['R26','R27','R28','R29']:
    assert parts[ref]['value'] == '10k'

if a.native_only:
    print(json.dumps({'native_outline_and_pin_contract':'PASS','mounting_holes':mounts,'connector_pin_rows':len(pins),'ERC_DRC_and_physical_tests':'NOT_EVALUATED'},indent=2))
    raise SystemExit(0)

netlist = ET.parse(V/'controller.net.xml').getroot()
sch_pins = {}
for net in netlist.findall('./nets/net'):
    name = normalize_net(net.attrib['name'])
    for node in net.findall('node'):
        sch_pins[(node.attrib['ref'],node.attrib['pin'])] = name
for ref, mapping in expected.items():
    for pin, net in mapping.items():
        assert sch_pins[(ref,pin)] == net, ('Schematic',ref,pin,net)

reports = {}
for name in ['erc','drc']:
    j = json.loads((V/(name+'.json')).read_text())
    if name == 'erc':
        violations = [v for s in j['sheets'] for v in s['violations']]
    else:
        violations = j['violations']+j['unconnected_items']+j['schematic_parity']
    assert not violations, (name,len(violations))
    forbidden_ignored = {'clearance','shorting_items','unconnected_items','schematic_parity','hole_clearance','power_pin_not_driven','text_height','silk_overlap','silk_edge_clearance','lib_footprint_mismatch'}
    assert not forbidden_ignored.intersection(x['key'] for x in j['ignored_checks']), ('Suppressed required check',name)
    reports[name]={'kicad_version':j['kicad_version'],'reported_violations':0,'ignored_check_types':j['ignored_checks']}


for report_name in ['controller_mount.json','native_controller_fit.json','controller_renders.json','jlc_review_export.json','native_checks.json']:
    j = json.loads((V/report_name).read_text())
    for key in ['source_sha256','output_sha256','images','outputs']:
        for name, expected_hash in j.get(key,{}).items():
            assert hashlib.sha256((R/name).read_bytes()).hexdigest() == expected_hash, ('Stale '+report_name,name)

files = [p for p in project_files() if p.is_relative_to(R/'electronics') and p.name != 'INTEGRATION_CHECKS.json']
files += list((R/'tools/hardware').glob('*.py'))+[R/'simulation/mujoco/ACTUATOR_MAP.json']
source_hashes = {str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
result={'project_version':'v0.0.1','passed':True,'scope':'Native-file/interface/BOM consistency and recorded KiCad checks only; not electrical or physical qualification.', 'BOM_rows':counts,'connector_pin_rows_checked':len(pins),'PCBA_BOM_reference_count':len(seen_refs),'datasheet_pin_mappings_checked':expected,'four_M3_mount_holes_match':True,'board_outline_mm':[80,32],'checks':reports,'physical_tested':False,'complete_vehicle_packaging_verified':False,'source_sha256':source_hashes}
report_path=V/'INTEGRATION_CHECKS.json'
if a.check:
    saved=json.loads(report_path.read_text())
    assert saved==result,'Hardware integration report is stale; rerun native checks and publish'
if a.publish:
    report_path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['passed','BOM_rows','connector_pin_rows_checked','four_M3_mount_holes_match','physical_tested','complete_vehicle_packaging_verified']},indent=2))
