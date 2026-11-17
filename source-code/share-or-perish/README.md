# Share or Perish — independent security & privacy review

Companion artifacts for [monero-project/research-lab#146](https://github.com/monero-project/research-lab/issues/146)
("Share or Perish", selfish-mining mitigation proposal by tevador).

Contents:

- `SECURITY-PRIVACY-REVIEW.md` — full review: verification runs, spec errata
  (E1–E10), security analysis (S1–S8), privacy analysis (P1–P5), simulator
  defects (B1–B10), negative results.
- `ERRATA.md` — triage-ready table with proposed resolutions (F1–F10 in the
  review map to these).
- `blockchain_sim.py` — patched appendix simulator: model logic unchanged;
  adds seeds, CLI, ZeroDivision guard, reorg-depth statistics, Poisson CI,
  and a difficulty-adjustment time-scale column. Original model
  (c) tevador, MIT; patches MIT.
- `results/` — command lines + outputs for every number quoted in the review.

All rates are reported in honest-only-difficulty sim-time (see review §2.1:
real-world intervals are ×(H+A)/H longer; the effect direction is
conservative for the proposal's security claims).
