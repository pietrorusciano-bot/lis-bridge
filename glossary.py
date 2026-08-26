import json
import os


class Glossary:
    def __init__(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "data", "glossary.json")
        with open(path, encoding="utf-8") as f:
            self.concepts = json.load(f)["concepts"]

    def match(self, text):
        lower = text.lower()
        found = []
        for concept in self.concepts:
            for kw in concept["keywords"]:
                if kw in lower:
                    found.append(concept)
                    break
        return found
