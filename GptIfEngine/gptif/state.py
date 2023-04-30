from __future__ import annotations

import re
import random
from dataclasses import dataclass, field
from io import StringIO
from typing import Dict, List, Optional, Set, Tuple
from enum import IntEnum
import yaml
from md2py import md2py, TreeOfContents
import jinja2
from gptif.cl_image import display_image_for_prompt
from gptif.console import console
import gptif.console
from rich.markdown import Markdown
from rich.console import Console

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from gptif.parser import get_hypernyms_set, get_verb_classes, get_verb_classes_for_list


class Gender(IntEnum):
    MALE = 1
    FEMALE = 2


@dataclass
class AgentProfile:
    name: str
    age: Optional[int]
    gender: Optional[Gender]
    occupation: Optional[str]
    personality: Optional[List[str]]
    backstory: Optional[List[str]]
    appearance: Optional[List[str]]
    hobbies: Optional[List[str]]
    goals: Optional[List[str]]

    @classmethod
    def load_yaml(cls, profile_yaml):
        return AgentProfile(
            profile_yaml["name"],
            profile_yaml["age"],
            profile_yaml["gender"],
            profile_yaml["occupation"],
            profile_yaml["personality"],
            profile_yaml["backstory"],
            profile_yaml["physical appearance"],
            profile_yaml["hobbies"],
            profile_yaml["goals"],
        )

    def init_player_visible(self) -> AgentProfile:
        return AgentProfile(
            self.name,
            self.age,
            self.gender,
            None,
            None,
            None,
            self.appearance,
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
    notes: List[str]
    aliases: List[str]
    movement: Movement

    player_visible_profile: AgentProfile
    room_id: Optional[str]
    tic_percentage: int = 0
    friend_points: int = 0

    @classmethod
    def load_yaml(cls, uid, agent_yaml):
        profile = AgentProfile.load_yaml(agent_yaml["Profile"])
        if "Tics" in agent_yaml:
            percent_increase_per_tic = agent_yaml["Tics"]["percent_increase_per_tick"]
            tic_creatives = [str(x) for x in agent_yaml["Tics"]["creative"]]
        else:
            percent_increase_per_tic = "0d1"
            tic_creatives = []
        movement = Movement.from_yaml(agent_yaml["movement"])

        return cls(
            uid,
            profile,
            percent_increase_per_tic,
            tic_creatives,
            agent_yaml["friend_questions"] if "friend_questions" in agent_yaml else [],
            agent_yaml.get("notes", []),
            agent_yaml.get("aliases", []),
            movement,
            profile.init_player_visible(),
            movement.starting_room,
        )

    @property
    def names(self) -> Set[str]:
        if self.profile.name is not None:
            return set(
                self.aliases + [self.profile.name, self.profile.name.split(" ")[0]]
            )
        return set(self.aliases)

    @property
    def name(self) -> str:
        return self.profile.name


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


world: World = None  # type: ignore


@dataclass
class World:
    rooms: Dict[str, Room] = field(default_factory=lambda: {})
    agents: Dict[str, Agent] = field(default_factory=lambda: {})

    waiting_for_player: bool = True
    active_agents: Set[str] = field(default_factory=set)
    current_room_id: str = ""
    time_in_room: int = 0
    visited_rooms: Set[str] = field(default_factory=set)
    on_chapter: int = 0
    time_in_chapter: int = 0
    wearing_uniform: bool = False

    version: int = 1

    def __post_init__(self):
        global world
        world = self

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
        with open("data/agents/agents.yaml", "r") as agent_file:
            all_agent_yaml = yaml.safe_load(agent_file)
            for agent_uid, agent_yaml in all_agent_yaml.items():
                self.agents[agent_uid] = Agent.load_yaml(agent_uid, agent_yaml)

        pass

    def save(self):
        saved_world = yaml.dump(self, Dumper=Dumper)
        return saved_world

    @classmethod
    def load(cls, yaml_text):
        world = yaml.load(yaml_text, Loader=Loader)
        return world

    def upgrade(self, newer_world: World):
        if self.version != newer_world.version:
            raise Exception("Can't load the saved game from a different version")
        # Not implemented
        # self.rooms = newer_world.rooms
        # for agent_uid in newer_world.agents.keys():
        #     if agent_uid not in self.agents:
        #         self.agents[agent_uid] = newer_world.agents[agent_uid]
        #     else:
        #         self.agents[agent_uid].upgrade(newer_world.agents[agent_uid])

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
        self.time_in_chapter += 1
        for agent in self.agents.values():
            if agent.room_id == self.current_room_id and len(agent.tic_creatives) > 0:
                # Pick a random tic
                self.play_sections([random.choice(agent.tic_creatives)], "purple")
            agent.movement.step(agent)
        if f"Tic {self.time_in_room}" in self.current_room.descriptions:
            self.play_sections(
                self.current_room.descriptions[f"Tic {self.time_in_room}"], "purple"
            )

        if self.on_chapter == 4 and self.time_in_chapter == 7:
            self.play_sections(
                """Terrus pushes past David, making the older gentleman stumble and fall to one knee.  You run over to help David up as June spins around to face the tour.

**June Hope**: Pardon me, sir, but the tour is still ongoing!

**Terrus Black**: Apologies, but I have urgent matters to attend to.

Terrus walks through June as if she wasn't there.  June quickly steps to the side.
As Terrus exits down the stairs, you notice a surveillance earpiece in his right ear.
June is visibly upset but her professional instincts kick in and she smiles politely to the remainder of the group.

**June Hope**: Please bear with me for one moment.  Thank you!

June pulls out a two-way radio and murmurs something unintelligible.

{{ world.ask_to_press_key() }}

After a few moments, the short conversation is over and June turns back to face the tour.

**June Hope**: Alright, let's hurry along then!  Please enjoy this area for a moment longer, then the tour will continue shortly.
""".split(
                    "\n\n"
                )
            )
            self.agents["mercenary"].room_id = None

        if self.on_chapter == 4 and self.time_in_chapter == 20:
            # Captain yell
            self.start_ch5()

    def move_to(self, room_id):
        assert room_id in self.rooms
        self.current_room_id = room_id
        self.time_in_room = 0
        if room_id in self.visited_rooms:
            self.look_quickly()
        else:
            self.visited_rooms.add(room_id)
            self.look()

    def go(self, direction):
        direction = direction.lower()
        if direction not in self.current_room.exits:
            console.warning("You can't go that way.")
            return False
        if self.on_chapter == 3 or self.on_chapter == 4:
            if self.current_room_id == self.agents["tour_guide"].room_id:
                tour_guide_name = self.agents["tour_guide"].name
                console.print(
                    f'{tour_guide_name} holds up a hand: "Please stay close to me until the tour is over.  Soak up the sights and sounds!  There will be plenty of time to go back and visit a spot we missed.  Thank you!"'
                )
                return False
        exit = self.current_room.exits[direction]
        if exit.prescript is not None:
            result = jinja2.Environment().from_string(exit.prescript).render(world=self)
            # Extract tokens
            tokens = []

            def replace_tokens(matchobj):
                tokens.append(matchobj.group(1))
                return ""

            result_without_tokens = re.sub(r"%%(.*?)%%", replace_tokens, result, 0)

            if len(result_without_tokens) > 0:
                self.play_sections(result_without_tokens.split("\n\n"))
            if "False" in tokens:
                return False
        self.move_to(exit.room_uid)
        if exit.postscript is not None:
            jinja2.Environment().from_string(exit.postscript).render(world=self)
        return True

    def send_agent(self, agent: Agent, direction: str):
        assert agent.room_id is not None
        direction = direction.lower()
        agent_room = self.rooms[agent.room_id]
        assert direction in agent_room.exits
        if self.current_room_id == agent.room_id:
            console.print(f"{agent.name} walks {direction}.")
        self.move_agent(agent, self.rooms[agent_room.exits[direction].room_uid])
        if self.current_room_id == agent.room_id:
            console.print(f"{agent.name} walks in.")

    def move_agent(self, agent: Agent, room: Optional[Room]):
        if room is None:
            agent.room_id = None
        else:
            agent.room_id = room.uid

    def look(self):
        self.print_header()
        self.play_sections(self.current_room.descriptions["Long"], style="yellow")
        display_image_for_prompt(self.current_room.descriptions["Long"][0])
        self.print_footer()

    def look_quickly(self):
        self.print_header()
        self.play_sections(self.current_room.descriptions["Short"], style="yellow")
        self.print_footer()

    @property
    def current_quest(self) -> Optional[str]:
        if self.on_chapter == 1:
            return "Waiting to arrive at the cruise terminal."
        if self.on_chapter == 2:
            if "my_stateroom" not in world.visited_rooms:
                return "Exploring the Fortuna"
            elif world.current_room_id != "vip_lounge":
                return "Making my way to the VIP Room"
            else:
                return "Chatting with other VIPs"
        if self.on_chapter < 5:
            return "Looking around and chatting on the VIP Tour."
        if self.on_chapter == 5:
            return "Looking for an officer keycard"
        return None

    def print_goal(self):
        if self.current_quest is not None:
            console.print(
                "Your current goal is: " + self.current_quest, style="bright_blue bold"
            )

    def print_header(self):
        self.print_goal()
        console.print(self.current_room.title, style="yellow bold")

    def print_footer(self):
        self.print_agents()
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

    @property
    def agents_in_room(self) -> List[Agent]:
        def is_in_room(agent: Agent):
            return agent.room_id == self.current_room_id

        return list(filter(is_in_room, self.agents.values()))

    def print_agents(self):
        agent_text = [
            f"* {agent.name} is standing here.  " for agent in self.agents_in_room
        ]
        if len(agent_text) == 0:
            return
        console.print(Markdown("""**People Here:**\n""" + "\n".join(agent_text)))
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
                scenery_action = None
                if verb.lower() in scenery.actions:
                    scenery_action = verb.lower()
                else:
                    verb_classes = get_verb_classes(verb.lower())
                    for action in scenery.actions.keys():
                        if len(verb_classes.intersection(get_verb_classes(action))) > 0:
                            scenery_action = action
                            break
                if scenery_action is not None:
                    self.play_sections(scenery.actions[scenery_action], "yellow")
                    if verb == "look":
                        display_image_for_prompt(scenery.actions[scenery_action][0])
                    return True
        return False

    def play_sections(self, sections: List[str], style: Optional[str] = None):
        for section in sections:
            paragraph = jinja2.Environment().from_string(section).render(world=self)
            if len(paragraph) > 0 and paragraph != "None":
                console.print(Markdown(paragraph), style=style)
                console.print("")

    def persuade(self, agent: Agent):
        if agent.friend_points < 2:
            console.warning(
                f"You aren't close enough friends with {agent.name} to persuade them."
            )
            return

        if agent.uid == "port_security_officer":
            self.play_sections(
                """The security guard grabs your paperwork and begins reviewing it.  Other passengers are visibly annoyed at this.  One begins to approach the security desk, but Derrick holds up his palm.

**Derrick Williams (to other passenger):** VIP Guest, please wait your turn.

Derrick quickly scans your paperwork and hands you your room key.

**Derrick Williams:** Go north to board the ship, sir.""".split(
                    "\n\n"
                ),
                "yellow",
            )

    def start_chapter_one(self):
        self.active_agents = set(["taxi_driver", "port_security_officer"])
        self.current_room_id = "driving_to_terminal"
        self.time_in_room = 0
        self.on_chapter = 1
        self.time_in_chapter = 0

        with open("data/start_ch1.md", "r") as fp:
            sections = fp.read().split("\n\n")
            self.play_sections(sections, "yellow")

    def start_ch2(self):
        self.active_agents = set()
        self.on_chapter = 2
        self.time_in_chapter = 0

        with open("data/start_ch2.md", "r") as fp:
            sections = fp.read().split("\n\n")
            self.play_sections(sections, "yellow")

    def start_ch3(self):
        self.active_agents = set(
            [
                "tour_guide",
                "vip_reporter",
                "ex_convict",
                "research_scientist",
                "financier",
                "mercenary",
                "captain",
            ]
        )
        self.on_chapter = 3
        self.time_in_chapter = 0

        with open("data/start_ch3.md", "r") as fp:
            sections = fp.read().split("\n\n")
            self.play_sections(sections, "yellow")

    def start_ch4(self):
        self.on_chapter = 4
        self.time_in_chapter = 0

    def start_ch5(self):
        self.on_chapter = 5
        self.time_in_chapter = 0

        with open("data/start_ch5.md", "r") as fp:
            sections = fp.read().split("\n\n")
            self.play_sections(sections, "yellow")

        # Move some agents around
        self.agents["vip_reporter"].room_id = "pool_deck"
        self.agents["ex_convict"].room_id = "gym"
        self.agents["research_scientist"].room_id = "theater"
        self.agents["tour_guide"].room_id = None

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


class ScriptId(IntEnum):
    stationary = 0
    vip_tour_guest = 1
    tour_guide = 2
    nancy = 3
    financier = 4
    mercenary = 5
    captain = 6


class MovementScript:
    def step(self, agent: Agent):
        raise NotImplementedError()


class TourGuideMovementScript(MovementScript):
    def __init__(self):
        pass

    def step(self, agent: Agent):
        if world.on_chapter == 4:
            time_movement_map = {
                3: "down",
                6: "down",
                9: "down",
                12: "down",
                15: "down",
                18: "north",
            }
            if world.time_in_chapter in time_movement_map:
                direction = time_movement_map[world.time_in_chapter]
                if world.time_in_chapter < 7:
                    tour_group = [
                        world.agents["vip_reporter"],
                        world.agents["ex_convict"],
                        world.agents["research_scientist"],
                        world.agents["mercenary"],
                        None,
                    ]
                else:
                    tour_group = [
                        world.agents["vip_reporter"],
                        world.agents["ex_convict"],
                        world.agents["research_scientist"],
                        None,
                    ]
                random.shuffle(tour_group)
                # Move everyone to the pool deck
                console.print(Markdown("**June Hope:** Come along, everyone."))
                world.send_agent(agent, direction)
                [
                    world.send_agent(agent, direction)
                    if agent is not None
                    else world.go(direction)
                    for agent in tour_group
                ]


@dataclass
class Movement:
    starting_room: Optional[str]
    script_id: ScriptId
    script: Optional[MovementScript]

    @classmethod
    def from_yaml(cls, yaml):
        script_id = ScriptId[yaml.get("script_id", "stationary")]
        script = None
        if script_id == ScriptId.tour_guide:
            script = TourGuideMovementScript()
        return Movement(yaml["starting_room"], script_id, script)

    def step(self, agent: Agent):
        if self.script is None:
            return
        self.script.step(agent)
