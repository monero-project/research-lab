# Security & Privacy Review — "Share or Perish" (Monero research-lab issue #146)

Reviewer: independent review prepared for PR against `monero-project/research-lab`.
Reviewed text: issue #146 body as of 2026-11 (current revision, post-Oct-2026 edits),
all 20 comments through 2026-10-20, appendix simulator, and
`tevador/scratchpad` `share-or-perish/blockhain-sim.py` (commit `a111845`).

Method: manual spec analysis against the stated threat model (minority hashrate,
stubborn mining, eclipse), plus independent re-running and ablation of the
appendix Monte-Carlo simulation. All reproduction code is in this directory
(`sim_repro.py`); seeds and configs are printed with every result.

---

## 1. Summary

SoP is a well-motivated soft-fork fork-choice rule. We could not break its core
lateness argument for short forks, and our independent runs reproduce the
published short-fork attack rates. We found however:

- 1 **high-severity scoring-integrity gap**: pool-share scoring can be
  inflated by same-slot share variants (§3.2/F2);
- 1 **spec/comment drift hazard**: the Oct-2026 revisions described in
  comments (`main_seen`, `n_f`, "48 objects") are not in the issue body
  (E1) — implementers get two different specs;
- 3 **privacy leaks** in the workshare relay format that are fixable at zero
  consensus cost (P1–P3, §5);
- 1 **quantitative framing error**: §6.3 presents partition recovery as a
  win ("resolve after 3 blocks") while SoP is *slower* than Nakamoto on
  benign partitions (~3.4 vs ~1.1 blocks, measured by albinjm) — S4;
- ~10 simulator defects/gaps, incl. a time-scaling subtlety that makes all
  reported days/attack figures conservative by ≈1.5× at α=1/3 (B9).

We did **not** find an attack that defeats the subjective lateness design on
non-eclipsed nodes within the 10·w objective window, and the 170 MB/yr
storage figure checks out (§6, "negative results").

---

## 2. Verification of published claims (our runs)

Harness: `sim_repro.py` = appendix sim + RNG seed + env config + depth
statistics. Model logic is unchanged.

