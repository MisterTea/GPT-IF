from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import os
from typing import Optional

RUN_LOCALLY = True
CONVERSE_SERVER: Optional[str] = None
DEBUG_MODE = False
CLI_MODE = False

if "SQL_URL" not in os.environ:
    os.environ["SQL_URL"] = "sqlite:///~/.gptif"
