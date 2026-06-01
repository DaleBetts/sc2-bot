# Bot Analysis Report

**All-time win rate:** 45.4% (201W / 211L over 443 games)

**Recent 10-game win rate:** ↓ declining (recent 10.0% vs all-time 45.4%)

**By race (all-time):**
- Zerg: 64W / 71L  avg game 666s
- Protoss: 83W / 71L  avg game 670s
- Random: 28W / 27L  avg game 649s
- Terran: 26W / 42L  avg game 627s

**By strategy (all-time):**
- standard_macro: 71W / 126L
- dt_rush: 64W / 40L
- four_gate: 66W / 45L

**By strategy (recent 10 games):**
- standard_macro: 1W / 2L
- dt_rush: 0W / 4L
- four_gate: 0W / 3L

**Analysis:**
The bot is in severe decline (10% recent vs 45.4% all-time), with 9 of 10 recent games lost. The dominant pattern across games 1, 3, 4, 5, 6, 7, 8, 9 is that all workers are wiped (drop to 0) at various times (t=180s to t=1140s) while army remains at 0-1, meaning the worker-defense code is not functioning. The worker-drop detector fires every step and pulls workers to attack, but the workers die anyway — the issue is that pulling ALL workers away from mining to chase enemies means they stop mining AND die anyway since they can't fight army units. Games 3, 7, 9 show a secondary critical bug: army stays at exactly 0-1 for 600-1000+ seconds despite having 22-24 workers and pylons/structures — the dt_rush and four_gate strategies produce zero army units for the entire game duration, indicating the warpgate/gateway army production is silently failing (likely find_placement returning None repeatedly or the warpgate having no ready units due to the cheese state logic).

## Applied Improvements
- Fix the silent army production failure in dt_rush/four_gate: when cheese is active and army is 0 after t=240s, force-train zealots from idle gateways and attempt warpgate warpin every step, bypassing the spawn_near placement that may be returning None by using a position closer to the nexus
- Fix worker-wipe defense: instead of sending ALL workers to attack (which just kills them faster), only pull a small number of workers (max 4) to defend and keep the rest mining, unless the nexus itself is under direct attack — this prevents the mass-worker-suicide pattern seen in games 1,3,4,5,6,7,8,9
- Fix games 3,7,9 where dt_rush/four_gate produce 0 army for 600+ seconds: add a hard override that disables cheese_active and forces standard macro mode when army is 0 after t=360s regardless of cheese type, since the cheese has clearly failed by then