# AI Agent Platform Tools

How Codex/Claude, GitHub, Colab, Hugging Face, and Kaggle divide responsibility when an AI
agent is driving this workspace (Mission 28).

## Responsibilities

| Actor | Responsible for | Not responsible for |
|---|---|---|
| **Codex / Claude (this agent)** | Orchestrating the other four via VS Code tasks / shell scripts; writing/reviewing code, configs, docs; running local validation (compile, pytest, YAML/JSON/notebook checks); secret-scanning before any upload; reporting real observed state honestly (`NOT_EXECUTED` stays `NOT_EXECUTED` until actually verified). | Authenticating interactively on the user's behalf (OAuth/browser flows require the human); making any asset public; inventing IDs, hashes, or results it didn't observe. |
| **GitHub** | Canonical source of truth — code, configs, tests, CI, small evidence artifacts, Git history, PR review. | Compute, large artifact storage. |
| **Colab** | Primary cloud compute for real notebook execution (WSL2-CLI or interactive kernel). | Canonical code or canonical results storage. |
| **Hugging Face** | Research artifact hub — model/dataset cards, validated model releases, derived datasets. | Canonical source of truth; raw UCI data redistribution. |
| **Kaggle** | Independent reproduction platform — verifies GitHub-recorded results from the same Git SHA/dataset SHA/config, on separate infrastructure. | Canonical source of truth; primary compute. |

## The `hf-cli` agent skill

The installed `hf` CLI (1.27.0) offers `hf skills add`, which can generate a local `hf-cli`
skill (from the installed CLI version) or download a marketplace skill, optionally symlinked
into Claude's skills directory with `--claude`.

**This was investigated (`hf skills add --help`) but deliberately not installed automatically**
— Mission 28 requires inspecting before installing, and this repository's policy is not to
modify agent configuration outside an explicit user request. To install it:

```bash
hf skills add --claude          # project-local skill (.agents/skills)
hf skills add -g --claude       # user-level/global skill (~/.agents/skills)
```

Do this only if you (the user) want Claude's `hf` command usage informed by a skill generated
from your exact installed CLI version. It is optional and orthogonal to everything else in this
bridge — none of `scripts/bridge/*` depend on it.

## Agent-side guardrails already in place

- `src/research_bridge/secrets.py` — filename denylist + content pattern scan, run before every
  release bundle and every Hugging Face upload script.
- `configs/research_bridge.yaml` — `github.canonical: true` and
  `{huggingface,kaggle}.private_by_default: true` are enforced by the config loader itself
  (`BridgeConfigError` on violation), not just by convention.
- `push_hf_model.sh` refuses to run against any bundle whose `manifest.json.status` is not
  exactly `COMPLETED`.
- No script in `scripts/bridge/` or `scripts/colab/` ever prints a token; `gh auth status`,
  `hf auth whoami`, and `kaggle config view` output is captured and parsed, never echoed with
  `--show-token` or equivalent.
