"""Freeze Stage 13 inventories, golden vectors, and architecture decisions.

No model fitting, conversion, quantization, code generation, compilation, or hardware action occurs.
"""
from __future__ import annotations

import csv, hashlib, json, math, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.loader import batch_number, discover_batches, load_batch  # noqa: E402
from src.embedded.reference_inference import load_frozen_pipeline, model_path, reference_inference  # noqa: E402

GATE = "GATE-EMBED-EXPORT-001"
OUT = ROOT / "results/embedded"
OUT.mkdir(parents=True, exist_ok=True)


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name: str, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path = OUT / name
    fields = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
def csvrows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))
def j(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x))


def verify_inputs() -> None:
    expected: dict[str, str] = {}
    for manifest in [ROOT / "results/xai/stage10_input_manifest.csv", ROOT / "results/xai/stage11_input_manifest.csv", ROOT / "results/xai/stage12_input_manifest.csv", ROOT / "results/registry/artifacts.csv"]:
        if not manifest.exists(): continue
        for r in csvrows(manifest):
            rel = r.get("path") or r.get("artifact_path")
            if rel and r.get("sha256"): expected[rel.replace("\\", "/")] = r["sha256"]
    required = [model_path(f"MODEL-C{i}") for i in range(1, 5)] + [
        ROOT / "research/feature_metadata.csv", ROOT / "data/manifests/dataset_manifest.json",
        ROOT / "results/xai/stage09_manifest.csv", ROOT / "results/xai/stage10_manifest.csv",
        ROOT / "results/xai/stage11_manifest.csv", ROOT / "results/xai/stage12_manifest.csv",
        ROOT / "results/xai/stage12_latency_summary.csv", ROOT / "results/xai/stage10_fidelity_summary.csv",
        ROOT / "results/xai/stage11_stability_summary.csv",
    ]
    rows = []
    for path in required:
        if not path.is_file(): raise RuntimeError(f"BLOCKED_INPUT_INTEGRITY missing {path}")
        rel = path.relative_to(ROOT).as_posix(); actual = sha(path); prior = expected.get(rel)
        if prior and actual != prior: raise RuntimeError(f"BLOCKED_INPUT_INTEGRITY hash mismatch {rel}")
        rows.append({"gate_id": GATE, "artifact_id": "ART-" + actual[:12].upper(), "path": rel, "sha256": actual, "registered_sha256": prior or actual, "verification_status": "VERIFIED"})
    write("stage13_input_manifest.csv", rows)


