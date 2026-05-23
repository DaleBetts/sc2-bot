# Bot Analysis Report

**All-time win rate:** 49.4% (127W / 111L over 257 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 49.4%)

**By race (all-time):**
- Zerg: 43W / 43L  avg game 723s
- Protoss: 48W / 34L  avg game 733s
- Random: 17W / 12L  avg game 567s
- Terran: 19W / 22L  avg game 668s

**By strategy (all-time):**
- standard_macro: 39W / 79L
- dt_rush: 45W / 17L
- four_gate: 43W / 15L

**By strategy (recent 10 games):**
- standard_macro: 3W / 2L
- dt_rush: 3W / 1L
- four_gate: 0W / 1L

**Analysis:**
The bot is trending positively (60% recent vs 49.4% all-time), but the three recent losses reveal critical patterns: Game 1 (vs Zerg standard_macro) shows repeated worker wipes at t=360s, t=480s, t=900s, and t=960s where workers drop from 27→14, 14→4, 23→2 with army at 0-2 units — the defense logic fails to protect workers when army is near zero. Game 3 (dt_rush vs Zerg) is a catastrophic stall where 40+ workers and 1-base economy sit completely idle from t=480s to t=2700s with army=0-1 and minerals=5 — the DTs clearly all died around t=480s but the bot never transitioned out of cheese mode to attack or expand, just sat there. Game 6 (four_gate vs Zerg) shows all workers wiped at t=300s with army=0, suggesting the Zerg all-in overwhelmed defenses before the four_gate could fire. The highest priority fix is Game 3's permanent stall: when cheese_active expires (time>=480) but the bot has 40+ workers and no army and 1 base with minimal minerals, it must transition to expansion and army production rather than doing nothing.

## Applied Improvements
- Fix Game 3's catastrophic post-cheese stall: when dt_rush/four_gate cheese window ends (time>=480), if the bot has no real army and is still on 1 base with near-zero minerals being spent, force immediate expansion and reset cheese state so standard macro logic activates
- Fix Game 1's repeated worker wipes where army=0 and workers keep getting killed in waves: when there is NO army at all (army.amount==0) and enemy units are near base, pull ALL workers immediately rather than checking army ratios, since the current code returns early when army is empty but near_base check comes first
- Fix Game 3's single-base stall post-cheese where 42 workers sit on 1 base forever: in _expand, when cheese is no longer active and the bot has many workers but only 1 base, lower the has_defense requirement so it expands immediately rather than waiting for structures that were never built during the all-in