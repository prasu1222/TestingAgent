"""Cost agent implemented using LangGraph."""
from __future__ import annotations

import re
from typing import TypedDict

from langgraph.graph import StateGraph, END

from tools.cost_tools import latest_cost, cost_analysis


class CostState(TypedDict, total=False):
    question: str
    part_number: str
    route: str
    answer: str


def extract_part_number(text: str) -> str:
    """Extract a simple part number from the text."""
    match = re.search(r"\b\d+\b", text)
    return match.group(0) if match else "unknown"


class CostAgent:
    """Agent that answers cost related questions using tools."""

    def __init__(self) -> None:
        graph = StateGraph(CostState)

        graph.add_node("route", self.route)
        graph.add_node("latest_cost", self.call_latest_cost)
        graph.add_node("cost_analysis", self.call_cost_analysis)

        graph.set_entry_point("route")
        graph.add_conditional_edges("route", self.select_tool)
        graph.add_edge("latest_cost", END)
        graph.add_edge("cost_analysis", END)

        self.app = graph.compile()

    def route(self, state: CostState) -> CostState:
        question = state["question"]
        part_number = extract_part_number(question)
        state["part_number"] = part_number
        if "analysis" in question.lower():
            state["route"] = "cost_analysis"
        else:
            state["route"] = "latest_cost"
        return state

    def select_tool(self, state: CostState) -> str:
        return state.get("route", "latest_cost")

    def call_latest_cost(self, state: CostState) -> CostState:
        part = state.get("part_number", "unknown")
        state["answer"] = latest_cost(part)
        return state

    def call_cost_analysis(self, state: CostState) -> CostState:
        part = state.get("part_number", "unknown")
        state["answer"] = cost_analysis(part)
        return state

    def run(self, question: str) -> str:
        result = self.app.invoke({"question": question})
        return result.get("answer", "No answer")
