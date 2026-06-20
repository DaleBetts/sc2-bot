# Bot Analysis Report

**All-time win rate:** 49.2% (444W / 401L over 903 games)

**Recent 10-game win rate:** ↑ improving (recent 60.0% vs all-time 49.2%)

**By race (all-time):**
- Zerg: 108W / 130L  avg game 699s
- Protoss: 215W / 149L  avg game 647s
- Random: 49W / 42L  avg game 621s
- Terran: 72W / 80L  avg game 638s

**By strategy (all-time):**
- standard_macro: 174W / 232L
- dt_rush: 138W / 78L
- four_gate: 132W / 91L

**By strategy (recent 10 games):**
- standard_macro: 4W / 2L
- four_gate: 1W / 1L
- dt_rush: 1W / 0L

**Analysis:**
Recent win rate is 60% vs 49.2% all-time, showing clear improvement. However, the 3 losses reveal distinct patterns: Game 3 (Tie vs Terran) and Game 6 (Loss vs Zerg) both show the bot stalling on 1 base with 40 workers and a small army (army drops from 17 to 0-1 over ~400s) and then entering a zombie state where workers=42, army=0, minerals=20 persist for 600+ seconds without surrendering — Game 6 has bases=1 with army=0 from t=900 to t=1560 without triggering the hopeless_no_base surrender (which requires bases==0). Game 10 (Loss vs Zerg) shows the army oscillating at 5-8 units and never reaching the attack threshold, while workers drop from 32 to 0 at t=600-660 suggesting a catastrophic enemy attack that the bot failed to defend despite having 40 workers and 5 army at t=540.

## Applied Improvements
- Fix Game 3 and Game 6 zombie states: bot has 40+ workers, 0 army, 1 base, and tiny minerals for 600+ seconds without surrendering because hopeless_no_base only checks bases==0; add a surrender trigger for bases==1 with army==0 and workers stuck and minerals floored for extended time
- Fix Game 10 worker wipe at t=600: army drops from 8 to 0 and workers drop from 40 to 32 to 0 in 120s with no response; the current worker defense only pulls workers when enemy is within 20 tiles but by t=600 the Zerg army has overwhelmed the base — increase enemy detection radius to 30 tiles when army==0 and time>480 to catch large Zerg attacks earlier
- Fix Game 6 permanent 1-base stall: army oscillates between 0-17 on 1 base from t=300 to t=900 then collapses — when army reaches 0 with workers>=30 on 1 base after t=600 in standard_macro, force a full worker pull to defend rather than the capped 6-worker pull, because the base is already being overrun