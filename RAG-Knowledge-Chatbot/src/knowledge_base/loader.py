import json
import os
from pathlib import Path
from .validator import KnowledgeBaseValidator

class KnowledgeBaseLoader:
    """
    Loads and merges knowledge base JSON files (raw + indexes).
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.validator = KnowledgeBaseValidator()

    def load_file(self, filename: str) -> dict:
        """Load a single JSON file."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_index(self, index_file: str) -> list:
        """Load an index file and return its entries."""
        data = self.load_file(f"indexes/{index_file}")
        # Flatten index entries
        if isinstance(data, dict):
            return sum(data.values(), [])
        elif isinstance(data, list):
            return data
        return []

    def merge_all(self) -> dict:
        """
        Merge all modular JSON files into a unified dictionary.
        """
        knowledge = {}

        # Load raw knowledge base
        raw_kb = self.load_file("knowledge_base.json")
        knowledge["raw"] = raw_kb

        # Load indexes
        indexes = [
            "aws_index.json",
            "genai_index.json",
            "devops_index.json",
            "course_projects_index.json",
            "knowledge_index.json"
        ]

        for idx in indexes:
            try:
                entries = self.load_index(idx)
                knowledge[idx.replace(".json", "")] = entries
            except Exception as e:
                print(f"Warning: Could not load {idx} -> {e}")

        # Validate merged knowledge
        self.validator.validate_knowledge(knowledge)

        return knowledge
