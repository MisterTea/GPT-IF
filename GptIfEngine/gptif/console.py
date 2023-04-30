from typing import Any, Optional

from rich.console import Console

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

DEBUG_MODE = True


class ConsoleHandler:
    def __init__(self):
        self.console = Console()

    def get_input(self, prompt: str) -> str:
        if len(DEBUG_INPUT) > 0:
            x = DEBUG_INPUT[0]
            DEBUG_INPUT.pop(0)
            console.print()
            console.print(prompt + x)
            console.print("\n")
            return x

        console.print()
        x = self.console.input(prompt)
        console.print("\n")
        return x

    def print(self, *objects: Any, style: Optional[str] = None):
        self.console.print(*objects, style=style)

    def input(self, prompt: str):
        return self.console.input(prompt)

    def debug(self, *objects: Any):
        global DEBUG_MODE
        if DEBUG_MODE is True:
            self.console.print(*objects, style="bright_black on black")

    def warning(self, *objects: Any):
        self.console.print(*objects, style="red on black")
        if len(DEBUG_INPUT) > 0:
            # Shouldn't get warnings in debug mode...
            self.print("Got a warning in debug mode")


console = ConsoleHandler()
