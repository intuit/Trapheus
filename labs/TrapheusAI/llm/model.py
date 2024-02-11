import matplotlib
import openai
import pandas
import streamlit as streamlit
from dataclasses import asdict
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import Ollama
from llm.prompts import Prompt
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
from typing import Tuple, List

from pandasai.llm import LangchainLLM

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

def ask_foundational_data_model(dataframe: pandas.core.frame.DataFrame, query: str, llm_type):
    # local llm is still having issues, i have reported this at
    # https://github.com/gventuri/pandas-ai/issues/340#issuecomment-1637184573
    # seeing if chart introduction can help https://github.com/gventuri/pandas-ai/pull/497/files#r1341966270
    if llm_type == 'LocalLLM':
        olama = Ollama(model="llama2")
        llm = LangchainLLM(olama)
    else:
        llm = OpenAI(api_token=streamlit.secrets["OPENAI_API_KEY"])
    smart_df = SmartDataframe(dataframe, config={"llm": llm})
    response =  smart_df.chat(query)
    return response

