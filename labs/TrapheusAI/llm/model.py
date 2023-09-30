import pandas
from pandasai.llm.openai import OpenAI
from pandasai import SmartDataframe
from typing import Tuple, List
from llm.prompts import Prompt
from dataclasses import asdict

# Since most backends are non GUI setting this to Agg to pick this up later from a file
# TODO later let the user choose the ibackend he is operating on from a command line param.
import matplotlib
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
    llm = OpenAI(api_token='xxxx')
    smart_df = SmartDataframe(df, config={"llm": llm})
    response =  smart_df.chat(query)
    return response

