from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required variable in .env: {name}")
    return value


def load_source_loader(source_file: Path):
    sys.path.insert(0, str(source_file.parent))

    spec = importlib.util.spec_from_file_location(
        "court_graph_v2_source",
        source_file,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load source loader: {source_file}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    source_dir = Path(require_env("SOURCE_PIPELINE_DIR"))
    data_dir = Path(require_env("FULL_DATA_DIR"))
    source_loader = source_dir / "court_graph_v2.py"

    if not source_loader.exists():
        raise FileNotFoundError(f"Source loader not found: {source_loader}")

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    uri = require_env("NEO4J_URI")
    if not uri.startswith("neo4j+s://"):
        raise RuntimeError(
            "Safety stop: NEO4J_URI must be an Aura URI beginning with neo4j+s://"
        )

    legacy = load_source_loader(source_loader)

    legacy.DATA_DIR = data_dir
    legacy.JSON_FILES = ["5_9342e8f2_docs.json"]
    legacy.MAX_CASES_PER_FILE = int(os.getenv("AURA_MAX_CASES_PER_FILE", "10"))
    legacy.BATCH_SIZE = int(os.getenv("AURA_BATCH_SIZE", "10"))

    legacy.CLEAR_DB = False
    legacy.URI = uri
    legacy.USER = require_env("NEO4J_USER")
    legacy.PASSWORD = require_env("NEO4J_PASSWORD")
    legacy.DB_NAME = os.getenv("NEO4J_DATABASE", "neo4j")

    print("Aura subset import configuration")
    print(f"Source loader: {source_loader}")
    print(f"Source data: {data_dir}")
    print(f"Files: {len(legacy.JSON_FILES)}")
    print(f"Max cases per file: {legacy.MAX_CASES_PER_FILE}")
    print(f"Batch size: {legacy.BATCH_SIZE}")
    print("CLEAR_DB: False")
    print("Target: AuraDB")

    legacy.main()


if __name__ == "__main__":
    main()