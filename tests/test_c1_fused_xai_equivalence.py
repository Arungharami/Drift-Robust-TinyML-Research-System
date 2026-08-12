from pathlib import Path
import pandas as pd,yaml
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"results/embedded";GEN=ROOT/"embedded/generated/c1_fused"

def test_xai_protocol_and_scope():
 c=yaml.safe_load((ROOT/"configs/c1_fused_xai_equivalence.yaml").read_text());assert c["tolerances"]["attribution_max_absolute_error"]==2e-5;assert c["tolerances"]["vector_max_l1_error"]==5e-4;assert c["tolerances"]["additivity_max_absolute_error"]==2e-4
 src=(GEN/"xai_c1_fused.c").read_text();assert "x[i]-c1_xai_means[i]" in src and "double" not in src and "quant" not in src.lower()

def test_xai_all_rows_and_criteria():
 a=pd.read_csv(OUT/"c1_fused_xai_attribution_equivalence.csv");v=pd.read_csv(OUT/"c1_fused_xai_vector_summary.csv");t=pd.read_csv(OUT/"c1_fused_xai_topk_equivalence.csv");s=pd.read_csv(OUT/"c1_fused_xai_sign_equivalence.csv");d=pd.read_csv(OUT/"c1_fused_xai_additivity.csv")
 assert len(a)==54*128 and a.sample_id.nunique()==54;assert a.absolute_error.max()<=2e-5;assert v.attribution_vector_l1_error.max()<=5e-4;assert t.set_agreement.all();assert s.loc[s.eligible_for_mandatory_sign,"sign_agreement"].all();assert d.additivity_absolute_error.max()<=2e-4

def test_xai_claim_and_hardware_boundary():
 c=pd.read_csv(OUT/"c1_fused_xai_claim_evaluation.csv").iloc[0];assert c.status=="SUPPORTED"
 stages=yaml.safe_load((ROOT/"configs/pipeline_stages.yaml").read_text())["stages"];assert next(x for x in stages if x["id"]=="14F-XAI")["status"]=="EXECUTED";assert next(x for x in stages if x["id"]=="15")["status"]!="EXECUTED"
