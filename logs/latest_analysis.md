# Bot Analysis Report

**All-time win rate:** 50.9% (611W / 528L over 1200 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 50.9%)

**By race (all-time):**
- Zerg: 142W / 167L  avg game 714s
- Protoss: 297W / 209L  avg game 639s
- Random: 68W / 56L  avg game 585s
- Terran: 104W / 96L  avg game 619s

**By strategy (all-time):**
- standard_macro: 247W / 302L
- dt_rush: 182W / 106L
- four_gate: 182W / 120L

**By strategy (recent 10 games):**
- standard_macro: 2W / 2L
- four_gate: 4W / 0L
- dt_rush: 0W / 2L

**Analysis:**
The bot is performing well recently (60% vs 50.9% all-time), showing clear improvement. The two losses are: Game 5 (standard_macro vs Zerg) where army builds to 27 by t=780 on 1 base then completely collapses to 0 by t=840, with workers also dying from 40 to 25 by t=900 — the bot never expanded despite having 40 workers from t=420 onward; and Game 6 (dt_rush vs Zerg) where army builds to 25 by t=660 then bleeds to 2 by t=900 on 1 base with 40 workers, also never expanding. Game 8 (dt_rush vs Random) is a loss-in-progress at t=780 with army=16 on 1 base but workers oscillating 10-32 suggesting repeated worker wipes. The core pattern in the losses is: large army (20-27) built on 1 base with 40 workers, army gets attrited attacking Zerg (Game 5) or bleeds slowly (Game 6), but the bot never takes a second base despite workers>=40 from t=420+, leaving it unable to rebuild. The early_standard_expand condition requires army>=2 which should fire but clearly isn't triggering fast enough when workers>=40 at t=420 on 1 base.

## Applied Improvements
- Lower the early_standard_expand worker threshold from 25 to 22 and time threshold from 300 to 240, so the bot expands much earlier in standard_macro before army attrition begins — Games 5 and 6 both had 40 workers trapped on 1 base from t=420 onward
- Add early_standard_expand to the expansion condition list so it actually triggers expansion — it was computed but never included in the final if-statement, meaning the lowered thresholds had no effect
- In Game 5 and 6, dt_rush/standard_macro vs Zerg on 1 base with army 20-27 that then collapses — add a surrender trigger specifically for when army was large (>=15 peak) but has been below 5 for 120s on 1 base with workers>=30 past t=600, which is the exact pattern seen in Game 5 t=840 and Game 6 t=840-900