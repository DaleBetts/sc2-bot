# Bot Analysis Report

**All-time win rate:** 49.5% (457W / 409L over 924 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 49.5%)

**By race (all-time):**
- Zerg: 110W / 134L  avg game 706s
- Protoss: 223W / 152L  avg game 646s
- Random: 50W / 42L  avg game 618s
- Terran: 74W / 81L  avg game 636s

**By strategy (all-time):**
- standard_macro: 178W / 237L
- dt_rush: 141W / 79L
- four_gate: 138W / 93L

**By strategy (recent 10 games):**
- dt_rush: 2W / 0L
- standard_macro: 1W / 2L
- four_gate: 4W / 1L

**Analysis:**
The bot is performing well recently at 70% win rate vs 49.5% all-time, showing clear improvement. The two recent losses are Game 2 (standard_macro vs Protoss) and Game 9 (standard_macro vs Protoss), both showing the same pattern: army grows to 33-59 on 1 base, stalls indefinitely (supply locked at same value for 300+ seconds in Game 2, army collapses from 33 to 0 at t=600 in Game 9), and the bot never expands despite having 40 workers and full mineral income. Game 2 shows a permanent supply-cap stall where army sits at 59 supply for 300s with no attack, no expand, and no resolution until t=1140 when the bot collapses. Game 9 shows army wiped at t=600 with 40 workers, then a slow zombie death as workers bleed away with no surrender. Game 3 (four_gate vs Zerg) shows a sudden worker wipe at t=660 with workers dropping from 30 to 0 in 60s suggesting a missed defense trigger. The standard_macro strategy has a deeply broken 1-base endgame where the bot accumulates massive supply but never pushes or expands decisively.

## Applied Improvements
- Fix Game 2 permanent supply-cap stall: when supply_used equals supply_cap for 2+ consecutive snapshots with army>=40 and 1 base, force an immediate attack regardless of attack timers — the bot is deadlocked building nothing and attacking nothing
- Fix Game 9 slow zombie: army collapses from 33 to 1 between t=540 and t=660 on 1 base with 40 workers — current stuck_no_army_since requires minerals<=25 but Game 9 shows minerals=65-95 during the collapse; raise the minerals threshold to 100 to catch this pattern earlier and accelerate surrender
- Fix Game 3 sudden worker wipe at t=660: workers drop from 30 to 0 in 60s during four_gate with army=0 on 1 base — the late_no_army_defense detection radius of 30 tiles only applies after t=480 but the four_gate cheese is still nominally active; extend the large detection radius to also apply when army==0 and workers>=20 during four_gate regardless of time