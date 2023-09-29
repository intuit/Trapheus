import streamlit as streamlit
from typing import Optional, List, Tuple
from llm.prompts import Prompt, dialogue
from llm.model import ask_model


class Concept:

    def __init__(self, edges: Optional[List[Tuple[str, str]]]=None, nodes: Optional[List[str]]=None) -> None:
        self.edges = [] if edges is None else edges
        self.nodes = [] if nodes is None else nodes
        self.save()

    @classmethod
    def render(cls) -> Concept:
        if "concept" in streamlit.session_state:
            return streamlit.session_state["concept"]
        return cls()

    def save(self) -> None:
        streamlit.session_state["concept"] = self

    def is_empty(self) -> bool:
        return len(self.edges) == 0

    def render_initial_concepts(self, query: str) -> None:
        discourse = dialogue + [
            Prompt(f"""
                Ignore previous graphs and restart. I want you to do the following.
                {query}
            """, role="user")
        ]
        output , self.conversation = ask_model(discourse)
        self.add_relationships(output, replace=True)
