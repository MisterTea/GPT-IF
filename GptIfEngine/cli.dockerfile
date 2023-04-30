FROM continuumio/miniconda3

RUN pip install nltk==3.8.1 && pip install spacy==3.5.1

RUN python -m spacy download en_core_web_sm
# RUN python -m spacy download en_core_web_trf

RUN python -c "import nltk; nltk.download(\"popular\")"
RUN python -c "import nltk; nltk.download(\"verbnet\")"

#COPY gpt_models gpt_models

#RUN apt update
#RUN apt install pip

RUN apt update
RUN apt install -y build-essential

COPY requirements.txt .
COPY setup.py .

RUN pip install -r requirements.txt

COPY gptif gptif

RUN pip install -e .

RUN python -m gptif.parser

COPY data data

ENTRYPOINT [ "python", "-m", "gptif.play" ]
