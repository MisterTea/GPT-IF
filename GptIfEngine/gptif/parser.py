import os

os.environ["NLTK_DATA"] = "nltk_data"

from typing import Dict, List, Optional, Set, cast
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk import Nonterminal, nonterminals, Production, CFG
from nltk.corpus import verbnet
import yaml
import spacy
from collections.abc import Iterable
from gptif.console import console
from spacy.symbols import nsubj


def flatten(xs):
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


# if not os.path.exists(os.path.expanduser("~/nltk_data")):
# nltk.download("wordnet")
# nltk.download("verbnet")

nlp = None


def init_nlp():
    global nlp
    if nlp is None:
        if "STAGE" in os.environ:
            nlp = spacy.load(f"/var/task/en_core_web_sm/en_core_web_sm-3.5.0")
        else:
            nlp = spacy.load("en_core_web_sm")


class ParseException(Exception):
    pass


def get_verb_classes(verb: str) -> Set[str]:
    return set(
        [verbnet.shortid(x).split(".")[0] for x in verbnet.classids(lemma=verb.lower())]
    )


def get_verb_classes_for_list(verbs: Iterable[str]) -> Set[str]:
    retval = set()
    for verb in verbs:
        retval.update(
            set(
                [
                    verbnet.shortid(x).split(".")[0]
                    for x in verbnet.classids(lemma=verb.lower())
                ]
            )
        )
    return retval


def handle_user_input(user_input: str):
    global nlp
    init_nlp()

    user_input_tokens = word_tokenize(user_input)

    doc = nlp(user_input)

    pos_tags = []
    for token in doc:
        # Overwrite the nltk pos with spacy
        console.debug(
            token.text,
            token.lemma_,
            token.pos_,
            token.tag_,
            token.dep_,
            token.shape_,
            token.is_alpha,
            token.is_stop,
            list(token.children),
            list(token.ancestors),
        )
        pos_tags.append((token.text, token.tag_))

    if len(list(doc[0].ancestors)) > 0 or doc[0].tag_ != "VB":
        pass
        raise ParseException(
            f"({user_input}) invalid: Each command should start with a verb. {list(doc[0].ancestors)}, {doc[0].tag_}"
        )
    verb = doc[0].text

    # Pick the first pobj or dobj to be the sentence object
    def is_sentence_object(token):
        return token.dep_ == "pobj" or token.dep_ == "dobj"

    sentence_objects = list(filter(is_sentence_object, doc))

    if len(sentence_objects) < 1:
        raise ParseException(
            f"({user_input}) invalid: transitive verb requires a direct object"
        )

    sentence_object_noun = sentence_objects[0].text

    if False:
        pos_tags = nltk.pos_tag(user_input_tokens)

        pos_tag_set = set(pos_tags)
        pos_rules: Dict[str, List[str]] = {}
        for pos_tag in pos_tag_set:
            pos_rules[pos_tag[1]] = pos_rules.get(pos_tag[1], []) + [pos_tag[0]]
        console.debug(pos_rules)

        literal_rules = []

        # For nltk
        for pos_rule in pos_rules.items():
            literal_list = " | ".join([f'"{l}"' for l in pos_rule[1]])
            literal_rules.append(f"{pos_rule[0]} -> {literal_list}")

        grammar_str = """
        S -> VP PP | VP
        VP -> VB | VB NP | VBN TO NP | VB IN NP
        PP -> NP
        NP -> DT NN
        NP -> NN
        NPP -> NP PP | NP
        """ + "\n".join(
            literal_rules
        )
        grammar = CFG.fromstring(grammar_str)

        rd_parser = nltk.RecursiveDescentParser(grammar)
        parses = list(rd_parser.parse(user_input_tokens))
        if len(parses) <= 0:
            raise ParseException(f"Sentence {user_input} does not parse")
        if len(parses) > 1:
            raise ParseException(f"Sentence {user_input} is ambiguous")
        tree = parses[0]
        console.debug(tree)

        if len(tree) == 2:
            # Prepositional phrase.  For now, ignore
            pass

        verb_tree_node = tree[0][0]
        if verb_tree_node.label() != "VB" and verb_tree_node.label() != "VBN":  # type: ignore
            raise ParseException(f"{user_input} doesn't start with a verb")

        verb: str = cast(str, tree[0][0][0])
        console.debug(verb)

        sentence_object = tree[0][1]
        if sentence_object.label() == "TO" or sentence_object.label() == "IN":  # type: ignore
            sentence_object = tree[0][2]

        def is_noun(word_tag):
            return word_tag[1] == "NN" or word_tag[1] == "NNS"

        sentence_object_nouns = list(filter(is_noun, sentence_object.pos()))
        if len(sentence_object_nouns) > 1:
            raise ParseException(f"{user_input} has two objects of the verb.")

        sentence_object_noun = sentence_object_nouns[0][0]

        console.debug(sentence_object_noun)

    verb_hypernyms = set(
        [
            x.name()  # type: ignore
            for x in flatten(
                [x.hypernym_paths() for x in wordnet.synsets(verb, pos=wordnet.VERB)]  # type: ignore
            )
        ]
    )
    console.debug(verb_hypernyms)

    verb_classes = verbnet.classids(lemma=verb)

    verb_class_groups = set(
        [verbnet.shortid(x).split(".")[0] for x in verbnet.classids(lemma=verb.lower())]  # type: ignore
    )

    object_hypernyms = set(
        [
            x.name()  # type: ignore
            for x in flatten(
                [
                    x.hypernym_paths()  # type: ignore
                    for x in wordnet.synsets(sentence_object_noun, pos=wordnet.NOUN)
                ]
            )
        ]
    )
    console.debug(object_hypernyms)

    rooms_txt = open("data/rooms/rooms.yaml", "r")
    rooms_yaml = yaml.safe_load(rooms_txt)

    for action in rooms_yaml["cruise_terminal"]["actions"].values():
        action_verbs: Set[str] = set()
        for action_verb in action["verbs"]:
            action_verb_class_groups: Set[str] = set(
                [
                    verbnet.shortid(x).split(".")[0]  # type: ignore
                    for x in verbnet.classids(lemma=action_verb)
                ]
            )

            action_verbs.update(action_verb_class_groups)

        action_objects = set(action["objects"])

        console.debug(action_verbs.intersection(verb_class_groups))
        console.debug(action_objects.intersection(object_hypernyms))

        if (
            len(action_verbs.intersection(verb_class_groups)) > 0
            and len(action_objects.intersection(object_hypernyms)) > 0
        ):
            # Match! Take action
            console.debug(action["action"])


