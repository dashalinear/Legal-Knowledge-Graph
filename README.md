# LegalGraph-RU: Reproducible Pipeline for a Russian Legal Knowledge Graph

LegalGraph-RU is a minimal, reproducible implementation of a pipeline for building a knowledge graph from Russian criminal court decisions. The repository packages a compact end-to-end example around synthetic case files, rule-based named entity recognition, local graph construction with NetworkX, optional graph population in Neo4j, and an interactive Streamlit demo.[1][2]

The goal of this version of the README is reproducibility. Every step below is written so that another researcher can clone the repository, install dependencies, run the pipeline locally, and understand which files correspond to each stage of the workflow.[3][4]

## What the repository contains

This repository is intentionally small. It provides a demonstration version of the broader research workflow rather than the full private research environment. The included components are sufficient to reproduce the public demo pipeline from input JSON cases to extracted entities and graph outputs.[1][5]

### Core capabilities

- Load synthetic Russian criminal case documents from JSON files.[1]
- Extract article references from the Russian Criminal Code with deterministic regex-based rules.[1]
- Extract person mentions with a simple regex fallback recognizer.[1]
- Build a local case graph with NetworkX.[1]
- Populate a small global graph in Neo4j using cases, persons, and articles.[1]
- Inspect the results through a Streamlit interface.[1]

## Repository structure

```text
Legal-Knowledge-Graph/
├── README.md
├── LICENSE
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── load_cases.py
│   ├── regex_ner_articles.py
│   ├── regex_ner_persons.py
│   ├── build_local_graph.py
│   ├── build_neo4j_graph.py
│   ├── evaluation.py
│   └── demo_streamlit.py
├── data/
│   └── sample_cases/
│       ├── case_0001.json
│       └── case_0002.json
├── notebooks/
│   ├── 01_exploration.ipynb
│   └── 02_tsne_embeddings.ipynb
└── output/
```

### File roles

| Path | Purpose |
|------|---------|
| `src/load_cases.py` | Reads JSON case files from the configured data directory.[1] |
| `src/regex_ner_articles.py` | Extracts article references such as Criminal Code citations using regex rules.[1] |
| `src/regex_ner_persons.py` | Extracts person mentions using a lightweight fallback recognizer.[1] |
| `src/build_local_graph.py` | Creates a local per-case graph in NetworkX.[1] |
| `src/build_neo4j_graph.py` | Pushes entities and relations into Neo4j as a small global graph.[1] |
| `src/evaluation.py` | Computes basic precision, recall, and F1 metrics for extraction results.[1] |
| `src/demo_streamlit.py` | Launches the interactive demo for browsing cases and their graphs.[1] |
| `data/sample_cases/` | Synthetic example cases for reproducible local testing.[1] |
| `notebooks/` | Optional exploratory notebooks and visualization experiments.[1] |

## Reproducibility scope

This repository reproduces the public demonstration pipeline, not necessarily every private experiment used during research. The sample data is synthetic and exists so that the repository can be run safely and consistently without redistributing sensitive legal texts.[1][5]

A user should be able to reproduce the following outputs from the public repository:

- article extraction on sample documents;[1]
- person extraction on sample documents;[1]
- local case graph construction;[1]
- optional Neo4j population for a small global graph;[1]
- interactive browsing through Streamlit.[1]

## Environment setup

The project has been described as tested with Python 3.11 to 3.13, and Neo4j integration was described for Neo4j 5.x.[1]

### 1. Clone the repository

```bash
git clone https://github.com/dashalinear/Legal-Knowledge-Graph.git
cd Legal-Knowledge-Graph
```

### 2. Create a virtual environment

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify installation

A quick import check helps confirm that the environment is ready:

```bash
python -c "import networkx, streamlit; print('Environment OK')"
```

If this command runs without import errors, the minimal environment is likely configured correctly for the local demo pipeline.

## Data format

The demo data lives in `data/sample_cases/` and contains synthetic JSON files that mimic the structure of real criminal case documents.[1]

A case file is expected to contain fields similar to the following:

```json
{
  "case_id": "case_0001",
  "case_number": "1-123/2024",
  "court": "Example District Court",
  "text": "Подсудимый признан виновным по ст. 228 ч. 2 УК РФ..."
}
```

The exact field set may vary, but the pipeline assumes that each file contains enough metadata to identify the case and a `text` field for extraction.

## Running the pipeline

## Local Streamlit demo

This is the easiest way to reproduce the complete public demonstration.

```bash
streamlit run src/demo_streamlit.py
```

Expected workflow inside the app:

- sample JSON cases are loaded from `data/sample_cases/`;[1]
- article references are extracted with regex-based rules;[1]
- person mentions are extracted with a simple fallback recognizer;[1]
- a local directed graph is built for the selected case;[1]
- the graph is visualized in the Streamlit interface.[1]

Streamlit usually prints a local URL such as `http://localhost:8501`. Open that address in a browser and choose one of the sample cases from the interface.[1]

## Local graph construction from code

If the project exposes `build_local_graph.py` as a directly runnable module or script in your version of the repository, use the documented command in the repository. If not, the Streamlit app is the primary supported public entry point for reproducing local graphs from the sample cases.[1]

## Neo4j graph construction

