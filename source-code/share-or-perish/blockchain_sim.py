# Blockchain simulation for Share or Perish: https://github.com/monero-project/research-lab/issues/146
# Original model (c) 2025-2026 tevador, MIT license.
# Patched version (c) 2026, MIT license. Changes vs the issue appendix /
# tevador/scratchpad@master (model logic unchanged):
#   - RNG seeding (reproducibility)
#   - guard u=0.0 in get_random_hash_diff() (ZeroDivisionError)
#   - reorg-depth statistics (avg/median/max) - the "3-block reorg" claim in
#     section 6.2 is now computed, not asserted
#   - Poisson 95% CI on days/attack
#   - difficulty-adjustment time-scale column: the model fixes difficulty at
#     honest-only hashrate, so all simulated intervals are compressed by
#     (H+A)/H; live Monero DA includes the attacker, real intervals are longer
#   - config via CLI args; UNIQUE_SHARES=False caveat documented
#   - UNCLE_BLOCKS dead-code/comment mismatch documented (unreachable for the
#     attacker, which is the only caller passing other_bc=None)

import argparse
import math
import random
import statistics

p = argparse.ArgumentParser(description="Share or Perish attack-rate simulation (model: tevador, issue #146)")
p.add_argument("--honest-hr", type=float, default=6)
p.add_argument("--attack-hr", type=float, default=3)
p.add_argument("--w", type=int, default=16)
p.add_argument("--k", type=int, default=3)
p.add_argument("--stubbornness", type=int, default=10)
p.add_argument("--gamma", type=float, default=0.5)
p.add_argument("--rounds", type=int, default=1000000, help="contests (not seconds); exposure is reported")
p.add_argument("--min-reorg-depth", type=int, default=10)
p.add_argument("--no-unique-shares", action="store_true",
               help="disable uniqueness rule (list mode double-counts adopted+mined shares; ablation only)")
p.add_argument("--no-count-tip-shares", action="store_true",
               help="revert to pre-2026-10-20 protocol (tip shares not counted under sop_objective)")
p.add_argument("--uncle-blocks", action="store_true", help="ablation; see header comment")
p.add_argument("--seed", type=int, default=0)
args = p.parse_args()

HONEST_HR = args.honest_hr
ATTACK_HR = args.attack_hr
UNIQUE_SHARES = not args.no_unique_shares
UNCLE_BLOCKS = args.uncle_blocks
COUNT_TIP_SHARES = not args.no_count_tip_shares
W = args.w
K = args.k
STUBBORNNESS = args.stubbornness
GAMMA = args.gamma
SIM_ROUNDS = args.rounds
MIN_REORG_DEPTH = args.min_reorg_depth
random.seed(args.seed)

# The model fixes difficulty at honest-only hashrate. Live Monero DA retargets
# to total hashrate, compressing all simulated intervals by DA_SCALE.
BLOCK_DIFF = HONEST_HR * 120
SHARE_DIFF = BLOCK_DIFF / W
DA_SCALE = (HONEST_HR + ATTACK_HR) / HONEST_HR

def get_random_hash_diff():
    # uniform random number [0,1) simulates a hash value divided by 2^256
    u = random.random()
    if u <= 0.0:  # random.random() can return exact 0.0
        u = 2 ** -53
    # difficulty = 2^256 / H = 1.0 / u
    return int(1.0 / u)

class Blockchain:
    def __init__(self, name, hr):
        self.name = name
        self.hr = hr
        self.reset()

    def reset(self):
        self.shares = set() if UNIQUE_SHARES else list()
        self.num_blocks = 0
        self.weight = 0
        self.skip_weight = 0

    def soft_reset(self):
        self.num_blocks = 0
        self.weight = 0
        self.skip_weight = 0

    def add_share(self, shr):
        if len(self.shares) >= 200:
            return
        if isinstance(self.shares, set):
            self.shares.add(shr)
        else:
            self.shares.append(shr)

    def adopt_shares(self, shares):
        self.shares.clear()
        for shr in shares:
            self.add_share(shr)

    def total_work(self):
        return self.weight + len(self.shares)

    def score(self):
        return self.total_work() if COUNT_TIP_SHARES else self.weight

    def mine(self, output, other_bc):
        for j in range(int(self.hr)):
            h = get_random_hash_diff()
            if h >= BLOCK_DIFF:
                # found block
                wt = 1 + len(self.shares)
                self.num_blocks += 1
                self.weight += wt
                if self.num_blocks > 1:
                    self.skip_weight += wt
                self.shares.clear()
                # NOTE: this branch is unreachable for the attacker (attack_bc
                # is always mined with other_bc=None); as written the phantom
                # "-1" share goes to the OTHER chain.
                if UNCLE_BLOCKS and other_bc and self.num_blocks == 1 and other_bc.num_blocks == 0:
                    other_bc.add_share(-1)
            elif h >= SHARE_DIFF:
                # found share; len() numbering reproduces the minor_version
                # slot-collision semantics (set dedupe = same-slot collision)
                shr = len(self.shares)
                self.add_share(shr)
                # honest shares flow to the attacker until its first private block
                if other_bc and self.num_blocks == 0 and other_bc.num_blocks == 0:
                    other_bc.add_share(shr)
        return output

