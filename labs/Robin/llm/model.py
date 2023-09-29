import openai
from typing import Tuple, List
from llm.prompts import Prompt
from dataclasses import asdict

def ask_model(discussions: List[Prompt]) -> Tuple[str, List[Prompt]]:
    # Future scope to incldue model as a parameter as well as load a local
    # quantized llm
    result = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [asdict(d) for d in discussions]
    )
    msg = Prompt(**result["choices"][0]["message"])
    return msg.content, discussions + [msg]