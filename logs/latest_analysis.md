# Bot Analysis Report

**All-time win rate:** 44.8% (278W / 297L over 621 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 44.8%)

**By race (all-time):**
- Zerg: 79W / 94L  avg game 657s
- Protoss: 126W / 107L  avg game 666s
- Random: 38W / 34L  avg game 634s
- Terran: 35W / 62L  avg game 656s

**By strategy (all-time):**
- standard_macro: 100W / 170L
- dt_rush: 90W / 56L
- four_gate: 88W / 71L

**By strategy (recent 10 games):**
- dt_rush: 1W / 1L
- four_gate: 4W / 1L
- standard_macro: 2W / 0L

**Analysis:**
The bot is performing significantly better recently (70% vs 44.8% all-time), showing clear improvement. Game 8 is the critical loss: workers drop from 21 to 11 to 0 by t=240s, indicating a catastrophic early worker wipe against a Protoss four_gate strategy - the enemy probe/units killed all workers before any army existed. Game 1 (dt_rush loss) shows a different pattern: excellent economy builds up (42 workers, 4 bases by t=600) then collapses to 3 workers/2 bases at t=660, suggesting the bot's own DTs or the enemy caught workers during an undefended period. Game 4 is a tie (standard_macro) that goes to supply cap with 32 army units and 35000+ minerals never spent - the army sits completely idle from t=1920 to t=2520 never attacking, indicating the timed_out_attack and force_attack logic fails when supply=198/200 and army=32 for extended periods. The primary fixable issue is Game 4's permanent late-game stall where army=32 and minerals=35920 but no attack ever fires, likely because _last_attack_time keeps getting reset to self.time+30 in a loop without actually engaging the enemy.

## Applied Improvements
- Fix Game 4's permanent late-game stall: when army>=20 and minerals>5000 (economy completely floated) force immediate attack regardless of thresholds, as this indicates the attack logic has completely broken down and the bot is just sitting idle accumulating resources
- Fix Game 8's catastrophic early worker wipe (21->11->0 workers by t=240): the worker-defense logic in _maybe_log_periodic fires worker attacks but the _attack() method also has an enemy_near_workers block that pulls workers to fight when army < enemy*2 - disable that worker-pulling block in _attack() entirely as it causes all workers to suicide
- Fix the _last_attack_time reset adding +30 buffer which causes the 90s idle check to never trigger correctly after an attack wave — reset to self.time (not self.time+30) so the next timed_out_attack fires 90s after the last actual attack rather than 120s, reducing stall windows