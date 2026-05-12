import argparse
import asyncio
import sys

import aiohttp
from sc2 import maps
from sc2.client import Client
from sc2.data import Difficulty, Race
from sc2.main import _play_game, run_game
from sc2.player import Bot, Computer
from sc2.portconfig import Portconfig
from sc2.protocol import ConnectionAlreadyClosedError

from bot.bot import CompetitiveBot


def run_ladder_game(bot: Bot):
    parser = argparse.ArgumentParser()
    parser.add_argument("--GamePort", type=int, nargs="?")
    parser.add_argument("--StartPort", type=int, nargs="?")
    parser.add_argument("--LadderServer", type=str, nargs="?")
    parser.add_argument("--OpponentId", type=str, nargs="?")
    parser.add_argument("--RealTime", action="store_true")
    args, _ = parser.parse_known_args()

    host = args.LadderServer or "127.0.0.1"
    lan_port = args.StartPort
    bot.ai.opponent_id = args.OpponentId

    if lan_port is None:
        portconfig = None
    else:
        ports = [lan_port + p for p in range(1, 6)]
        portconfig = Portconfig()
        portconfig.server = [ports[1], ports[2]]
        portconfig.players = [[ports[3], ports[4]]]

    result = asyncio.run(
        _join_ladder_game(host, args.GamePort, bot, args.RealTime, portconfig)
    )
    return result, args.OpponentId


async def _join_ladder_game(host, port, bot: Bot, realtime: bool, portconfig):
    ws_url = f"ws://{host}:{port}/sc2api"
    async with aiohttp.ClientSession() as session:
        ws = await session.ws_connect(ws_url, timeout=aiohttp.ClientWSTimeout(ws_close=120))
        client = Client(ws)
        try:
            result = await _play_game(bot, client, realtime, portconfig)
        except ConnectionAlreadyClosedError:
            result = None
        finally:
            await ws.close()
    return result


def main():
    bot = Bot(Race.Protoss, CompetitiveBot())

    if "--LadderServer" in sys.argv:
        result, opponent_id = run_ladder_game(bot)
        print(result, "against opponent", opponent_id)
    else:
        run_game(
            maps.get("AcropolisAIE"),
            [bot, Computer(Race.Zerg, Difficulty.VeryHard)],
            realtime=False,
            save_replay_as="replay.SC2Replay",
        )


if __name__ == "__main__":
    main()
