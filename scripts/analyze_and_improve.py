#!/usr/bin/env python3
"""Analyze accumulated game logs and apply AI-generated improvements to the bot.

Workflow:
  1. Load all game_*.jsonl files from logs/
  2. Compute win/loss stats broken down by race and strategy
  3. Send stats + recent game timelines + full bot source to Claude
  4. Claude returns up to 3 surgical old_code → new_code patches
  5. Each patch is applied only if old_code appears verbatim and the result
     passes a Python syntax check
  6. Writes logs/latest_analysis.md with findings

Requires env var:
  ANTHROPIC_API_KEY

Exits 0 with no changes when win rate ≥ 60% or no games are logged yet.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from textwrap import indent

import anthropic

LOGS_DIR = Path(__file__).parent.parent / "logs"
BOT_FILE = Path(__file__).parent.parent / "bot" / "bot.py"
MODEL = "claude-sonnet-4-6"
WIN_RATE_THRESHOLD = 60.0  # skip improvement run if already winning this % of games
MIN_GAMES = 5              # need at least this many completed games before analysing


# ── data loading ──────────────────────────────────────────────────────────────

def load_games() -> list[dict]:
    games: list[dict] = []
    for path in sorted(LOGS_DIR.glob("game_*.jsonl")):
        events = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        if not events:
            continue

        game: dict = {"file": path.name, "events": events}
        for e in events:
            if e["event"] == "game_start":
                for k in ("opponent_race", "map_name", "strategy", "opponent_id"):
                    if k in e:
                        game[k] = e[k]
            elif e["event"] == "game_end":
                game["result"] = e.get("result", "Unknown")
                game["duration_s"] = e.get("game_time", 0)
                game["final_workers"] = e.get("final_workers", 0)
                game["final_bases"] = e.get("final_bases", 0)
                game["final_supply"] = e.get("final_supply", 0)

        # Only include games that actually finished
        if "result" in game:
            games.append(game)

    return games


# ── stats ─────────────────────────────────────────────────────────────────────

def compute_stats(games: list[dict]) -> dict:
    total = len(games)
    wins = sum(1 for g in games if g.get("result") == "Victory")
    losses = sum(1 for g in games if g.get("result") == "Defeat")

    by_race: dict = defaultdict(lambda: {"wins": 0, "losses": 0, "avg_duration": []})
    by_strategy: dict = defaultdict(lambda: {"wins": 0, "losses": 0})

    for g in games:
        race = g.get("opponent_race", "Unknown")
        strat = g.get("strategy", "Unknown")
        result = g.get("result", "Unknown")
        duration = g.get("duration_s", 0)

        if result == "Victory":
            by_race[race]["wins"] += 1
            by_strategy[strat]["wins"] += 1
        elif result == "Defeat":
            by_race[race]["losses"] += 1
            by_strategy[strat]["losses"] += 1

        by_race[race]["avg_duration"].append(duration)

    # Compute average game durations
    for race_data in by_race.values():
        durations = race_data.pop("avg_duration")
        race_data["avg_duration_s"] = round(sum(durations) / len(durations)) if durations else 0

    return {
        "total_games": total,
        "wins": wins,
        "losses": losses,
        "win_rate_pct": round(wins / total * 100, 1) if total else 0,
        "by_race": {k: dict(v) for k, v in by_race.items()},
        "by_strategy": {k: dict(v) for k, v in by_strategy.items()},
    }


def build_timeline(game: dict) -> str:
    lines = [f"  map={game.get('map_name','?')} vs {game.get('opponent_race','?')} "
             f"strategy={game.get('strategy','?')} result={game.get('result','?')}"]
    for e in game["events"]:
        if e["event"] == "periodic":
            lines.append(
                f"  t={e['game_time']:.0f}s  workers={e.get('workers',0)}  "
                f"bases={e.get('bases',0)}  supply={e.get('supply_used',0)}/{e.get('supply_cap',0)}  "
                f"army={e.get('army_count',0)}  minerals={e.get('minerals',0)}"
            )
    return "\n".join(lines)


# ── Claude interaction ────────────────────────────────────────────────────────

def build_prompt(stats: dict, recent_games: list[dict], bot_code: str) -> str:
    timelines = "\n\n".join(
        f"Game {i+1}:\n{build_timeline(g)}"
        for i, g in enumerate(recent_games[-8:])
    )
    return f"""You are an expert StarCraft 2 AI bot developer analysing a Protoss ladder bot (burnysc2 framework).

## Win/Loss Statistics
{json.dumps(stats, indent=2)}

## Recent Game Timelines (economy + army snapshots every 60 s)
{timelines}