| Config (20k rounds, α=1/3, T10) | attacks | days/attack | avg reorg depth |
|---|---|---|---|
| DEPTH=1, seed 1 | 36 | 1.62 | 3.78 |
| DEPTH=1, seed 7 | 38 | 1.53 | 2.84 |
| DEPTH=1, seed 7, UNIQUE_SHARES=0 | 644 | 0.111 | 3.82 |
| DEPTH=1, seed 7, COUNT_TIP_SHARES=0 | 101 | 0.576 | 3.13 |
| DEPTH=10, seed 42, 3M rounds | 23 | 381 (CI 263–602) | 10.04 |
| DEPTH=1, seed 7, K=4 (48-object trigger, comments' reading) | 3 | 19.4 | 2.00 |

- **§6.2 "once per 1.5 days, ~3-block reorg" — reproduced** (1.53–1.62 days,
  avg depth 2.8–3.8). ✔
- **Uniqueness-rule benefit — confirmed at depth 1**: removing it raises
  attack frequency 13.7× (0.111 vs 1.53 days/attack). The claim in §2.2 is
  "up to 2 orders of magnitude" for *long* reorgs; at depth 1 we measure
  ~1.1 orders. Consistent; long-depth ablation is future work (each run
  costs hours of wall time). ✔ (partial)
- **Oct-2026 tip-share fix — confirmed**: reverting `COUNT_TIP_SHARES`
  (pre-2026-10-20 protocol) raises attack frequency 2.7× at depth 1. The
  fix materially closed the dry-spell weakness tevador described. ✔
- **E1's 32-vs-48 discrepancy is load-bearing**: modeling the comments'
  48-object objective trigger (K=4) instead of the body's 32 (K=3) changes
  depth-≥1 attack frequency by **12.7×** (19.4 vs 1.53 days/attack, seed 7).
  Which reading is normative materially changes the security conclusions.
- **§6.2's "1 per 2 years" for 10+ reorgs — NOT reproduced with the
  published config**: seed 42, 3M contests (757M s ≈ 24 sim-years exposure)
  yields 23 events → **381 days/attack (95% CI 263–602)**, i.e. ~1.04
  sim-years/attack; the claimed 730 days is outside the CI. Direction is
  conservative for the proposal (attacks ≈2× more frequent than claimed),
  but the figure is not reproducible from the appendix constants — likely
  small-sample variance or a stale config (scratchpad@master still has
  STUBBORNNESS=5 while the appendix has 10). This is B4 in practice:
  published rates need multi-seed runs with CIs. Additional seeds queued;
  see `results/depth10_*.log`.

### 2.1 Time-scaling subtlety (B9) — read days/attack as conservative

`BLOCK_DIFF = HONEST_HR * 120` fixes difficulty at honest-only hashrate. Monero's
live difficulty retargets to *total* hashrate: D_real = (1+α/(1−α))·720 = 1080 at
α=1/3. Every rate in the model (block arrivals, share arrivals, stubbornness
accumulation) scales linearly in 1/D, so **all simulated intervals are
compressed by exactly 1.5×**: sim "1 per 2 years" ≈ 1 per 3 real years.
Direction: conservative for security claims (attacks look *more* frequent than
reality), but the code comment gives the wrong reason and §6.2 does not state
the unit. Fix: print a DA-scaled column (`f = (H + A)/H`).

---

## 3. Spec errata (evidence-linked)

| ID | Sev | Location | Issue | Fix |
|----|-----|----------|-------|-----|
| E1 | **High** | body vs comments | 2026-10-15/17 comments describe renamed `main_seen`, `n_f`, and "objective if either chain has ≥48 work objects"; body still says `ref_seen`, `n_max < (k−1)·w` (=32), no `n_f`. Two contradictory specs are live. Appendix sim matches the *body* (32), comments say 48. **Material impact (measured, §2):** the readings differ by 12.7× in depth-≥1 attack frequency (1.53 vs 19.4 days/attack). | Reconcile; state which condition is normative. |
| E2 | Med | §2.1 option 2 | "commitment to the **set** of workshares" is under-specified: shares are slot-ordered (§2.2), so the commitment must be over an ordered list, otherwise two builders committing the same shares in different orders produce different commitments and the uniqueness rule is unverifiable from the commitment alone. | Specify ordered commitment (e.g., Merkle over slot-major order) + leaf encoding. |
| E3 | **High** | §2.3, §4, Table 3 | Pool semantics undefined for duplicate slots. Multiple valid shares may exist for the same `minor_version` slot (distinct nonces). §4 counts *all* pool shares extending the tip under `sop_objective` → a node whose pool holds n variants of slot k scores n·diff/w where any block can only ever include 1. Attack: attacker sprays ~50 same-slot variants above its own tip → its chain gains ~49·diff/w phantom objective weight in exactly the 32–160-object region where objective scoring decides. Pool has no defined cap either. | Pool counts **at most one share per minor_version (first-seen)**; pool bounded by 200 entries; P2P rate-limits same-slot relays. |
| E4 | Low-Med | §4, Table 3 | `y.height` is never defined (shares carry no height). Validation difficulty likewise: "1/w of the current block difficulty" — *current at which tip?* | Define `y.height := height(y.prev_id) + 1`; share PoW threshold := diff(y.height)/w, i.e., difficulty of extending `y.prev_id`. |
| E5 | Low | Table 1 | `k` is called "partition recovery, same as PoP" but in SoP `k` is a **work-object** threshold `(k−1)·w`, not blocks. | Rename or redefine in Table 1. |
| E6 | Low | §5 note | Hardcodes "160 below the highest known chain tip"; everywhere else the constant is `10·w`. | Use `10·w` (parameter-independence). |
| E7 | Low | Tables 4–5 | Boundary asymmetry: block late iff `> d`; share late iff `≤ d`. With integer-second timestamps this hands a 1-second boundary game to the fastest propagator. | Half-open intervals consistently; consider millisecond timestamps. |
| E8 | Low | §2.2 | 200-cap is justified via `uint8_t`, but the real bound is `255 − major_version` (200-slot cap plus major up to 55 coincide today; not forever). Also "the **first** 200" is unspecified (builder's choice — fine, but say so). | State cap as `min(200, 255 − major_version)`; note builder's choice. |
| E9 | Low | §2.3 | Sequentiality for *pool* shares ("minor_version that follows the sequentiality rule") is undefined without a containing block — which slot does a pool share occupy? | Define: pool share occupies the first slot not yet filled in the node's pool for that tip. |
| E10 | Med | §2.2 | Share's own `minor_version` is not in the 4-field serialization; slot is implied by tx_extra position (option 1), but option 2's P2P message must then carry slot explicitly or fixed order — unstated. | State where slot lives in the P2P serialization for option 2. |

---

## 4. Security analysis (gaps, not breaks)

### S1. Exact-score ties are common; §5.1 random tie-break → split-brain (Med)

Scores are small-integer multiples of `diff(h)/w`. Two symmetric racing sides
have Poisson(≈15) share counts; P(counts equal) ≈ 1/√(4πμ) ≈ 7% per fork
(estimate, μ=15). Ties across *different heights* are also possible (a shorter
chain heavy with shares can tie a longer chain). §5.1 then picks **randomly**,
including between chains of different heights. Consequences: (a) nodes
disagree (split-brain) until the objective window; (b) a 50% chance of
preferring the *shorter* chain. albinjm's honest-only 10+ reorgs
(0.13–3.94/yr at 3–10 s mean delay) are plausibly this mechanism.

**Proposed:** tie-break order = (1) greater height, (2) random among
equal-height. Grindability note: equalizing a shorter chain to a taller one
costs real withheld work, so the height preference also weakens the incentive
to engineer ties.

### S2. Iterative removal removes all lowest-scoring chains at once (Low-Med)

§5 step 4 removes *all* lowest-scoring chains simultaneously. A chain tied for
lowest at fork height h_f might beat the winner after h_f moves up (its
sub-fork is what carries the weight). Batch removal can therefore discard a
would-be winner that single removal (random among ties, recalc, repeat) would
keep. Needs either a proof that batch removal is order-independent for this
scoring family, or switch to one-at-a-time.

### S3. Eclipse attacks: bounded, but unquantified (Med)

All §3 inputs (`block_seen`, `share_seen`, reference times) are attacker-
visible and attacker-orderable on an eclipsed node; the §2.2 uniqueness-rule
benefit ("2 orders of magnitude") presumes honest share flow the attacker
cannot see — under eclipse that presumption fails. Damage is bounded by the
objective windows (subjective ≤ 1 block + 32 objects; everything beyond
160 blocks is nakamoto), but the spec never states this bound nor quantifies
eclipse+stubborn mining (the cited [4] is exactly the setting). **Proposed:**
add the explicit damage-bound statement and an eclipse-mode run of the
simulator.

### S4. Partition recovery is a trade-off, currently framed as a win (Med)

§6.3: "network partitions will on average resolve after 3 blocks". albinjm
measured (honest-only): SoP 3.44 / 3.43 / 2.04 blocks after reunion for 1-1 /
2-2 / 3-3 splits vs ~1.1 under Nakamoto. SoP trades slightly slower benign
partition recovery for much slower adversarial reorgs. That trade is good —
but §6.3 must present both numbers, and "3 blocks" should be defined relative
to the fork point (tevador's answer 4) not reunion.

### S5. Incentive analysis absent (Med)

Shares never pay; the only return is fork-race weight. The spec should argue
why relaying is equilibrium behavior: (a) a block's weight advantage (1+w−1
objects) only materializes in races; (b) shares you withhold extend only your
own tip and die with it (perish); (c) first-seen builders enrich competitors.
Pool-level free-riding (two colliding pools α=0.4 publishing shares but
opportunistically withholding blocks) is unanalyzed; the single-attacker sim
doesn't cover it.

### S6. Builder slot-selection policy unspecified (Low)

When several valid candidates exist for a slot, which one a builder includes
is unspecified. Recommend a SHOULD: first-seen per slot (deterministic-ish,
ungrindable beyond relay races), plus the E3 relay rate-limit.

### S7. First-seen advantage is inherited from PoP and amplified (Note)

`ref_seen` stickiness means the first block appended at a height is never
late and all competitors arriving >d later are zeroed on that node — this
rewards propagation advantage (well-connected pools) in every race. Symmetric
between honest parties, but it concentrates race wins in low-latency miners.
Worth one paragraph + a decentralization note in §6.

### S8. d-sensitivity is asserted, not shown (Med)

tevador's 0.5 s share-propagation estimate applies to well-connected pools;
solo miners over Tor/high-latency links see more. albinjm measured 15–16%
honest-share loss to slot collisions at 3 s mean delay (0% at 0 s). §6 should
include a delay-sensitivity row (0.5/1/3/5 s) or state the assumption
explicitly, since `d=5` and the collision loss both scale with it.

---

## 5. Privacy analysis

SoP doesn't touch tx privacy, but it adds ~15 relayed objects per block and a
permanent on-chain record. Five findings; P1–P3 are fixable at **zero
consensus cost**.

### P1. `tx_tree_hash` + `num_transactions` in relayed shares leak pre-publication mempool state (Med)

A share is a real 76-byte hashing blob, so it commits to the miner's tx set
*at mining time*, before any block exists. Passive observers collecting
relayed shares can: link shares ↔ miner/pool via repeated tx-tree prefixes;
fingerprint solo miners whose mempool view contains distinctive pending
transactions (e.g., their own spends); and, once the block is published,
reconstruct per-miner mempool composition timelines.

**Fix (spec amendment, no consensus change):** share validity needs only
{prev_id, slot, difficulty} — *not* the tx contents. Allow/RECOMMEND miners to
substitute a random `tx_tree_hash` and `num_transactions` in **relayed
shares** (blocks keep the real values). PoW verification is unchanged; the
containing block embeds the randomized bytes. One-line change in share
construction.

### P2. Option 1 (tx_extra) creates a permanent, unprunable miner-behavior dataset (Med)

170 MB/yr (verified, §6) of per-share `{timestamp, nonce, tree, count}` never
prunes. That is a forever-growing forensic corpus (P1 analysis persists for
all future analysts, forever). **Recommendation:** make option 2 (commitment +
prunable P2P-side data) the *required* long-term design; option 1 acceptable
only as an interim deployment with a migration plan.

### P3. Share-relay cadence is a new timing-analysis surface (Low-Med)

Blocks give 1 timing event/120 s; shares add ~15 → 15× finer localization
resolution for passive Sybil observers (miner-location/pool-graph inference).
Volume is negligible (~0.5 KB/block); the metadata is the issue. **Fix:**
batch/jitter share relay (e.g., flush accumulated shares on a fixed schedule
or piggybacked on other messages); note the trade-off in the spec.

### P4. Share `timestamp` is unvalidated — say so, and consider randomizing (Low)

Block timestamps have consensus rules; share timestamps only feed the hash.
Spec is silent. State that share timestamps carry no consensus meaning; miners
MAY randomize them (also degrades P3 and reduces on-chain junk under option 1).

### P5. Subjective state is local-only (positive note)

`h_0` and arrival tables are never persisted or gossiped — no new privacy
leak from node state itself. Worth stating explicitly in §3 as a design
property.

---

## 6. Simulator defects & gaps (for the scratchpad PR)

| ID | Sev | Issue | Fix |
|----|-----|-------|-----|
| B1 | Low | `random.random()` can return 0.0 → `ZeroDivisionError` in `1.0/u` (p≈2⁻⁵³/call; real). | Guard u≤0. |
| B2 | Med | No RNG seed → published numbers irreproducible exactly. | `--seed`, multi-seed runs. |
| B3 | Med | §6.2 claims "on average a 3-block reorg" but the sim computes no depth statistic. | Track avg/median/max depth of successes. |
| B4 | Low | No CI on days/attack; "1 per 2 years" needs ~60+ 1M-round runs for a stable rate; single-run variance unreported. | Poisson/exposure CI, batch runner. |
| B5 | Low | `UNCLE_BLOCKS` comment ("attacker can use honest blocks as uncles") mismatches code: the phantom `-1` share is added to the *other* chain, and the branch is unreachable for the attacker (`mine(output, None)`). Dead in all reported configs. | Fix comment or implement the intended model. |
| B6 | Low | `UNIQUE_SHARES=False` list-mode double-counts adopted+mined duplicates (ablation-only; note in docstring). | Document; or model collisions explicitly in list mode. |
| B7 | Low | `SIM_ROUNDS` bounds *contests*, not time; `total_seconds` is the exposure. Fine, but undocumented (days/attack depends on it). | Docstring. |
| B8 | Info | Post-success `honest_bc.adopt_shares(attack_bc.shares)` is correct under the spec (private-tip shares survive the reorg) — worth a comment, reviewers will flag it. | Comment. |
| B9 | **Med** | Time compression: fixed honest-only difficulty compresses all intervals by `(H+A)/H` = 1.5× at α=1/3 (§2.1). Effect is conservative, comment's rationale is misleading, §6.2 doesn't state units. | Print DA-scaled days column. |
| B10 | Med | No propagation-delay model: `d` never appears; lateness is abstracted to the "1 block + 32 objects" rule. Defensible abstraction, but albinjm's independent sim shows results are delay-sensitive — the spec should say the appendix sim ignores `d`. | Note in header; optionally add a delay layer. |

## 7. Negative results (things we checked that are *not* bugs)

- 170 MB/yr tx_extra figure: correct (262,800 blocks/yr × 15 × 43 B ≈ 170 MB).
- Slot-flooding attack (attacker races honest miners for slots): **neutral** —
  one share per slot either way, block weight unchanged; flooding *future*
  slots is self-defeating (sequentiality forbids gaps).
- Adopted honest shares in the attacker's first private block are legitimately
  scoreable when the attacker's block lands first (ref_seen = block_seen), and
  unusable afterwards (prev_id changes) — the sim models this correctly via
  index dedupe; we verified the `shr = len(self.shares)` numbering reproduces
  the §2.2 collision semantics.
- Table 5's "at least 6 seconds" phrasing is consistent with strict `> d` on
  integer-second timestamps.

## 8. Proposed changes (PR payload)

- **F1** Reconcile body vs comments (E1); publish the normative revision as a
  file, not only issue edits.
- **F2** Pool = ≤1 counted share per slot, first-seen; cap 200; relay
  rate-limit per slot (E3).
- **F3** Ordered commitment for option 2 (E2, E10).
- **F4** Define `y.height` + share difficulty (E4).
- **F5** Tie-break: height first, then random (S1).
- **F6** One-at-a-time removal or order-independence proof (S2).
- **F7** Eclipse damage-bound statement + eclipse sim mode (S3).
- **F8** §6.3 rewrite with the Nakamoto comparison (S4).
- **F9** Privacy amendments P1–P4 (randomized share fields; option 2 as
  target; relay batching; unvalidated timestamps).
- **F10** Sim fixes B1–B10 (`blockchain_sim.py` in this PR).

*Estimated tie probability and ablation CIs are labeled as such; everything
else in §2 is reproducible from the seeds given.*
