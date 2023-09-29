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

    def add_relationships(self, output: str, replace: bool=True):
        add_delete_pattern = r'(add|delete)\("([^()"]+)",\s*"([^()"]+)"\)'
        delete_pattern = r'(delete)\("([^()"]+)"\)'

        actions = re.findall(add_delete_pattern, output) + re.findall(delete_pattern, output)
        new_relationships = []
        remove_relationships = set()
        remove_concept = set()
        for action in actions:
            operation, *args = action
            add = operation == "add"
            if add or (operation == "delete" and len(args)==2):
                a, b = args
                if a == b:
                    continue
                if add:
                    new_relationships.append((a, b))
                else:
                    remove_relationships.add(frozenset([a, b]))
            else:
                remove_concept.add(args[0])
        if replace:
            edges = new_relationships
        else:
            edges = self.edges + new_relationships
        concepts_added = set()
        for edge in edges:
            concepts = frozenset(edge)
            if concepts in concepts_added or concepts & remove_concept or concepts in remove_relationships:
                continue
            concepts_added.add(concepts)
        self.edges = list([tuple(concept) for concept in concepts_added])
        self.nodes = list(set([node for edge in self.edges for node in edges]))
        self.save()