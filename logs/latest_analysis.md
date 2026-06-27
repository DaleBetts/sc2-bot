# Bot Analysis Report

**All-time win rate:** 50.2% (534W / 469L over 1064 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 50.2%)

**By race (all-time):**
- Zerg: 124W / 152L  avg game 714s
- Protoss: 261W / 181L  avg game 655s
- Random: 60W / 48L  avg game 592s
- Terran: 89W / 88L  avg game 629s

**By strategy (all-time):**
- standard_macro: 215W / 272L
- dt_rush: 158W / 90L
- four_gate: 161W / 107L

**By strategy (recent 10 games):**
- standard_macro: 5W / 2L
- four_gate: 2W / 1L

**Analysis:**
The bot is performing well recently at 70% win rate vs 50.2% all-time, showing clear improvement. The 3 losses are: Game 3 (Random, standard_macro) where army erodes from 7 to 0 over t=480-720s on 1 base with workers surviving until t=780 when they suddenly all die — the army is slowly ground down but never expands or commits; Game 6 (Terran, standard_macro) where army peaks at 18 at t=480 then collapses to 4 by t=540 and the bot never expands beyond 1 base with 40 workers, then workers start dying at t=660; Game 9 (Zerg, four_gate) where the bot accumulates army=30 on 1 base from t=480-1140s never attacking with permanent_attack_mode requiring time>720 and army>=20 but somehow failing to fire — army stays at 28-30 for 400+ seconds then collapses at t=1140 suggesting the bot is attacking into a fortified position without proper force. The core issues are: (1) standard_macro never expands on 1 base when army is small (Game 3/6), (2) Game 9 four_gate post-cheese stall with army=30 idling for 10+ minutes on 1 base — the permanent_attack_mode fires but army keeps returning (not permanent), suggesting it needs to also prevent retreat.

## Applied Improvements
- Fix Game 3 and Game 6 standard_macro single-base trap: army slowly erodes while bot stays on 1 base with 38-40 workers and tiny army — lower safety_expand worker threshold from 22 to 18 and raise army threshold from <6 to <10 so the bot expands earlier before army is ground down
- Fix Game 9 four_gate permanent stall: army=30 idles on 1 base from t=480-1140s because permanent_attack_mode requires time>720 — lower the time threshold to 480 and also require townhalls==1 so large armies on a single base always commit to attack rather than oscillating
- Fix Game 6 and Game 3 surrender delay: after army collapses to 0 with 34-40 workers still alive on 1 base, the bot lingers for minutes while workers die — add a fast surrender trigger when army drops to 0 from a meaningful peak and workers have been dying for 60s consecutively