def get_direct_object(command: str) -> str:
    global nlp
    init_nlp()
    # user_input_tokens = word_tokenize(user_input)

    doc = nlp(command)

    pos_tags = []
    for token in doc:
        # Overwrite the nltk pos with spacy
        # console.debug(
        #     token.text,
        #     token.lemma_,
        #     token.pos_,
        #     token.tag_,
        #     token.dep_,
        #     token.shape_,
        #     token.is_alpha,
        #     token.is_stop,
        #     list(token.children),
        #     list(token.ancestors),
        # )
        pos_tags.append((token.text, token.tag_, token.dep_))

    if len(list(doc[0].ancestors)) > 0 or doc[0].tag_[:2] != "VB":
        raise ParseException(
            f'({command}) invalid: Each command should start with a verb.  Some verbs are phrasal and require a preposition such as "LOOK AT"'
        )
    verb = doc[0].text

    direct_object = None
    for i, token in enumerate(doc):
        if token.dep_ == "pobj" or token.dep_ == "dobj" or token.dep == nsubj:
            direct_object = token.text
            # Add compound prefix
            while i > 0 and doc[i - 1].dep_ == "compound":
                direct_object = doc[i - 1].text + " " + direct_object
                i -= 1
            break

    if direct_object is None:
        raise ParseException(
            f'({command}) invalid: {verb} is transitive and requires an object (for example, "STAND (ON THE CHAIR)").'
        )

    return direct_object


def get_hypernyms(s: str):
    object_hypernyms = [
        [y.name() for y in x.hypernym_paths()]  # type: ignore
        for x in wordnet.synsets(s, pos=wordnet.NOUN)
    ]
    return object_hypernyms


def get_hypernyms_set(s: str):
    object_hypernyms = [
        x.name()  # type: ignore
        for x in flatten(
            [
                x.hypernym_paths()  # type: ignore
                for x in wordnet.synsets(s, pos=wordnet.NOUN)
            ]
        )
    ]
    return set(object_hypernyms)


if __name__ == "__main__":
    pass
