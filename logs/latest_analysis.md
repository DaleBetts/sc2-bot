# Bot Analysis Report

**All-time win rate:** 47.3% (191W / 184L over 404 games)

**Recent 10-game win rate:** ↓ declining (recent 20.0% vs all-time 47.3%)

**By race (all-time):**
- Zerg: 60W / 65L  avg game 684s
- Protoss: 77W / 60L  avg game 678s
- Random: 28W / 21L  avg game 631s
- Terran: 26W / 38L  avg game 631s

**By strategy (all-time):**
- standard_macro: 65W / 112L
- dt_rush: 62W / 33L
- four_gate: 64W / 39L

**By strategy (recent 10 games):**
- dt_rush: 0W / 3L
- four_gate: 1W / 4L
- standard_macro: 1W / 1L

**Analysis:**
The bot is in severe decline (20% recent vs 47.3% all-time), with 7 of 10 recent losses caused by workers being wiped to 0 before any meaningful army exists (Games 1, 2, 3, 6, 7, 8, 9, 10). The worker-drop detector in _maybe_log_periodic only fires once per minute (periodic log), so a rush that kills workers between log intervals gets no response until the next minute check — by then all workers are dead. Games 2, 3, 7, 8 show the four_gate strategy stagnating on 1 base with 22 workers capped and army building slowly while the enemy attacks and wipes everything around t=420-600s. The emergency defense logic in _attack checks enemy_units but by the time enemies are detected near structures, workers are already dead with no army to respond.

## Applied Improvements
- Move worker-drop detection and emergency defense from the once-per-minute log function into on_step so it fires every iteration, catching early rushes before they wipe all workers
- Fix four_gate single-base stagnation (Games 2, 3, 7) where 22 workers and growing army sit on 1 base forever — force expand in four_gate when army>=8 and workers>=20 and time>=300 since cheese window at t=300 with army means we can safely take a natural
- Wire the four_gate_mid_expand flag into the expand condition check so it actually triggers expansion