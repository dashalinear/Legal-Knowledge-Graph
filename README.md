# LegalGraph-RU: Reproducible Pipeline for a Russian Legal Knowledge Graph

LegalGraph-RU is a minimal, reproducible implementation of a pipeline for building a knowledge graph from Russian criminal court decisions. The repository packages a compact end-to-end example around synthetic case files, rule-based named entity recognition, local graph construction with NetworkX, optional graph population in Neo4j, and an interactive Streamlit demo.

The goal of this README is reproducibility. Every step below is written so that another researcher can clone the repository, install dependencies, run the pipeline locally, and understand which files correspond to each stage of the workflow, as well as where the paper's source files and figures live.

## What the repository contains

This repository is intentionally small. It provides a demonstration version of the broader research workflow rather than the full private research environment. The included components are sufficient to reproduce the public demo pipeline from input JSON cases to extracted entities and graph outputs, and it also bundles the LaTeX source of the corresponding paper.

### Core capabilities

- Load synthetic Russian criminal case documents from JSON files.
- Extract article references from the Russian Criminal Code with deterministic regex-based rules.
- Extract person mentions with a simple regex fallback recognizer.
- Build a local case graph with NetworkX.
- Populate a small global graph in Neo4j using cases, persons, and articles.
- Inspect the results through an interactive Streamlit interface built on `vis.js`.

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
├── lib/
│   ├── bindings/
│   │   └── utils.js
│   ├── tom-select/
│   │   ├── tom-select.complete.min.js
│   │   └── tom-select.css
│   └── vis-9.1.2/
│       ├── vis-network.css
│       └── vis-network.min.js
├── output/
│   └── local_graph.html
└── paper/
    ├── main.tex
    ├── references.bib
    └── figures/
        ├── demo_graph_roles_case_001.png
        └── embeddings_tsne.png
```

### File roles

| Path | Purpose |
|------|---------|
| `src/load_cases.py` | Reads JSON case files from the configured data directory. |
| `src/regex_ner_articles.py` | Extracts article references such as Criminal Code citations using regex rules. |
| `src/regex_ner_persons.py` | Extracts person mentions using a lightweight fallback recognizer. |
| `src/build_local_graph.py` | Creates a local per-case graph in NetworkX. |
| `src/build_neo4j_graph.py` | Pushes entities and relations into Neo4j as a small global graph. |
| `src/evaluation.py` | Computes basic precision, recall, and F1 metrics for extraction results. |
| `src/demo_streamlit.py` | Launches the interactive demo for browsing cases and their graphs. |
| `data/sample_cases/` | Synthetic example cases for reproducible local testing. |
| `lib/` | Frontend assets (`vis.js` network rendering, `tom-select`, DOM binding helpers) used by the interactive graph visualization. |
| `output/local_graph.html` | Example pre-rendered local case graph, useful as a quick sanity check without running the pipeline. |
| `paper/main.tex` | LaTeX source of the paper. |
| `paper/references.bib` | Bibliography for the paper. |
| `paper/figures/` | Figures used in the paper (local case graph visualization, t-SNE embedding plot). |

## Reproducibility scope

This repository reproduces the public demonstration pipeline behind the paper, not necessarily every private experiment used during research. The sample data is synthetic and exists so that the repository can be run safely and consistently without redistributing sensitive legal texts.

A user should be able to reproduce the following outputs from the public repository:

- article extraction on sample documents;
- person extraction on sample documents;
- local case graph construction, matching the example in `output/local_graph.html`;
- optional Neo4j population for a small global graph;
- interactive browsing through Streamlit;
- the paper itself, by compiling the sources in `paper/`.

## Environment setup

The project has been tested with Python 3.11 to 3.13. Neo4j integration was tested with Neo4j 5.x.

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

```bash
python -c "import networkx, streamlit; print('Environment OK')"
```

If this command runs without import errors, the environment is configured correctly for the local demo pipeline.

## Data format

The demo data lives in `data/sample_cases/` and contains synthetic JSON files that mimic the structure of real criminal case documents.

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

### Local Streamlit demo

This is the easiest way to reproduce the complete public demonstration.

```bash
streamlit run src/demo_streamlit.py
```

Expected workflow inside the app:

- sample JSON cases are loaded from `data/sample_cases/`;
- article references are extracted with regex-based rules;
- person mentions are extracted with a simple fallback recognizer;
- a local directed graph is built for the selected case using `src/build_local_graph.py`;
- the graph is visualized in the browser using the `vis.js` assets in `lib/vis-9.1.2/`.

Streamlit prints a local URL such as `http://localhost:8501`. Open that address in a browser and select one of the sample cases from the dropdown.

### Viewing a pre-rendered graph without running the pipeline

For a quick sanity check, open `output/local_graph.html` directly in a browser. It shows an example local case graph, similar to what the Streamlit app produces at runtime.

