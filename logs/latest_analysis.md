# Bot Analysis Report

**Win rate:** 54.8% (46W / 31L over 84 games)

**By race:**
- Zerg: 16W / 12L  avg game 766s
- Protoss: 15W / 11L  avg game 880s
- Random: 8W / 4L  avg game 537s
- Terran: 7W / 4L  avg game 844s

**By strategy:**
- standard_macro: 12W / 24L
- dt_rush: 20W / 5L
- four_gate: 14W / 2L

**Analysis:**
The standard_macro strategy is catastrophically underperforming (12W/24L vs 34W/7L combined for cheese strategies). Game 1 shows workers collapsing from 19 to 3 by t=240s with bases dropping from 2 to 1, indicating the bot expands too early without defensive structures and loses both bases to early pressure. Game 3 (DT rush vs Terran) shows the bot getting supply-capped at 140/159 for 20+ minutes with 58 army units doing nothing — the attack threshold of 15 is met but units appear stuck, and the single-base DT rush fails to expand or apply pressure late. Game 7 shows massive mineral banking (19,000+ minerals) due to hitting supply cap at 200 with only 44 army units and no spending mechanism, meaning the standard_macro army composition and spending logic is broken at scale.

## Applied Improvements
- Lower the attack threshold from 15 to 8 for standard_macro so the bot doesn't bank an idle army while getting outmacro'd, and remove the idle-only filter so engaged units also push forward
- Add a defensive cannon/battery fallback during standard_macro expansion: require at least one Forge or ShieldBattery to be pending before expanding, preventing the early double-base loss seen in Game 1 where workers dropped from 19 to 3 after a premature expand
- Fix the massive mineral banking in late standard_macro (Game 7: 19000+ minerals) by spending excess minerals on additional Gateways when minerals exceed 800, allowing the bot to actually spend its income