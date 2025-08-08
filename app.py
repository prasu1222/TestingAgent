"""Streamlit entry point for the cost assistant."""
from __future__ import annotations

import streamlit as st

from agents.intent_agent import IntentAgent
from agents.cost_agent import CostAgent

intent_agent = IntentAgent()
cost_agent = CostAgent()


def main() -> None:
    st.title("Cost Assistant")
    question = st.text_input("Ask a question about cost or price:")
    if st.button("Submit") and question:
        intent = intent_agent.classify(question)
        if intent == "cost":
            answer = cost_agent.run(question)
            st.write(answer)
        else:
            st.write("I can only answer cost related questions.")


if __name__ == "__main__":
    main()
