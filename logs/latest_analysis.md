# Bot Analysis Report

**All-time win rate:** 50.9% (645W / 562L over 1268 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 50.9%)

**By race (all-time):**
- Zerg: 150W / 178L  avg game 712s
- Protoss: 312W / 222L  avg game 632s
- Random: 73W / 60L  avg game 582s
- Terran: 110W / 102L  avg game 617s

**By strategy (all-time):**
- standard_macro: 260W / 318L
- dt_rush: 190W / 117L
- four_gate: 195W / 127L

**By strategy (recent 10 games):**
- dt_rush: 3W / 0L
- four_gate: 2W / 1L
- standard_macro: 2W / 2L

**Analysis:**
The bot is performing well recently at 70% win rate vs 50.9% all-time, showing clear improvement from recent fixes. The 3 losses are: Game 3 (four_gate vs Random, defeat at t=780s with army=36 on 1 base, never expanding despite 40 workers by t=720), Game 4 (standard_macro vs Zerg, defeat at t=960s with army=27 on 1 base, 40 workers trapped, never expanding despite the early_standard_expand fix), and Game 7 (standard_macro vs Zerg, defeat at t=960s with army collapsing from 20 to 0 at t=900, then army=0 for 60s before surrender). Games 3 and 4 share a critical pattern: workers reach 36-40 on 1 base well past t=480 with meaningful armies but the bot never expands, suggesting the expansion conditions are being blocked. Game 7 shows the bot grinding on with army=0 at t=900-960 without surrendering fast enough.

## Applied Improvements
- Fix Game 3 and 4: four_gate and standard_macro with 36-40 workers on 1 base past t=480 never expands despite oversaturated_expand — the cheese_active guard is blocking it; ensure oversaturated_expand fires unconditionally when workers>=36 on 1 base regardless of cheese state
- Fix Game 3 and 4: the expand call must include hard_oversaturated_expand in its condition list, and remove the cheese_active early return guard for it
- Fix Game 7: army collapses from 15 to 0 between t=840 and t=900 on 1 base with 40 workers, then bot grinds at army=0 for 60s before surrendering — the _large_army_1base_since trigger fires at t=840 (army=15>=30 fails) but the rapid_army_collapse to 0 should trigger surrender faster; lower the grind surrender persist timeout when army==0 and workers>=30 past t=600