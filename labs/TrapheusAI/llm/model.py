import openai
from typing import Tuple, List
from llm.prompts import Prompt
from dataclasses import asdict


def ask_foundational_model(discourses: List[Prompt]) -> Tuple[str, List[Prompt]]:
    # TODO Add the foundational language model as a param either local or a hosted one providing users with options to
    # choose one for privacy or other reasons.
    result = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [asdict(discourse) for discourse in discourses]
    )

    answer = Prompt(**result["choices"][0]["message"])
    return answer.content, discourses + [answer]