# Bot Analysis Report

**Win rate:** 53.8% (63W / 44L over 117 games)

**By race:**
- Zerg: 23W / 14L  avg game 782s
- Protoss: 21W / 14L  avg game 812s
- Random: 9W / 6L  avg game 593s
- Terran: 10W / 10L  avg game 771s

**By strategy:**
- standard_macro: 22W / 34L
- dt_rush: 24W / 6L
- four_gate: 17W / 4L

**Analysis:**
The standard_macro strategy loses 34 of 56 games (61% loss rate) while cheese strategies win at 80%+ rates, indicating the macro build is the core weakness. Game 8 (Terran loss) shows the bot stuck at 1 base with only 10 army units at t=600s despite 40 workers, then losing everything at t=660s — it never expanded and had insufficient army to defend. Game 3 (tie) shows the bot frozen at 1 base for the entire 1860s game, with supply cap actually decreasing from t=1080s onward (pylons being destroyed/desynced) and the bot unable to win despite 54 army units. The bot's expansion trigger requires a Forge or Shield Battery before expanding, creating a chicken-and-egg delay that keeps it on 1 base too long against aggressive opponents, and the attack threshold of 10 units is too conservative when the bot has a large army but never pushes.

## Applied Improvements
- Lower the defensive infrastructure requirement for expansion so the bot doesn't stay stuck on 1 base — 2 gateways and 4 army units is sufficient defense without needing a Forge or Shield Battery first
- Reduce the standard_macro attack threshold from 10 to 6 units so the bot actually applies pressure instead of banking a large idle army while the opponent macro-booms unopposed
- Increase pylon pre-build trigger from 8 to 12 supply remaining and allow up to 4 pending pylons so the bot doesn't get supply-blocked during macro games, which was evident in Game 8 where army stayed at 10 units for 3 minutes