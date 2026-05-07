import asyncio
import sys

from sc2 import maps
from sc2.data import Difficulty, Race  # noqa: F401
from sc2.main import run_game, run_ladder_game
from sc2.player import Bot, Computer

from bot.bot import CompetitiveBot


def main():
    bot = Bot(Race.Protoss, CompetitiveBot())

    if "--LadderServer" in sys.argv:
        # AI Arena / ladder mode — args parsed by run_ladder_game
        run_ladder_game(bot)
    else:
        # Local testing
        asyncio.run(
            run_game(
                maps.get("GoldenWallLE"),
                [bot, Computer(Race.Random, Difficulty.Hard)],
                realtime=False,
                save_replay_as="replay.SC2Replay",
            )
        )


if __name__ == "__main__":
    main()
