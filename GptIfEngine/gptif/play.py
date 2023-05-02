import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import random

import click
from rich.markdown import Markdown

import gptif.settings
from gptif.console import console
from gptif.converse import check_if_more_friendly, converse
from gptif.db import create_db_and_tables
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

    if not debug:
        gptif.settings.DEBUG_INPUT.clear()
        gptif.settings.DEBUG_MODE = False

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

                    world_copy = copy.deepcopy(world)
                    serialized_world = world.save()

                    world = World()
                    assert world.load(serialized_world)

                    assert world.save() == world_copy.save()
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
