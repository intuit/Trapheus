from dataclasses import dataclass
from typing import Literal
from textwrap import dedent

@dataclass
class Prompt:

    content: str
    role: Literal["user", "system" ,"assistant"]

    def __post_init__(self):
        self.content = dedent(self.content).strip()

dialogue = [
    Prompt (
        """
            You are a useful and trained concept graph agent in Trapheus which uses artificial intelligence and 
            machine learning and can generate relationships among multi dimensional concepts.
        """, role="system"),
    Prompt (
        """
        You can generate a graph of concepts given a text search asking about an entity as input.
        
        1. add(node1, node2) - add an edge between node1 and node2
        2. delete(node1, node2) - delete an edge between node1 and node2
        3. delete(node1) - deletes every edge connected to node1
        
        Its an undirected graph that is generated hence the order of nodes does not matter and so does duplicates. 
        Also its a sparse graph which means it has a lot more nodes and a lot less number of edges. If edges will be more 
        then it will make it difficult to read and comprehend a graph. The answer should only have actions that can be 
        perfomed and nothing else. You have to generate a graph even if instructions are not very clear or even 
        its a single word that is provided as input. You need to generate a graph of multiple nodes and edges which
        makes sense given the input in the given context. Think step by step and evaluate the pros and cons before 
        giving an answer so that answer is the best possible one for a given input text.
        
        This is my first text input: Give me a concept graph of Quickbooks Online.
        """, role="user"),
    Prompt ("""
        add("Quickbooks Online", "Invoicing")
        add("Quickbooks Online", "Financial Management")
        add("Quickbooks Online", "Payroll Management")
        add("Quickbooks Online", "Accounting")
        add("Quickbooks Online", "Reporting")
        add("Quickbooks Online", "Bank Integration")
        add("Quickbooks Online", "Tax Management")
        add("Quickbooks Online", "Mobile App")
        add("Quickbooks Online", "Expense Tracking")
        add("Quickbooks Online", "Cloud based")
        add("Quickbooks Online", "Small Business")
        add("Quickbooks Online", "Invoice Approvals")
        add("Quickbooks Online", "Workflows")
        """, role="assistant"),

    Prompt ("""
    Remove Tax Management
    """, role="user"),

    Prompt ("""
    delete("Tax Management")
    """, role="assistant")
]
