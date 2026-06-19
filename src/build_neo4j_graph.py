# src/build_neo4j_graph.py
from typing import List, Dict, Any

from neo4j import GraphDatabase

from .config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class Neo4jCaseGraph:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
        )

    def close(self):
        self.driver.close()

    def create_case_graph(
        self,
        cases: List[Dict[str, Any]],
        extract_articles_fn,
        extract_persons_fn,
    ):
        with self.driver.session() as session:
            for case in cases:
                session.execute_write(
                    self._create_case_tx,
                    case,
                    extract_articles_fn,
                    extract_persons_fn,
                )

    @staticmethod
    def _create_case_tx(tx, case, extract_articles_fn, extract_persons_fn):
        case_id = case.get("case_id")
        text = case.get("text", "")

        # Узел дела
        tx.run(
            """
            MERGE (c:Case {id: $case_id})
            SET c.case_number = $case_number,
                c.court = $court
            """,
            case_id=case_id,
            case_number=case.get("case_number"),
            court=case.get("court"),
        )

        # Статьи УК
        articles = extract_articles_fn(text)
        for art in articles:
            for num in art.get("article_numbers", []):
                tx.run(
                    """
                    MERGE (a:Article {number: $num})
                    MERGE (c:Case {id: $case_id})
                    MERGE (c)-[:INVOLVES_ARTICLE]->(a)
                    """,
                    num=num,
                    case_id=case_id,
                )

        # Персоны
        persons = extract_persons_fn(text)
        for person in persons:
            raw_name = person["text"]
            norm_name = person.get("normalized") or raw_name

            tx.run(
                """
                MERGE (p:Person {normalized_name: $norm_name})
                ON CREATE SET p.name = $raw_name
                ON MATCH SET p.name = p.name
                MERGE (c:Case {id: $case_id})
                MERGE (c)-[:ACCUSED_IN]->(p)
                """,
                norm_name=norm_name,
                raw_name=raw_name,
                case_id=case_id,
            )
