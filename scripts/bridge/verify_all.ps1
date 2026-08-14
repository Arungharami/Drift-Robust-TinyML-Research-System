# scripts/bridge/verify_all.ps1 — Windows-native equivalent of verify_all.sh.
# gh / hf / kaggle all run natively on Windows (unlike the WSL-gated Colab CLI), so this
# wrapper needs neither WSL nor Git Bash — useful when a user prefers a plain PowerShell task.
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $RepoRoot

function Log($msg) { Write-Output "[bridge] $msg" }

Log "=== GitHub ==="
$ghVersion = (gh --version | Select-Object -First 1)
$authStatus = (gh auth status 2>&1 | Out-String)
$branch = (git branch --show-current)
$sha = (git rev-parse HEAD)
$remote = (git remote get-url origin)
$repository = (python scripts/bridge/read_config.py github.repository)
python scripts/bridge/write_platform_status.py github --cli-version "$ghVersion" --auth-status "$authStatus" --repository "$repository" --branch "$branch" --commit "$sha" --remote "$remote"

Log "=== Hugging Face ==="
$hfVersion = (hf version 2>&1 | Out-String)
$whoami = (hf auth whoami 2>&1 | Out-String)
python scripts/bridge/write_platform_status.py huggingface --cli-version "$hfVersion" --whoami "$whoami"

Log "=== Kaggle ==="
$kaggleVersion = (kaggle --version 2>&1 | Out-String)
$probe = (kaggle config view 2>&1 | Out-String)
python scripts/bridge/write_platform_status.py kaggle --cli-version "$kaggleVersion" --auth-probe "$probe"

Log "Status files written under results/reproducibility/bridge/."
Log "Run: python scripts/bridge/bridge_status.py   for a consolidated summary (includes Colab/Drive)."
