# Manuscript workflow

The manuscript is downstream of the evidence system.

## Rule

Do not write numerical Results claims before the corresponding executed artifact exists and has been checked against the frozen protocol.

## Recommended structure

```text
paper/
├── notes/              # literature notes and advisor decisions
├── tables/             # manuscript-ready tables generated from evidence
├── figures/            # manuscript-ready figures generated from evidence
├── drafts/             # working manuscript source
└── final/              # validated submission/final PDF
```

## Evidence-to-paper gate

A result may enter the manuscript only when all relevant items are available:

1. experiment configuration;
2. data/split manifest;
3. source commit;
4. saved metric or raw measurement log;
5. model/export checksum when applicable;
6. hardware build/log/PPK2 trace when a hardware claim is made;
7. table/figure generation path.

Failures and `NOT EXECUTED` outcomes should remain visible in the project record rather than being silently removed.
