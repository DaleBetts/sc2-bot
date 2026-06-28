# Bot Analysis Report

**All-time win rate:** 50.6% (548W / 474L over 1083 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 50.6%)

**By race (all-time):**
- Zerg: 129W / 153L  avg game 712s
- Protoss: 267W / 184L  avg game 650s
- Random: 61W / 48L  avg game 590s
- Terran: 91W / 89L  avg game 627s

**By strategy (all-time):**
- standard_macro: 222W / 275L
- dt_rush: 162W / 90L
- four_gate: 164W / 109L

**By strategy (recent 10 games):**
- four_gate: 3W / 1L
- standard_macro: 1W / 2L
- dt_rush: 3W / 0L

**Analysis:**
The bot is performing well recently at 70% win rate vs 50.6% all-time, showing clear improvement. The 3 losses are: Game 3 (standard_macro vs Zerg) where the army stalls at 6-14 units on 1 base for 800+ seconds with 40+ workers and never expands despite the safety_expand threshold being met, then slowly erodes until workers=0 at t=1440; Game 5 (standard_macro vs Protoss) where workers drop catastrophically from 29 to 9 in 60s at t=300 with army=0, triggering an early wipe the bot doesn't recover from; Game 7 (four_gate vs Protoss) where workers drop from 19 to 8 at t=180 then to 1 at t=240 with army=0 suggesting an enemy rush that the bot fails to detect and defend. The key pattern in all 3 losses is early-to-mid game inability to defend against enemy pressure with no army present.

## Applied Improvements
- Game 3: army oscillates 3-14 on 1 base with 40+ workers from t=480-1440 never triggering safety_expand because army briefly exceeds 10 — lower safety_expand army threshold from <10 to <15 and lower worker threshold from 18 to 16 to catch this persistent single-base trap earlier
- Game 5 and Game 7: workers drop by 16-20 in a single 60s window at t=180-300 with army=0 and the bot never recovers — add an ultra-fast surrender trigger when workers drop by 15+ in one snapshot window with no army before t=400 to avoid prolonged hopeless games
- Game 3: army stays tiny (3-14) on 1 base with 40+ workers for 800s because stuck_no_army_since requires army<=5 but army briefly exceeds 5 resetting the timer — add a separate long-stall surrender when workers>=35 on 1 base with army<15 and minerals<200 persisting for 300s past t=600, indicating the bot is permanently grinding down