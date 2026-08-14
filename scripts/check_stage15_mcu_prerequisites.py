"""Record the non-invasive Stage-15 physical-hardware prerequisite gate."""
from __future__ import annotations
import csv,hashlib,json,platform,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"results/embedded";EID="EXP-MCU-C1-FP32-PORT-001"
TOOLS=("west","nrfjprog","JLinkExe","cmake","ninja","arm-none-eabi-gcc")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ps(command):
 r=subprocess.run(["powershell","-NoProfile","-Command",command],capture_output=True,text=True)
 return r.returncode,r.stdout.strip(),r.stderr.strip()
def main():
 devices_cmd="Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'nRF|Nordic|J-Link|JLink|CMSIS-DAP|DAPLink|SEGGER|PCA10056' -or $_.InstanceId -match 'VID_1366|VID_1915|VID_0D28' } | Select-Object Status,Class,FriendlyName,InstanceId | ConvertTo-Json -Compress"
 serial_cmd="Get-CimInstance Win32_SerialPort -ErrorAction SilentlyContinue | Select-Object DeviceID,Name,PNPDeviceID | ConvertTo-Json -Compress"
 _,dev,dev_err=ps(devices_cmd);_,serial,serial_err=ps(serial_cmd)
 tool_rows=[]
 for name in TOOLS:
  path=shutil.which(name);tool_rows.append({"experiment_id":EID,"tool":name,"status":"FOUND" if path else "NOT_FOUND","resolved_path":path or "","version":"NOT_QUERIED_NO_FUNCTIONING_INSTALL" if not path else "INSTALLED_VERSION_QUERY_DEFERRED_UNTIL_BOARD_GATE"})
 board_detected=bool(dev and dev not in ("null","[]"));status="BLOCKED_HARDWARE" if not board_detected else "BOARD_DETECTED_REQUIRES_IDENTITY_CONFIRMATION"
 report={"experiment_id":EID,"timestamp_utc":datetime.now(timezone.utc).isoformat(),"scientific_execution_status":status,"host_os":platform.platform(),"physical_debug_probe_or_board_detected":board_detected,"board_identity":"UNRESOLVED_NO_SUPPORTED_DEVICE_DETECTED" if not board_detected else "REQUIRES_EXACT_TARGET_DISCOVERY","zephyr_board_target":"NOT_SELECTED","pnp_detection_json":dev or "[]","serial_ports_json":serial or "[]","detection_stderr":dev_err,"serial_detection_stderr":serial_err,"smoke_test":"NOT_EXECUTED","build_a":"NOT_EXECUTED","build_b":"NOT_EXECUTED","build_c":"NOT_EXECUTED","build_d":"NOT_EXECUTED","flash":"NOT_EXECUTED","physical_golden":"NOT_EXECUTED","physical_boundary":"NOT_EXECUTED","physical_xai":"NOT_EXECUTED","linked_rom_footprint":"NOT_MEASURED","linked_static_ram":"NOT_MEASURED","mcu_latency":"NOT_MEASURED","mcu_xai_latency":"NOT_MEASURED","energy":"NOT_MEASURED","quantization":"NOT_EXECUTED","reason":"No physical nRF52840 board/debug probe was detected; physical execution is mandatory." if not board_detected else "Board identity must be confirmed before choosing a target."}
 (OUT/"stage15_hardware_detection.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 with (OUT/"stage15_toolchain_inventory.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=tool_rows[0]);w.writeheader();w.writerows(tool_rows)
 inputs=["results/embedded/c1_fused_manifest.csv","results/embedded/c1_fused_xai_manifest.csv","embedded/generated/c1_fused/model_c1_fused.c","embedded/generated/c1_fused/inference_c1_fused.c","embedded/generated/c1_fused/xai_c1_fused.c","configs/nrf52840_resource_budget.yaml"]
 manifest=[{"experiment_id":EID,"artifact_path":r,"sha256":sha(ROOT/r),"role":"IMMUTABLE_AUTHORIZED_INPUT","status":status} for r in inputs]
 for r in ["results/embedded/stage15_hardware_detection.json","results/embedded/stage15_toolchain_inventory.csv","docs/embedded/EXP_MCU_C1_FP32_PORT_001.md"]:
  manifest.append({"experiment_id":EID,"artifact_path":r,"sha256":sha(ROOT/r),"role":"BLOCKED_GATE_EVIDENCE","status":status})
 with (OUT/"stage15_manifest.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=manifest[0]);w.writeheader();w.writerows(manifest)
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
