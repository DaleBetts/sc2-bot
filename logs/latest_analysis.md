# Bot Analysis Report

**All-time win rate:** 44.1% (261W / 287L over 592 games)

**Recent 10-game win rate:** ↓ declining (recent 40.0% vs all-time 44.1%)

**By race (all-time):**
- Zerg: 73W / 94L  avg game 658s
- Protoss: 120W / 102L  avg game 659s
- Random: 36W / 32L  avg game 640s
- Terran: 32W / 59L  avg game 662s

**By strategy (all-time):**
- standard_macro: 96W / 165L
- dt_rush: 84W / 53L
- four_gate: 81W / 69L

**By strategy (recent 10 games):**
- standard_macro: 2W / 3L
- dt_rush: 1W / 1L
- four_gate: 1W / 2L

**Analysis:**
The recent 40% win rate is below the all-time 44.1%, indicating decline. The most critical pattern is permanent stalls after cheese strategies fail: Game 4 (four_gate) freezes at army=1 from t=600s to t=1860s on 1 base, Game 9 (standard_macro) freezes at army=13-14 from t=840s to t=1260s on 1 base never expanding or attacking, and Games 5/7/8 show worker wipes leaving 0 workers and 0 army. Game 7 is particularly severe with workers dropping from 18 to 2 by t=300s suggesting the worker-defense logic in _maybe_log_periodic is still pulling workers into combat early game. Game 9 stalls because the bot stays on 1 base with 40-42 workers and army of 13-14 never attacking despite timed_out_attack supposedly triggering at army>=10 after 90s idle — the _last_attack_time reset appears broken. Game 4 stalls because after four_gate cheese the army collapses to 1-3 units from t=600s onward and the bot never rebuilds enough to trigger the force_attack_threshold=12.

## Applied Improvements
- Fix Game 9's permanent stall: the timed_out_attack fires but _last_attack_time gets reset to self.time each trigger, so the army just attacks once and re-idles; add a post-attack rally reset and ensure that when timed_out_attack fires with army>=10 on 1 base we also force an expand to break the 1-base deadlock
- Fix Game 4's permanent post-cheese stall where army stays at 1-3 for 20+ minutes: after cheese expires (time>=480) and army<6, aggressively lower force_attack_threshold to 3 and lower post_cheese_army_emergency threshold so zealots are trained and immediately sent to attack rather than camping
- Fix Game 7's early worker wipe (workers 18->2 by t=300s): the should_defend_workers condition in _maybe_log_periodic fires when enemy_near_base_early is non-empty AND army<3, which is true almost all early game; this pulls up to 4 workers into combat against any scouting probe and chains into worker deaths; require the enemy units to be within 15 units (not 20) AND at least 2 enemy combat units present before pulling workers