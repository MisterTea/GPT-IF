import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

from fastapi import FastAPI
from pydantic import BaseModel

from gptif.db import (
    GptDialogue,
    create_db_and_tables,
    get_answer_if_cached,
    put_answer_in_cache,
)
from gptif.llm import LlamaCppLanguageModel, OpenAiLanguageModel

stage = os.environ.get("STAGE", None)
root_path = f"/{stage}" if stage else "/"

app = FastAPI(title="MyAwesomeApp", root_path=root_path)

openai_model = OpenAiLanguageModel()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/fetch_dialogue")
async def fetch_dialogue(query: GptDialogue) -> str:
    answer = get_answer_if_cached(query)
    if answer is None and query.model_version == openai_model.model_name():
        # Grab the answer from openai
        assert query.stop_words is not None
        answer = openai_model.llm(
            query.context, stop=query.stop_words.split(","), echo=False
        )
        query.answer = answer
        put_answer_in_cache(query)
        return answer

    return "None" if answer is None else answer


@app.post("/put_dialogue")
async def put_dialogue(query: GptDialogue):
    put_answer_in_cache(query)


@app.get("/")
async def root():
    return {"message": "Hello World!"}
