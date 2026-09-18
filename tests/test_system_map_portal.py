import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTAL = ROOT / "research-portal"


def _system_components_source() -> str:
    return (PORTAL / "lib/digital-twin/system-components.ts").read_text(encoding="utf-8")


def _extract_node_blocks(source: str):
    # Split on top-level object starts within the `components` array literal; good enough for
    # this file's consistent formatting (id is always the first key of each node object).
    return re.findall(r"\{\s*id: \"([a-z0-9-]+)\",.*?dependencies: \[([^\]]*)\]", source, re.S)


def test_system_map_nodes_have_unique_ids():
    source = _system_components_source()
    ids = re.findall(r'^\s*id: "([a-z0-9-]+)",', source, re.M)
    assert len(ids) >= 18, f"expected at least 18 system-map nodes, found {len(ids)}"
    assert len(ids) == len(set(ids)), f"duplicate system-map node id: {ids}"


def test_system_map_dependencies_reference_known_ids():
    source = _system_components_source()
    ids = set(re.findall(r'^\s*id: "([a-z0-9-]+)",', source, re.M))
    blocks = _extract_node_blocks(source)
    assert blocks, "could not parse any system-map node blocks — regex may be stale"
    for node_id, deps_raw in blocks:
        deps = re.findall(r'"([a-z0-9-]+)"', deps_raw)
        for dep in deps:
            assert dep in ids, f"system-map node '{node_id}' depends on unknown id '{dep}'"


def test_system_components_ts_has_its_own_runtime_dependency_guard():
    source = _system_components_source()
    assert "unknown dependency" in source and "throw new Error" in source


def test_research_status_field_is_never_named_plain_status():
    # The mandatory research-vs-UI-implementation distinction (Phase C Part 19) is encoded by
    # naming the field `researchStatus`, not `status` — this asserts that naming didn't drift.
    source = _system_components_source()
    assert "researchStatus:" in source
    assert re.search(r"^\s*status:", source, re.M) is None


def test_system_map_page_carries_research_vs_ui_disclaimer():
    page = (PORTAL / "app/system-map/page.tsx").read_text(encoding="utf-8")
    assert "not a software-implementation status" in page


def test_system_map_reads_only_through_shared_evidence_module():
    source = _system_components_source()
    assert 'from "@/lib/evidence"' in source
    assert "data/evidence/" not in source, "system-components.ts must not import evidence JSON directly"


def test_operations_layer_nodes_are_planned_not_claimed_executed():
    # Monitoring / adaptation / gateway-telemetry have no implementing code anywhere in the
    # repository — this guards against a future edit optimistically marking them EXECUTED.
    source = _system_components_source()
    for node_id in ("gateway-telemetry", "monitoring", "adaptation"):
        match = re.search(r'id: "' + node_id + r'".*?researchStatus: "([A-Z_]+)"', source, re.S)
        assert match, f"could not find node '{node_id}'"
        assert match.group(1) == "PLANNED", f"'{node_id}' must stay PLANNED until it has real evidence"


def test_system_map_supports_stage_deep_link_server_side():
    page = (PORTAL / "app/system-map/page.tsx").read_text(encoding="utf-8")
    explorer = (PORTAL / "components/system-map/SystemMapExplorer.tsx").read_text(encoding="utf-8")
    assert "searchParams" in page and "stage" in page
    # Deliberately NOT importing useSearchParams() in the client component — see
    # docs/architecture/system-map.md for why (it would force a client-side-rendering bailout for
    # a page with no WebGL dependency). Checked against the actual import line, not any mention
    # of the hook's name, since the file documents this choice in a comment.
    navigation_import = re.search(r'import \{([^}]*)\} from "next/navigation"', explorer)
    assert navigation_import, "expected a next/navigation import in SystemMapExplorer.tsx"
    imported_names = {name.strip() for name in navigation_import.group(1).split(",")}
    assert "useSearchParams" not in imported_names


def test_system_map_has_no_3d_dependency():
    for path in [
        PORTAL / "app/system-map/page.tsx",
        PORTAL / "components/system-map/SystemMapExplorer.tsx",
        PORTAL / "components/system-map/SystemMapGraph.tsx",
        PORTAL / "components/system-map/SystemMapInspector.tsx",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "three" not in text.lower() and "@react-three" not in text
