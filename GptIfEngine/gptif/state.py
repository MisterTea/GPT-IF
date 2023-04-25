from __future__ import annotations

import random
from dataclasses import dataclass, field
from io import StringIO
from typing import Dict, List, Optional, Set, Tuple
from enum import IntEnum
import yaml
from md2py import md2py, TreeOfContents
import jinja2
from gptif.console import console
import gptif.console
from rich.markdown import Markdown
from rich.console import Console

from gptif.parser import get_hypernyms_set, get_verb_classes, get_verb_classes_for_list


class Gender(IntEnum):
    MALE = 1
    FEMALE = 2


@dataclass
class AgentProfile:
    name: Optional[str]
    aliases: List[str]
    age: Optional[int]
    gender: Optional[Gender]
    occupation: Optional[str]
    personality: Optional[List[str]]
    backstory: Optional[List[str]]
    appearance: Optional[List[str]]
    hobbies: Optional[List[str]]
    goals: Optional[List[str]]
    notes: Optional[List[str]]

    @classmethod
    def load_yaml(cls, profile_yaml):
        return AgentProfile(
            profile_yaml["name"],
            profile_yaml["aliases"],
            profile_yaml["age"],
            profile_yaml["gender"],
            profile_yaml["occupation"],
            profile_yaml["personality"],
            profile_yaml["backstory"],
            profile_yaml["physical_appearance"],
            profile_yaml["hobbies"],
            profile_yaml["goals"],
            profile_yaml["notes"],
        )

    @property
    def names(self) -> Set[str]:
        if self.name is not None:
            return set(self.aliases + [self.name])
        return set(self.aliases)

    def init_player_visible(self) -> AgentProfile:
        return AgentProfile(
            self.name,
            self.aliases,
            self.age,
            self.gender,
            None,
            None,
            None,
            self.appearance,
            None,
            None,
            None,
        )


@dataclass
class Agent:
    uid: str
    profile: AgentProfile
    percent_increase_per_tic: str
    tic_creatives: List[str]
    friend_questions: List[str]

    player_visible_profile: AgentProfile
    room_id: str
    tic_percentage: int = 0
    friend_points: int = 0

    @classmethod
    def load_yaml(cls, uid, agent_yaml):
        profile = AgentProfile.load_yaml(agent_yaml["Profile"])
        percent_increase_per_tic = agent_yaml["Tics"]["percent_increase_per_tick"]
        tic_creatives = [str(x) for x in agent_yaml["Tics"]["creative"]]

        return cls(
            uid,
            profile,
            percent_increase_per_tic,
            tic_creatives,
            agent_yaml["friend_questions"] if "friend_questions" in agent_yaml else [],
            profile.init_player_visible(),
            agent_yaml["StartingRoom"],
        )


@dataclass
class Scenery:
    uid: str
    room_scope: Optional[Set[str]]
    names: Set[str]
    actions: Dict[str, List[str]]

    @property
    def nouns(self):
        return [x.strip() for x in id.split("/")]


@dataclass
class Exit:
    room_uid: str
    prescript: Optional[str]
    postscript: Optional[str]


@dataclass
class Room:
    uid: str
    title: str
    descriptions: Dict[str, List[str]]
    scenery: List[Scenery] = field(default_factory=lambda: [])
    exits: Dict[str, Exit] = field(default_factory=dict)


