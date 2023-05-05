import os
import re
from typing import Optional

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import random

import click
from rich.markdown import Markdown

from gptif.console import console
from gptif.converse import check_if_more_friendly, converse
from gptif.db import create_db_and_tables
from gptif.parser import (
    ParseException,
    get_direct_object,
    get_verb_classes,
    handle_user_input,
)
from gptif.world import World

DIRECTION_VERBS = (
    "NORTH",
    "SOUTH",
    "EAST",
    "WEST",
    "UP",
    "DOWN",
    "N",
    "S",
    "E",
    "W",
    "U",
    "D",
)

DIRECTION_SHORT_LONG_MAP = {
    "N": "NORTH",
    "S": "SOUTH",
    "W": "WEST",
    "E": "EAST",
    "U": "UP",
    "D": "DOWN",
}


def handle_input(world: World, command: str) -> bool:
    # Convert unicode quotes
    command = re.sub("[\u201c\u201d]", '"', command)

    # Remove redundant whitespace
    command = " ".join(command.split())

    if len(command) == 0:
        return True

    if command[0] == '"':
        # Shortcut for chatting when only one person around
        agents_in_room = world.agents_in_room
        if len(agents_in_room) == 0:
            console.warning("There is no one to talk to here")
            return True
        if len(agents_in_room) > 1:
            console.warning(
                f'Who did you want to talk to?  For example, to talk to {agents_in_room[0].name}, type TELL {agents_in_room[0].name} "Hi!"'
            )
            return True
        command = f"TELL {agents_in_room[0].name} {command}"

    verb = command.split(" ")[0].upper()

    if verb == "GOAL":
        world.print_goal()
        return True

    command_minus_verb = " ".join(command.split(" ")[1:])
    verb_classes = get_verb_classes(verb)
    if verb == "EXIT" or verb == "QUIT" or verb == "Q":
        if len(command_minus_verb) > 0:
            console.warning('Type "EXIT" with no arguments to leave the game')
            return True
        else:
            console.print()
            console.print("[blue]Thanks for playing![/]")
            return False

    if verb not in DIRECTION_VERBS and verb != "L" and len(verb_classes) == 0:
        console.warning(
            f"Sorry, I don't understand the verb {verb}. Remember that each sentence must begin with an action verb."
        )
        return True
    if verb in DIRECTION_VERBS or "51" in verb_classes:  # Go
        if verb in DIRECTION_VERBS:
            direction = verb
        else:
            direction = command_minus_verb.upper().strip()
            if direction not in DIRECTION_VERBS:
                if len(direction) == 0:
                    console.warning(f"{verb} requires a direction (e.g. {verb} EAST).")
                else:
                    console.warning(f"Invalid direction: {direction}")
                return True
        if direction in DIRECTION_SHORT_LONG_MAP.keys():
            direction = DIRECTION_SHORT_LONG_MAP[direction]
        world.go(direction)
    elif "L" == verb or "30" in verb_classes:  # Look
        if len(command_minus_verb) == 0:
            world.look()
            world.step()
        else:
            try:
                direct_object = get_direct_object(command)
                if world.act_on("look", direct_object):
                    world.step()
                else:
                    console.warning(f"Could not find a {direct_object} to look at")
            except ParseException as pe:
                console.warning(pe)
    elif verb == "WAIT":  # Wait
        console.print("Time passes...\n", style="yellow")
        world.step()
    elif "37" in verb_classes:  # Tell/Ask
        # Handle speaking
        num_quotes = command_minus_verb.count('"')
        if num_quotes != 2:
            console.warning(
                f'When speaking, you must wrap your text in double-quotes.  For example: TELL JUAN "Hello!"'
            )
            return True
        target_name = command_minus_verb[: command_minus_verb.find('"')].strip()
        statement = command_minus_verb[command_minus_verb.find('"') - 1 :]

        target_agent = None
        missing_target_agent = None
        for agent_id, agent in world.agents.items():
            if target_name.lower() in [x.lower() for x in agent.names]:
                if (
                    agent_id in world.active_agents
                    and agent.room_id == world.current_room_id
                ):
                    target_agent = agent
                missing_target_agent = agent

        if target_agent is None:
            if missing_target_agent is not None:
                console.print(f"{missing_target_agent.profile.name} is not nearby.")
            else:
                console.warning(f"Sorry, I don't know who {target_name} is.")
        else:
            answer = converse(target_agent, statement)
            if answer is not None:
                console.debug("(RAW ANSWER)", answer)
                console.print(Markdown("> " + answer.strip('"')))
                console.print("\n")

                if (
                    len(target_agent.friend_questions) > 0
                    and target_agent.friend_points < 2
                ):
                    is_more_friendly = check_if_more_friendly(
                        target_agent,
                        statement,
                    )

                    if is_more_friendly:
                        target_agent.friend_points += 1
                        if target_agent.friend_points >= 2:
                            console.print(
                                f"[light_green]{target_agent.profile.name} is now your friend!\n[/]"
                            )

                            if target_agent.uid == "port_security_officer":
                                console.print(
                                    Markdown(
                                        """```You made your first friend! When a character becomes your friend, you can PERSUADE them to do something that they wouldn't do for a stranger.  Go ahead and try it: type PERSUADE DERRICK.```"""
                                    )
                                )
                        else:
                            console.print(
                                f"[green]{target_agent.profile.name} is more friendly towards you.\n[/]"
                            )

                            if (
                                target_agent.friend_points == 1
                                and target_agent.uid == "port_security_officer"
                            ):
                                console.print(
                                    Markdown(
                                        """```Good job!  You found out what Derrick likes to talk about and you mentioned it in your conversation.  This earned you a friend point with Derrick.  Friend points persist across playthroughs: once you make a friend, you have a friend for life.  Keep earning friend points to make Derrick a friend```"""
                                    )
                                )

                world.step()
    elif "58" in verb_classes:  # PERSUADE
        target_name = command_minus_verb

        target_agent = None
        missing_target_agent = None
        for agent_id, agent in world.agents.items():
            if target_name.lower() in [x.lower() for x in agent.names]:
                if (
                    agent_id in world.active_agents
                    and agent.room_id == world.current_room_id
                ):
                    target_agent = agent
                missing_target_agent = agent

        if target_agent is None:
            if missing_target_agent is not None:
                console.print(f"{missing_target_agent.profile.name} is not nearby.")
            else:
                console.warning(f"Sorry, I don't know who {target_name} is.")
        else:
            world.persuade(target_agent)
    elif verb.lower() == "help":
        console.print("TODO: HELP")
    else:
        try:
            direct_object = get_direct_object(command)
            if world.act_on(verb, direct_object):
                world.step()
            else:
                console.warning(f"Could not find a {direct_object} to {verb}")
        except ParseException as pe:
            console.warning(pe)
    return True
