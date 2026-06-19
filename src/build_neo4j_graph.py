# build_neo4j_graph.py
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from load_cases import load_cases
from regex_ner_articles import extract_articles
from regex_ner_persons import extract_persons


class Neo4jCaseGraph:
    """Wrapper around the Neo4j driver for creating a simple case graph."""

    def __init__(self) -> None:
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
        )

    def close(self) -> None:
        self.driver.close()

    def create_case_graph(
        self,
        cases: List[Dict[str, Any]],
        extract_articles_fn: Callable[[str], List[Dict]],
        extract_persons_fn: Callable[[str], List[Dict]],
    ) -> None:
        """Populate Neo4j with Case, Article, Person nodes and relationships."""
        with self.driver.session() as session:
            for case in cases:
                session.execute_write(
                    self._create_case_tx,
                    case,
                    extract_articles_fn,
                    extract_persons_fn,
                )

    @staticmethod
    def _create_case_tx(tx, case, extract_articles_fn, extract_persons_fn) -> None:
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

        persons = extract_persons_fn(text)
        for person in persons:
            tx.run(
                """
                MERGE (p:Person {name: $name})
                MERGE (c:Case {id: $case_id})
                MERGE (c)-[:ACCUSED_IN]->(p)
                """,
                name=person["text"],
                case_id=case_id,
            )


if __name__ == "__main__":
    # Minimal CLI entrypoint: build graph for sample cases.
    from .load_cases import load_cases
    from .regex_ner_articles import extract_articles
    from .regex_ner_persons import extract_persons

    cases = load_cases()
    graph = Neo4jCaseGraph()
    try:
        graph.create_case_graph(cases, extract_articles, extract_persons)
    finally:
        graph.close()