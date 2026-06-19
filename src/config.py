import os
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

DATA_DIR = os.getenv("DATA_DIR", "data/sample_cases")