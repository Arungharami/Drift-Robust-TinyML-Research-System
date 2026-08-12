"""Build Stage 10 figures from saved CSV evidence only."""
from pathlib import Path
import csv, hashlib
import matplotlib.pyplot as plt
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; out=ROOT/"results/figures"; src=out/"sources"; src.mkdir(parents=True,exist_ok=True)
plt.style.use("seaborn-v0_8-whitegrid")

g=pd.read_csv(ROOT/"results/xai/stage10_fidelity_global.csv")
d=g.groupby(["model_id","method","k"],as_index=False)[["macro_f1_damage","random_damage_mean"]].mean(); d.to_csv(src/"fid_01_deletion_vs_random.csv",index=False)
fig,ax=plt.subplots(figsize=(10,5)); labels=d.model_id+"\n"+d.method.str.replace("PERMUTATION_IMPORTANCE_MACRO_F1","PERMUTATION",regex=False); x=range(len(d)); ax.scatter(x,d.macro_f1_damage,label="Top-K",s=24); ax.scatter(x,d.random_damage_mean,label="Matched random",s=24); ax.set_xticks(list(x),labels,rotation=90,fontsize=6); ax.set_ylabel("Mean macro-F1 damage (proportion)"); ax.legend(); fig.tight_layout(); fig.savefig(out/"fid_01_deletion_vs_random.png",dpi=180); fig.savefig(out/"fid_01_deletion_vs_random.svg"); plt.close(fig)

c=g.groupby(["model_id","method","batch"],as_index=False).selected_minus_random.mean(); c.to_csv(src/"fid_02_chronological_fidelity.csv",index=False)
fig,ax=plt.subplots(figsize=(9,5));
for keys,z in c.groupby(["model_id","method"]): ax.plot(z.batch,z.selected_minus_random,marker="o",label=" / ".join(keys))
ax.axhline(0,color="black",lw=.8); ax.set(xlabel="Chronological batch",ylabel="Mean selected − random macro-F1 damage"); ax.legend(fontsize=6,ncol=2); fig.tight_layout(); fig.savefig(out/"fid_02_chronological_fidelity.png",dpi=180); fig.savefig(out/"fid_02_chronological_fidelity.svg"); plt.close(fig)

l=pd.read_csv(ROOT/"results/xai/stage10_fidelity_local.csv"); e=l.groupby(["model_id","method","category"],as_index=False).selected_minus_random.mean(); e.to_csv(src/"fid_03_error_conditioned.csv",index=False)
fig,ax=plt.subplots(figsize=(10,5)); pivot=e.pivot_table(index=["model_id","method"],columns="category",values="selected_minus_random"); pivot.plot.bar(ax=ax); ax.set_ylabel("Mean selected − random target-score drop"); ax.legend(fontsize=6); fig.tight_layout(); fig.savefig(out/"fid_03_error_conditioned.png",dpi=180); fig.savefig(out/"fid_03_error_conditioned.svg"); plt.close(fig)

s=pd.read_csv(ROOT/"results/xai/stage10_fidelity_sensor_groups.csv"); z=s.groupby(["model_id","method","sensor_k"],as_index=False).selected_minus_random.mean(); z.to_csv(src/"fid_04_sensor_groups.csv",index=False)
fig,ax=plt.subplots(figsize=(9,5));
for keys,q in z.groupby(["model_id","method"]): ax.plot(q.sensor_k,q.selected_minus_random,marker="o",label=" / ".join(keys))
ax.axhline(0,color="black",lw=.8); ax.set(xlabel="Top sensor groups removed",ylabel="Mean selected − random macro-F1 damage"); ax.legend(fontsize=6,ncol=2); fig.tight_layout(); fig.savefig(out/"fid_04_sensor_groups.png",dpi=180); fig.savefig(out/"fid_04_sensor_groups.svg"); plt.close(fig)
manifest=ROOT/"results/xai/stage10_manifest.csv"; existing=pd.read_csv(manifest).to_dict("records")
paths=[]
for stem in ("fid_01_deletion_vs_random","fid_02_chronological_fidelity","fid_03_error_conditioned","fid_04_sensor_groups"):
    paths += [out/f"{stem}.png",out/f"{stem}.svg",src/f"{stem}.csv"]
known={r["artifact_path"] for r in existing}
for path in paths:
    rel=path.relative_to(ROOT).as_posix()
    if rel not in known: existing.append({"experiment_id":"EXP-XAI-FIDELITY-001","artifact_path":rel,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"rows":sum(1 for _ in path.open(encoding="utf-8"))-1 if path.suffix==".csv" else "","status":"EXECUTED"})
with manifest.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["experiment_id","artifact_path","sha256","rows","status"]); w.writeheader(); w.writerows(existing)
print("Generated FID-01 through FID-04 from saved source CSVs and hashed every artifact.")
