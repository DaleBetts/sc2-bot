# Bot Analysis Report

**All-time win rate:** 45.5% (293W / 304L over 644 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 45.5%)

**By race (all-time):**
- Zerg: 82W / 97L  avg game 660s
- Protoss: 132W / 110L  avg game 664s
- Random: 39W / 34L  avg game 630s
- Terran: 40W / 63L  avg game 650s

**By strategy (all-time):**
- standard_macro: 106W / 172L
- dt_rush: 92W / 59L
- four_gate: 95W / 73L

**By strategy (recent 10 games):**
- four_gate: 2W / 1L
- standard_macro: 3W / 2L
- dt_rush: 1W / 0L

**Analysis:**
The bot has improved significantly from 45.5% all-time to 60.0% in recent games, indicating recent fixes are working. However, Game 1 (Tie vs Protoss) shows a critical failure pattern: the bot builds 58 army supply on 1 base by t=900s, then the army completely collapses (army drops from 58 to 1 by t=1200s) and the bot enters a permanent stall with 42 workers, 1 army, 60 minerals, and 135 supply cap for 15+ minutes - the army died in an attack and the bot never rebuilt. Games 6 and 8 show the bot losing to Zerg with standard_macro: in Game 6 the army stays tiny (2-5 units) until the base is destroyed at t=600s, suggesting production is failing vs Zerg pressure; in Game 8 the four_gate army peaks at 27 then bleeds away while on 1 base until workers are wiped at t=960s, indicating the bot attacks into a wall and the economy never recovers. The single-base stall pattern (Game 1: 40 workers on 1 base for the entire game, never expanding) is the most glaring structural issue.

## Applied Improvements
- Fix Game 1's permanent post-battle stall: after the army is wiped (army<3 and supply_cap>=135 and workers>=40 and bases==1) the bot never rebuilds or expands; force an immediate expand and lower army rally threshold to 3 to get units moving again after losing a big army on 1 base
- Include post_battle_expand in the expand condition to actually trigger the fix for Game 1's permanent 1-base stall after army wipe
- Fix Game 6 and Game 8 Zerg losses where army stays tiny (2-5 units) while enemy destroys the base: reduce timed_out_attack threshold to 7 units (from 10) and 60s idle (from 90s) when on 1 base vs Zerg so the bot doesn't camp waiting for a critical mass that never arrives while being overrun