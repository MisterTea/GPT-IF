from typing import Any, Optional
from rich.console import Console

DEBUG_INPUT = [
    'ASK Juan "Where are you from?"',  #
    "LOOK",  #
    'ASK Juan "What are you doing right now?"',  #
    # 3 turns driving
    "LOOK AT RIVER",  #
    "LOOK AT THE RIVER",  #
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
    "NORTH",
    # On Gangway
    "Look at gangway",
    "look at passengers",
    "WALK NORTH",
]


class ConsoleHandler:
    def __init__(self):
        self.console = Console()

    def get_input(self, prompt: str) -> str:
        if len(DEBUG_INPUT) > 0:
            x = DEBUG_INPUT[0]
            DEBUG_INPUT.pop(0)
            console.print(prompt + x)
            console.print("\n")
            return x

        x = self.console.input(prompt)
        console.print("\n")
        return x

    def print(self, *objects: Any, style: Optional[str] = None):
        self.console.print(*objects, style=style)

    def input(self, prompt: str):
        return self.console.input(prompt)

    def debug(self, *objects: Any):
        self.console.print(*objects, style="bright_black on black")

    def warning(self, *objects: Any):
        self.console.print(*objects, style="red on black")
        if len(DEBUG_INPUT) > 0:
            # Shouldn't get warnings in debug mode...
            self.print("Got a warning in debug mode")


console = ConsoleHandler()