def structure(est: Any) -> tuple[dict[str, Any], dict[str, Any], int]:
    inv: dict[str, Any] = {k: "NOT_APPLICABLE" for k in ["number_of_support_vectors_if_any", "number_of_trees_if_any", "tree_depth_statistics_if_any", "number_of_nodes_if_any", "layer_sizes_if_any", "activation_if_any", "coefficient_shapes", "intercept_shapes"]}
    ops: dict[str, Any] = {"coefficients": "NOT_APPLICABLE", "bias_values": "NOT_APPLICABLE", "macs": "NOT_APPLICABLE", "class_score_operations": "NOT_APPLICABLE", "trees": "NOT_APPLICABLE", "total_nodes": "NOT_APPLICABLE", "leaf_count": "NOT_APPLICABLE", "max_depth": "NOT_APPLICABLE", "average_depth": "NOT_APPLICABLE", "comparison_count_estimate": "NOT_APPLICABLE", "support_vectors": "NOT_APPLICABLE", "kernel_evaluations": "NOT_APPLICABLE", "dot_or_distance_operations": "NOT_APPLICABLE", "weights": "NOT_APPLICABLE", "biases": "NOT_APPLICABLE", "activation_buffer_elements": "NOT_APPLICABLE", "output_buffer_elements": len(est.classes_)}
    if isinstance(est, LogisticRegression):
        count = est.coef_.size + est.intercept_.size
        inv.update(coefficient_shapes=j(list(est.coef_.shape)), intercept_shapes=j(list(est.intercept_.shape)))
        ops.update(coefficients=est.coef_.size, bias_values=est.intercept_.size, macs=est.coef_.size, class_score_operations=len(est.classes_))
    elif isinstance(est, RandomForestClassifier):
        nodes = sum(t.tree_.node_count for t in est.estimators_); leaves = sum(t.tree_.n_leaves for t in est.estimators_); depths = [t.tree_.max_depth for t in est.estimators_]
        # Structural elements include node feature, threshold, child indices, and leaf class values.
        count = nodes * 4 + sum(t.tree_.value.size for t in est.estimators_)
        inv.update(number_of_trees_if_any=len(est.estimators_), tree_depth_statistics_if_any=j({"min": min(depths), "mean": float(np.mean(depths)), "max": max(depths)}), number_of_nodes_if_any=nodes)
        ops.update(trees=len(est.estimators_), total_nodes=nodes, leaf_count=leaves, max_depth=max(depths), average_depth=float(np.mean(depths)), comparison_count_estimate=float(sum(depths)))
    elif isinstance(est, SVC):
        count = est.support_vectors_.size + est.dual_coef_.size + est.intercept_.size + est._probA.size + est._probB.size
        inv.update(number_of_support_vectors_if_any=est.support_vectors_.shape[0], coefficient_shapes=j(list(est.dual_coef_.shape)), intercept_shapes=j(list(est.intercept_.shape)))
        ops.update(support_vectors=est.support_vectors_.shape[0], kernel_evaluations=est.support_vectors_.shape[0], dot_or_distance_operations=est.support_vectors_.shape[0] * est.support_vectors_.shape[1], coefficients=est.dual_coef_.size, bias_values=est.intercept_.size)
    elif isinstance(est, MLPClassifier):
        weights = sum(x.size for x in est.coefs_); biases = sum(x.size for x in est.intercepts_); count = weights + biases
        layers = [est.coefs_[0].shape[0]] + [x.shape[1] for x in est.coefs_]
        inv.update(layer_sizes_if_any=j(layers), activation_if_any=est.activation, coefficient_shapes=j([list(x.shape) for x in est.coefs_]), intercept_shapes=j([list(x.shape) for x in est.intercepts_]))
        ops.update(weights=weights, biases=biases, macs=weights, activation_buffer_elements=max(layers[1:-1]), output_buffer_elements=layers[-1])
    else: raise RuntimeError(f"Unsupported inspected estimator {type(est)}")
    return inv, ops, int(count)


def inventories() -> tuple[dict[str, Any], dict[str, int]]:
    fmap = pd.read_csv(ROOT / "results/xai/stage09_feature_map.csv").sort_values("feature_index")
    order = fmap.original_name.astype(str).tolist(); order_hash = hashlib.sha256("\n".join(order).encode()).hexdigest()
    model_info = {}; parameter_counts = {}; inv_rows = []; prep_rows = []; op_rows = []; mem_rows = []
    for i in range(1, 5):
        mid = f"MODEL-C{i}"; pipe = load_frozen_pipeline(mid); scaler = pipe.named_steps["scaler"]; est = pipe.named_steps["model"]
        specific, ops, count = structure(est); parameter_counts[mid] = count
        params = est.get_params(deep=False)
        info = {"class": type(est).__name__, "module": type(est).__module__, "count": count}; model_info[mid] = info
        inv_rows.append({"model_id": mid, "python_estimator_class": type(est).__name__, "module": type(est).__module__, "hyperparameters": j(params), "number_of_input_features": est.n_features_in_, "number_of_classes": len(est.classes_), "number_of_parameters_or_equivalent_structural_elements": count, "model_specific_structure": j(ops), "requires_scaler": True, "requires_probability_calibration": isinstance(est, SVC) and bool(est.probability), "decision_function_type": "OVR" if getattr(est, "decision_function_shape", None) == "ovr" else "CLASS_SCORES" if hasattr(est, "decision_function") else "TREE_VOTE_PROBABILITIES", "supports_predict_proba": hasattr(est, "predict_proba"), "uses_kernel": isinstance(est, SVC), "kernel_type_if_any": est.kernel if isinstance(est, SVC) else "NOT_APPLICABLE", **specific, "serialized_python_artifact_bytes": model_path(mid).stat().st_size, "source_sha256": sha(model_path(mid))})
        constants = np.concatenate([scaler.mean_, scaler.scale_, scaler.var_])
        prep_rows.append({"model_id": mid, "input_dimension": scaler.n_features_in_, "feature_order": j(order), "feature_order_sha256": order_hash, "scaling_operation": "(x - mean_) / scale_", "stored_means": j(scaler.mean_), "stored_scales": j(scaler.scale_), "stored_variances": j(scaler.var_), "constants_sha256": hashlib.sha256(constants.astype("<f8").tobytes()).hexdigest(), "dtype": "float64_reference", "missing_value_behavior": "scaler_propagates_nonfinite; embedded protocol rejects nonfinite", "clipping": "NONE", "transform_ordering": "RAW_FEATURE_ORDER_THEN_STANDARD_SCALER_THEN_ESTIMATOR", "class_encoding": j(est.classes_), "output_decoding": "classes_[argmax_or_predict_index]"})
        op_rows.append({"gate_id": GATE, "model_id": mid, "model_type": type(est).__name__, **ops, "measurement_type": "DERIVED_ANALYTICAL"})
        # Raw scalar-equivalent parameter count is deliberately not compiled-memory evidence.
        for dtype, width, meaningful in [("FP64", 8, True), ("FP32", 4, True), ("INT16", 2, not isinstance(est, RandomForestClassifier)), ("INT8", 1, not isinstance(est, RandomForestClassifier))]:
            mem_rows.append({"gate_id": GATE, "model_id": mid, "model_type": type(est).__name__, "numeric_type": dtype, "structural_scalar_equivalents": count, "analytical_parameter_bytes": count * width if meaningful else "NOT_APPLICABLE", "preprocessing_constant_bytes": 256 * width if meaningful else "NOT_APPLICABLE", "measurement_type": "DERIVED_ANALYTICAL", "compiled_flash": "NOT_MEASURED", "compiled_sram": "NOT_MEASURED", "caveat": "Raw scalar-equivalent storage only; tree representation/runtime metadata may differ."})
    write("stage13_model_inventory.csv", inv_rows); write("stage13_preprocessing_inventory.csv", prep_rows); write("stage13_operation_counts.csv", op_rows); write("stage13_analytical_memory.csv", mem_rows)
    return model_info, parameter_counts


