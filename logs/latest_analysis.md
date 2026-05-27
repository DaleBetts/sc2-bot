# Bot Analysis Report

**All-time win rate:** 48.5% (163W / 149L over 336 games)

**Recent 10-game win rate:** ↓ declining (recent 30.0% vs all-time 48.5%)

**By race (all-time):**
- Zerg: 50W / 59L  avg game 699s
- Protoss: 65W / 47L  avg game 704s
- Random: 24W / 14L  avg game 594s
- Terran: 24W / 29L  avg game 654s

**By strategy (all-time):**
- standard_macro: 50W / 98L
- dt_rush: 59W / 24L
- four_gate: 54W / 27L

**By strategy (recent 10 games):**
- dt_rush: 1W / 2L
- four_gate: 1W / 2L
- standard_macro: 1W / 2L

**Analysis:**
The bot is declining significantly — 30% win rate in recent games vs 48.5% all-time. The dominant failure pattern across Games 1, 2, 3, 6, 7, 9 is workers being massacred (dropping to 0-4) with no meaningful army response, suggesting the emergency defense triggers are still failing. Game 1 shows the most critical new pattern: the bot reaches 54 army supply at t=960s-t=1260s but NEVER attacks (supply frozen at 150/183 for 5 minutes), then workers die and game is lost — the army.amount>=25 force-attack condition should have triggered but the army is stuck in idle rally loop. Games 3 and 7 show macro stagnation with only 4-10 army units on 2 bases for 600+ seconds while Zerg scales up, and Game 1 specifically shows the bot sitting on 1 base with 54 army units for 20+ minutes never pressing the attack, indicating the force-attack threshold of 25 is not reliably executing when units are not idle or moving.

## Applied Improvements
- Fix Game 1's catastrophic army stall where 54 units sit frozen for 300+ seconds — the force-attack block only runs if army.amount>=25 but the units may be in an 'attacking' state pointing at a rally point; force ALL army units to attack the target every step when army>=20 regardless of unit state, not just idle/moving units
- Fix Games 3 and 7 where army stays at 0-8 on 2 bases for 600+ seconds against Zerg — the standard_macro expand logic correctly fires but army production is negligible because gateways are idle while workers pile up; add an emergency unit production flush that trains zealots from ALL idle gateways+warpgates when minerals>300 and army<10 to prevent economic stagnation turning into a loss
- Fix Games 2, 4, 9 where workers drop to 0-1 very early (t=120-180s) with 0 army and no response — the current emergency defense requires enemy_units to be detected but early rushes may kill workers before detection; add a worker-count-drop detector that immediately pulls all surviving workers to fight when worker count drops by 4+ in a single check interval