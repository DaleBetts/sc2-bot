# Bot Analysis Report

**All-time win rate:** 50.9% (578W / 497L over 1136 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 50.9%)

**By race (all-time):**
- Zerg: 135W / 159L  avg game 713s
- Protoss: 282W / 196L  avg game 644s
- Random: 65W / 50L  avg game 582s
- Terran: 96W / 92L  avg game 624s

**By strategy (all-time):**
- standard_macro: 232W / 285L
- dt_rush: 173W / 98L
- four_gate: 173W / 114L

**By strategy (recent 10 games):**
- four_gate: 3W / 1L
- standard_macro: 3W / 2L
- dt_rush: 0W / 1L

**Analysis:**
Recent win rate (60%) significantly exceeds all-time (50.9%), showing improvement. The 4 recent losses break down as: Game 1 (four_gate vs Zerg) - army builds to 24 then bleeds from t=480-840 on 1 base, never triggering surrender despite tiny_army_grind thresholds; Game 3 (standard_macro vs Protoss) - army builds to 11 then collapses to 2 by t=540 and game ends, but standard_macro defense_emergency should have fired; Game 7 (dt_rush vs Protoss) - workers wiped from 20 to 1 at t=180, fast surrender fires correctly; Game 8 (standard_macro vs Protoss) - massive army builds to 59 on 1 base through t=840-960 and supply_used goes to 158/135 (over cap) suggesting a frozen/deadlocked state, yet frozen_state trigger never fires because it resets when army changes. Game 1 is the most critical: four_gate vs Zerg, army bleeds from 24->1 over 360s on 1 base with 40+ workers and minerals 0-95, but _grind_army_threshold for cheese is 12 so army 23,15,9,6,2,1 doesn't trigger until army<12 - yet army oscillates above 12 early resetting the timer each time.

## Applied Improvements
- Fix Game 1 four_gate vs Zerg bleed: army decays from 23->1 over t=480-840 on 1 base with 40 workers, but tiny_army_grind_since keeps resetting because army briefly exceeds the threshold; add a separate trigger specifically for four_gate vs Zerg where army peaked above 15 but has been declining for 300s with workers>=30 and no expansion
- Fix Game 8 standard_macro vs Protoss frozen stall: army=59 workers=40 on 1 base from t=840-960 with supply_used=158-160 and supply_cap=135-183 showing a deadlocked/confused state; the frozen trigger resets when army value changes by even 1 unit, so add a secondary check when army>=40 on 1 base past t=600 with no expansion pending for 240s regardless of minor army fluctuations
- Fix Game 1 four_gate vs Zerg never attacking: army builds to 24 at t=420 on 1 base but _four_gate_force_attack requires army>=8 and time>360 which should fire — however the army bleeds from 24 to 1 suggesting attacks are happening but losing; the bot should force surrender faster when four_gate vs Zerg results in army<8 with workers>=35 on 1 base past t=540 since this is unrecoverable