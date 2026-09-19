import jsonschema

class KnowledgeBaseValidator:
    """
    Validates knowledge base JSON files against a schema.
    """

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "course": {"type": "string"},
            "category": {"type": "string"},
            "topic": {"type": "string"},
            "subtopic": {"type": "string"},
            "question": {"type": "string"},
            "answer": {"type": "string"},
            "course_context": {"type": "object"},
            "key_concepts": {"type": "array"},
            "workflow": {"type": "array"},
            "devops_application": {"type": "string"},
            "official_evidence": {"type": "array"},
            "related_topics": {"type": "array"}
        },
        "required": ["id", "course", "category", "topic", "question", "answer"]
    }

    def validate_entry(self, entry: dict) -> bool:
        """Validate a single knowledge base entry."""
        try:
            jsonschema.validate(instance=entry, schema=self.schema)
            return True
        except jsonschema.ValidationError as e:
            print(f"Validation error in entry {entry.get('id', 'unknown')}: {e.message}")
            return False

    def validate_knowledge(self, knowledge: dict) -> None:
        """Validate all entries in the merged knowledge base."""
        for domain, entries in knowledge.items():
            if isinstance(entries, list):
                for entry in entries:
                    self.validate_entry(entry)
            elif isinstance(entries, dict):
                self.validate_entry(entries)
