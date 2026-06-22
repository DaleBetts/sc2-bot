# Bot Analysis Report

**All-time win rate:** 49.4% (467W / 419L over 945 games)

**Recent 10-game win rate:** ↓ declining (recent 40.0% vs all-time 49.4%)

**By race (all-time):**
- Zerg: 111W / 139L  avg game 709s
- Protoss: 228W / 156L  avg game 647s
- Random: 52W / 42L  avg game 615s
- Terran: 76W / 82L  avg game 634s

**By strategy (all-time):**
- standard_macro: 186W / 243L
- dt_rush: 142W / 81L
- four_gate: 139W / 95L

**By strategy (recent 10 games):**
- four_gate: 1W / 2L
- standard_macro: 2W / 3L
- dt_rush: 1W / 1L

**Analysis:**
The bot is declining — recent 40% WR vs 49.4% all-time. Three distinct failure patterns emerge: (1) Games 1, 5, 8 show the bot accumulating 39-40 workers and a large army (21-39 units) on 1 base, the army gets wiped in a single engagement around t=480-600, then the bot enters a zombie state rebuilding workers to 40 with 0 army for 120-240s before workers get wiped — the late_no_army_defense and stuck_no_army_since triggers aren't catching this fast enough. (2) Game 6 DT rush shows extreme mineral float (1375 at t=480, 1045 at t=720-780) with tiny army (3-10 units) on 3 bases — minerals are never spent on army units during the post-cheese phase. (3) Games 1 and 10 show four_gate staying on 1 base for 900-960s with army oscillating 18-21 and never attacking decisively — the attack threshold and expansion logic aren't forcing resolution. The _stuck_no_army_since threshold of 120s is too slow to catch rapid worker wipes in Games 5 and 8 where workers go from 40 to 0 in 60-120s after army collapse.

## Applied Improvements
- Fix Games 5 and 8 rapid post-army-wipe worker annihilation: when army drops from 20+ to 0 on 1 base after t=480, immediately trigger full worker pull defense rather than waiting for the _stuck_no_army_since 120s timer — army collapses at t=480-600 and workers are wiped within 60-120s before the timer fires
- Fix Game 6 extreme mineral float during dt_rush post-cheese: minerals sitting at 1000+ with tiny army means the bot never spends minerals on gateway units after cheese window — force zealot/stalker production from all gateways every step when minerals exceed 500 and army is under 15 regardless of cheese state
- Fix Games 1 and 10 four_gate permanent 1-base stall: army oscillates 18-21 for 600+ seconds on 1 base without attacking or expanding — lower the four_gate attack threshold from 6 to 4 and force immediate expand when four_gate army >= 12 and time > 420 to break the stall