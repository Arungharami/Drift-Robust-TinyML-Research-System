# Platform Provenance Graph

How a result flows from code to verified cross-platform evidence, and which platform is allowed
to originate what. See [`docs/RESEARCH_PLATFORM_BRIDGE.md`](RESEARCH_PLATFORM_BRIDGE.md) for the
full policy this diagram summarizes.

```
             GitHub  (canonical: code, configs, tests, CI, manifests, paper source)
               |
         Git SHA / CI
               |
              VS Code  (Codex / Claude control plane)
               |
         Research Bundle  (scripts/bridge/build_release_bundle.sh — secret-scanned)
          /           \
      Colab           Kaggle
        |                |
  Primary Compute   Independent Repro
  (WSL2-gated CLI    (same Git SHA / dataset SHA /
   or interactive     config as GitHub evidence —
   kernel)             never live-synced from Colab)
        |
   Verified Results
   (hash-checked: local SHA-256
    == downloaded-remote SHA-256)
        |
   GitHub Evidence
   (results/reproducibility/, committed)
        |
    Hugging Face
  Models / Artifacts
  (private by default; only
   COMPLETED, validated
   bundles are ever pushed)
```

Google Drive sits beside Colab as persistent storage for large temporary artifacts (executed
notebooks, large predictions, checkpoints, logs) — it is never in this evidence chain as a
source, only as overflow storage a Colab session writes to and a human later triages.

## Reading the graph

- **Downward arrows are what's allowed to happen.** GitHub → VS Code → bundle → {Colab, Kaggle}
  → verified results → GitHub evidence → Hugging Face. There is no arrow from Hugging Face or
  Kaggle back into "GitHub canonical" — a Hub/Kaggle asset can only ever be evidence *derived
  from* a GitHub-recorded state, never the other way around.
- **Colab and Kaggle are parallel, not sequential.** Colab is primary compute; Kaggle is
  independent verification of the same Git SHA. Neither platform's raw session state feeds the
  other directly — only a versioned bundle does.
- **Every arrow that crosses a platform boundary carries a hash.** Local SHA-256 computed before
  upload, remote SHA-256 recomputed after download, compared, recorded in
  `results/reproducibility/bridge/artifact_index.csv`. An arrow without a verified hash is not
  yet trusted evidence.
- **The graph terminates at GitHub evidence before Hugging Face, not after.** A model or dataset
  only reaches Hugging Face after its results are already committed as GitHub evidence — Hugging
  Face publishes what GitHub has already recorded, it never originates it.
