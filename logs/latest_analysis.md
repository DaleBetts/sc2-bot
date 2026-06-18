# Bot Analysis Report

**All-time win rate:** 48.7% (417W / 386L over 856 games)

**Recent 10-game win rate:** ↓ declining (recent 40.0% vs all-time 48.7%)

**By race (all-time):**
- Zerg: 105W / 124L  avg game 681s
- Protoss: 198W / 143L  avg game 649s
- Random: 48W / 41L  avg game 614s
- Terran: 66W / 78L  avg game 636s

**By strategy (all-time):**
- standard_macro: 163W / 222L
- dt_rush: 126W / 77L
- four_gate: 128W / 87L

**By strategy (recent 10 games):**
- standard_macro: 3W / 6L
- four_gate: 1W / 0L

**Analysis:**
The recent 40% win rate is notably below the 48.7% all-time average, indicating regression. The most critical failures are: (1) Games 4 and 6 show catastrophic early worker wipes at t=300-360 (workers drop from 30+ to 0-3) with no army response — the early defense detection is failing against early aggression vs Random and Zerg; (2) Game 7 is the most damning: a 59-unit army sits idle on 1 base from t=840 to t=1200 never attacking, eventually collapsing to 0 supply — the timed_out_attack logic fires but evidently the bot is not successfully attacking or the supply_cap>=150 threshold requires 150 but the bot caps at 183 supply with army=59 which should be enough, yet the game drags 1200s suggesting the attack is somehow stalling/retreating repeatedly; (3) Game 9 shows a proxy rush wipe at t=240 (workers drop from 25 to 4, bases drop to 0) with no recovery and the auto-surrender takes 660s to trigger — the zombie detection needs to catch 0-base states faster. Game 7's permanent stall with 59 army on 1 base for 300+ seconds is the most severe single bug: supply_cap=183 and army=59 should trigger the supply_cap>=150 && army>=40 attack every 60s, but the army never moves, suggesting the attack target resolution is broken when enemy_structures is empty and enemy_start_locations attack keeps getting interrupted and units retreat back.

## Applied Improvements
- Fix Game 7 permanent 59-army stall: the timed_out_attack fires every 90s but army immediately retreats to rally point because near_base check intercepts next step — force a persistent attack flag when army>=30 and time>600 so units don't keep reverting to rally movement
- Fix Games 4 and 6 catastrophic early worker wipes: the early defense detection at t<300 with workers<30 needs to pull ALL nearby workers immediately when enemy units are within 20 tiles and current army is 0, not just 6 — a full worker pull is better than total annihilation
- Fix Game 9 slow zombie surrender: bot has 0 bases and 5 workers with 0 army from t=300 to t=660 (360s zombie) — accelerate surrender when bases==0 and army==0 and workers are stuck with no minerals to rebuild (minerals<=5 for extended period)