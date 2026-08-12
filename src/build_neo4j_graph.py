from typing import Any, Dict, List

from neo4j import GraphDatabase

from .config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER
from .load_cases import load_cases
from .regex_ner_articles import extract_articles
from .regex_ner_persons import extract_persons


class Neo4jCaseGraph:
    def __init__(self):
        if not NEO4J_URI or not NEO4J_PASSWORD:
            raise RuntimeError(
                "Neo4j is not configured. "
                "Set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD in .env."
            )

        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
        )
        self.driver.verify_connectivity()

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

        articles = extract_articles_fn(text)
        for article in articles:
            for number in article.get("article_numbers", []):
                tx.run(
                    """
                    MERGE (a:Article {number: $number})
                    MERGE (c:Case {id: $case_id})
                    MERGE (c)-[:INVOLVES_ARTICLE]->(a)
                    """,
                    number=number,
                    case_id=case_id,
                )

        persons = extract_persons_fn(text)
        for person in persons:
            raw_name = person["text"]
            normalized_name = person.get("normalized") or raw_name

            tx.run(
                """
                MERGE (p:Person {normalized_name: $normalized_name})
                ON CREATE SET p.name = $raw_name
                MERGE (c:Case {id: $case_id})
                MERGE (c)-[:ACCUSED_IN]->(p)
                """,
                normalized_name=normalized_name,
                raw_name=raw_name,
                case_id=case_id,
            )


def main():
    cases = load_cases()

    if not cases:
        raise RuntimeError("No case files found in data/sample_cases.")

    graph_db = Neo4jCaseGraph()
    try:
        graph_db.create_case_graph(
            cases,
            extract_articles,
            extract_persons,
        )
        print(f"Neo4j graph created successfully: {len(cases)} cases loaded.")
    finally:
        graph_db.close()


if __name__ == "__main__":
    main()
