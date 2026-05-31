# Bot Analysis Report

**All-time win rate:** 47.2% (200W / 194L over 424 games)

**Recent 10-game win rate:** ↓ declining (recent 40.0% vs all-time 47.2%)

**By race (all-time):**
- Zerg: 63W / 69L  avg game 674s
- Protoss: 83W / 63L  avg game 673s
- Random: 28W / 23L  avg game 643s
- Terran: 26W / 39L  avg game 634s

**By strategy (all-time):**
- standard_macro: 70W / 119L
- dt_rush: 64W / 34L
- four_gate: 66W / 41L

**By strategy (recent 10 games):**
- four_gate: 1W / 2L
- standard_macro: 3W / 3L
- dt_rush: 0W / 1L

**Analysis:**
The recent 40% win rate is well below the 47.2% all-time average, indicating a clear regression. The dominant failure pattern in 6 of the last 10 games is catastrophic early worker wipeout: Games 2, 4, 5, 6, 8 all show workers dropping to 0-1 before t=180s with zero army response, indicating that early rushes (proxy gates, 2-gate, speedling all-ins) are killing all probes before any defense fires. The worker-drop detector added previously only triggers when 'worker_drop >= 2' but this may still be too slow since workers go from 16-20 to 0 in a single 60s snapshot, suggesting the detector fires too late or the response (attacking closest enemy) is insufficient because no army exists. Game 1 shows a different problem: the four_gate strategy builds a reasonable army but never expands off one base for 1320 seconds, keeping bases=1 throughout the entire game until death, and the four_gate_mid_expand condition requiring army>=8 is apparently never satisfied consistently enough to trigger.

## Applied Improvements
- Lower worker-drop threshold from 2 to 1 and also pull workers when enemy units are detected near base even without a worker drop, to catch proxy/rush threats sooner before all workers are dead
- Fix Game 1's permanent single-base stagnation in four_gate: lower the four_gate_mid_expand army threshold from 8 to 4 and also trigger expansion when minerals float above 300 on 1 base with 20+ workers, since the bot clearly accumulates minerals (t=300: 320 minerals, t=360: army=9) but never expands
- Add a nexus chrono-boost on probes to accelerate early probe production and reduce the window where the bot has few workers and no army, making it harder to be worker-wiped by early rushes