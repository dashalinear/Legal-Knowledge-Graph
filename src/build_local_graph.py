from typing import Dict, Any, List

import networkx as nx


def build_local_case_graph(
    case: Dict[str, Any],
    articles: List[Dict],
    persons: List[Dict],
) -> nx.DiGraph:
    """
    Build a local directed graph for a single case.

    Nodes: Case, Article, Person
    Edges:
      - Case -> Article (INVOLVES_ARTICLE)
      - Case -> Person (ACCUSED_IN)
    """
    G = nx.DiGraph()

    case_id = case.get("case_id", "UNKNOWN_CASE")
    G.add_node(case_id, label="Case", type="Case")

    for art in articles:
        for num in art.get("article_numbers", []):
            article_node = f"UK_{num}"
            if not G.has_node(article_node):
                G.add_node(article_node, label=f"Article {num}", type="Article")
            G.add_edge(case_id, article_node, type="INVOLVES_ARTICLE")

    for idx, person in enumerate(persons):
        person_node = f"{case_id}_P{idx}"
        G.add_node(person_node, label=person["text"], type="Person")
        G.add_edge(case_id, person_node, type="ACCUSED_IN")

    return G