# Bot Analysis Report

**All-time win rate:** 51.2% (592W / 503L over 1156 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 51.2%)

**By race (all-time):**
- Zerg: 140W / 159L  avg game 711s
- Protoss: 288W / 198L  avg game 643s
- Random: 66W / 52L  avg game 584s
- Terran: 98W / 94L  avg game 624s

**By strategy (all-time):**
- standard_macro: 239W / 289L
- dt_rush: 178W / 100L
- four_gate: 175W / 114L

**By strategy (recent 10 games):**
- standard_macro: 5W / 2L
- dt_rush: 1W / 1L
- four_gate: 1W / 0L

**Analysis:**
Recent win rate (70%) is significantly above all-time (51.2%), indicating the bot is improving. The 3 losses are: Game 1 (standard_macro vs Terran, ends at t=540 with 2 base then collapses to 1 base with army=2-4 and workers bleeding), Game 2 (dt_rush vs Protoss, catastrophic permanent freeze at t=960-1200 with army=37, workers=42 on 1 base, supply identical every step — the existing frozen_state trigger requires army>=20 but army=37 satisfies this, yet the supply_used+army check must not be firing because supply_used may fluctuate slightly), Game 4 (standard_macro vs Random, ends at t=780 with 40 workers, army oscillating 3-7 on 1 base from t=540 onward — the tiny_army_grind_since and stuck_no_army triggers should be catching this but army oscillates 3-7 which is above the army<=5 threshold for _army_effectively_zero). Game 2 is the most critical: from t=960-1200 supply_used=116, army=37, workers=42 are completely frozen — the frozen_state trigger should fire but clearly is not, possibly because supply_used fluctuates minimally or the snapshot is being reset.

## Applied Improvements
- Fix Game 2 dt_rush permanent freeze: the frozen state detector resets whenever supply_used OR army changes by even 1, but also add a secondary check tracking army+workers together being unchanged for 180s past t=600 specifically when on 1 base — use a tolerance-based comparison instead of exact equality so minor fluctuations don't reset the timer
- Fix Game 4 standard_macro vs Random: army oscillates 3-7 on 1 base from t=540-780 with 40 workers — the _army_effectively_zero threshold of <=5 misses army=6-7; raise the stuck_no_army threshold to 8 when time>480 on 1 base with workers>=35 to catch this oscillating small army pattern faster
- Fix Game 1 standard_macro vs Terran collapse: bot expands to 2 bases at t=180 but immediately loses workers (14 at t=240) and retreats to 1 base with army=2-4 and never recovers; when bases drop from 2 to 1 after t=180 with army<5 and workers<20, immediately force all available units to defend and reduce the stuck_no_army surrender timer to 60s instead of 90s for this rapid-collapse scenario