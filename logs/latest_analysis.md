# Bot Analysis Report

**All-time win rate:** 49.5% (107W / 92L over 216 games)

**Recent 10-game win rate:** ↓ declining (recent 20.0% vs all-time 49.5%)

**By race (all-time):**
- Zerg: 39W / 33L  avg game 685s
- Protoss: 38W / 30L  avg game 743s
- Random: 14W / 10L  avg game 557s
- Terran: 16W / 19L  avg game 703s

**By strategy (all-time):**
- standard_macro: 34W / 65L
- dt_rush: 39W / 16L
- four_gate: 34W / 11L

**By strategy (recent 10 games):**
- standard_macro: 1W / 6L
- dt_rush: 1W / 1L

**Analysis:**
The bot is severely declining — 20% win rate vs 49.5% all-time, with 7 losses in the last 10 games. The dominant failure pattern across Games 1, 2, 3, 6, 7, and 8 is catastrophic early worker loss (workers dropping to 0-14 at t=300-480s) while the bot has only 1-8 army units, indicating the bot is getting all-in rushed and has zero effective defense. The recently added base defense logic (pulling workers to fight) is clearly not working — in Game 8, workers go from 31 to 14 at t=300s and 0 at t=360s with army at 2, suggesting the defense threshold/response is too slow or not triggering. Game 9 shows a separate critical bug: the army accumulates 58 units on 1 base but never attacks (supply caps at 158/183 for 20+ minutes, 0 minerals for extended periods), indicating the attack threshold or idle logic is completely broken for large armies, wasting the game into a tie.

## Applied Improvements
- Fix the catastrophic early worker wipe by adding aggressive worker defense: when enemy units are within 20 tiles of start location and workers outnumber the defending army by more than 3x, pull ALL nearby workers to fight rather than just 4, since the current limit of 4 worker defenders is clearly insufficient to stop early all-ins
- Fix the Game 9 army stall bug where 58 units sit idle for 20+ minutes: the attack logic only moves idle units but if units are already on a move order toward rally they are not idle, causing them to perpetually hold at rally — change army.idle to the full army when army is large enough to attack, and lower the post-600s standard macro threshold from 4 to 2 so large armies actually commit
- Lower the standard macro attack threshold from 6 to 4 pre-600s and from 4 to 3 post-600s, and remove the separate post-600s branch since the bot is losing workers before it can ever accumulate 6 units — smaller army attacks keep pressure on opponents who are rushing and prevent the bot from being passive while being dismantled