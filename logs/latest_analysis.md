# Bot Analysis Report

**All-time win rate:** 49.1% (155W / 140L over 316 games)

**Recent 10-game win rate:** ↑ improving (recent 50.0% vs all-time 49.1%)

**By race (all-time):**
- Zerg: 49W / 55L  avg game 708s
- Protoss: 61W / 44L  avg game 711s
- Random: 22W / 14L  avg game 593s
- Terran: 23W / 27L  avg game 652s

**By strategy (all-time):**
- standard_macro: 48W / 95L
- dt_rush: 55W / 21L
- four_gate: 52W / 24L

**By strategy (recent 10 games):**
- dt_rush: 1W / 2L
- standard_macro: 1W / 2L
- four_gate: 3W / 1L

**Analysis:**
Recent win rate (50.0%) is marginally above all-time (49.1%), showing very slight improvement. The critical failures in the last 10 games are: (1) Games 1, 3, and 5 show workers being completely wiped to 0 by t=180-360s with army=0 and no defense triggered — the enemy reaches workers before any army exists; (2) Game 10 shows a four_gate that survives its cheese phase but then permanently stagnates on 1 base with 40 workers and army oscillating 0-12 for 900+ seconds, never expanding despite workers>=28, suggesting the force_expand check or the four_gate->macro transition is failing; (3) Game 2 shows standard_macro with 40 workers on 1 base from t=360 all the way to t=600+ with a growing army but never expanding, indicating the expand formula or has_defense check is still blocking expansion in non-cheese games even with large armies.

## Applied Improvements
- Fix Game 10's permanent single-base stagnation where four_gate ends but bot never transitions to expansion — after cheese window closes (time>=480), force expand immediately if workers>=22 and bases==1, bypassing the standard has_defense check since a post-cheese bot with 18+ workers and existing structures is always safe to expand
- Fix Games 1, 3, and 5 where workers are wiped before any army exists — when workers are dying fast (worker count drops) and enemy units are near any worker, immediately pull ALL workers to fight without requiring army to exist first, and also widen the threat detection radius to catch enemies approaching from natural distance
- Fix Game 2's standard_macro single-base stagnation where 40 workers sit on 1 base from t=360 to t=600+ — the expand target formula 1+(workers//12) should give target=4 at 40 workers but has_defense or already_pending is blocking it; add a strong override that forces expansion when workers>=36 and army>=10 regardless of all other conditions