# Bot Analysis Report

**All-time win rate:** 50.0% (521W / 462L over 1043 games)

**Recent 10-game win rate:** → stable (50.0%)

**By race (all-time):**
- Zerg: 122W / 149L  avg game 712s
- Protoss: 255W / 179L  avg game 651s
- Random: 58W / 47L  avg game 598s
- Terran: 86W / 87L  avg game 631s

**By strategy (all-time):**
- standard_macro: 208W / 267L
- dt_rush: 155W / 89L
- four_gate: 158W / 106L

**By strategy (recent 10 games):**
- four_gate: 0W / 3L
- dt_rush: 2W / 0L
- standard_macro: 3W / 2L

**Analysis:**
The bot is stagnating at exactly 50% win rate both all-time and recently, suggesting no net improvement from recent patches. The critical failures in the last 10 games are: (1) Game 1 - four_gate vs Protoss where workers drop from 19 to 1 at t=180s, indicating an extremely early rush that kills workers before any defense fires (the catastrophic_wipe detection requires army==0 but may not be responding fast enough); (2) Game 8 - four_gate vs Zerg where a maxed army of 73 units on 2 bases is completely wiped at t=1200s going from 47 workers to 0 instantly, suggesting the bot attacked with everything and got annihilated without the _permanent_attack_mode being the issue - the army was sent into a losing fight; (3) Games 3 and 4 - four_gate continues to lose (0W-3L recently) with the bot either dying early to worker wipes or stalling post-cheese; and (4) Game 9 - standard_macro vs Zerg where army of 52 collapses to 0 between t=900-1020s then workers are lost, suggesting the surrender timer is not firing fast enough after total army collapse.

## Applied Improvements
- Fix Game 8 catastrophic late-game wipe: army=73 on 2 bases gets wiped and workers=47 drop to 0 at t=1200s — the _permanent_attack_mode forces attack when army>=20 and time>720, but the army was sent into certain death; add a check that when workers drop by 10+ in a single 60s window with bases<=1 remaining, immediately surrender rather than losing all workers
- Fix Game 1 early worker wipe at t=180s: workers drop from 19 to 1 during four_gate — the catastrophic_wipe threshold of worker_drop>=4 per step should also trigger when workers fall below 5 total with no army regardless of drop rate, and should pull ALL remaining workers immediately
- Fix Game 9 slow surrender after army collapse: army goes from 52 to 4 between t=900-960s then workers start dying — the stuck_no_army_since timer requires 90s but workers are all dead within 60s of army collapse; when army collapses from peak>=30 to <=4 and workers>=35 on 1 base, cut the surrender timer to 45s