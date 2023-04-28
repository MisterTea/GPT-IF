import os
from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

from gptif.console import console

engine = None


class GptDialogue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    character_name: str = Field(index=True)
    model_version: Optional[str] = Field(index=True, nullable=False)
    question: str = Field(index=True)
    context: str = Field(index=True)
    answer: Optional[str] = Field(default=None, nullable=False)
    stop_words: Optional[str] = Field(default=None)


def create_db_and_tables():
    sql_url = os.environ["SQL_URL"]
    if sql_url.startswith("sqlite"):
        sql_file_path = os.path.expanduser(sql_url[len("sqlite:///") :])
        os.makedirs(sql_file_path, exist_ok=True)
        sql_url = "sqlite:///" + sql_file_path
        sql_url += "/dialogue.sqlite"
        connect_args = {"check_same_thread": False}
    else:
        connect_args = {}
    console.debug("OPENING DB AT", sql_url)

    global engine
    engine = create_engine(sql_url, echo=False, connect_args=connect_args)

    SQLModel.metadata.create_all(engine)


def get_answer_if_cached(dialogue: GptDialogue) -> Optional[str]:
    with Session(engine) as session:
        statement = (
            select(GptDialogue)
            .where(GptDialogue.character_name == dialogue.character_name)
            .where(GptDialogue.model_version == dialogue.model_version)
            .where(GptDialogue.question == dialogue.question)
            .where(GptDialogue.context == dialogue.context)
            .where(GptDialogue.stop_words == dialogue.stop_words)
        )
        results = list(session.exec(statement))
        if len(results) == 0:
            return None
        return results[0].answer


def put_answer_in_cache(dialogue: GptDialogue):
    with Session(engine) as session:
        session.add(dialogue)

        session.commit()
