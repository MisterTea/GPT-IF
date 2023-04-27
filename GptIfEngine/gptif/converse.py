import os

from typing import Optional

import requests
from gptif.state import Agent
from llama_cpp import Llama
from gptif.world import world
from gptif.console import console
from gptif import db
from rich.progress import Progress

llm = None
MODEL_NAME = "koala-13B-4bit-128g.GGML.bin"

RUN_LOCALLY = True
CONVERSE_SERVER: Optional[str] = None


def download_file(url):
    local_filename = url.split("/")[-1]
    # NOTE the stream=True parameter below
    try:
        with requests.get(url, stream=True) as r:
            content_length = int(r.headers["Content-Length"])
            with Progress() as progress:
                task1 = progress.add_task(
                    "[light_green]Downloading GPT model (this only happens once)...",
                    total=content_length,
                )

                r.raise_for_status()
                with open("gpt_models/" + local_filename, "wb") as f:
                    total_downloaded = 0
                    for chunk in r.iter_content(chunk_size=64 * 1024 * 1024):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)
                        total_downloaded += len(chunk)
                        # print(f"Downloaded {int((total_downloaded*100.0)/content_length)}%")
                        progress.update(task1, completed=total_downloaded)
        return local_filename
    except:
        console.warning("Error downloading file")
        if os.path.exists("gpt_models/" + local_filename):
            os.remove("gpt_models/" + local_filename)
        raise


def init_llm():
    global llm
    if llm is None:
        model_path = f"gpt_models/{MODEL_NAME}"
        if not os.path.exists(model_path):
            if not os.path.exists("gpt_models"):
                raise Exception(
                    'gpt_models path is missing.  Did you forget to add "-v gpt_models:/gpt_models" to your docker run?'
                )
            # Download the model
            download_file(
                f"https://huggingface.co/TheBloke/koala-13B-GPTQ-4bit-128g-GGML/resolve/main/{MODEL_NAME}"
            )
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=20,
            embedding=True,
            verbose=False,
        )


def get_answer_from_cache(dialogue: db.GptDialogue) -> Optional[str]:
    global CONVERSE_SERVER
    if CONVERSE_SERVER is not None:
        response = requests.post(
            CONVERSE_SERVER + "/fetch_dialogue", json=dialogue.dict()
        )

        # TODO: More gracefully handle errors
        assert response.status_code == 200
        console.debug("RESPONSE", response)
        console.debug(response.content)

        x = response.content.decode()
        if x == "None" or x == '"None"':
            return None
        return x
    else:
        return db.get_answer_if_cached(dialogue)


def put_answer_in_cache(dialogue: db.GptDialogue):
    console.debug("PUTTING ANSWER IN CACHE")
    global CONVERSE_SERVER
    if CONVERSE_SERVER is not None:
        response = requests.post(
            CONVERSE_SERVER + "/put_dialogue", json=dialogue.dict()
        )

        # TODO: More gracefully handle errors
        assert response.status_code == 200
    else:
        db.put_answer_in_cache(dialogue)


def converse(target_agent: Agent, statement: str) -> Optional[str]:
    global llm
    init_llm()
    assert llm is not None

    context = f"""Given a character and question, answer the question in a paragraph.

    Character:

**Name:** {target_agent.profile.name}
**Age:** {target_agent.profile.age}
**Gender:** {target_agent.profile.gender}
**Occupation:** {target_agent.profile.occupation}
**Personality:** {". ".join(target_agent.profile.personality)}
**Backstory:** {". ".join(target_agent.profile.backstory)}
**Goals:**   {". ".join(target_agent.profile.goals)}

Jason: What is your name?
{target_agent.profile.name}: \"My name is {target_agent.profile.name}.\"

Jason: {statement}
{target_agent.profile.name}: \""""

    assert target_agent.profile.name is not None

    dialogue = db.GptDialogue(
        character_name=target_agent.profile.name,
        model_version=MODEL_NAME,
        question=statement,
        context=context,
    )

    cached_answer = get_answer_from_cache(dialogue)
    console.debug("Cached answer:", cached_answer)
    if cached_answer is not None:
        return cached_answer
    console.print(f"[purple]{target_agent.profile.name} thinks for a moment...[/]")
    while True:
        answer = llm(
            dialogue.context, max_tokens=1500, stop=["Jason:", "\n"], echo=False
        )
        answer_text = answer["choices"][0]["text"]  # type: ignore
        completion_tokens = answer["usage"]["completion_tokens"]  # type: ignore
        if completion_tokens > 3:
            put_answer_in_cache(
                db.GptDialogue(
                    character_name=dialogue.character_name,
                    model_version=dialogue.model_version,
                    question=dialogue.question,
                    context=dialogue.context,
                    answer=answer_text,
                )
            )
            return answer_text


def check_if_more_friendly(target_agent: Agent, statement: str) -> bool:
    global llm
    init_llm()
    assert llm is not None

    for friendly_question in target_agent.friend_questions:
        context = f"""Answer questions about the following statement:

\"{statement}\"

Is the statement above about chocolate?
No

{friendly_question}
"""

        assert target_agent.profile.name is not None

        cached_answer = get_answer_from_cache(
            db.GptDialogue(
                character_name=target_agent.profile.name,
                model_version=MODEL_NAME,
                question=statement,
                context=context,
            )
        )
        if cached_answer is not None:
            if "yes" in cached_answer.lower():
                return True
            else:
                assert "no" in cached_answer.lower(), cached_answer
                return False
        console.print(f"[purple]{target_agent.profile.name} thinks for a moment...[/]")
        while True:
            answer = llm(context, max_tokens=1500, stop=["?", "\n\n"], echo=False)
            answer_text = answer["choices"][0]["text"]  # type: ignore
            console.debug("RAW ANSWER", answer_text)
            if "yes" in answer_text.lower():
                is_yes = True
            elif "no" in answer_text.lower():
                is_yes = False
            else:
                continue
            put_answer_in_cache(
                db.GptDialogue(
                    character_name=target_agent.profile.name,
                    model_version=MODEL_NAME,
                    question=statement,
                    context=context,
                    answer=answer_text,
                )
            )
            if is_yes:
                return True
    return False
