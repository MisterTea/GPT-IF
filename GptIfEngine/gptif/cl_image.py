from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import base64
import io

import openai
import requests

import os

stage = os.environ.get("STAGE", None)
if stage is None:
    from climage.__main__ import _get_color_type, _toAnsi


from PIL import Image

import gptif.settings
from gptif.console import console
from gptif.db import (
    AiImage,
    get_ai_image_from_id,
    get_ai_image_if_cached,
    put_ai_image_in_cache,
)


def display_image(image_data_bytes: bytes):
    if stage is None:
        im = Image.open(io.BytesIO(image_data_bytes))
        ctype = _get_color_type(
            is_truecolor=False, is_256color=True, is_16color=False, is_8color=False
        )
        output = _toAnsi(
            im, oWidth=80, is_unicode=True, color_type=ctype, palette="default"
        )
        print(output)


def display_image_for_prompt(prompt: str):
    if gptif.settings.DEBUG_MODE == True:
        return
    query = AiImage(model_version="dalle", prompt=prompt)
    if gptif.settings.CONVERSE_SERVER is None:
        ai_image = get_ai_image_if_cached(query)
        if ai_image is None:
            # Grab the ai_image from openai
            import openai

            response = openai.Image.create(
                prompt=query.prompt,
                n=1,
                size="256x256",
                response_format="b64_json",
            )

            image_data_b64 = response["data"][0]["b64_json"]
            image_data_bytes = base64.b64decode(image_data_b64)
            query.result = image_data_bytes

            put_ai_image_in_cache(query)

            assert query.id is not None

            ai_image_id = query.id
        else:
            assert ai_image.id is not None
            ai_image_id = ai_image.id

        assert ai_image_id is not None
        if not gptif.settings.CLI_MODE:
            console.print(f"%%IMAGE%% {ai_image_id}")
            return

        ai_image = get_ai_image_from_id(ai_image_id)

        assert ai_image is not None
        assert ai_image.result is not None
        display_image(ai_image.result)

    else:
        response = requests.post(
            f"{gptif.settings.CONVERSE_SERVER}/fetch_image_id_for_caption",
            json=query.dict(),
        )

        console.debug("RESPONSE", response)
        console.debug(response.content)

        # TODO: More gracefully handle errors
        assert response.status_code == 200

        image_id = int(response.content.decode().strip('"'))

        response = requests.get(f"{gptif.settings.CONVERSE_SERVER}/ai_image/{image_id}")

        # TODO: More gracefully handle errors
        assert response.status_code == 200

        # print(response.content)

        # image_data_b64 = response["data"][0]["b64_json"]
        # image_data_bytes = base64.b64decode(image_data_b64)

        display_image(response.content)


if __name__ == "__main__":
    gptif.settings.CONVERSE_SERVER = "http://localhost:8000"
    display_image_for_prompt("Two dogs farting")
