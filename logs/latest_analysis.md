# Bot Analysis Report

**All-time win rate:** 48.7% (114W / 102L over 234 games)

**Recent 10-game win rate:** ↑ improving (recent 50.0% vs all-time 48.7%)

**By race (all-time):**
- Zerg: 42W / 37L  avg game 695s
- Protoss: 41W / 33L  avg game 730s
- Random: 14W / 12L  avg game 561s
- Terran: 17W / 20L  avg game 696s

**By strategy (all-time):**
- standard_macro: 35W / 72L
- dt_rush: 40W / 16L
- four_gate: 39W / 14L

**By strategy (recent 10 games):**
- four_gate: 4W / 0L
- standard_macro: 0W / 4L
- dt_rush: 1W / 0L

**Analysis:**
The recent 10 games show a clear split: four_gate is 4-0 and dt_rush is 1-0, while standard_macro is 0-4. All 4 standard_macro losses share a catastrophic worker wipe pattern — Game 2 loses all workers by t=240s, Game 4 loses workers between t=300-420s, Game 6 loses workers between t=360-420s, and Game 8 loses all workers at t=660s. In every case the army is tiny (0-6 units) when workers are wiped, meaning the defense logic is failing to respond adequately. Game 7 (tie) shows 59 units sitting idle from t=840s to t=1020s before being destroyed, suggesting the attack commitment logic still stalls. The bot is marginally improving (50% vs 48.7% all-time) but entirely due to cheese strategies; standard_macro is broken.

## Applied Improvements
- Fix standard_macro worker wipe by pulling ALL workers to defend (not just 6) when enemy is near base and army is small, and also trigger defense when workers are being killed (current worker count drops significantly from previous snapshot)
- Fix the Game 7 army stall where 59 units sit idle for 180+ seconds — force attack when army exceeds 40 units regardless of threshold, and also attack when army hasn't changed size for a long time indicating a stall
- Fix standard_macro mineral float and single-base stagnation seen in Games 6 and 8 where the bot stays on 1 base with 30-40 workers but never expands — lower expansion defense requirement so second base is taken earlier when any army exists