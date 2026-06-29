# Bot Analysis Report

**All-time win rate:** 50.5% (556W / 485L over 1102 games)

**Recent 10-game win rate:** ↓ declining (recent 40.0% vs all-time 50.5%)

**By race (all-time):**
- Zerg: 130W / 156L  avg game 715s
- Protoss: 271W / 189L  avg game 649s
- Random: 62W / 49L  avg game 587s
- Terran: 93W / 91L  avg game 625s

**By strategy (all-time):**
- standard_macro: 225W / 282L
- dt_rush: 166W / 93L
- four_gate: 165W / 110L

**By strategy (recent 10 games):**
- standard_macro: 2W / 4L
- dt_rush: 1W / 2L
- four_gate: 1W / 0L

**Analysis:**
The bot is declining sharply (40% recent vs 50.5% all-time). The clearest patterns: Games 4 and 8 show workers wiped to 0 at t=180-240s (standard_macro vs Protoss) with only 1-2 army, indicating early rushes that the bot fails to detect and defend against — the 45s dead_since timer means the bot lingers after all workers die. Game 1 shows a catastrophic stall where army=59 and workers=42 sit frozen on 1 base from t=960-1440s (army unchanged, supply unchanged, minerals=40 frozen) then all die simultaneously at t=1500s — the permanent_attack_mode fires at t=480 with army>=20 but somehow the army never moves or the attack timer is being reset. Games 2 and 10 show dt_rush failing against Zerg and Terran respectively, with army oscillating 3-10 from t=360-660s on 1 base with workers recovering to 22-33 but never enough army to push. The _tiny_army_grind_since and _stuck_no_army_since surrender timers are not triggering because army briefly exceeds 5 or 15 resetting them.

## Applied Improvements
- Fix Game 1 frozen stall: army=59 workers=42 frozen on 1 base from t=960-1440s then all die at t=1500 — add a surrender trigger when supply_used and army_count are unchanged for 300+ seconds past t=600, indicating the game is completely frozen/deadlocked
- Fix Games 4 and 8: workers wiped to 0 at t=180-240s vs Protoss standard_macro — the dead_since timer waits 45s after workers=0 before surrendering; reduce to 5s when workers==0 AND army==0 AND time>60 to avoid prolonged dead games
- Fix Games 2 and 10 dt_rush failure: army oscillates 3-10 from t=360-660s on 1 base with workers=22-33, never recovering or attacking — when dt_rush cheese has expired (time>=480) and army<8 and workers>=20, immediately switch to zealot spam from all gateways every step rather than waiting for post_cheese_army_emergency which requires cheese_type not None AND not cheese_active AND army<12