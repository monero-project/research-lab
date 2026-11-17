# Share or Perish — errata & proposed amendments

Actionable companion to `SECURITY-PRIVACY-REVIEW.md`. IDs match the review.
Severities: High = exploitable or produces divergent implementations; Med =
spec gap that needs an answer before implementation; Low = editorial.

## Spec (issue #146 body)

| ID | Sev | Where | Problem | Proposed resolution |
|----|-----|-------|---------|---------------------|
| E1 | High | body vs 2026-10-15/17 comments | Body still has `ref_seen`, `n_max < (k−1)·w` (32 objects); comments describe `main_seen`, `n_f`, "≥48 work objects". Appendix sim matches body (32). **Measured impact: the readings differ 12.7× in depth-≥1 attack frequency** (§2 of the review). | Publish one normative revision; state explicitly whether the objective trigger is 32 or 48 objects. |
| E3 | High | §2.3, §4 | Pool scoring counts *all* valid pool shares extending the tip; duplicate-slot variants are never excluded, and the pool has no cap. An attacker can spray many valid same-slot variants above its own tip and inflate its `sop_objective` score by (n−1)·diff/w in exactly the 32–160-object region. | Count at most one share per `minor_version` slot (first-seen); pool capped at 200 entries; P2P rate-limit per slot. |
| E2 | Med | §2.1 | Option 2 commits to a *set* of workshares but shares are slot-ordered; commitment construction unspecified. | Ordered commitment (slot-major Merkle); specify leaf encoding. |
| E10 | Med | §2.2 | Slot (`minor_version`) not present in the 4-field share serialization; position-in-tx_extra implies it for option 1, option 2 P2P format unstated. | State where the slot lives in the P2P serialization. |
| E9 | Med | §2.3 | "minor_version that follows the sequentiality rule" undefined without a containing block. | Pool share occupies the first unfilled slot for that tip. |
| E4 | Low-Med | §4 | `y.height` undefined; share validation difficulty ambiguous. | `y.height := height(y.prev_id)+1`; threshold `diff(y.height)/w`. |
| E5 | Low | Table 1 | `k` redefined vs PoP (objects, not blocks) without saying so. | Redefine in Table 1. |
| E6 | Low | §5 note | Hardcoded "160"; elsewhere `10·w`. | Use `10·w`. |
| E7 | Low | Tables 4–5 | Mixed boundary rules (`>d` vs `≤d`) + integer timestamps → 1-second edge game. | Consistent half-open intervals; consider ms. |
| E8 | Low | §2.2 | 200-cap vs real bound `255 − major_version`; "first 200" unspecified. | `min(200, 255−major)`; note builder's choice. |

## Security amendments

| ID | Sev | Topic | Proposal |
|----|-----|-------|----------|
| S1 | Med | §5.1 tie-breaking | Exact ties are not rare (≈7% of symmetric forks by share-count equality, plus cross-height ties). Prefer greater height on tie, then random; document split-brain exposure. |
| S2 | Low-Med | §5 step 4 | Batch removal of all lowest-scoring chains can discard a would-be winner after h_f advances; prove order-independence or remove one-at-a-time. |
| S3 | Med | §6 | Add explicit eclipse damage bound (subjective+objective windows ≤ 160 blocks) and an eclipse-mode simulation; the uniqueness-rule advantage presumes honest share flow. |
| S4 | Med | §6.3 | Present partition recovery as a trade-off: SoP ≈ 3.4/3.4/2.0 blocks for 1-1/2-2/3-3 splits vs ≈1.1 Nakamoto (independent measurement); define "3 blocks from the fork point". |
| S5 | Med | §6 | Add incentive analysis (orphan-rate reduction vs relay cost; two-pool collusion case). |
| S6 | Low | §2.2/§2.3 | Builder SHOULD include first-seen valid share per slot. |
| S8 | Med | §6.2 | Add d-sensitivity results (0.5/1/3/5 s) or state the 0.5 s assumption as an assumption; 15–16% honest-share loss at 3 s mean delay has been measured. |

## Privacy amendments (zero consensus cost)

| ID | Sev | Topic | Proposal |
|----|-----|-------|----------|
| P1 | Med | §2.1/§2.3 | `tx_tree_hash`+`num_transactions` in relayed shares leak pre-publication mempool state. Shares need not carry real tx data: allow/RECOMMEND randomizing both fields in relayed shares (blocks keep real values). |
| P2 | Med | §2.1 | Option 1 (tx_extra) is a permanent unprunable miner dataset (170 MB/yr, verified). Make option 2 (commitment + prunable side-data) the required target; option 1 only interim with migration plan. |
| P3 | Low-Med | §2.3 | ~15× more relay events per block = finer miner-localization via timing. Batch/jitter share relay; note the trade-off. |
| P4 | Low | §2 | State share `timestamp` has no consensus meaning; MAY be randomized. |

## Simulator (issue appendix / tevador/scratchpad)

B1–B10 in `SECURITY-PRIVACY-REVIEW.md` §6; fixes implemented in
`blockchain_sim.py` in this directory (seeds, ZeroDivision guard, depth
statistics, CI, difficulty-adjustment time-scale column, CLI). Notably:

- **B9**: all days/attack figures are in honest-only-difficulty time; real
  intervals are ×(H+A)/H = **1.5× longer** at α=1/3. Effect is conservative
  (attacks overcounted), but §6.2 should state the unit.
- **B4**: published rates carry no CI and single-run variance is large —
  in practice, three seeds at the published config give 381/796/438
  days/attack (pooled 487, 95% CI 381–652). §6.2's "1 per 2 years" holds
  only under DA-scaled (×1.5) reporting, which the sim doesn't state.
  Multi-seed runs with CIs are required.
- **B3**: the "~3-block reorg" claim is now computed: avg 3.78, median 4
  (seed 1, 20k rounds, depth ≥ 1).
