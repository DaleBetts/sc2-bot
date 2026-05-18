# Bot Analysis Report

**Win rate:** 50.9% (81W / 66L over 159 games)

**By race:**
- Zerg: 30W / 22L  avg game 716s
- Protoss: 28W / 21L  avg game 766s
- Random: 10W / 8L  avg game 575s
- Terran: 13W / 15L  avg game 713s

**By strategy:**
- standard_macro: 27W / 47L
- dt_rush: 32W / 13L
- four_gate: 22W / 6L

**Analysis:**
The standard_macro strategy has a catastrophic 36% win rate (27W/47L) while cheese strategies perform well (DT rush 71%, 4-gate 79%). In standard_macro losses (Games 3, 6, 7), the bot never expands beyond 1 base despite having 40 workers, starving its army at only 9-13 supply of army units while supply caps sit at 87-167. The single-base constraint means the bot eventually gets overwhelmed by mid-game timing attacks. Additionally, in Game 2 (DT rush defeat), the bot was still on 1 base when wiped at t=480s, and in Games 6/7 (DT/standard defeats), the army collapses around t=900s suggest the bot fails to rebuild or defend after losing its army because it has no economy redundancy from a second base.

## Applied Improvements
- Fix expansion logic: the has_defense check is too permissive but the real blocker is that target = 1 + (workers // 16) with 40 workers only targets 3 bases, yet the bot stays on 1 base in all observed games — the issue is the has_defense condition combined with army_size threshold; lower the army threshold to 2 and add a time-based override after 7 minutes to force expansion
- Fix the DT rush transition: after the cheese window expires (t>=480), the bot has 20 workers and 1 base with no macro infrastructure; add a post-cheese recovery path in _train_probes that ramps worker cap back up to 40 once cheese_active is false, already handled by the else branch — but the real fix is to not hard-cap workers at 20 during DT rush after the dark shrine is already built and DTs are on the field, reducing the window from 480s to after dark shrine is ready
- Fix army attack threshold: standard_macro games show army sitting idle at rally point (9 units for many minutes in Games 3/6/7) because the threshold is 6 but army never pushes; reduce attack threshold to 4 for standard macro and add a time-based forced attack after 10 minutes to prevent indefinite stalling on one base with no aggression