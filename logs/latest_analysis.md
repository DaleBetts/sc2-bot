# Bot Analysis Report

**Win rate:** 50.7% (69W / 56L over 136 games)

**By race:**
- Zerg: 25W / 19L  avg game 751s
- Protoss: 24W / 18L  avg game 794s
- Random: 10W / 7L  avg game 580s
- Terran: 10W / 12L  avg game 748s

**By strategy:**
- standard_macro: 25W / 43L
- dt_rush: 26W / 7L
- four_gate: 18W / 6L

**Analysis:**
Standard macro games are losing at a 43/25 rate (63% loss rate), while cheese strategies win reliably. The timelines reveal three critical issues: (1) Game 1 shows supply_cap dropping to 23 at t=360s (supply blocked with 28 workers), causing army and worker production to collapse; (2) Games 2, 6 show the bot plateaus at 1 base for 10+ minutes with no expansion despite having 40 workers and 87 supply cap, so it never takes a second base; (3) Game 8 ends at t=300s with supply=16/15 and 0 army, suggesting an early aggression/bio push killed workers before any defense was established, and the single-base standard macro leaves no economic buffer to recover.

## Applied Improvements
- Increase pylon build-ahead threshold from 12 to 16 supply left and raise max pending pylons from 4 to 6, preventing the supply blocks seen in Game 1 where supply_cap crashed to 23 mid-game
- Loosen the expansion defense requirement so the bot expands after 1 gateway and 4 army units (instead of requiring 2 gateways and 4 army), fixing the chronic single-base stagnation seen in Games 2 and 6 where 40 workers sat on 1 base for 10+ minutes
- Build a second gateway immediately after Cybernetics Core even during standard macro (target_gw minimum raised from 2 to 3 for non-cheese), so the bot has faster army production to defend early pressure like the Game 8 Terran bio that wiped workers at t=300s before any army existed