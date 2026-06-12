# Bot Analysis Report

**All-time win rate:** 45.9% (321W / 331L over 700 games)

**Recent 10-game win rate:** ↑ improving (recent 50.0% vs all-time 45.9%)

**By race (all-time):**
- Zerg: 88W / 105L  avg game 660s
- Protoss: 147W / 119L  avg game 660s
- Random: 42W / 36L  avg game 625s
- Terran: 44W / 71L  avg game 647s

**By strategy (all-time):**
- standard_macro: 120W / 189L
- dt_rush: 98W / 63L
- four_gate: 103W / 79L

**By strategy (recent 10 games):**
- four_gate: 3W / 2L
- standard_macro: 0W / 3L
- dt_rush: 2W / 0L

**Analysis:**
Recent win rate (50.0%) is up from the all-time 45.9%, showing modest improvement. However, Games 3, 4, 6, 8, and 10 reveal a persistent catastrophic pattern: workers are being wiped out before t=300s (Game 3: 19->7->0 workers by t=240; Game 4: workers 30->0 by t=300; Game 6: workers 22->1->0 by t=420; Game 8: workers 40->12->0 by t=480; Game 10: workers 40->26->0 by t=480). The bot's worker defense logic is either failing to respond early enough or is itself causing the wipes by sending workers into unwinnable fights. Standard_macro is 0-3 in recent games, suggesting a fundamental vulnerability to pressure when not using cheese — the bot masses workers to 30-40 but never takes a second base or builds enough army to defend, leaving a giant worker blob vulnerable to any attack.

## Applied Improvements
- Fix Game 10's standard_macro collapse: workers reach 40 on 1 base (army only 2-8) while supply_cap never grows past 79 — the bot is massively oversaturating on 1 base with no army; force expand earlier by lowering the oversaturated threshold to 30 workers (not 40) and add a safety expand when workers>=22 and army<5 and time>300 to get a second base before the bot becomes helpless
- Include safety_expand in the expand condition trigger to actually apply the new safety expand logic
- Fix Games 4/8/10 standard_macro army starvation: workers reach 30-40 but army stays at 2-8 because standard_macro delays gateway unit production waiting for infrastructure; when not cheese_active and workers>=20 and army<8, aggressively train zealots from ALL gateways (not just idle) every step to build a minimum defensive force before the base gets overrun