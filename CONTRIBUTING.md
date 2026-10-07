# Contributing

Useful contributions to **Drift-Robust-TinyML-Research-System** include:

- Reproduce an existing host-side check and report the exact configuration and source commit.
- Improve instructions for an existing export or explanation workflow.
- Review the real-board instrumentation plan without substituting host measurements for physical evidence.

## Reporting a problem

Check existing issues first. Include the source commit or branch, environment, minimal steps, expected behavior, actual behavior, and a redacted error. State whether you used real data, an educational fixture, or exported results. Keep credentials and personal records out of public reports.

## Proposing a change

Choose one bounded task. Describe the intended behavior and how it will be checked before a large implementation. Use a focused branch and draft pull request; link any existing issue. Record exactly which checks ran, including failures and unavailable checks. Do not report a full suite as passed after running only a subset.

## Relevant local checks

These are focused checks, not a replacement for the full project workflow in the README.

```bash
python -m compileall -q src
pytest -q
```

## Project evidence and boundaries

Follow AGENTS.md. Preserve frozen protocols and unsupported findings. No stage registry, generated portal evidence, manuscript result, or hardware measurement is changed by this contribution guide.

[Project overview and setup](README.md) · [Issues](https://github.com/Arungharami/Drift-Robust-TinyML-Research-System/issues) · [Author's portfolio](https://arungharami.info)
