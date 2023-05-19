from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import os
from typing import Optional
import random

import click
from rich.markdown import Markdown

import gptif.settings
from gptif.console import console
from gptif.converse import check_if_more_friendly, converse
from gptif.db import GameState, create_db_and_tables
from gptif.handle_input import handle_input
from gptif.parser import (
    ParseException,
    get_direct_object,
    get_verb_classes,
    handle_user_input,
)
from gptif.world import World


class DummyContext(object):
    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass


@click.command()
@click.option("--debug", default=False, is_flag=True)
@click.option("--no-converse-server", default=False, is_flag=True)
@click.option(
    "--converse-server-url",
    default="https://i00ny5xb4e.execute-api.us-east-1.amazonaws.com",
)
@click.option("--sql-url", default=None)
def play(
    debug: bool,
    no_converse_server: bool,
    converse_server_url: str,
    sql_url: Optional[str],
):
    if sql_url is not None:
        os.environ["SQL_URL"] = sql_url

    gptif.settings.CLI_MODE = True

    if debug:
        gptif.settings.DEBUG_MODE = True

    if no_converse_server == False:
        gptif.settings.RUN_LOCALLY = False
        gptif.settings.CONVERSE_SERVER = converse_server_url

    create_db_and_tables()

    world = World()

    with DummyContext():
        world.start_chapter_one()

        while True:
            while world.waiting_for_player is True:
                if gptif.settings.DEBUG_MODE:
                    import copy

                    game_state = GameState(session_id="")  # type: ignore
                    world.save(game_state)

                    world = World()
                    assert world.load(game_state)
                    new_game_state = GameState(session_id="")  # type: ignore
                    world.save(new_game_state)

                    if game_state != new_game_state:
                        print(game_state)
                        print(new_game_state)
                        assert False
                try:
                    command = console.get_input(">").strip()
                except KeyboardInterrupt as ki:
                    console.print()
                    console.print("[blue]Thanks for playing![/]")
                    return

                if handle_input(world, command) == False:
                    return
            while world.waiting_for_player is False:
                world.step()


if __name__ == "__main__":
    play()
