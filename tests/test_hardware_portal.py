from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def test_hardware_page_preserves_blocked_evidence_boundary():
    page=(ROOT/"research-portal/app/hardware/page.tsx").read_text(encoding="utf-8")
    gate=json.loads((ROOT/"results/embedded/stage15_hardware_detection.json").read_text())
    assert gate["scientific_execution_status"]=="BLOCKED_HARDWARE"
    assert "getEmbedded" in page and "scientific_execution_status" in page
    assert "Hardware execution blocked" in page and "linked_rom_footprint" in page
    assert "random" not in page.lower() and "simulated value" in page.lower()

def test_hardware_images_and_diagrams_are_honest_and_accessible():
    page=(ROOT/"research-portal/app/hardware/page.tsx").read_text(encoding="utf-8")
    diagram=(ROOT/"research-portal/components/HardwareConnectionDiagram.tsx").read_text(encoding="utf-8")
    assert 'from "next/image"' in page and page.count("<Image")==2 and page.count("alt=\"")==2
    assert "nordicsemi.cn/assets/images/nrf52840dk.png" in page and "nordicsemi.cn/assets/images/ppk2.png" in page
    assert "PLANNED CONNECTION — NOT PHYSICALLY EXECUTED" in diagram
    assert "<title" in diagram and "<desc" in diagram and "P22 / SB40" in diagram

def test_hardware_mobile_cards_and_measurement_states():
    css=(ROOT/"research-portal/app/globals.css").read_text(encoding="utf-8")
    status=(ROOT/"research-portal/components/HardwareStatus.tsx").read_text(encoding="utf-8")
    assert "hardware-measurement-cards" in css and "@media (max-width: 640px)" in css
    assert status.count('status="NOT_MEASURED"')>=2
    assert "0 KB" not in status and "0 ms" not in status and "0 µJ" not in status
