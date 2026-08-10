# Google Colab guide

In VS Code, open a notebook and choose **Select Kernel → Colab → Auto Connect**. Run notebook 00 first. A Colab run is genuine only when `in_colab` is `true` in `results/reproducibility/environment.json` and notebook execution metadata/output is retained.

For private GitHub access, add `GITHUB_TOKEN` under Colab **Secrets** and enable notebook access. Read it only with `from google.colab import userdata; token = userdata.get("GITHUB_TOKEN")`. Never print, display, persist, or embed the token in a remote URL stored by Git. Prefer a short-lived, least-privilege token and remove authenticated remotes after cloning.