print(f"W={W}")
print(f"STUBBORNNESS={STUBBORNNESS}")
print(f"UNIQUE_SHARES={UNIQUE_SHARES}")
print(f"UNCLE_BLOCKS={UNCLE_BLOCKS}")
print(f"COUNT_TIP_SHARES={COUNT_TIP_SHARES}")
print(f"SEED={args.seed}")

honest_bc = Blockchain("honest", HONEST_HR)
attack_bc = Blockchain("attacker", ATTACK_HR)

total_seconds = 0
num_attacks = 0
depths = []
reorg = False

for i in range(SIM_ROUNDS):
    if reorg:
        honest_bc.reset()
        attack_bc.soft_reset()  # keep shares (private-tip shares survive the reorg)
        if COUNT_TIP_SHARES:
            # attacker is publishing his shares
            honest_bc.adopt_shares(attack_bc.shares)
    else:
        honest_bc.soft_reset()  # keep shares
        attack_bc.reset()
        attack_bc.adopt_shares(honest_bc.shares)
    reorg = False
    while (honest_bc.total_work() - attack_bc.total_work()) <= STUBBORNNESS:
        honest_bc.mine("", attack_bc)
        attack_bc.mine("", None)
        total_seconds += 1
        if honest_bc.score() - attack_bc.score() <= 0 \
            and (attack_bc.skip_weight >= W * (K - 1) or honest_bc.skip_weight >= W * (K - 1)) \
            and honest_bc.num_blocks >= MIN_REORG_DEPTH:
            break
    diff = honest_bc.score() - attack_bc.score()
    if attack_bc.skip_weight < W * (K - 1) and honest_bc.skip_weight < W * (K - 1) \
        or honest_bc.num_blocks < MIN_REORG_DEPTH:
        continue
    if diff < 0 or (diff == 0 and random.random() > GAMMA):
        num_attacks += 1
        depths.append(honest_bc.num_blocks)
        reorg = True
        continue

print()
if num_attacks > 0:
    days = total_seconds / num_attacks / 86400
    # Garwood (variance-stabilized) 95% CI for the Poisson rate n/T:
    s = math.sqrt(num_attacks)
    lam_lo = (s - 0.98) ** 2 / total_seconds
    lam_hi = (s + 0.98) ** 2 / total_seconds
    days_lo = 1 / (lam_hi * 86400)
    days_hi = 1 / (lam_lo * 86400) if lam_lo > 0 else float("inf")
    depths.sort()
    print(f"Time: {total_seconds} s, attacks: {num_attacks}, "
          f"{days:.3f} days/attack (95% CI {days_lo:.3f}-{days_hi:.3f}), "
          f"DA-scaled x{DA_SCALE:.2f}: {days * DA_SCALE:.3f} days/attack")
    print(f"Reorg depth: avg {statistics.fmean(depths):.2f} "
          f"median {depths[len(depths)//2]} max {depths[-1]} (n={num_attacks})")
else:
    # 0 events: one-sided 95% upper bound on the rate (3.69/T)
    print(f"Time: {total_seconds}, attacks: 0, "
          f">= {total_seconds / (3.69 * 86400):.2f} days/attack (95%, 0 events); "
          f"exposure {total_seconds/86400/365:.2f} sim-years, "
          f"{total_seconds*DA_SCALE/86400/365:.2f} DA-scaled years")

print()
print(f"W={W}")
print(f"STUBBORNNESS={STUBBORNNESS}")
print(f"UNIQUE_SHARES={UNIQUE_SHARES}")
print(f"UNCLE_BLOCKS={UNCLE_BLOCKS}")
print(f"COUNT_TIP_SHARES={COUNT_TIP_SHARES}")
print(f"SEED={args.seed}")
