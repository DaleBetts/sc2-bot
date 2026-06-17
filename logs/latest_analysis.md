# Bot Analysis Report

**All-time win rate:** 48.8% (406W / 373L over 832 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 48.8%)

**By race (all-time):**
- Zerg: 104W / 119L  avg game 679s
- Protoss: 192W / 138L  avg game 649s
- Random: 48W / 39L  avg game 615s
- Terran: 62W / 77L  avg game 638s

**By strategy (all-time):**
- standard_macro: 159W / 212L
- dt_rush: 123W / 74L
- four_gate: 124W / 87L

**By strategy (recent 10 games):**
- standard_macro: 5W / 2L
- four_gate: 1W / 0L
- dt_rush: 1W / 0L

**Analysis:**
The bot is performing well recently at 70% win rate (up from 48.8% all-time), showing clear improvement. The two losses are Game 6 (early proxy/cannon rush wipe at t=180s — workers drop from 19 to 10 to 2 to 0 within 120s despite existing defenses) and Game 10 (Terran standard_macro loss where army oscillates 6-8-2-7-4-3 from t=360-660s, never rebuilding effectively, then workers bleed from 40 to 0 by t=840s). Game 4 is a Tie that dragged to 2040s with 0 workers and 1 army unit surviving on 0 minerals — the auto-surrender logic requires workers==0 AND army==0, but 1 army unit keeps the bot alive forever. Game 10's army oscillation suggests the bot is repeatedly sending tiny armies of 2-8 to attack and losing them, then rebuilding slowly and repeating. The safety_expand condition fires but since workers stay at 40 on 1 base the economy can't support rapid army rebuilding — the bot needs to avoid attacking when army is below a safe threshold while under economic pressure.

## Applied Improvements
- Fix Game 4 permanent zombie state: auto-surrender should trigger when workers==0 AND army<=1 AND bases==0 (not army==0) to catch the 0-worker/1-unit/0-base stall that lasted 1000+ seconds
- Fix Game 10 army oscillation death spiral: when standard_macro army drops below 6 after t=360 with workers>=30 on 1 base, raise the attack threshold to 10 to prevent sending suicidally small armies repeatedly and bleeding to 0
- Fix Game 6 early wipe: enemy detection radius for early defense is 15 but proxy cannon/zealot rush kills workers before reaching it; lower to 20 tiles and also check at t<180 for any combat unit within 25 tiles when workers are fewer than 16