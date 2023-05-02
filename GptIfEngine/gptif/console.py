import contextvars
from typing import Any, Dict, List, Optional, Tuple, cast
from rich.markdown import Markdown


from rich.console import Console

import gptif.settings

DEBUG_INPUT = [
    'ASK Juan "Where are you from?"',  #
    "L",  #
    'ASK Juan "What are you doing right now?"',  #
    # 3 turns driving
    "LOOK AT RIVER",  #
    "LOOK AT THE RIVER",  #
    "GOAL",  # GOAL does not cost a turn
    "WAIT",  #
    # 6 turns driving, at the terminal now
    "watch the television",
    "watch tv",
    "look at the television on the column",
    "look at the desk",
    "sit on the desk",
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
    "weSt",
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
    "Look",
    "Look",
    "Look",
    # 3 steps, move
    "Look",
    "Look",
    "Look",
    # 3 steps, move
    "Look",
    "Look",
    "Look",
    # 3 steps, move
    "Look",
    "Look",
    "Look",
    # 3 steps, move
    "Look",
    "Look",
    "Look",
    # 2 steps until event
    "wait",
    "wait",
]

request_id_contextvar = contextvars.ContextVar("request_id", default="")


class ConsoleHandler:
    def __init__(self):
        self._console = Console()
        self.buffers: Dict[str, List[Tuple[str, Optional[str]]]] = {}

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
        request_id = request_id_contextvar.get()
        if len(request_id) > 0:
            if request_id not in self.buffers:
                self.buffers[request_id] = []
            self.buffers[request_id].append(
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
        if gptif.settings.DEBUG_MODE is True:
            self._console.print(*objects, style="bright_black on black")

    def warning(self, *objects: Any):
        self.print(*objects, style="red on black")
        if len(DEBUG_INPUT) > 0:
            # Shouldn't get warnings in debug mode...
            self.print("Got a warning in debug mode")


console = ConsoleHandler()
