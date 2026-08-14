"""Generate Stage 11 figures exclusively from saved Stage 11/10 CSV evidence."""
from pathlib import Path
import csv,hashlib
import matplotlib.pyplot as plt
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];out=ROOT/"results/figures";src=out/"sources";src.mkdir(parents=True,exist_ok=True);plt.style.use("seaborn-v0_8-whitegrid")
spec=[]
gr=pd.read_csv(ROOT/"results/xai/stage11_global_rank_stability.csv")
d=gr.groupby(["model_id","comparison_type"],as_index=False)[["jaccard_at_5","jaccard_at_10","jaccard_at_20"]].mean();spec.append(("stab_01_topk_overlap",d,"bar",["jaccard_at_5","jaccard_at_10","jaccard_at_20"],"Top-K Jaccard"))
d=gr.groupby(["model_id","comparison_type"],as_index=False)[["spearman","kendall_tau_b"]].mean();spec.append(("stab_02_rank_stability",d,"bar",["spearman","kendall_tau_b"],"Rank correlation"))
s=pd.read_csv(ROOT/"results/xai/stage11_sensor_stability.csv");d=s.groupby("model_id",as_index=False)[["sensor_spearman","sensor_importance_l1_distance"]].mean();spec.append(("stab_03_sensor_stability",d,"bar",["sensor_spearman","sensor_importance_l1_distance"],"Sensor stability metric"))
f=pd.read_csv(ROOT/"results/xai/stage11_feature_family_stability.csv");d=f.groupby("model_id",as_index=False)[["family_rank_spearman","family_importance_l1_distance","dominant_family_changed"]].mean();spec.append(("stab_04_family_evolution",d,"bar",["family_rank_spearman","family_importance_l1_distance","dominant_family_changed"],"Family metric"))
r=pd.read_csv(ROOT/"results/xai/stage11_relative_stability.csv");r=r[r.epsilon==1e-6];d=r[["model_id","method","batch_a","batch_b","comparison_type","explanation_distance","input_change","model_macro_f1_change"]];spec.append(("stab_05_explanation_vs_input",d,"scatter",["input_change","explanation_distance"],"Explanation vs input change"));spec.append(("stab_06_explanation_vs_performance",d,"scatter",["model_macro_f1_change","explanation_distance"],"Explanation vs macro-F1 change"))
n=pd.read_csv(ROOT/"results/xai/stage11_local_neighbor_stability.csv");d=n.groupby(["model_id","method","category"],as_index=False).explanation_distance.mean();spec.append(("stab_07_error_conditioned",d,"bar",["explanation_distance"],"Mean explanation distance"))
l=pd.read_csv(ROOT/"results/xai/stage11_fidelity_stability_link.csv");d=l[["scope","model_id","method","n","spearman","ci_low","ci_high"]];spec.append(("stab_08_fidelity_vs_stability",d,"point",["spearman"],"Spearman correlation"))
created=[]
for stem,d,kind,cols,ylabel in spec:
 d.to_csv(src/f"{stem}.csv",index=False);fig,ax=plt.subplots(figsize=(10,5))
 if kind=="scatter":
  for m,g in d.groupby("model_id"):ax.scatter(g[cols[0]],g[cols[1]],label=m,alpha=.75)
  ax.set_xlabel(cols[0].replace("_"," "));ax.legend(fontsize=7)
 elif kind=="point":
  x=range(len(d));ax.errorbar(list(x),d.spearman,yerr=[d.spearman-d.ci_low,d.ci_high-d.spearman],fmt="o");ax.set_xticks(list(x),(d.model_id+"\n"+d.scope).tolist(),rotation=70,fontsize=7);ax.axhline(0,color="black",lw=.8)
 else:
  index=[c for c in d.columns if c not in cols];d.set_index(index)[cols].plot.bar(ax=ax);ax.legend(fontsize=7)
 ax.set_ylabel(ylabel);fig.tight_layout();fig.savefig(out/f"{stem}.png",dpi=180);fig.savefig(out/f"{stem}.svg");plt.close(fig);created += [out/f"{stem}.png",out/f"{stem}.svg",src/f"{stem}.csv"]
manifest=ROOT/"results/xai/stage11_manifest.csv";records=pd.read_csv(manifest).to_dict("records");known={r["artifact_path"] for r in records}
for p in created:
 rel=p.relative_to(ROOT).as_posix()
 if rel not in known:records.append({"experiment_id":"EXP-XAI-STABILITY-001","artifact_path":rel,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"rows":sum(1 for _ in p.open(encoding="utf-8"))-1 if p.suffix==".csv" else "","status":"EXECUTED"})
with manifest.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["experiment_id","artifact_path","sha256","rows","status"]);w.writeheader();w.writerows(records)
print("Generated STAB-01 through STAB-08 with source CSVs and hashes.")
