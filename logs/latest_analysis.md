# Bot Analysis Report

**All-time win rate:** 50.9% (701W / 614L over 1376 games)

**Recent 10-game win rate:** ↓ declining (recent 30.0% vs all-time 50.9%)

**By race (all-time):**
- Zerg: 163W / 189L  avg game 708s
- Protoss: 337W / 247L  avg game 627s
- Random: 80W / 66L  avg game 587s
- Terran: 121W / 112L  avg game 615s

**By strategy (all-time):**
- standard_macro: 283W / 348L
- dt_rush: 205W / 127L
- four_gate: 213W / 139L

**By strategy (recent 10 games):**
- standard_macro: 2W / 6L
- dt_rush: 0W / 1L
- four_gate: 1W / 0L

**Analysis:**
The bot is in significant decline (30% vs 50.9% all-time), with 7 losses in the last 10 games. The clearest failure patterns are: Game 3 (standard_macro vs Protoss) runs for 1860s with a maxed 75-79 army sitting on 2-4 bases doing nothing — the stable_army_1base trigger doesn't fire because bases>1, the large_army stall trigger requires 1 base, and the frozen_state 300s timeout on 2+ bases is far too long; Game 6 (standard_macro vs Protoss) shows 40 workers + army growing from 20-39 on 1 base from t=360-780 and never expanding or attacking — the large_army_1base_attack override should be triggering but army is apparently fluctuating enough to reset timers; Game 5 (standard_macro vs Zerg) collapses at t=540 with army dropping to 2 on 1 base with 40 workers showing the bot never expanded despite workers>=40 on 1 base. The frozen_state timeout of 300s on multi-base games is the most critical bug since Game 3 dragged on for 1860s with army stable at 75-79.

## Applied Improvements
- Reduce frozen_state timeout on 2+ bases from 300s to 90s and add a multi-base stable-army surrender for army>=40 stable for 120s on 2+ bases, since Game 3 shows 75-army sitting idle for 1000+ seconds across 4 bases with no attack
- Add a multi-base large-army stall surrender: if army>=40 is stable (within 5 units) on 2+ bases past t=600 for 120s with minerals>500 (meaning no spending), surrender — catches Game 3's 75-army sitting on 4 bases for 1200s
- Force permanent attack on 2+ bases when army>=40 past t=600 to break Game 3's maxed-army camping pattern — add a multi-base large army attack override alongside the existing 1-base override