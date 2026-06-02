# Bot Analysis Report

**All-time win rate:** 44.2% (207W / 227L over 468 games)

**Recent 10-game win rate:** ↓ declining (recent 20.0% vs all-time 44.2%)

**By race (all-time):**
- Zerg: 66W / 75L  avg game 663s
- Protoss: 87W / 76L  avg game 667s
- Random: 28W / 29L  avg game 675s
- Terran: 26W / 47L  avg game 635s

**By strategy (all-time):**
- standard_macro: 74W / 133L
- dt_rush: 66W / 45L
- four_gate: 67W / 49L

**By strategy (recent 10 games):**
- four_gate: 0W / 2L
- standard_macro: 1W / 4L
- dt_rush: 1W / 2L

**Analysis:**
The bot is in severe decline (20% recent vs 44.2% all-time). The dominant pattern across 7 of 10 recent games is total worker wipe before t=180s (Games 1, 4, 7) or between t=180-300s (Games 3, 6, 8, 9), after which the bot sits dead with 0 workers, 0 army, and ~20 minerals for hundreds of seconds yet never concedes. The worker defense code is actively harmful: the condition `enemy_near_base_early = self.enemy_units.closer_than(40, self.start_location)` combined with `army.amount < 3` triggers ALL workers to attack-move every step when any enemy is within 40 units, which suicides them into the enemy force. Additionally, Game 6 reveals the bot never surrenders when all workers/army are dead — it runs for 35+ minutes doing nothing, wasting ladder time. The _attack function also sends all workers to fight when `army.amount < 3 and all_enemy_near_base`, which is the mass-worker-suicide pattern causing most losses.

## Applied Improvements
- Fix the primary worker-suicide bug: the on_step worker defense pulls workers to attack whenever ANY enemy is within 40 units AND army<3, which fires constantly during normal early-game scouting and suicides all workers; raise the proximity threshold to 20 units and require enemy_near_base to have actual combat units (not just workers/overlords) before pulling workers
- Fix the _attack worker-suicide: the block that sends ALL workers to attack when army<3 and enemy is near base triggers on scout probes or any unit within 30 units, wiping the economy; restrict this to only fire when enemy combat units (non-workers) are within 20 units AND workers are already under direct attack (within 10 units)
- Add an auto-surrender when the game is clearly lost (0 workers, 0 army, 0 bases or nexus under attack with no hope of recovery for 60+ seconds) to stop the bot from sitting dead for 35 minutes like Game 6, which wastes ladder MMR time and distorts statistics