# Bot Analysis Report

**All-time win rate:** 47.0% (355W / 351L over 756 games)

**Recent 10-game win rate:** ↑ improving (recent 70.0% vs all-time 47.0%)

**By race (all-time):**
- Zerg: 94W / 111L  avg game 663s
- Protoss: 166W / 128L  avg game 652s
- Random: 43W / 38L  avg game 627s
- Terran: 52W / 74L  avg game 641s

**By strategy (all-time):**
- standard_macro: 137W / 199L
- dt_rush: 104W / 68L
- four_gate: 114W / 84L

**By strategy (recent 10 games):**
- four_gate: 2W / 2L
- standard_macro: 4W / 1L
- dt_rush: 1W / 0L

**Analysis:**
The bot is performing well recently at 70% win rate (up from 47% all-time), showing clear improvement from previous fixes. The 3 losses are: Game 1 (four_gate vs Zerg, Torches) where the army plateaus at 28-32 on 1 base for 600+ seconds then collapses catastrophically with workers dying from 42 to 0 between t=1140-1260 while army shrinks from 19 to 1, suggesting the bot camps on 1 base with a large army and gets overwhelmed by late-game Zerg; Game 2 (standard_macro vs Protoss, Pylon) where 40 workers and 60 army sit on 1 base from t=540-960 never expanding, then army drops from 30 to 0 at t=1020 and workers die at t=1080, a textbook permanent-stall-on-1-base loss; Game 10 (four_gate vs Terran, Torches) where the four_gate attack fires at t=300-420 reducing army from 11 to 5, then the bot never recovers — army bleeds to 1 by t=720 while workers grow to 38 on 1 base with no expansion and then everyone dies. The core remaining bugs are: (1) Game 2's 60-army stall on 1 base — the bot has 40 workers and 60 army for 400+ seconds and never expands because all expand conditions require army<6 or small worker counts, but with large army the timed_out_attack fires but sends units to die rather than expanding; (2) Game 1 and Game 10's post-cheese/post-battle collapse where the army gets ground down over hundreds of seconds on 1 base with no expansion happening.

## Applied Improvements
- Fix Game 2's permanent 1-base stall with large army (40 workers, 60 army, never expands): add an expand trigger when army>=20 and workers>=36 and on 1 base, since none of the existing expand conditions catch this state (oversaturated_expand requires army<6 via safety_expand, but oversaturated_expand itself only checks workers>=30 — however the cheese_active guard at the top of _expand blocks it if four_gate is still nominally active; the real issue is that with bases=1, workers=40, army=60, timed_out_attack fires repeatedly attacking but nobody expands)
- Wire large_army_expand into the actual expand trigger condition so it fires
- Fix Game 10 four_gate post-attack collapse: after four_gate attack reduces army from 11 to 5-7 at t=360-480, the bot never rebuilds army (army bleeds to 1 by t=720) because post_cheese_army_emergency only triggers when cheese_active is False, but four_gate cheese is still nominally active until t=480; extend the emergency army rebuild to also fire during four_gate when army<8 and time>300 to catch the partial-attack-failure case