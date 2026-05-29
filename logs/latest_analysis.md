# Bot Analysis Report

**All-time win rate:** 48.0% (182W / 170L over 379 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 48.0%)

**By race (all-time):**
- Zerg: 56W / 64L  avg game 693s
- Protoss: 73W / 55L  avg game 685s
- Random: 27W / 17L  avg game 617s
- Terran: 26W / 34L  avg game 637s

**By strategy (all-time):**
- standard_macro: 60W / 108L
- dt_rush: 60W / 27L
- four_gate: 62W / 35L

**By strategy (recent 10 games):**
- standard_macro: 4W / 2L
- four_gate: 2W / 1L
- dt_rush: 0W / 1L

**Analysis:**
The bot is trending positively at 60% recent win rate vs 48% all-time, showing clear improvement. However, Game 5 (four_gate vs Terran) and Game 7 (dt_rush vs Random) show catastrophic losses where workers survive until t=300-360 then collapse entirely to 0 by t=420. Game 5 is particularly alarming: workers stay at exactly 18 from t=120 to t=360 with minerals accumulating (160, 160, 195) suggesting probes are being trained but immediately dying or production is capped, then total wipeout with 0 army ever produced. Game 7 shows a permanent single-base stagnation with 40 workers and only 2-3 army units for 400+ seconds before late collapse — the dt_rush failed but the bot never transitioned to producing a meaningful army or expanding. Game 10 shows a similar pattern: 2 bases, 45 workers, but army never exceeds 8, minerals accumulate (85, 125, 100), and the base gets overwhelmed at t=660+. The core issues are: (1) failed cheese strategies leave the bot with no army and no expansion drive, (2) standard_macro games on 2 bases fail to convert worker advantage into army fast enough when minerals are floating above 50.

## Applied Improvements
- Fix Game 7's post-DT-fail stagnation: when dt_rush cheese is inactive (failed/expired) and army is tiny (<8) but workers are high (>=22), aggressively build gateways and force unit production every step rather than waiting for idle gateway checks — add a post-cheese army emergency production block that trains from ALL gateways+warpgates every step regardless of idle state
- Fix Game 10 and Game 7's army stagnation on 2 bases: the force-attack threshold of army>=20 is too high — games show army plateauing at 6-8 with minerals floating, bot never attacks; lower force-attack to army>=12 to push aggression earlier and also fix the mineral-float issue by lowering the emergency production threshold from minerals>300 to minerals>200 (already done above) and attack threshold from army>=20 to army>=12
- Fix Game 5's worker freeze at exactly 18 for 240 seconds with floating minerals — the four_gate worker cap of 18 is too restrictive and combines with no army production to leave the bot defenseless; raise four_gate worker cap to 22 so the bot keeps training probes when idle and can defend rushes while also adding a gateway building trigger when minerals float above 150 during four_gate to ensure gates are being built