### Neo4j graph construction

Neo4j is optional. It is only needed to reproduce the small global graph database version rather than the local in-memory graph demo.

#### 1. Create a `.env` file in the project root

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
DATA_DIR=data/sample_cases
```

#### 2. Start Neo4j

Use Neo4j Desktop, Docker, or a local Neo4j server, and make sure the credentials in `.env` match the running instance.

#### 3. Build the Neo4j graph

```bash
python -m src.build_neo4j_graph
```

This step creates case nodes, article nodes, person nodes, and connects them via `INVOLVES_ARTICLE` and `ACCUSED_IN` relationships.

#### 4. Inspect the graph

In Neo4j Browser:

```cypher
MATCH (c:Case)-[r:INVOLVES_ARTICLE]->(a:Article)
RETURN c, r, a
LIMIT 50;
```

This query verifies that cases and article citations were successfully inserted.

## Evaluation

The repository includes a minimal evaluation utility for article extraction.

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

This toy example illustrates the evaluation protocol used in the underlying research: matching spans and article numbers, and reporting precision, recall, and F1 for article extraction on a small annotated set.

## Building the paper

The `paper/` folder contains the full LaTeX source used to produce the associated paper.

```text
paper/
├── main.tex
├── references.bib
└── figures/
    ├── demo_graph_roles_case_001.png
    └── embeddings_tsne.png
```

To compile locally with a standard TeX distribution (TeX Live, MiKTeX, or Overleaf):

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Running `pdflatex` twice more after `bibtex` ensures citations and cross-references resolve correctly. Alternatively, upload the `paper/` folder as a project on Overleaf and compile there.

## How the repository maps to the paper

| Paper component | Repository component |
|------------------|-----------------------|
| Sample legal corpus | `data/sample_cases/` |
| Rule-based legal entity extraction | `src/regex_ner_articles.py`, `src/regex_ner_persons.py` |
| Local graph construction | `src/build_local_graph.py`, visualized via `lib/vis-9.1.2/` |
| Graph database population | `src/build_neo4j_graph.py` |
| Demo and qualitative inspection | `src/demo_streamlit.py`, `output/local_graph.html` |
| Basic extraction evaluation | `src/evaluation.py` |
| Local case graph figure | `paper/figures/demo_graph_roles_case_001.png` |
| Embedding visualization figure | `paper/figures/embeddings_tsne.png` |
| Paper text and bibliography | `paper/main.tex`, `paper/references.bib` |

## Recommended reproduction checklist

1. Clone the repository.
2. Create a clean virtual environment.
3. Install `requirements.txt`.
4. Confirm that the sample case files are present in `data/sample_cases/`.
5. Launch `streamlit run src/demo_streamlit.py`.
6. Verify that sample cases load and the graph renders, or open `output/local_graph.html` directly.
7. Optionally configure Neo4j through `.env` and run `python -m src.build_neo4j_graph`.
8. Run the evaluation example to confirm the extraction utilities behave as documented.
9. Compile `paper/main.tex` to confirm the paper builds and figures render.

If all steps succeed, the repository has been reproduced at the level of its public demo workflow and the paper artifact.

## Troubleshooting

### Streamlit does not start

- Make sure the virtual environment is activated.
- Reinstall dependencies with `pip install -r requirements.txt`.
- Check whether Streamlit is available with `python -m streamlit --version`.

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
- Keep in mind that the recognizers are intentionally simple and deterministic, so they will not cover all natural language variation.

### The paper does not compile

- Confirm a LaTeX distribution is installed (TeX Live or MiKTeX), or use Overleaf instead of a local install.
- Make sure `references.bib` is in the same folder as `main.tex`.
- Run `pdflatex` and `bibtex` in the exact order shown above; skipping a pass is the most common cause of missing citations.

## Limitations

The current implementation is tailored to Russian criminal court decisions and, in particular, to citation patterns of the Russian Criminal Code. The regex-based NER patterns are designed for standardized legal references and will not automatically generalize to other jurisdictions or domains.

Sample data is synthetic; any real-world deployment must consider privacy, data protection, and the potential harms of aggregating legal information into a graph.

## Research context and citation

This repository was created as an open artifact for a research project on Natural Legal Language Processing (NLLP) and legal knowledge graphs. The `paper/` folder contains the exact LaTeX source and bibliography used to produce the associated paper. If you use this code, the paper, or the underlying ideas in your research, please cite the paper once a preprint or final version link is available.

```bibtex
@misc{legalgraphrudemo,
  title  = {LegalGraph-RU: A Reproducible Pipeline for a Russian Legal Knowledge Graph},
  author = {Daria ...},
  year   = {2026},
  url    = {https://github.com/dashalinear/Legal-Knowledge-Graph}
}
```

For questions, feel free to open an issue or discussion on GitHub.

## License

This project is released under the MIT License (see `LICENSE` for details).
