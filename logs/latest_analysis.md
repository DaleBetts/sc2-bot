# Bot Analysis Report

**Win rate:** 53.2% (50W / 36L over 94 games)

**By race:**
- Zerg: 18W / 13L  avg game 766s
- Protoss: 16W / 13L  avg game 841s
- Random: 8W / 5L  avg game 552s
- Terran: 8W / 5L  avg game 800s

**By strategy:**
- standard_macro: 15W / 26L
- dt_rush: 21W / 6L
- four_gate: 14W / 4L

**Analysis:**
Standard macro has a terrible 15W-26L record, the worst of all strategies. The timelines reveal two compounding problems: (1) worker counts plateau at exactly 22 in nearly every game and never grow beyond that even in the late game, starving the economy of income needed to sustain a macro game; (2) the bot never expands beyond 1 base in any losing standard_macro or four_gate game, meaning supply caps stay low (~71) and army sizes stagnate around 6-10 units after the initial push is repelled. Game 8 (DT rush vs Protoss) is a catastrophic 4-minute loss where workers drop to 0 at t=240s, suggesting the bot's own DT units are killing its probes — the DT harass sends idle DTs to attack enemy workers but the find_placement near start_location may be spawning DTs inside the bot's own base.

## Applied Improvements
- Fix DT spawn location to use a pylon near the enemy side rather than near start_location, preventing DTs from spawning in and attacking the bot's own workers
- Raise the worker cap in standard macro from townhalls*22 to a minimum of 40 workers before the first expansion check, so the bot actually saturates and funds a macro game instead of idling at 22
- Loosen the expansion condition so standard macro expands earlier — remove the forge/battery defense prerequisite when the bot already has 2+ gateways and an army, since the current gate forces it to stay on 1 base for the entire game