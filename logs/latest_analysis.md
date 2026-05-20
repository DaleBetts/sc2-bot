# Bot Analysis Report

**All-time win rate:** 51.2% (103W / 82L over 201 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 51.2%)

**By race (all-time):**
- Zerg: 37W / 30L  avg game 698s
- Protoss: 37W / 27L  avg game 738s
- Random: 14W / 8L  avg game 542s
- Terran: 15W / 17L  avg game 726s

**By strategy (all-time):**
- standard_macro: 32W / 58L
- dt_rush: 38W / 14L
- four_gate: 33W / 10L

**By strategy (recent 10 games):**
- four_gate: 1W / 1L
- standard_macro: 2W / 1L
- dt_rush: 4W / 0L

**Analysis:**
The bot is clearly improving (70% recent vs 51.2% all-time), driven by strong DT rush performance (4W-0L recent). The two recent losses reveal specific problems: Game 8 (four_gate vs Protoss) shows a sharp army collapse at t=420s (army drops from 14 to 7, then to 1 by t=480s) with supply dropping from 48 to 22, suggesting the bot lost its army and couldn't rebuild due to staying on one base with only 18-20 workers and insufficient gates; Game 9 (standard_macro vs Protoss) shows catastrophic worker loss starting at t=180s (workers drop from 19 to 13, then to 0 by t=360s) while army never builds, indicating the bot was proxy-rushed or cannon-rushed and had no defensive response — workers were killed and the bot never rallied army to defend. Game 5's tie shows a critical mineral float problem (15,153 minerals unspent at supply cap) where the bot hits 200/200 at t=660s and stops spending, wasting thousands of minerals instead of expanding or warping in more units.

## Applied Improvements
- Fix the massive mineral float in late-game supply-capped situations by continuously building additional gateways when minerals exceed 400 and supply is near cap, not just when minerals exceed 800
- Add active base defense: when workers are under attack (worker count drops significantly) immediately pull nearby workers to fight and rally idle army to defend, addressing the Game 9 pattern where workers were killed with zero defensive response
- Lower the four_gate attack threshold from 8 to 6 units since Game 8 shows the bot was accumulating 9-14 units but never reached the threshold decisively before losing them — attacking sooner keeps pressure and prevents the army from being picked off while idle