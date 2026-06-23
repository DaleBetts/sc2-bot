# Bot Analysis Report

**All-time win rate:** 49.7% (480W / 427L over 966 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 49.7%)

**By race (all-time):**
- Zerg: 113W / 143L  avg game 709s
- Protoss: 235W / 160L  avg game 647s
- Random: 54W / 42L  avg game 611s
- Terran: 78W / 82L  avg game 632s

**By strategy (all-time):**
- standard_macro: 189W / 247L
- dt_rush: 147W / 83L
- four_gate: 144W / 97L

**By strategy (recent 10 games):**
- dt_rush: 2W / 1L
- standard_macro: 1W / 2L
- four_gate: 3W / 1L

**Analysis:**
The bot is performing well recently at 60% vs 49.7% all-time, but two losses share a critical pattern: Game 1 (dt_rush defeat) shows workers surviving to t=600 with army=3, then workers drop from 30 to 0 at t=660 — a rapid worker wipe with no response despite the existing defense logic. Game 2 (standard_macro defeat) shows the bot stalling on 1 base from t=600 to t=1260 with army oscillating 1-3 and workers at 40+ for 660 seconds before finally losing — the _stuck_no_army threshold of minerals<=100 is too tight since minerals sit at 55 the entire time. Game 4 (four_gate vs Zerg defeat) shows army collapsing from 21 to 0 between t=420 and t=660 with workers wiped at t=660, similar to Game 1. Game 10 (standard_macro vs Zerg defeat) shows the army slowly eroding from 49 down to 16 from t=840 to t=1260 without ever attacking — the bot is on 1 base the entire time with army>=30 but the large_army_stall condition requires townhalls<=1 AND time>600 which should be firing but _last_attack_time keeps getting reset preventing the timed attack from breaking the stall.

## Applied Improvements
- Fix Game 2 zombie stall: army sits at 1-3 with 40+ workers on 1 base for 660s — the stuck_no_army threshold of minerals<=100 excludes this pattern where minerals=55; raise threshold to 150 and also reduce the required idle time from 120s to 90s to surrender faster
- Fix Games 1 and 4 late worker wipe: workers drop from 30 to 0 in 60s at t=660 when army=0 — the rapid_army_collapse detection requires peak_army>=15 but at t=600 army is only 3 for Game 1; add a direct trigger: when workers drop by 5+ in a single step with no army, immediately pull ALL remaining workers to fight rather than capping at 6
- Fix Game 10 standard_macro vs Zerg slow army erosion: army decays from 49 to 16 over 420s on 1 base without attacking — the large_army_stall fires every 30s but _last_attack_time gets reset each time, then the army retreats and rebuilds slowly; force a continuous attack (not rally) when army>=20 on 1 base past t=720 with no second base so the bot commits rather than yo-yoing