import multiprocessing
import os
from typing import List, Optional

import openai
import requests
from llama_cpp import Llama
from rich.progress import Progress

from gptif import db
from gptif.console import console
from gptif.state import Agent
from gptif.world import world


class LargeLanguageModel:
    def llm(self, question: str, stop: List[str] = [], echo: bool = False) -> str:
        raise NotImplementedError()

    def model_name(self):
        raise NotImplementedError()


class LlamaCppLanguageModel:
    MODEL_NAME = "koala-13B-4bit-128g.GGML.bin"

    def __init__(self):
        self.llm_model = None

    def model_name(self):
        return LlamaCppLanguageModel.MODEL_NAME

    def llm(self, question: str, stop: List[str] = [], echo: bool = False) -> str:
        if self.llm_model == None:
            model_path = f"gpt_models/{self.model_name()}"
            if not os.path.exists(model_path):
                if not os.path.exists("gpt_models"):
                    os.makedirs("gpt_models")
                    console.warning(
                        'gpt_models path is missing.  Did you forget to add "-v gpt_models:/gpt_models" to your docker run?'
                    )
                # Download the model
                download_file(
                    f"https://huggingface.co/TheBloke/koala-13B-GPTQ-4bit-128g-GGML/resolve/main/{self.model_name()}"
                )
            self.llm_model = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=multiprocessing.cpu_count(),
                embedding=True,
                verbose=False,
            )

        return self.llm_model(question, stop=stop, echo=echo)["choices"][0]["text"]  # type: ignore


class OpenAiLanguageModel:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def model_name(self):
        return "gpt-3.5-turbo"

    def llm(self, question: str, stop: List[str] = [], echo: bool = False) -> str:
        response = openai.ChatCompletion.create(
            model=self.model_name(),
            messages=[
                {"role": "user", "content": question},
            ],
            stop=stop,
        )
        return response["choices"][0]["message"]["content"]


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


# llm = LlamaCppLanguageModel()
llm = OpenAiLanguageModel()
