import streamlit as st
from typing import Optional, List, Tuple

class ConceptMap:

    def __init__(self, edges: Optional[List[Tuple[str, str]]]=None, nodes: Optional[List[str]]=None) -> None:
        self.edges = [] if edges is None else edges
        self.nodes = [] if nodes is None else nodes
        self.save()

    @classmethod
    def load(cls) -> ConceptMap:
        if "conceptmap" in st.session_state:
            return st.session_state["conceptmap"]
        return cls()

    def save(self) -> None:
        st.session_state["conceptmap"] = self

    def is_empty(self) -> bool:
        return len(self.edges) == 0

