import json
from pathlib import Path
import pandas as pd,yaml
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"results/embedded"
def test_stage15_is_blocked_without_physical_board():
 d=json.loads((OUT/"stage15_hardware_detection.json").read_text());assert d["scientific_execution_status"]=="BLOCKED_HARDWARE";assert d["physical_debug_probe_or_board_detected"] is False;assert d["zephyr_board_target"]=="NOT_SELECTED"
def test_no_physical_or_resource_claims_exist():
 d=json.loads((OUT/"stage15_hardware_detection.json").read_text());assert d["physical_golden"]==d["physical_boundary"]==d["physical_xai"]=="NOT_EXECUTED";assert d["linked_rom_footprint"]==d["linked_static_ram"]=="NOT_MEASURED";assert d["mcu_latency"]==d["energy"]=="NOT_MEASURED"
def test_stage15_lineage_and_pipeline_status():
 m=pd.read_csv(OUT/"stage15_manifest.csv");assert m.status.eq("BLOCKED_HARDWARE").all();assert m.sha256.str.fullmatch(r"[0-9a-f]{64}").all();stages=yaml.safe_load((ROOT/"configs/pipeline_stages.yaml").read_text())["stages"];assert next(x for x in stages if x["id"]=="15")["status"]=="BLOCKED"
