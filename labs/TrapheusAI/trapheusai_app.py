from __future__ import annotations

from glob import glob

import openai
import pandas as pd
import streamlit as streamlit
from PIL import Image

from concepts.conceptSearch import ConceptSearch
from llm.model import ask_foundational_data_model
from providers.github_provider import Github

streamlit.set_page_config(page_title="Concept and data search", layout="wide")
openai.api_key = streamlit.secrets["OPENAI_API_KEY"]


def initialize_page():
    style_page()
    streamlit.sidebar.image("logo/TrapheusAILogo.png", use_column_width=True)
    streamlit.sidebar.subheader("Select the type of analysis")
    analysis_type = streamlit.sidebar.selectbox("", options=["Concept Search", "Dataset Search"])
    if analysis_type == "Dataset Search":
        handle_dataset_search()
    else:
        handle_concept_search()

# TODO Later move analysis types to a common abstract factory
def handle_dataset_search():
    query = streamlit.sidebar.text_area(
        "Search for data",
        value=streamlit.session_state.get("dataset-input", ""),
        key="dataset-input",
        height=200)
    submit = streamlit.sidebar.button("Submit", key='dataset-submit')
    if "clicked" not in streamlit.session_state:
        streamlit.session_state.clicked = False
    if submit or streamlit.session_state["clicked"]:
        streamlit.session_state["clicked"] = True
        with streamlit.spinner(text="Loading data ..."):
            streamlit.session_state["loading"] = True
            response = Github().extract_data(query)
            choice = streamlit.selectbox("Choose a DataSet", [result["repo"] for result in response])

            if choice:
                data = next(result for result in response if result["repo"] == choice)
                repository_url = data["fullurl"]
                df = pd.read_csv(repository_url)
                updated_df = streamlit.data_editor(df)
                streamlit.download_button(
                    "Download as CSV", data = updated_df.to_csv(index=False), file_name=f"{choice}.csv", 
                    mime = "text/csv", on_click = showDownloadMessage)
                question = streamlit.chat_input("Ask any question related to the dataset")
                if question:

                    answer = ask_foundational_data_model(df, question)
                    print(question)
                    if ("plot" or "Plot" or "Chart" or "chart" or "Graph" or "graph") in question:
                        print('inside')
                        plot_folder = glob("exports/charts/temp_chart.png")
                        print (plot_folder)
                        plot = Image.open(plot_folder[0])
                        streamlit.image(plot, use_column_width=False)
                    else:
                        streamlit.write(answer)

def handle_concept_search():
    concept_search = ConceptSearch.render()
    empty = concept_search.is_empty()
    reset = empty or streamlit.sidebar.checkbox("Reset concept search", value=False)
    query = streamlit.sidebar.text_area(
        "Ask anything" if reset else "Expand your concept space",
        value=streamlit.session_state.get("concept-search", ""),
        key="concept-search",
        height=200)
    submit = streamlit.sidebar.button("Submit", key="conceptsearch-submit")
    valid_submission = submit and query != ""
    if empty and not valid_submission:
        return
    with streamlit.spinner(text="Loading concepts..."):
        # if submit and non-empty query, then update graph
        if valid_submission:
            if reset:
                # completely new mindmap
                concept_search.render_initial_concepts(query=query)
            else:
                # extend existing mindmap
                concept_search.drill_down(text=query)
            # since inputs also have to be updated, everything
            # is rerun
            streamlit.experimental_rerun()
        else:
            concept_search.render_concepts()

def style_page():
    style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
    streamlit.markdown(style, unsafe_allow_html=True)

def showDownloadMessage():
    streamlit.success("Your dataset has been saved")


if __name__ == "__main__":
    initialize_page()

