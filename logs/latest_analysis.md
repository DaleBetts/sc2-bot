# Bot Analysis Report

**All-time win rate:** 50.8% (634W / 553L over 1248 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 50.8%)

**By race (all-time):**
- Zerg: 147W / 175L  avg game 711s
- Protoss: 308W / 218L  avg game 635s
- Random: 71W / 59L  avg game 583s
- Terran: 108W / 101L  avg game 618s

**By strategy (all-time):**
- standard_macro: 256W / 313L
- dt_rush: 187W / 116L
- four_gate: 191W / 124L

**By strategy (recent 10 games):**
- standard_macro: 2W / 3L
- dt_rush: 2W / 1L
- four_gate: 2W / 0L

**Analysis:**
Recent win rate of 60% is significantly above the all-time 50.8%, indicating the bot is genuinely improving. The two recent losses worth fixing are Game 1 (standard_macro vs Protoss: army of 30 at t=480 collapses to 6 then 1 by t=660 on 1 base with 40+ workers — a clear death-spiral that the existing grind/frozen detection misses because army oscillates above thresholds) and Game 7 (standard_macro vs Protoss: army grows to 58 by t=840 on 1 base but never attacks — the _large_army_1base_since trigger requires army>=40 AND workers>=36 AND no pending Nexus, but this game might be building a Nexus or fluctuating just below threshold). Game 5 (standard_macro vs Zerg) also loses with army decaying from 36 at t=540 to 18 at t=660 while permanently stuck on 1 base, suggesting the early_standard_expand and safety_expand conditions are either not triggering or the expansion attempt fails on this map. The core unresolved issue is standard_macro getting locked on 1 base with 40 workers and a large army that slowly bleeds out against Protoss and Zerg.

## Applied Improvements
- Game 7 fix: army of 58 on 1 base at t=840 never attacks — lower the _large_army_1base_since army threshold from 40 to 30 and workers threshold from 36 to 30 so large armies on 1 base are forced to attack sooner, and also reduce the timeout from 240s to 120s since this pattern is clearly unwinnable
- Game 1 and 5 fix: standard_macro army collapses from 30 to 1-6 over 60-120s on 1 base with 40 workers — the frozen_state detection misses this because army IS changing (collapsing); add a rapid_army_collapse surrender trigger that fires when army drops from a peak of >=25 to <=6 on 1 base with workers>=30 past t=480 and persists for 90s, catching the death-spiral before it grinds on for 300+ more seconds