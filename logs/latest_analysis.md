# Bot Analysis Report

**All-time win rate:** 51.0% (658W / 571L over 1290 games)

**Recent 10-game win rate:** ↓ declining (recent 40.0% vs all-time 51.0%)

**By race (all-time):**
- Zerg: 153W / 180L  avg game 711s
- Protoss: 319W / 226L  avg game 630s
- Random: 74W / 61L  avg game 583s
- Terran: 112W / 104L  avg game 619s

**By strategy (all-time):**
- standard_macro: 266W / 323L
- dt_rush: 195W / 119L
- four_gate: 197W / 129L

**By strategy (recent 10 games):**
- four_gate: 1W / 1L
- standard_macro: 1W / 4L
- dt_rush: 2W / 1L

**Analysis:**
The bot is declining (40% recent vs 51% all-time). The clearest failures are: Game 1 (four_gate vs Protoss) where army builds to 50 on 1 base by t=720 but never attacks or expands — the permanent_attack_mode threshold of 20 should fire but something is blocking it; Game 6 (dt_rush vs Terran) where army reaches 34 on 1 base at t=900 and grinds on indefinitely — the _large_army_1base_since trigger (army>=30, time>600) should fire but the game continues past t=900; Game 3 (standard_macro vs Zerg) where workers collapse from 46 to 12 between t=480-600 while army holds at 24, then the bot grinds on 1 base with army=29-30 from t=720-1140 for 420 seconds — the frozen_state detection should catch army stable at 29-30 for 180s but it requires army>=20 AND workers>=20 and the tolerance of 3 means 29-30 passes as stable, so the issue is the _frozen_state_since timer resetting or the 180s timeout being too long for 1-base stalls.

## Applied Improvements
- Game 1 fix: four_gate army grows to 50 on 1 base by t=720 but never attacks — the _four_gate_post_cheese_large_army path requires army>=15 but the _permanent_attack_mode path (army>=20, time>480) should also fire; add explicit hard attack override for any strategy when army>=20 on 1 base past t=480 with workers>=20 to catch this stall before the frozen_state timer fires
- Game 6 fix: dt_rush vs Terran, army=34 on 1 base at t=900 never triggers surrender — the _large_army_1base_since trigger requires not already_pending(NEXUS) but may be getting reset; also reduce the frozen_state timeout on 1 base from 180s to 90s so Game 3's army=29-30 stable for 420s surrenders much sooner
- Game 3 fix: standard_macro vs Zerg, army stable at 24-30 on 1 base from t=720-1140 (420s) — frozen_state never fires because workers fluctuate 12-33 resetting the snapshot; add a dedicated grind surrender when army is stable (peak>=20, current>=20) on 1 base with workers>=10 past t=600 persisting 120s, independent of worker count fluctuations