# Bot Analysis Report

**All-time win rate:** 50.7% (567W / 491L over 1119 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 50.7%)

**By race (all-time):**
- Zerg: 133W / 158L  avg game 713s
- Protoss: 276W / 191L  avg game 647s
- Random: 64W / 50L  avg game 583s
- Terran: 94W / 92L  avg game 626s

**By strategy (all-time):**
- standard_macro: 228W / 283L
- dt_rush: 170W / 97L
- four_gate: 169W / 111L

**By strategy (recent 10 games):**
- standard_macro: 1W / 1L
- dt_rush: 3W / 2L
- four_gate: 2W / 1L

**Analysis:**
The bot is trending positively at 60% recent win rate vs 50.7% all-time, with clean wins in PvP (3-0) and reasonable PvZ (2-2). The two clear loss patterns are: Game 2 (dt_rush vs Zerg) where the army slowly erodes from 12 to 0 over 780s on 1 base with workers climbing to 40, never attacking or surrendering - the zealot spam emergency triggers but army bleeds away anyway; Game 9 (four_gate vs Terran) where army oscillates 3-12 from t=360-900s on 1 base with workers 22-41, never expanding or attacking decisively, running well past the 15-minute mark despite the permanent_attack_mode fix. Game 3 (dt_rush vs Random) ends quickly at t=300s which appears to be the ultra-fast surrender working correctly after worker wipe at t=240. The core remaining failure is the single-base grind where army is small (3-12) but fluctuates above the 5-unit threshold enough to reset surrender timers, and the four_gate permanent_attack_mode requires army>=20 but army never gets there.

## Applied Improvements
- Fix Game 9 four_gate vs Terran permanent stall: army of 3-12 on 1 base for 540s never attacks because permanent_attack_mode requires army>=20; lower the permanent_attack_mode threshold to 8 when cheese is active (four_gate) and time>360 to force early aggression before army bleeds out
- Fix Game 2 dt_rush vs Zerg slow bleed: army grows to 12 then decays to 0 over 780s while workers climb to 40 on 1 base; the tiny_army_grind_since trigger requires army<15 and minerals<200 and time>600 but army is often 9-12 with minerals~20-105 starting at t=360 - lower the time threshold to 360 and reduce the army threshold to 12 to catch earlier stalls, and also lower the persistence timer from 300s to 180s for single-base dt_rush games
- Fix Game 9 four_gate vs Terran never expands: army oscillates 3-12 on 1 base with 22-41 workers for 540s; the four_gate_mid_expand requires workers>=20 and (army>=4 OR minerals>=300) which should fire but minerals are low (0-100) and army is often 3-7; lower the army threshold to 3 and add a time-based override for four_gate stalling past t=480 on 1 base