@dataclass
class World:
    rooms: Dict[str, Room] = field(default_factory=lambda: {})
    agents: Dict[str, Agent] = field(default_factory=lambda: {})

    waiting_for_player: bool = True
    active_agents: Set[str] = field(default_factory=set)
    current_room_id: str = ""
    time_in_room: int = 0

    def __post_init__(self):
        # Load room descriptions
        room_descriptions: Dict[str, Dict[str, List[str]]] = {}

        current_room = ""
        current_topic = ""
        with open("data/rooms/room_descriptions.md", "r") as fp:
            sections = fp.read().split("\n\n")
            for section in sections:
                if section[:2] == "##":
                    current_topic = section[2:].strip()
                    room_descriptions[current_room][current_topic] = []
                elif section[:1] == "#":
                    current_room = section[1:].strip()
                    room_descriptions[current_room] = {}
                else:
                    assert current_room != ""
                    assert current_topic != ""
                    room_descriptions[current_room][current_topic].append(section)

        # Load rooms
        with open("data/rooms/rooms.yaml", "r") as rooms_file:
            rooms_yaml = yaml.safe_load(rooms_file)
            for room_uid, room_yaml in rooms_yaml.items():
                assert room_uid not in self.rooms, f"Duplicate room_uid, {room_uid}"
                room_title = room_yaml["title"]
                exits = {}
                if "exits" in room_yaml:
                    for exit_direction, exit in room_yaml["exits"].items():
                        exits[exit_direction] = Exit(
                            exit["room"],
                            exit.get("prescript", None),
                            exit.get("postscript", None),
                        )
                self.rooms[room_uid] = Room(
                    room_uid, room_title, room_descriptions[room_uid], [], exits
                )

        # Load scenery descriptions
        scenery_actions: Dict[str, Dict[str, List[str]]] = {}

        current_scenery = ""
        current_action = ""
        with open("data/rooms/scenery_actions.md", "r") as fp:
            sections = fp.read().split("\n\n")
            for section in sections:
                if section[:2] == "##":
                    current_action = section[2:].strip()
                    scenery_actions[current_scenery][current_action] = []
                elif section[:1] == "#":
                    current_scenery = section[1:].strip()
                    scenery_actions[current_scenery] = {}
                else:
                    assert current_scenery != ""
                    assert current_action != ""
                    scenery_actions[current_scenery][current_action].append(section)

        # Load scenery
        with open("data/rooms/scenery.yaml", "r") as fp:
            all_scenery_yaml = yaml.safe_load(fp)
            for scenery_uid, scenery_yaml in all_scenery_yaml.items():
                scenery = Scenery(
                    scenery_uid,
                    set(scenery_yaml["rooms"]),
                    set(scenery_yaml["names"]),
                    scenery_actions[scenery_uid],
                )
                # Attach scenery to all rooms listed
                for room_id in scenery_yaml["rooms"]:
                    self.rooms[room_id].scenery.append(scenery)

        # Load agents
        with open("data/agents/chapter_1.yaml", "r") as agent_file:
            all_agent_yaml = yaml.safe_load(agent_file)
            for agent_uid, agent_yaml in all_agent_yaml.items():
                self.agents[agent_uid] = Agent.load_yaml(agent_uid, agent_yaml)

        pass

    def ask_to_press_key(self):
        if len(gptif.console.DEBUG_INPUT) > 0:
            console.print("[blue]Press enter to continue...[/]")
        else:
            console.input("[blue]Press enter to continue...[/]")
        console.print("\n")

    @property
    def current_room(self):
        return self.rooms[self.current_room_id]

    def step(self):
        self.time_in_room += 1
        for agent in self.agents.values():
            if agent.room_id == self.current_room_id:
                # Pick a random tic
                self.play_sections([random.choice(agent.tic_creatives)], "purple")
        if f"Tic {self.time_in_room}" in self.current_room.descriptions:
            self.play_sections(
                self.current_room.descriptions[f"Tic {self.time_in_room}"], "purple"
            )
        pass

    def move_to(self, room_id):
        assert room_id in self.rooms
        self.current_room_id = room_id
        self.time_in_room = 0
        self.look()

    def go(self, direction):
        direction = direction.lower()
        if direction not in self.current_room.exits:
            console.warning("You can't go that way.")
            return False
        exit = self.current_room.exits[direction]
        if exit.prescript is not None:
            result = jinja2.Environment().from_string(exit.prescript).render(world=self)
            if "False" in result:
                return False
            assert "True" in result
        self.move_to(exit.room_uid)
        if exit.postscript is not None:
            jinja2.Environment().from_string(exit.postscript).render(world=self)

    def look(self):
        console.print(self.current_room.title, style="yellow bold")
        self.play_sections(self.current_room.descriptions["Full"], style="yellow")
        self.print_exits()

    def print_exits(self):
        exit_text = [
            f"* {direction}: **{self.rooms[exit.room_uid].title}**"
            for direction, exit in self.current_room.exits.items()
        ]
        if len(exit_text) == 0:
            return
        console.print(Markdown("""**Exits:**\n""" + "\n".join(exit_text)))
        console.print()

    def act_on(self, verb: str, look_object: str) -> bool:
        hypernyms_set = get_hypernyms_set(look_object)
        # Loop through all scenery in the room, looking for a match
        for scenery in self.current_room.scenery:
            if (
                look_object.lower() in scenery.names
                or len(scenery.names.intersection(hypernyms_set)) > 0
            ):
                # Got a match
                if (
                    verb.lower() in scenery.actions
                    or len(
                        get_verb_classes(verb.lower()).intersection(
                            get_verb_classes_for_list(scenery.actions.keys())
                        )
                    )
                    > 0
                ):
                    self.play_sections(scenery.actions[verb.lower()], "yellow")
                    return True
        return False

    def play_sections(self, sections: List[str], style: Optional[str] = None):
        buffer = ""
        for section in sections:
            if section[:2] == "{{":
                # Special command, dump the buffer first
                if len(buffer) > 0:
                    console.print(Markdown(buffer))
                    console.print("\n")
                    buffer = ""
            paragraph = jinja2.Environment().from_string(section).render(world=self)
            if section[:2] != "{{":
                if len(buffer) > 0:
                    buffer += "\n\n"
                buffer += paragraph
        if len(buffer) > 0:
            console.print(Markdown(buffer), style=style)
            console.print("\n")
            buffer = ""

    def start_chapter_one(self):
        self.active_agents = set(["taxi_driver", "port_security_officer"])
        self.current_room_id = "driving_to_terminal"
        self.time_in_room = 0

        with open("data/start_ch1.md", "r") as fp:
            sections = fp.read().split("\n\n")
            self.play_sections(sections, "yellow")

    def start_ch2(self):
        self.active_agents = set(["tour_guide"])

        with open("data/start_ch2.md", "r") as fp:
            sections = fp.read().split("\n\n")
            self.play_sections(sections, "yellow")

    def check_can_board_ship(self):
        if self.agents["port_security_officer"].friend_points >= 2:
            console.print(
                Markdown(
                    """The security officer waves you along with a smile.

```
Congratulations!  You solved your first puzzle.  More adventure awaits!
```"""
                )
            )
            return True
        console.print(
            'The security officer blocks your path.  "Excuse me sir, there\'s other things I need to do right now."\n'
        )
        console.print(
            Markdown(
                """```
This is your first empathy puzzle!  Ask the officer questions and learn what they want to talk about, then ask questions about what they like to talk about until they become your friend.
```"""
            )
        )
        return False
