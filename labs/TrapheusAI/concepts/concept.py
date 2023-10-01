import re
import constants
import streamlit as streamlit
from typing import Optional, List, Tuple
from llm.prompts import Prompt, dialogue
from llm.model import ask_foundational_model
from streamlit_agraph import agraph, Node, Edge, Config


class Concept:

    def __init__(self, relationships: Optional[List[Tuple[str, str]]]=None, concepts: Optional[List[str]]=None) -> None:
        self.relationships = [] if relationships is None else relationships
        self.concepts = [] if concepts is None else concepts
        self.save()

    @classmethod
    def render(cls) -> Concept:
        if "concept" in streamlit.session_state:
            return streamlit.session_state["concept"]
        return cls()

    def save(self) -> None:
        streamlit.session_state["concept"] = self

    def is_empty(self) -> bool:
        return len(self.relationships) == 0

    def render_initial_concepts(self, query: str) -> None:
        discourse = dialogue + [
            Prompt(f"""
                Ignore previous graphs and restart. I want you to do the following.
                {query}
            """, role="user")
        ]
        output , self.conversation = ask_foundational_model(discourse)
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
        self.relationships = list([tuple(concept) for concept in concepts_added])
        self.concepts = list(set([node for edges in self.relationships for node in edges]))
        self.save()

    def delete_concept(self, concept) -> None:
        self.relationships = [e for e in self.relationships if concept not in frozenset(e)]
        self.concepts = list(set([n for e in self.relationships for n in e]))
        self.conversation.append(Prompt(
            f'delete("{concept}")',
            role="user"
        ))
        self.save()

    def drill_down_and_remove_concept(self, concept) -> None:
        streamlit.sidebar.subheader(concept)
        cols = streamlit.sidebar.columns(2)
        cols[0].button(
            label="Drill Down",
            type="primary",
            on_click=self.drill_down,
            key=f"drill_down_{concept}",
            kwargs={"selected_node": cols}
        )
        cols[1].button(
            label="Remove Concept",
            on_click=self.remove_concept,
            key=f"remove_{concept}",
            args=(concept,)
        )

    def render_concepts(self) -> None:
        selected_concept = streamlit.session_state.get("previous_selection")
        multiplier = constants.GRAPH_MULTIPLIER
        additive = constants.GRAPH_ADDITIVE
        concepts = [
                Node(
                    id=concept,
                    label=concept,
                    size=multiplier+additive*(concept==selected_concept),
                    color=constants.GRAPH_DEFAULT_COLOR if concept != selected_concept else constants.GRAPH_SELECTED_COLOR
                )
                for concept in self.concepts
            ]
        relaltionships = [Edge(source=a, target=b) for a, b in self.edges]
        dimensions = Config(width=constants.GRAPH_WIDTH,
                            height=constants.GRAPH_HEIGHT,
                            directed=False,
                            physics=True,
                            hierarchical=False,
                            )
        selected_concept = agraph(nodes=concepts,
                                  edges=relaltionships,
                                  config=dimensions)
        if selected_concept is not None:
            self.drill_down_and_remove_concept(selected_concept)
            return
        for concept in sorted(self.concepts):
            self.drill_down_and_remove_concept(concept)