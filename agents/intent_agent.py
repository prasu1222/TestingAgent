"""Simple intent classification agent."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class IntentAgent:
    """Classifies user questions to determine if they relate to cost."""

    def classify(self, question: str) -> str:
        """Classify the question intent.

        Args:
            question: The user question.

        Returns:
            str: "cost" if question relates to cost/price, otherwise "other".
        """
        lowered = question.lower()
        if "cost" in lowered or "price" in lowered:
            return "cost"
        return "other"
