# Bot Analysis Report

**All-time win rate:** 44.5% (246W / 264L over 553 games)

**Recent 10-game win rate:** ↑ improving (recent 80.0% vs all-time 44.5%)

**By race (all-time):**
- Zerg: 71W / 85L  avg game 659s
- Protoss: 110W / 92L  avg game 654s
- Random: 35W / 32L  avg game 645s
- Terran: 30W / 55L  avg game 661s

**By strategy (all-time):**
- standard_macro: 90W / 153L
- dt_rush: 80W / 51L
- four_gate: 76W / 60L

**By strategy (recent 10 games):**
- four_gate: 2W / 0L
- standard_macro: 2W / 0L
- dt_rush: 4W / 0L

**Analysis:**
The bot is performing excellently in recent games with an 80% win rate (up from 44.5% all-time), showing the previous fixes have been highly effective. However, two structural issues remain: Game 2 and Game 6 both end as Ties rather than wins — Game 2 shows the bot completely freezing at t=480s with 42 workers, 33 army, and 15 minerals forever (stuck in a 1-base stall with 108/135 supply), and Game 6 shows a worker wipe down to 11 workers with 0 army and 10 minerals from t=120s onward. Additionally, Games 1, 3, 5, 7, 8, 9, 10 all show the bot staying on 1 base far too long despite having 22+ workers and sufficient army — the four_gate_mid_expand and post_cheese_expand triggers are clearly not firing reliably enough during the critical window when cheese expires around t=480s.

## Applied Improvements
- Fix Game 2's permanent freeze: the bot reaches supply cap (108/135) on 1 base with 42 workers and never expands or attacks — add a hard override that forces expansion when on 1 base with 40+ workers regardless of cheese state, and force an all-out attack when army >= 20 and has been idle for 60+ seconds at supply near cap
- Wire the oversaturated_expand condition into the expand trigger, and also lower the post_cheese_expand worker threshold from 22 to 20 to catch the common case where cheese ends at t=480 with exactly 22 workers
- Fix Game 2's permanent stall by tracking last-attack time and forcing an all-out attack when army >= 20 and supply utilization is above 75% and we haven't attacked in 120+ seconds, preventing the bot from camping forever with a large army