"""Cost agent implemented using LangGraph."""
from __future__ import annotations

from typing import TypedDict

from langgraph.graph import StateGraph, END

from tools.cost_tools import latest_cost, cost_analysis


class CostState(TypedDict, total=False):
    question: str
    part_number: str
    route: str
    answer: str


def extract_part_number(text: str) -> str:
    """Extract a simple part number from the text using an LLM.

    This function calls OpenAI's API to identify a part number within the
    provided text.  If the API is unavailable or fails for any reason, the
    function returns ``"unknown"``.
    """
    try:
        from openai import OpenAI

        client = OpenAI()
        prompt = (
            "Extract the part number from the following text. Respond with only "
            "the part number. If no part number is present, respond with 'unknown'.\n\n"
            f"{text}"
        )
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            max_output_tokens=10,
        )
        content = response.output[0].content[0].text.strip()
        return content if content else "unknown"
    except Exception:
        return "unknown"


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