## Current Bot Source (bot/bot.py)
```python
{bot_code}
```

Analyse the loss patterns from the timelines and statistics, then suggest up to 3 targeted code improvements.

Respond with ONLY a valid JSON object — no markdown fences, no prose outside the JSON:
{{
  "analysis": "2-4 sentence summary of the main loss patterns observed",
  "improvements": [
    {{
      "description": "one-line description of what this change does and why",
      "old_code": "exact verbatim substring of the current bot code to replace",
      "new_code": "replacement string (same indentation)"
    }}
  ]
}}

Hard rules:
- old_code MUST be a verbatim substring of the bot source shown above
- Do not duplicate an old_code across multiple improvements
- Limit to 3 improvements
- Only fix things directly evidenced by the loss data (short game duration → early pressure; low worker counts → production issues; etc.)
- Preserve all existing indentation and style"""


def call_claude(prompt: str) -> dict:
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip()
    # Strip accidental markdown code fences if the model adds them
    if text.startswith("```"):
        text = "\n".join(
            line for line in text.splitlines()
            if not line.startswith("```")
        ).strip()
    return json.loads(text)


# ── patch application ─────────────────────────────────────────────────────────

def syntax_ok(code: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-c", f"import ast; ast.parse({repr(code)})"],
        capture_output=True,
    )
    return result.returncode == 0


def apply_improvements(improvements: list[dict], bot_code: str) -> tuple[str, list[str]]:
    applied: list[str] = []
    for imp in improvements:
        old = imp.get("old_code", "")
        new = imp.get("new_code", "")
        desc = imp.get("description", "")
        if not old or old not in bot_code:
            print(f"  SKIP (old_code not found): {desc}")
            continue
        candidate = bot_code.replace(old, new, 1)
        if not syntax_ok(candidate):
            print(f"  SKIP (syntax error): {desc}")
            continue
        bot_code = candidate
        applied.append(desc)
        print(f"  APPLIED: {desc}")
    return bot_code, applied


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    games = load_games()
    if len(games) < MIN_GAMES:
        print(f"Only {len(games)} completed game(s) logged — need {MIN_GAMES} before analysing. Skipping.")
        sys.exit(0)

    stats = compute_stats(games)
    wr = stats["win_rate_pct"]
    print(f"Stats: {stats['wins']}W / {stats['losses']}L  ({wr}% win rate over {stats['total_games']} games)")

    if wr >= WIN_RATE_THRESHOLD:
        print(f"Win rate ≥ {WIN_RATE_THRESHOLD}% — no improvement needed this run.")
        sys.exit(0)

    bot_code = BOT_FILE.read_text(encoding="utf-8")
    prompt = build_prompt(stats, games, bot_code)

    print("Calling Claude for analysis…")
    try:
        payload = call_claude(prompt)
    except (json.JSONDecodeError, Exception) as exc:
        print(f"Claude call failed: {exc}")
        sys.exit(1)

    analysis = payload.get("analysis", "")
    improvements = payload.get("improvements", [])
    print(f"\nAnalysis: {analysis}")
    print(f"Improvements suggested: {len(improvements)}\n")

    if not improvements:
        print("No improvements suggested.")
    else:
        new_code, applied = apply_improvements(improvements, bot_code)
        if applied:
            BOT_FILE.write_text(new_code, encoding="utf-8")
            print(f"\n{len(applied)} improvement(s) written to {BOT_FILE}")
        else:
            print("No improvements could be safely applied.")
            applied = []

    # Always write the analysis report so it gets committed
    LOGS_DIR.mkdir(exist_ok=True)
    report = (
        f"# Bot Analysis Report\n\n"
        f"**Win rate:** {wr}% ({stats['wins']}W / {stats['losses']}L over {stats['total_games']} games)\n\n"
        f"**By race:**\n"
        + "\n".join(
            f"- {race}: {d['wins']}W / {d['losses']}L  avg game {d['avg_duration_s']}s"
            for race, d in stats["by_race"].items()
        )
        + f"\n\n**By strategy:**\n"
        + "\n".join(
            f"- {strat}: {d['wins']}W / {d['losses']}L"
            for strat, d in stats["by_strategy"].items()
        )
        + f"\n\n**Analysis:**\n{analysis}\n\n"
        + (
            "## Applied Improvements\n" + "\n".join(f"- {d}" for d in applied)
            if "applied" in dir() and applied
            else "## No improvements applied this run"
        )
    )
    (LOGS_DIR / "latest_analysis.md").write_text(report, encoding="utf-8")
    print(f"\nReport written to logs/latest_analysis.md")


if __name__ == "__main__":
    main()
