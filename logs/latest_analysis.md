# Bot Analysis Report

**All-time win rate:** 45.9% (308W / 315L over 671 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 45.9%)

**By race (all-time):**
- Zerg: 86W / 99L  avg game 662s
- Protoss: 141W / 113L  avg game 663s
- Random: 40W / 36L  avg game 627s
- Terran: 41W / 67L  avg game 653s

**By strategy (all-time):**
- standard_macro: 114W / 177L
- dt_rush: 95W / 62L
- four_gate: 99W / 76L

**By strategy (recent 10 games):**
- standard_macro: 5W / 3L
- dt_rush: 0W / 1L
- four_gate: 1W / 0L

**Analysis:**
Recent win rate (60%) is significantly above all-time (45.9%), showing clear improvement. However, 3 of 4 losses share critical failure patterns: Game 7 (PvP) shows a catastrophic 1-base stall where 58 army units sit completely idle from t=840s to t=1140s with supply_cap=191 and minerals staying at 70 — the timed_out_attack should fire but army never moves, suggesting the attack target logic is failing or the army is stuck in a rally loop after supply_cap hits max. Game 1 (PvZ) shows army collapsing from 14 to 2 by t=600s then workers dying out — classic post-battle stall with no recovery. Game 5 (DT rush PvP) is a worker wipe at t=240s with workers dropping from 22 to 2, indicating enemy DTs killed all workers while our DT rush was still building — the worker defense logic failed. Game 8 (PvT) shows army dropping from 12 to 0 between t=300-540s with workers then dying, another failed defense scenario.

## Applied Improvements
- Fix Game 7's permanent stall (58 army, supply_cap=191, never attacks): when supply_cap>=150 and army>=40 and minerals<200 (economy not floated) and time-since-last-attack>60s, force attack regardless of other conditions — this catches the case where the army is maxed-out but the force_attack_threshold logic fails to trigger
- Fix Game 5's worker wipe during DT rush: when cheese is active and enemy units are detected near base early, the bot should pull workers to defend even during cheese — currently the should_defend_workers logic only pulls workers if army<3 but during DT rush army is 0 for a long time; specifically during DT rush allow worker defense when any enemy combat units are within 10 units of start location
- Fix Game 1 and Game 8 post-battle collapse: after army drops from a high count to near-zero (army<=3) with workers>=20 and time>480, lower the timed_out_attack idle threshold to 30s and min_army to 3 so newly rebuilt units attack immediately rather than camping at rally waiting for a critical mass that never comes while the base is being destroyed