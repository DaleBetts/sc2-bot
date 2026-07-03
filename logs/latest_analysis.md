# Bot Analysis Report

**All-time win rate:** 51.1% (602W / 515L over 1178 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 51.1%)

**By race (all-time):**
- Zerg: 141W / 163L  avg game 711s
- Protoss: 292W / 204L  avg game 641s
- Random: 68W / 53L  avg game 584s
- Terran: 101W / 95L  avg game 621s

**By strategy (all-time):**
- standard_macro: 244W / 293L
- dt_rush: 182W / 104L
- four_gate: 176W / 118L

**By strategy (recent 10 games):**
- dt_rush: 3W / 2L
- four_gate: 1W / 1L
- standard_macro: 2W / 1L

**Analysis:**
The bot is trending positively at 60% recent win rate vs 51.1% all-time, showing improvement. The two clearest failures in recent games are: Game 2 (four_gate vs Zerg) where army grows steadily from 14 to 39 on 1 base over 1080s but never attacks — the four_gate_force_attack and permanent_attack_mode triggers are not firing because cheese is still active (t<480) initially and then army>=20 but conditions aren't met; Game 5 (dt_rush vs Protoss) where army grows to 32 at t=480 then collapses to 3 by t=660 and never recovers; and Game 8 (dt_rush vs Protoss) where army peaks at 11 at t=300 then decays to 0 by t=540 with workers also dying, suggesting the DT rush failed completely and the post-cheese recovery never triggered fast enough. Game 2's core issue is that with 39 army on 1 base at t=960 the bot never attacks — permanent_attack_mode requires army>=20 AND time>480 which should fire, but the four_gate cheese is no longer active past t=480 so _four_gate_force_attack is False, yet the army just sits there suggesting _permanent_attack_mode should be firing but the target resolution or attack command is failing for the four_gate vs Zerg stall case.

## Applied Improvements
- Fix Game 2 four_gate vs Zerg 1080s stall: army grows to 39 on 1 base but never attacks — add a hard override that forces attack when army>=15 on 1 base past t=600 regardless of cheese state or other conditions, since this is clearly unwinnable without aggression
- Fix Game 5 and Game 8 dt_rush collapse: army peaks then crashes to 0-3 after t=480 with growing worker count — when dt_rush cheese has expired (time>=480) and army<5 and workers>=20 on 1 base, surrender faster by reducing the _grind_persist_timeout to 60s instead of 180s since DT rush with no army on 1 base past t=540 is unrecoverable
- Fix Game 9 standard_macro vs Zerg collapse: army of 16 at t=420 decays to 0 by t=720 on 1 base while workers drop from 40 to 28 — the oversaturated_expand fires too late; add an earlier mandatory expand for standard_macro when workers>=25 on 1 base past t=300 with any army presence, to get a second base before the army bleeds out