def golden_vectors() -> None:
    paths = {batch_number(p): p for p in discover_batches(ROOT / "data/raw")}; data = {b: load_batch(paths[b]) for b in [2, 6, 10]}
    dataset_hash = sha(ROOT / "data/manifests/dataset_manifest.json"); records = []; boundary_keys = set()
    for i in range(1, 5):
        mid = f"MODEL-C{i}"; pipe = load_frozen_pipeline(mid)
        for batch in [2, 6, 10]:
            x, y = data[batch]; prob = pipe.predict_proba(x); pred = pipe.predict(x); order = np.sort(prob, axis=1); margins = order[:, -1] - order[:, -2]
            selected: dict[int, set[str]] = {}
            for label in sorted(np.unique(y)):
                idxs = np.flatnonzero(y == label); idx = int(idxs[np.argmin(margins[idxs])]); selected.setdefault(idx, set()).add(f"CLASS_{label}_BOUNDARY")
            for idx, tag in [(int(np.argmin(margins)), "BATCH_NEAREST_BOUNDARY"), (int(np.argmax(prob.max(axis=1))), "BATCH_HIGH_CONFIDENCE")]: selected.setdefault(idx, set()).add(tag)
            correct = np.flatnonzero(pred == y); wrong = np.flatnonzero(pred != y)
            if len(correct): selected.setdefault(int(correct[0]), set()).add("CORRECT")
            if len(wrong): selected.setdefault(int(wrong[0]), set()).add("MISCLASSIFIED")
            boundary = np.argsort(margins)[:2]
            for idx in boundary:
                idx = int(idx); boundary_keys.add((mid, batch, idx)); selected.setdefault(idx, set()).add("BOUNDARY_STRESS_TOP2")
            for idx, tags in sorted(selected.items()):
                result = reference_inference(mid, x[idx]); raw = np.asarray(result["raw_features"]); transformed = np.asarray(result["transformed_features"])
                sample_hash = hashlib.sha256(np.asarray(raw, dtype="<f8").tobytes() + f"{batch}:{idx}".encode()).hexdigest()
                row = {"gate_id": GATE, "sample_id": f"GOLD-{mid}-B{batch}-R{idx:05d}", "model_id": mid, "batch": batch, "row_index_in_batch": idx, "true_label": int(y[idx]), "selection_categories": "|".join(sorted(tags)), "correct_prediction": bool(pred[idx] == y[idx]), "frozen_model_prediction": int(result["predicted_label"]), "predicted_label": int(result["predicted_label"]), "decision_scores": j(result["decision_scores"]), "probabilities": j(result["probabilities"]), "margin": result["margin"], "confidence": result["confidence"], "nearest_competing_class": result["nearest_competing_class"], "source_artifact": paths[batch].relative_to(ROOT).as_posix(), "source_dataset_manifest_sha256": dataset_hash, "source_sample_sha256": sample_hash, "model_sha256": result["model_sha256"]}
                row.update({f"raw_feature_{k:03d}": float(v) for k, v in enumerate(raw)}); row.update({f"transformed_feature_{k:03d}": float(v) for k, v in enumerate(transformed)}); records.append(row)
    write_path = ROOT / "data/manifests/embedded_golden_vectors.csv"; pd.DataFrame(records).to_csv(write_path, index=False)
    boundary = [r for r in records if (r["model_id"], r["batch"], r["row_index_in_batch"]) in boundary_keys]
    pd.DataFrame(boundary).to_csv(ROOT / "data/manifests/embedded_boundary_vectors.csv", index=False)


