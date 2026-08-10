# platforms/ — staged external-platform assets

Everything under this directory is staged content for Hugging Face Hub and Kaggle — cards,
metadata, and an independent reproduction notebook. **Nothing here uploads itself.** GitHub
remains canonical; see [`docs/RESEARCH_PLATFORM_BRIDGE.md`](../docs/RESEARCH_PLATFORM_BRIDGE.md).

- `huggingface/dataset/README.md` — dataset card for the private HF evidence repo (Mission 7).
- `huggingface/model/README.md` — model card template; stays `NOT_EXECUTED` until a real
  `COMPLETED` experiment bundle exists (Mission 8).
- `kaggle/dataset/` — staged by `scripts/bridge/prepare_kaggle_dataset.py`: small evidence files
  + `dataset-metadata.json`. `id` reads `USERNAME_NOT_DISCOVERED/...` until `kaggle auth login`
  succeeds and the script is re-run — that placeholder is intentional, not a bug, and a real
  push (`kaggle datasets create`) with that placeholder in place would fail loudly rather than
  silently uploading to the wrong account.
- `kaggle/kernel/` — `drift_tinyml_reproduction.ipynb` (Missions 12-13, template/NOT_EXECUTED)
  + `kernel-metadata.json` staged by `scripts/bridge/prepare_kaggle_kernel.py`, same placeholder
  behavior as above.

Re-run the two `prepare_kaggle_*` scripts after authenticating to replace the placeholder
username with the real one before ever running `kaggle datasets create` / `kaggle kernels push`.
