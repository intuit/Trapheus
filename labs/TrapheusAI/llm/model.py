from dataclasses import asdict
from typing import Tuple, List
import openai

import matplotlib
import pandas
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI

from llm.prompts import Prompt

# Since most backends are non GUI setting this to Agg to pick this up later from a file
# TODO later let the user choose the ibackend he is operating on from a command line param.
matplotlib.use('Agg')


def ask_foundational_model(discourses: List[Prompt]) -> Tuple[str, List[Prompt]]:
    # TODO Add the foundational language model as a param either local or a hosted one providing users with options to
    # choose one for privacy or other reasons.
    result = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [asdict(discourse) for discourse in discourses]
    )

    answer = Prompt(**result["choices"][0]["message"])
    return answer.content, discourses + [answer]

def ask_foundational_data_model(dataframe: pandas.core.frame.DataFrame, query: str):
    # local llm is still having issues, i have reported this at
    # https://github.com/gventuri/pandas-ai/issues/340#issuecomment-1637184573
    # seeing if chart introduction can help https://github.com/gventuri/pandas-ai/pull/497/files#r1341966270
    llm = OpenAI(api_token='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')
    smart_df = SmartDataframe(dataframe, config={"llm": llm})
    response =  smart_df.chat(query)
    return response