def matrices(info: dict[str, Any], counts: dict[str, int]) -> None:
    paths = {
        "MODEL-C1": [("MANUAL_STATIC_PARAMETERS", "SELECTED", "Direct multiclass linear scores plus stable softmax; transparent constants."), ("CMSIS_DSP", "DEFERRED", "Optional matrix kernels; unnecessary for first equivalence implementation."), ("ONNX_INTERMEDIATE", "VALIDATION_ONLY", "May validate conversion later; not an MCU runtime.")],
        "MODEL-C2": [("GENERATED_TREE_CODE", "SELECTED", "Direct static tree traversal is representable; compiled size remains unknown."), ("CUSTOM_EMBEDDED_KERNEL", "DEFERRED", "Possible static node arrays; higher verification complexity."), ("ONNX_INTERMEDIATE", "VALIDATION_ONLY", "Intermediate validation only.")],
        "MODEL-C3": [("GENERATED_SVM_CODE", "DEFERRED", "131 RBF support vectors are representable but kernel/probability semantics are difficult."), ("CUSTOM_EMBEDDED_KERNEL", "DEFERRED", "Requires exact RBF and pairwise multiclass/probability coupling."), ("ONNX_INTERMEDIATE", "VALIDATION_ONLY", "Intermediate validation only.")],
        "MODEL-C4": [("DIRECT_C_CPP", "SELECTED", "Dense 128-64-32-6 ReLU network can use static arrays and buffers."), ("CMSIS_NN", "DEFERRED", "Consider after transparent FP32 equivalence; neural kernels may help later."), ("TFLITE_MICRO", "DEFERRED", "Runtime overhead and operator support must be established later."), ("ONNX_INTERMEDIATE", "VALIDATION_ONLY", "Intermediate validation only.")],
    }
    rows=[]
    for mid, options in paths.items():
        for path, selection, reason in options:
            external = path in {"CMSIS_DSP", "CMSIS_NN", "TFLITE_MICRO", "ONNX_INTERMEDIATE"}
            rows.append({"model_id": mid, "export_path": path, "model_type_supported": "ANALYTICALLY_PLAUSIBLE", "preprocessing_supported": "DIRECT_STATIC_STANDARDIZATION", "probability_output_supported": "REQUIRES_EQUIVALENCE_VALIDATION", "required_runtime": "NONE_CUSTOM_STATIC" if not external else path, "dynamic_memory_required": False if path not in {"TFLITE_MICRO"} else "TBD", "static_memory_possible": True, "floating_point_required": "INITIAL_FP32_PATH", "integer_quantization_possible": "FUTURE_MODEL_APPROPRIATE_EVALUATION", "requires_model_internals": True, "requires_external_library": external, "library_version": "TBD_BEFORE_EXPORT" if external else "NOT_APPLICABLE", "license": "TBD_BEFORE_EXPORT" if external else "PROJECT_LICENSE", "expected_implementation_complexity": "HIGH" if mid in {"MODEL-C2", "MODEL-C3"} else "LOW" if mid == "MODEL-C1" else "MEDIUM", "verification_difficulty": "HIGH" if mid in {"MODEL-C2", "MODEL-C3"} else "MEDIUM", "embedded_feasibility_state": "UNTESTED_ANALYTICALLY_PLAUSIBLE", "selection_status": selection, "reason": reason})
    write("stage13_export_path_matrix.csv", rows)

    fidelity = pd.read_csv(ROOT / "results/xai/stage10_fidelity_summary.csv"); stability = pd.read_csv(ROOT / "results/xai/stage11_stability_summary.csv"); latency = pd.read_csv(ROOT / "results/xai/stage12_fidelity_stability_cost.csv"); op = pd.read_csv(ROOT / "results/xai/stage12_operation_counts.csv")
    xai=[]
    choices = [("MODEL-C1", "STATIC_GLOBAL_IMPORTANCE", "GLOBAL", "PRECOMPUTED_STATIC_EXPLANATION"), ("MODEL-C1", "LOCAL_LINEAR_CONTRIBUTION", "LOCAL", "PROTOCOL_DEFINED_EXPORT_CANDIDATE")]
    for mid in [f"MODEL-C{i}" for i in range(1,5)]:
        choices += [(mid, "LOCAL_VECTOR_ABLATION", "LOCAL", "DEFERRED_RESOURCE_INTENSIVE"), (mid, "SENSOR_GROUP_EXPLANATION", "DERIVED_VIEW", "DERIVED_SENSOR_GROUP_VIEW_ONLY"), (mid, "HOST_ONLY_XAI", "HOST", "AVAILABLE")]
        if mid == "MODEL-C2": choices.append((mid, "STATIC_GLOBAL_IMPORTANCE", "GLOBAL", "PRECOMPUTED_STATIC_EXPLANATION"))
    for mid, method, scope, state in choices:
        f = fidelity[fidelity.model_id.eq(mid)]; s = stability[stability.model_id.eq(mid)]; l = latency[latency.model_id.eq(mid)]; c = op[op.model_id.eq(mid)]
        repeated = method == "LOCAL_VECTOR_ABLATION"; static = method == "STATIC_GLOBAL_IMPORTANCE"
        xai.append({"model_id":mid,"XAI_method":method,"XAI_scope":scope,"Stage10_fidelity_evidence":j(f[["scope","method","mean"]].to_dict("records")),"Stage11_stability_evidence":j(s[["scope","method","metric_name","mean"]].to_dict("records")),"Stage12_host_cost":j(l[["method","scope","median_us","p95_us"]].to_dict("records")),"prediction_calls":2 if repeated else 0 if static else "METHOD_DEPENDENT","parameter_requirements":"128 feature values" if method in {"LOCAL_LINEAR_CONTRIBUTION","LOCAL_VECTOR_ABLATION"} else "stored ranking/vector","requires_labels":False,"requires_dataset":False,"requires_model_internals":method in {"LOCAL_LINEAR_CONTRIBUTION","STATIC_GLOBAL_IMPORTANCE"},"requires_repeated_inference":repeated,"can_be_precomputed":static,"supports_local_online_explanation":method in {"LOCAL_LINEAR_CONTRIBUTION","LOCAL_VECTOR_ABLATION"},"numerical_verification_path":"feature attribution vector then ranking equivalence","embedded_feasibility_status":state})
    write("stage13_xai_architecture_matrix.csv", xai)

    # Deterministic tiers use export transparency, analytical size, and evidence limitations—not a weighted score.
    tier = {"MODEL-C1":"TIER_A_EXPORT_FIRST","MODEL-C2":"TIER_B_EXPORT_IF_RESOURCES_ALLOW","MODEL-C3":"TIER_C_RESEARCH_COMPARATOR","MODEL-C4":"TIER_A_EXPORT_FIRST"}
    method = {"MODEL-C1":"LOCAL_LINEAR_CONTRIBUTION","MODEL-C2":"STATIC_GLOBAL_IMPORTANCE","MODEL-C3":"HOST_ONLY_XAI","MODEL-C4":"NO_ON_DEVICE_XAI"}
    path = {"MODEL-C1":"MANUAL_STATIC_PARAMETERS","MODEL-C2":"GENERATED_TREE_CODE","MODEL-C3":"GENERATED_SVM_CODE","MODEL-C4":"DIRECT_C_CPP"}
    candidates=[]
    for mid in tier:
        fp32=counts[mid]*4; int8=counts[mid] if mid != "MODEL-C2" else "NOT_APPLICABLE"
        candidates.append({"candidate_id":f"EMBED-{mid[-2:]}","model_id":mid,"model_type":info[mid]["class"],"export_path":path[mid],"preprocessing_path":"DIRECT_STATIC_STANDARD_SCALER","numeric_type_initial":"FP32","XAI_method":method[mid],"XAI_scope":"LOCAL" if method[mid]=="LOCAL_LINEAR_CONTRIBUTION" else "GLOBAL" if method[mid]=="STATIC_GLOBAL_IMPORTANCE" else "HOST","Stage10_fidelity_summary":"SEE_STAGE13_XAI_ARCHITECTURE_MATRIX","Stage11_stability_summary":"SEE_STAGE13_XAI_ARCHITECTURE_MATRIX","Stage12_host_cost_summary":"SEE_STAGE13_XAI_ARCHITECTURE_MATRIX","structural_parameter_count":counts[mid],"analytical_fp32_parameter_bytes":fp32,"analytical_int8_parameter_bytes_if_valid":int8,"runtime_prediction_calls":1,"requires_dynamic_memory":False,"requires_runtime_dataset":False,"requires_labels":False,"expected_static_storage":True,"equivalence_test_defined":True,"quantization_candidate":"FUTURE_ONLY_MODEL_APPROPRIATE","hardware_compile_candidate":"AFTER_FP32_EQUIVALENCE","status":tier[mid],"reason":{"MODEL-C1":"Transparent compact linear path and validated inexpensive local contribution; still requires FP32 equivalence.","MODEL-C2":"Tree comparator retained for scientific evidence; analytical structure is larger and compile size unknown.","MODEL-C3":"Prediction export remains research comparator; current XAI evidence is weak and RBF/probability verification is difficult.","MODEL-C4":"Static dense FP32 path is plausible; on-device XAI deferred because only repeated ablation is validated."}[mid]})
    write("stage13_candidate_matrix.csv", candidates)
    write("stage13_decision.csv", [{"gate_id":GATE,"timestamp":datetime.now(timezone.utc).isoformat(),"stage13_protocol_status":"FROZEN","model_export_status":"NOT_EXECUTED","quantization_status":"NOT_EXECUTED","firmware_status":"NOT_EXECUTED","mcu_measurement_status":"NOT_EXECUTED","energy_status":"NOT_EXECUTED","decision":"AUTHORIZE_FP32_EXPORT_EQUIVALENCE_TEST","authorized_next_scope":"Separate future experiment; C1 and C4 first; no quantization authorization","reason":"C1 and C4 have transparent static FP32 representations and frozen three-level equivalence criteria; C2 remains a resource-dependent comparator and C3 a research comparator."}])


