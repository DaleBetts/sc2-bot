# Bot Analysis Report

**All-time win rate:** 49.1% (136W / 121L over 277 games)

**Recent 10-game win rate:** ↓ declining (recent 40.0% vs all-time 49.1%)

**By race (all-time):**
- Zerg: 45W / 47L  avg game 725s
- Protoss: 51W / 38L  avg game 734s
- Random: 19W / 13L  avg game 584s
- Terran: 21W / 23L  avg game 664s

**By strategy (all-time):**
- standard_macro: 41W / 84L
- dt_rush: 50W / 18L
- four_gate: 45W / 19L

**By strategy (recent 10 games):**
- dt_rush: 1W / 1L
- standard_macro: 2W / 3L
- four_gate: 1W / 2L

**Analysis:**
The recent 40% win rate is significantly below the all-time 49.1%, indicating the bot is declining. The most critical pattern across recent losses is catastrophic worker wipes with no army response: Game 1 drops from 22 workers to 0 by t=420s with army=0, Game 2 loses 47 workers between t=600-780s while army stays at 2-3 (massive mineral float of 3075-4035 suggests no spending/fighting), Game 4 bleeds workers from 43 to 0 between t=360-600s with army=0 the whole time, and Game 8 loses 39 workers instantly at t=600s. The mineral float in Game 2 (3075 minerals at t=600s, 4035 at t=660s) is the clearest bug: the bot is accumulating enormous mineral banks while workers die, meaning army production and expansion logic are completely broken in standard_macro late game. Game 5 also shows a one-base standard_macro that never expands despite 40 workers for 10+ minutes, and Game 9 shows a four_gate where all 19 workers died at t=240s with only 1 army unit surviving.

## Applied Improvements
- Fix the Game 2 catastrophic mineral float (3000+ minerals) by aggressively training units from all idle gateways and warpgates when minerals exceed 800, bypassing the normal unit priority to dump minerals into zealots/stalkers immediately
- Fix Game 5's permanent single-base stagnation where 40 workers sit on 1 base for 600+ seconds: lower the expansion target formula to expand earlier by reducing the worker-per-base divisor from 16 to 12, so the bot expands to 2 bases with ~24 workers instead of waiting for 32
- Fix Games 2, 4, and 8 where army stays at 0-3 while workers die in waves with no defense triggered: the near_base check uses distance 25 from start_location but enemy armies attacking workers may be at the natural or mid-map — add a broader worker threat check that pulls all workers to fight when workers are dying (worker count dropped more than 5 from previous check) even if no army exists near the main base