from langgraph.graph import StateGraph, START, END

from .stage4_state import Stage4State
from .stage4_nodes import (
    initialize_node,
    ensure_prediction_node,
    comparison_node,
    report_node,
    history_node,
    intent_node,
    escalation_node,
    answer_node,
    finalize_node,
)


def build_stage4_graph():
    builder = StateGraph(Stage4State)

    builder.add_node("initialize", initialize_node)
    builder.add_node("ensure_prediction", ensure_prediction_node)
    builder.add_node("comparison", comparison_node)
    builder.add_node("report", report_node)
    builder.add_node("history", history_node)
    builder.add_node("intent", intent_node)
    builder.add_node("escalation", escalation_node)
    builder.add_node("answer", answer_node)
    builder.add_node("finalize", finalize_node)

    builder.add_edge(START, "initialize")
    builder.add_edge("initialize", "ensure_prediction")
    builder.add_edge("ensure_prediction", "comparison")
    builder.add_edge("comparison", "report")
    builder.add_edge("report", "history")
    builder.add_edge("history", "intent")
    builder.add_edge("intent", "escalation")
    builder.add_edge("escalation", "answer")
    builder.add_edge("answer", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile()


stage4_graph = build_stage4_graph()