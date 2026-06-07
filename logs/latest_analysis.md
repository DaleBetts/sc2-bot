# Bot Analysis Report

**All-time win rate:** 44.0% (252W / 277L over 573 games)

**Recent 10-game win rate:** ↓ declining (recent 20.0% vs all-time 44.0%)

**By race (all-time):**
- Zerg: 71W / 93L  avg game 655s
- Protoss: 116W / 95L  avg game 659s
- Random: 35W / 32L  avg game 645s
- Terran: 30W / 57L  avg game 660s

**By strategy (all-time):**
- standard_macro: 93W / 160L
- dt_rush: 81W / 52L
- four_gate: 78W / 65L

**By strategy (recent 10 games):**
- dt_rush: 1W / 1L
- standard_macro: 1W / 3L
- four_gate: 0W / 3L

**Analysis:**
The recent 20% win rate (vs 44% all-time) shows severe regression. The critical failure pattern is workers being wiped out extremely early: Games 5, 7, 9 all end with 0 workers before t=300s, Game 2 loses all workers by t=480s, Game 6 loses all workers at t=480s, and Game 8 has 0 workers at t=240s with 915 minerals unspent. The worker defense code in _maybe_log_periodic and _attack is still triggering mass worker suicide - the 'enemy near base' conditions are firing on scouts/early units and sending workers to their deaths. Game 1 shows a separate stall bug: 42 workers on 1 base with 0 army from t=720s onward, and Game 3 shows the same permanent freeze with 60 army units that never attacks (the timed_out_attack condition at supply_utilization>=0.75 is clearly not firing because supply=162/183=88.5% which should exceed 75%, meaning the attack timer is resetting or _last_attack_time is being updated incorrectly). The four_gate strategy has a 0-3 record recently and appears catastrophically broken, killing workers almost immediately.

## Applied Improvements
- Remove the mass worker-attack logic from _attack() that sends ALL workers to fight whenever enemy units are near base - this is the primary cause of worker wipes in Games 2,5,6,7,8,9; replace with a much more conservative defense that only pulls workers when nexus is directly under attack
- Remove the aggressive worker-pulling block at the top of _attack() that sends all workers to attack when army=0 and any enemy is near base - this fires constantly in early game before army exists and suicides all workers (root cause of Games 5,7,9 early wipes)
- Fix Game 3's permanent stall (60 army, 42 workers, never attacks for 40+ minutes) and Game 1's stall by resetting _last_attack_time when the army attacks so timed_out_attack fires correctly, and lower the timed_out_attack threshold to army>=10 with 90s idle to prevent camping