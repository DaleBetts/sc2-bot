# Bot Analysis Report

**All-time win rate:** 50.0% (496W / 437L over 992 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 50.0%)

**By race (all-time):**
- Zerg: 116W / 143L  avg game 707s
- Protoss: 243W / 166L  avg game 656s
- Random: 56W / 44L  avg game 606s
- Terran: 81W / 84L  avg game 634s

**By strategy (all-time):**
- standard_macro: 195W / 253L
- dt_rush: 150W / 83L
- four_gate: 151W / 101L

**By strategy (recent 10 games):**
- standard_macro: 2W / 3L
- four_gate: 2W / 1L
- dt_rush: 2W / 0L

**Analysis:**
The bot is improving significantly (60% recent vs 50% all-time), with dt_rush and four_gate performing well. The three losses are: Game 3 (standard_macro vs Protoss) where army collapses from 12 to 3-4 at t=480-540 and then stalls at army=4-5 on 1 base for 540+ seconds before workers are wiped at t=1020; Game 6 (standard_macro vs Protoss) where workers drop from 20 to 4 by t=180 suggesting an early cannon rush or proxy — bot loses all workers by t=240; Game 7 (standard_macro vs Protoss) where army builds to 59 on 1 base and sits completely idle from t=900 to t=1080 before workers are suddenly wiped at t=1140 — the permanent_attack_mode requires townhalls<=1 but army=59 with supply_cap=183 should be attacking. Game 9 (four_gate vs Terran) is a defeat where the army oscillates at 4-8 from t=360 to t=960 with workers building back to 40 — the bot transitions away from four_gate but never commits a real attack. The critical fix needed is Game 7: army=59 stalls from t=900-1080 because _permanent_attack_mode checks townhalls<=1 but the supply_cap>=150 check requires army>=40 AND a 60s cooldown — the combination misses sustained stalls; also Game 3 needs the stuck_no_army surrender to fire faster since army hovers at 3-5 (above the <=2 threshold) for 480s.

## Applied Improvements
- Fix Game 7 permanent army stall: army=59 sits idle from t=900-1080 because _permanent_attack_mode requires townhalls<=1 but the supply_cap/army>=40 path has a 60s cooldown that resets — lower the large_army_stall cooldown to 15s and remove the townhalls<=1 restriction from _permanent_attack_mode so a maxed army always attacks
- Fix Game 3 zombie stall: army hovers at 3-5 (above the <=2 threshold) for 480+ seconds on 1 base — raise the army_effectively_zero threshold to <=5 so the stuck_no_army surrender fires for this pattern
- Fix Game 9 four_gate post-cheese stall: army oscillates at 4-8 from t=360-960 with workers rebuilding to 40 but post_cheese_stall requires time>=600 — lower the post_cheese_stall time threshold to 420 so the bot attacks sooner after cheese fails rather than dithering for 9 minutes