import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTAL = ROOT / "research-portal"


def _device_data_source() -> str:
    return (PORTAL / "components/digital-twin/device-data.ts").read_text(encoding="utf-8")


def test_device_page_declares_conceptual_flag():
    page = (PORTAL / "app/digital-twin/device/page.tsx").read_text(encoding="utf-8")
    assert "CONCEPTUAL ENGINEERING VIEW" in page


def test_device_layers_have_unique_ids():
    source = _device_data_source()
    ids = re.findall(r'\bid: "([a-z0-9-]+)"', source)
    assert len(ids) == 10, f"expected 10 device layers, found {len(ids)}: {ids}"
    assert len(ids) == len(set(ids)), f"duplicate device layer id in device-data.ts: {ids}"


def test_mcu_layer_status_is_sourced_from_the_real_hardware_gate_not_hardcoded():
    source = _device_data_source()
    gate = json.loads((ROOT / "results/embedded/stage15_hardware_detection.json").read_text())
    assert gate["scientific_execution_status"] == "BLOCKED_HARDWARE"
    # The MCU layer must read the gate object, not assign a literal status string.
    assert "hardwareStatus: hardwareStatus" in source or "hardwareStatus," in source
    assert "gate?.scientific_execution_status" in source
    assert '"mcu"' in source
    # No device layer may hardcode the literal string as a bare status assignment.
    assert 'status: "BLOCKED_HARDWARE"' not in source


def test_device_view_reuses_hardware_status_component_instead_of_reimplementing_it():
    page = (PORTAL / "app/digital-twin/device/page.tsx").read_text(encoding="utf-8")
    assert 'from "@/components/HardwareStatus"' in page and "<HardwareStatus" in page
    # The measurement row labels must exist in exactly one place (HardwareStatus.tsx itself).
    hardware_status = (PORTAL / "components/HardwareStatus.tsx").read_text(encoding="utf-8")
    assert "Linked ROM / Flash" in hardware_status
    assert "Linked ROM / Flash" not in page


def test_device_view_never_shows_fabricated_zero_measurements():
    for path in [
        PORTAL / "app/digital-twin/device/page.tsx",
        PORTAL / "components/digital-twin/device-data.ts",
        PORTAL / "components/digital-twin/DeviceStatusTimeline.tsx",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "0 KB" not in text and "0 ms" not in text and "0 µJ" not in text, path


def test_device_status_timeline_reads_pipeline_and_gate_evidence():
    source = (PORTAL / "components/digital-twin/DeviceStatusTimeline.tsx").read_text(encoding="utf-8")
    assert "getPipeline" in source and "getEmbedded" in source and "getDataset" in source
    # Must not hand-type a status for the physically-blocked stages instead of deriving it.
    assert 'status: "BLOCKED_HARDWARE"' not in source


def test_device_view_supports_component_deep_link():
    explorer = (PORTAL / "components/digital-twin/DeviceExplorer.tsx").read_text(encoding="utf-8")
    assert 'searchParams.get("component")' in explorer
    assert 'params.set("component"' in explorer


def test_device_view_has_non_3d_text_equivalent_and_webgl_fallback():
    explorer = (PORTAL / "components/digital-twin/DeviceExplorer.tsx").read_text(encoding="utf-8")
    assert "TwinComponentList" in explorer
    assert "supportsWebGL" in explorer and "TwinCanvasBoundary" in explorer


def test_component_inspector_extension_is_additive_only():
    # The Phase-B /digital-twin components must never set the new Phase-C-only object-literal
    # fields — otherwise the shared ComponentInspector's original rendering path would change.
    # Checked as "<field>:" (property-key form) so this doesn't false-positive on unrelated
    # identifiers such as twin-data.ts's own local `hardwareStatus` variable.
    twin_data = (PORTAL / "components/digital-twin/twin-data.ts").read_text(encoding="utf-8")
    for field in ("hardwareStatus:", "researchPurpose:", "relatedModels:", "relatedExperiments:", "limitations:", "category:"):
        assert field not in twin_data, f"twin-data.ts must stay untouched by Phase-C fields ({field})"
