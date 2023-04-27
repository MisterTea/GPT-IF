from pygpt4all.models.gpt4all import GPT4All


def new_text_callback(text):
    print(text, end="")


model = GPT4All("./gpt_models/ggml-gpt4all-j.bin")
model.generate(
    """Answer questions about the following statement:

"What is a quark?"

Does the question above end in a question mark?
Yes

Does the question above ask about Einstein?
No

Is the question above about the military?

""",
    n_predict=55,
    new_text_callback=new_text_callback,
)
