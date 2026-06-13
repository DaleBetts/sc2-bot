# Bot Analysis Report

**All-time win rate:** 46.5% (337W / 338L over 724 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 46.5%)

**By race (all-time):**
- Zerg: 92W / 107L  avg game 661s
- Protoss: 155W / 123L  avg game 658s
- Random: 42W / 37L  avg game 621s
- Terran: 48W / 71L  avg game 643s

**By strategy (all-time):**
- standard_macro: 128W / 194L
- dt_rush: 100W / 64L
- four_gate: 109W / 80L

**By strategy (recent 10 games):**
- standard_macro: 4W / 2L
- four_gate: 3W / 1L

**Analysis:**
The bot is performing well recently at 70% win rate (up from 46.5% all-time), showing the recent improvements are working. The two losses are Game 1 (Protoss, 3 minutes — workers drop from 20 to 1 at t=180s suggesting a proxy or cannon rush wipe with no defense) and Game 3 (Zerg, 11 minutes — army stays at 1-4 units across 9 minutes of 3-base macro before workers suddenly drop at t=660s, classic case of massively over-droning with no army production). Game 6 is a four_gate loss where after the attack fails at t=480s the bot rebuilds workers to 40 on 1 base with army falling to 0 and stays in a permanent stall for 700+ seconds before dying — the four_gate_mid_expand and safety_expand logic should have triggered but the cheese_active check blocks expansion since four_gate is still technically active until t=480. Game 3 shows the standard_macro army starvation problem persists vs Zerg with 3 bases and 63 workers but only 4-8 army units, meaning the standard_macro_defense_emergency zealot training is not helping enough when workers>=60.

## Applied Improvements
- Fix Game 6 four_gate permanent stall: after four_gate army is wiped and cheese window closes (t>=480), the bot rebuilds workers but expansion is blocked by the cheese_active check — add a post_cheese_expand that fires in _expand even when cheese_type==_CHEESE_4GATE and the bot has been sitting on 1 base past t=480 with workers>=22, by moving the cheese_active early return to allow post-cheese expansion
- Fix Game 3 Zerg loss where 3-base macro produces 63 workers but only 4-8 army units: the standard_macro_defense_emergency threshold of army<8 only applies when workers>=20, but with 63 workers the bot should be producing far more army — raise the army threshold to 16 when workers>=40 to force aggressive gateway production at large worker counts vs Zerg
- Fix Game 1 early proxy/cannon rush wipe: at t=180s workers drop from 20 to 1 with no army and no recovery — the enemy_near_base_early defense check uses closer_than(15) but a proxy cannon or zealot rush can kill workers before reaching that threshold; also the max_worker_defenders cap of 4 is too low when nexus is not yet detected as under_attack — lower enemy detection radius to 20 for non-cheese early defense and increase worker defenders to 6 when workers are dying rapidly