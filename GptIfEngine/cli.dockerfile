FROM continuumio/miniconda3

#COPY gpt_models gpt_models

#RUN apt update
#RUN apt install pip

RUN apt update
RUN apt install -y build-essential

COPY requirements.txt .
COPY setup.py .

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_sm
# RUN python -m spacy download en_core_web_trf

RUN python -c "import nltk; nltk.download(\"popular\")"
RUN python -c "import nltk; nltk.download(\"verbnet\")"

COPY gptif gptif

RUN pip install -e .

RUN python -m gptif.parser

COPY data data

ENTRYPOINT [ "python", "-m", "gptif.play", "--converse-server=https://i00ny5xb4e.execute-api.us-east-1.amazonaws.com" ]
