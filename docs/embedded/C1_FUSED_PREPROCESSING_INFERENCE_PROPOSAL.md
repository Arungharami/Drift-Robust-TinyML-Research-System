# C1 fused preprocessing/inference proposal — not executed

A future separately frozen experiment may derive `w_raw[c,i]=w[c,i]/scale[i]` and `b_raw[c]=intercept[c]-sum_i(w[c,i]*mean[i]/scale[i])`, then infer directly from raw inputs. This cannot retroactively satisfy explicit preprocessing equivalence and was not generated, compiled, or tested in Stage 14R.