def manifest() -> None:
    paths = [
        "docs/embedded/STAGE13_EMBEDDED_EXPORT_PROTOCOL.md", "docs/embedded/EMBEDDED_NUMERICAL_EQUIVALENCE_PROTOCOL.md",
        "docs/embedded/EMBEDDED_ARCHITECTURE_DECISION.md", "configs/embedded_equivalence_protocol.yaml",
        "configs/nrf52840_resource_budget.yaml", "embedded/preprocessing_spec.yaml",
        "data/manifests/embedded_golden_vectors.csv", "data/manifests/embedded_boundary_vectors.csv",
    ] + [f"results/embedded/{name}" for name in ["stage13_input_manifest.csv", "stage13_model_inventory.csv", "stage13_preprocessing_inventory.csv", "stage13_export_path_matrix.csv", "stage13_candidate_matrix.csv", "stage13_analytical_memory.csv", "stage13_operation_counts.csv", "stage13_xai_architecture_matrix.csv", "stage13_decision.csv"]]
    rows=[]
    for rel in paths:
        path=ROOT/rel
        if not path.exists(): continue
        rows.append({"gate_id":GATE,"artifact_path":rel,"sha256":sha(path),"rows":sum(1 for _ in path.open(encoding="utf-8"))-1 if path.suffix==".csv" else "","evidence_state":"PROTOCOL_FROZEN"})
    write("stage13_manifest.csv", rows)


def main() -> None:
    verify_inputs(); info, counts = inventories(); golden_vectors(); matrices(info, counts); manifest()
    print(json.dumps({"gate_id":GATE,"protocol":"FROZEN","model_export":"NOT_EXECUTED","quantization":"NOT_EXECUTED","firmware":"NOT_EXECUTED","mcu_measurement":"NOT_EXECUTED","energy":"NOT_EXECUTED"}, indent=2))


if __name__ == "__main__": main()
