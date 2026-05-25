# Bot Analysis Report

**All-time win rate:** 48.8% (145W / 131L over 297 games)

**Recent 10-game win rate:** ↓ declining (recent 30.0% vs all-time 48.8%)

**By race (all-time):**
- Zerg: 47W / 53L  avg game 722s
- Protoss: 55W / 40L  avg game 731s
- Random: 21W / 13L  avg game 582s
- Terran: 22W / 25L  avg game 669s

**By strategy (all-time):**
- standard_macro: 45W / 91L
- dt_rush: 52W / 18L
- four_gate: 48W / 22L

**By strategy (recent 10 games):**
- standard_macro: 1W / 5L
- four_gate: 1W / 2L
- dt_rush: 1W / 0L

**Analysis:**
The bot is clearly declining from 48.8% all-time to 30% in the last 10 games. The most critical pattern is catastrophic early worker wipes in Games 3, 7, 8 (workers drop to 0 by t=240s), suggesting the bot fails to defend against early rushes before it has any army. Game 9 shows a different failure: 35-40 workers on 1 base for 1000+ seconds with army=35-40 sitting idle, never attacking or expanding — the force-attack threshold of 30 units is clearly not working since the bot reaches 40 units but units are not all attacking. Game 2 shows a late-game collapse where workers suddenly drop from 45 to 1 at t=900s with army=0, meaning enemies killed all workers while the army was away attacking. The standard_macro strategy is 1W/5L in recent games indicating systemic failures across multiple scenarios.

## Applied Improvements
- Fix Game 9's permanent single-base stagnation with 35-40 army sitting idle for 600+ seconds — the force-attack condition 'army.amount >= 30' only lowers the threshold to itself which does nothing meaningful; instead force ALL units to attack immediately when army exceeds 25 regardless of idle state or threshold
- Fix Game 9's single-base stagnation where 40 workers sit on 1 base forever — the expand formula target=1+(workers//12) requires 24 workers for 2 bases but has_defense conditions block expansion; add an explicit rule that forces expansion when workers>=28 and only 1 base regardless of has_defense since by that point any defense requirement is moot
- Fix Games 3 and 7 where workers are wiped to 0 by t=180-240s with no army and no defense triggered — the current enemy_near_any_structure check only unions enemies near townhalls but the loop variable shadows the initial value; rewrite to correctly aggregate all enemy units near any structure or worker