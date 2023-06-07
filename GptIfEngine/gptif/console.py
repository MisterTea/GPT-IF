import contextvars
from typing import Any, Dict, List, Optional, Tuple, cast
from rich.markdown import Markdown


from rich.console import Console

import gptif.settings

DEBUG_INPUT = [
    'ASK Juan "Where are you from?"',  #
    "LOOK AT THE TERMINAL",  #
    "GOAL",  # GOAL does not cost a turn
    '"What are you doing right now?"',  #
    # At the terminal now
    "watch the television",
    "watch tv",
    "look at the television on the column",
    "look at the desk",
    "sit on the desk",
    "look at derrick",
    "look at officer",
    "N",
    'ASK officer "How long were you in the military?"',
    'ASK officer "What was it like serving in Iraq?"',
    "PERSUADE DeRRiCK",
    "NORTH",
    # On Gangway
    "Look at gangway",
    "look at passengers",
    "WALK NORTH",
    "look at fountain",
    "d",
    "d",  # At crew quarters
    "n",  # Can't go north yet
    "d",  # Can't go down yet
    "w",  # In medical
    "e",
    "u",
    "u",
    "u",
    "U",
    "uP",
    "d",
    "weSt",  # Going to your room
    '"ocean"',  # Telling the safe the password
    "e",
    "u",
    "u",
    "d",
    'TELL captain "When did you become a captain?"',
    'TELL captain "I\'m worried about you"',
    'tell captain "I think someone is trying to kill you"',
    'tell mercenary "Why are you on this cruise?"',
    'tell mercenary "You are going to blow up the ship"',
    # 5 steps, advance
    'tell nancy "What do you do for a living?"',
    'tell nancy "Feminism is great"',
    # 2 steps, advance
    'tell nancy "Women should have the right to vote"',
    'tell David "What is your research area?"',
    'tell David "Tell me about particle physics"',
    # 3 steps, move
    "Look at nancy",
    "Look at nancy",
    "Look at nancy",
    # 3 steps, move
    "Look at nancy",
    "Look at nancy",
    "Look at nancy",
    # 3 steps, move
    "Look at nancy",
    "Look at nancy",
    "Look at nancy",
    # 3 steps, move
    "Look at nancy",
    "Look at nancy",
    "Look at nancy",
    # 3 steps, move
    "Look at nancy",
    "Look at nancy",
    "Look at nancy",
    # 2 steps until event
    "wait",
    "wait",
    # Go to gym locker
    "u",
    "u",
    "n",
    "w",
    "look at locker",
    "open the locker",
    # Go to engine room
    "e",
    "s",
    "d",
    "d",
    "d",
    "d",
    "d",  # In engine room, get cutscene
    "u",
    "u",
    "n",
    '"What is a black hole?"',
    '"What is your favorite physics lesson?"',
    "persuade david",
    "s",
    "u",
    "u",
    "e",
    '"dogfart"',
    "w",
    "u",
    "persuade nancy",
    #'"poverty"',
]

session_id_contextvar = contextvars.ContextVar("session_id", default="")


class ConsoleHandler:
    def __init__(self):
        self._console = Console()
        self.buffers: Dict[str, List[Tuple[str, Optional[str]]]] = {}
        self.step_mode = False

    def get_input(self, prompt: str) -> str:
        if len(DEBUG_INPUT) > 0:
            x = DEBUG_INPUT[0]
            DEBUG_INPUT.pop(0)
            self._console.print()
            self._console.print(prompt + x)
            self._console.print("\n")
            return x

        self._console.print()
        x = self._console.input(prompt)
        self._console.print("\n")
        return x

    def print(self, *objects: Any, style: Optional[str] = None):
        session_id = session_id_contextvar.get()
        if len(session_id) > 0:
            if session_id not in self.buffers:
                self.buffers[session_id] = []
            self.buffers[session_id].append(
                (ConsoleHandler.merge_parameters(objects), style)
            )
        else:
            self._console.print(*objects, style=style)

    @staticmethod
    def merge_parameters(*objects: Any) -> str:
        def replace_markdown(o: Any):
            if isinstance(o, Markdown):
                return cast(Markdown, o).markup
            return str(o)

        return ", ".join(map(replace_markdown, *objects))

    def input(self, prompt: str):
        return self._console.input(prompt)

    def debug(self, *objects: Any):
        if gptif.settings.DEBUG_MODE is True or gptif.settings.CLI_MODE is False:
            self._console.print(*objects, style="bright_black on black")

    def warning(self, *objects: Any):
        self.print(*objects, style="red on black")
        if gptif.settings.DEBUG_MODE:
            # Shouldn't get warnings in debug mode...
            self.print("Got a warning in debug mode")

    def ask_to_press_key(self):
        if gptif.settings.DEBUG_MODE or not gptif.settings.CLI_MODE:
            self.print("[blue]Press enter to continue...[/]")
        else:
            self.input("[blue]Press enter to continue...[/]")
        self.print("\n")


console = ConsoleHandler()
