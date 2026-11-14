# Export provenance

ERC.json and DRC.json are unedited native KiCad10.0.8 CLI JSON reports. The final DRC run uses0.10mm minimum track,0.127mm minimum electrical clearance,0.10mm silk clearance and0.8mm minimum silk text height. There are no DRC exclusions or ignored DRC checks. ERC retains only SPICE model checking as ignored; no SPICE simulation is claimed.

The XML netlist is exported from the final native schematic. Only design/source is changed from an absolute local path to SimpleROV001_control.kicad_sch; its electrical nodes/parts/nets are untouched. All CSVs use LF. STEP export uses --user-origin0x32mm. Mated connector and wire reservations use the final native physical_placement.json. The assembly bottom PDF is a view-only projection with copper tracks/zones removed to show bare test pads and the actual back silk; the checked native PCB is never replaced by that drawing copy.

The full replay into an independent directory passes ERC0, DRC0, unconnected0 and schematic-parity0 under the final project rules. REBUILD_ERC.json and REBUILD_DRC.json retain those native results. CONTRACT_CHECKS.json independently compares the exported electrical pin requirements and reports analytical values; none of these reports substitutes for physical bench qualification.
