# Bot Analysis Report

**All-time win rate:** 51.0% (624W / 538L over 1223 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 51.0%)

**By race (all-time):**
- Zerg: 146W / 169L  avg game 710s
- Protoss: 302W / 213L  avg game 638s
- Random: 70W / 57L  avg game 583s
- Terran: 106W / 99L  avg game 617s

**By strategy (all-time):**
- standard_macro: 253W / 305L
- dt_rush: 184W / 110L
- four_gate: 187W / 123L

**By strategy (recent 10 games):**
- four_gate: 3W / 2L
- dt_rush: 1W / 0L
- standard_macro: 3W / 1L

**Analysis:**
The bot is performing well recently at 70% win rate vs 51% all-time, showing clear improvement. The two losses are Game 3 (four_gate vs Protoss: army grows to 52 on 1 base by t=840-900 but never attacks — the _four_gate_force_attack fires at army>=8 after t=360 but the permanent_attack_mode requires army>=20 after t=480, yet the army sits at 52 for 120s without attacking, suggesting the attack logic is being overridden by cheese state checks or the target selection is failing) and Game 8 (four_gate vs Protoss: army peaks at 13 at t=360 then collapses to 3-8 oscillating from t=420-720, indicating repeated attacks are being launched but lost, and the bot never surrenders despite being stuck in an unrecoverable loop). Game 9 (standard_macro vs Terran) shows a collapse pattern where army decays from 8 to 0 by t=600 with 40 workers on 1 base and workers then drop from 40 to 31 — the surrender triggers should catch this but apparently don't fire before t=600. The primary fixes needed are: forcing surrender in Game 8's oscillating small army pattern for four_gate vs Protoss, ensuring Game 3's large army actually attacks when cheese is nominally expired, and catching the Game 9 rapid collapse faster.

## Applied Improvements
- Game 3 fix: army of 52 on 1 base at t=840-900 never attacks — the cheese active check blocks permanent_attack_mode; add a hard override that forces attack when four_gate cheese has expired (time>=480) and army>=15 on 1 base regardless of any other condition
- Game 8 fix: four_gate vs Protoss oscillates army 3-13 from t=420-720 on 1 base — surrender faster when four_gate cheese has expired and army has been below 10 for 90s past t=480 with workers>=20, since this oscillating small army pattern is unrecoverable
- Game 9 fix: standard_macro vs Terran, army decays from 8 to 0 by t=600 with 40 workers on 1 base, workers then drop 9 in 60s — the worker snapshot fires correctly but the slow_wipe_since timer only triggers after 60s of consecutive drops; reduce the slow wipe surrender timer to 30s and lower the worker drop threshold to 2 when army is 0 and time>480 with workers>=30 to catch this faster