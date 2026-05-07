import asyncio
import sys

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from bot.bot import CompetitiveBot


def _arg(flag: str, default: str = "") -> str:
    argv = sys.argv
    return argv[argv.index(flag) + 1] if flag in argv else default


def main():
    bot = Bot(Race.Protoss, CompetitiveBot())

    if "--LadderServer" in sys.argv:
        # BurnySc2 5.x: connect_to_port joins an already-running SC2 process
        # run_ladder_game was removed in newer versions of the library
        asyncio.run(
            run_game(
                None,
                [bot],
                host=_arg("--LadderServer", "127.0.0.1"),
                connect_to_port=int(_arg("--GamePort", "5000")),
            )
        )
    else:
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