Neo4j is optional. It is only needed if the goal is to reproduce the small global graph database version rather than the local in-memory graph demo.[1]

### 1. Create a `.env` file in the project root

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
DATA_DIR=data/sample_cases
```

### 2. Start Neo4j

Use Neo4j Desktop, Docker, or a local Neo4j server, and make sure the credentials in `.env` match the running instance.

### 3. Build the Neo4j graph

```bash
python -m src.build_neo4j_graph
```

According to the repository description, this step should create case nodes, article nodes, person nodes, and relations between them.[1]

### 4. Inspect the graph

In Neo4j Browser, a simple query is:

```cypher
MATCH (c:Case)-[r:INVOLVES_ARTICLE]->(a:Article)
RETURN c, r, a
LIMIT 50;
```

This query helps verify that cases and article citations were successfully inserted, as described in the repository overview.[1]

## Evaluation

The repository includes a minimal evaluation utility for article extraction.[1]

Example usage:

```python
from src.evaluation import compute_f1
from src.regex_ner_articles import extract_articles

text = "Подсудимый признан виновным по ст. 228 ч. 2 УК РФ."
gold = [
    {
        "text": "ст. 228 ч. 2",
        "start": 30,
        "end": 43,
        "article_numbers": ["228", "2"],
    }
]
pred = extract_articles(text)

precision, recall, f1 = compute_f1(gold, pred)
print(precision, recall, f1)
```

This toy example demonstrates the evaluation protocol described in the repository: comparison of spans and article numbers with precision, recall, and F1 reporting.[1]

## Recommended reproduction checklist

To fully reproduce the public code artifact, follow this order:

1. Clone the repository.
2. Create a clean virtual environment.
3. Install `requirements.txt`.
4. Confirm that the sample case files are present in `data/sample_cases/`.
5. Launch `streamlit run src/demo_streamlit.py`.
6. Verify that sample cases load and the graph renders.
7. Optionally configure Neo4j through `.env`.
8. Run `python -m src.build_neo4j_graph`.
9. Run the evaluation example to confirm the extraction utilities behave as documented.

If all steps succeed, the repository has been reproduced at the level of its public demo workflow.[1][4]

## How this repository maps to the paper

This repository should be treated as an executable appendix to the paper rather than as a complete archive of every experimental artifact. Its strongest reproducibility value is that it exposes the core logic of the pipeline end-to-end in a compact and inspectable form.[3][4]

Suggested mapping for the paper:

| Paper component | Repository component |
|----------------|----------------------|
| Sample legal corpus | `data/sample_cases/` |
| Rule-based legal entity extraction | `src/regex_ner_articles.py`, `src/regex_ner_persons.py` |
| Local graph construction | `src/build_local_graph.py` |
| Graph database population | `src/build_neo4j_graph.py` |
| Demo and qualitative inspection | `src/demo_streamlit.py` |
| Basic extraction evaluation | `src/evaluation.py` |

If the paper contains figures or tables generated by additional private notebooks or scripts, those should be added explicitly to the repository in a future update for stronger artifact completeness.

## Troubleshooting

### Streamlit does not start

- Make sure the virtual environment is activated.
- Reinstall dependencies with `pip install -r requirements.txt`.
- Check whether `streamlit` is available with `python -m streamlit --version`.

### Neo4j connection fails

- Verify that Neo4j is running.
- Check `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` in `.env`.
- Confirm that port `7687` is accessible.

### No cases appear in the app

- Check that `data/sample_cases/` contains JSON files.
- Confirm that `DATA_DIR` in the configuration points to the correct directory.
- Validate JSON syntax in the sample case files.

### Extraction results look empty

- Confirm that the sample texts actually contain article references and person mentions in forms covered by the regex rules.
- Keep in mind that the recognizers are intentionally simple and deterministic, so they will not cover all natural language variation.[1]

## Limitations

The current implementation is tailored to Russian criminal court decisions and especially to citation patterns of the Russian Criminal Code.[1] The regex-based approach is intentionally lightweight and will not generalize automatically to other legal systems or noisier text domains without rule changes.[1]

The sample data is synthetic. Any extension to real legal texts should account for privacy, legal compliance, ethical constraints, and the possible harms of aggregating sensitive legal information into structured graphs.[1][5]

## Recommended additions for a stronger artifact

For article submission or advisor review, the repository would become more complete if it also included:

- a `paper/` folder with the LaTeX source, bibliography, and figures for the paper;
- a pinned release or tag corresponding to the submitted article version;
- a short `REPRODUCIBILITY.md` file listing exact commands used for each table or figure;
- example output files or screenshots for quick verification;
- a note linking the repository version to the paper title and submission date.[4]

## Citation and usage

This repository is presented as an open artifact for research and teaching on legal NLP and legal knowledge graphs. The repository already states that a citation to the corresponding paper should be added once a preprint or final paper link is available.[1]

A practical citation block to add later could look like this:

```bibtex
@misc{legalgraphrudemo,
  title  = {LegalGraph-RU: Reproducible Pipeline for a Russian Legal Knowledge Graph},
  author = {Daria ...},
  year   = {2026},
  url    = {https://github.com/dashalinear/Legal-Knowledge-Graph}
}
```

## License

The repository is released under the MIT License, as already indicated in the current project files.[1]
