from __future__ import annotations

from typing import Any, Dict, List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from ml.stage5.stage5_core import (
    get_upload_meta,
    ensure_prediction,
    get_report,
    get_comparison,
    get_recent_history,
    assess_signal_quality,
    compute_confidence,
    analyze_trend,
    build_explainability,
    assess_risk,
    build_recommendation,
    build_answer,
)


class Stage5State(TypedDict, total=False):
    mode: str
    upload_id: int
    question: str

    upload_meta: Dict[str, Any]
    prediction: Dict[str, Any]
    report: Dict[str, Any]
    comparison: Dict[str, Any]
    history: Dict[str, Any]

    signal_quality: Dict[str, Any]
    confidence: Dict[str, Any]
    trend: Dict[str, Any]
    explainability: Dict[str, Any]
    risk: Dict[str, Any]
    recommendation: Dict[str, Any]

    final_answer: str
    response_payload: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


def initialize_node(state: Stage5State) -> Dict[str, Any]:
    return {
        "upload_meta": get_upload_meta(state["upload_id"]),
        "errors": state.get("errors", []),
        "warnings": state.get("warnings", []),
    }


def prediction_node(state: Stage5State) -> Dict[str, Any]:
    return {"prediction": ensure_prediction(state["upload_id"])}


def report_node(state: Stage5State) -> Dict[str, Any]:
    return {"report": get_report(state["upload_id"])}


def comparison_node(state: Stage5State) -> Dict[str, Any]:
    return {"comparison": get_comparison(state["upload_id"])}


def history_node(state: Stage5State) -> Dict[str, Any]:
    return {"history": get_recent_history(state["upload_id"])}


def signal_quality_node(state: Stage5State) -> Dict[str, Any]:
    return {"signal_quality": assess_signal_quality(state.get("prediction", {}))}


def confidence_node(state: Stage5State) -> Dict[str, Any]:
    return {
        "confidence": compute_confidence(
            prediction=state.get("prediction", {}),
            signal_quality=state.get("signal_quality", {}),
        )
    }


def trend_node(state: Stage5State) -> Dict[str, Any]:
    return {"trend": analyze_trend(state.get("history", {}))}


def explainability_node(state: Stage5State) -> Dict[str, Any]:
    return {"explainability": build_explainability(state.get("prediction", {}))}


def risk_node(state: Stage5State) -> Dict[str, Any]:
    return {
        "risk": assess_risk(
            prediction=state.get("prediction", {}),
            comparison=state.get("comparison", {}),
            confidence=state.get("confidence", {}),
            trend=state.get("trend", {}),
        )
    }


def recommendation_node(state: Stage5State) -> Dict[str, Any]:
    return {
        "recommendation": build_recommendation(
            prediction=state.get("prediction", {}),
            signal_quality=state.get("signal_quality", {}),
            confidence=state.get("confidence", {}),
            trend=state.get("trend", {}),
            risk=state.get("risk", {}),
        )
    }


def answer_node(state: Stage5State) -> Dict[str, Any]:
    mode = state.get("mode", "analyze")

    if mode == "chat":
        answer = build_answer(
            question=state.get("question", ""),
            upload_meta=state.get("upload_meta", {}),
            prediction=state.get("prediction", {}),
            report=state.get("report", {}),
            comparison=state.get("comparison", {}),
            history=state.get("history", {}),
            signal_quality=state.get("signal_quality", {}),
            confidence=state.get("confidence", {}),
            trend=state.get("trend", {}),
            explainability=state.get("explainability", {}),
            risk=state.get("risk", {}),
            recommendation=state.get("recommendation", {}),
        )
    else:
        pred = state.get("prediction", {})
        risk = state.get("risk", {})
        conf = state.get("confidence", {})
        trend = state.get("trend", {})
        answer = (
            f"Stage 5 analysis complete for upload {state['upload_id']}. "
            f"Predicted label: {pred.get('predicted_label', 'Unknown')}, "
            f"probability: {float(pred.get('probability', 0.0)):.4f}, "
            f"confidence: {conf.get('confidence_band')}, "
            f"trend: {trend.get('direction')}, "
            f"risk: {risk.get('risk_level')}."
        )

    return {"final_answer": answer}


def finalize_node(state: Stage5State) -> Dict[str, Any]:
    payload = {
        "mode": state.get("mode"),
        "upload_id": state.get("upload_id"),
        "upload_meta": state.get("upload_meta", {}),
        "prediction": state.get("prediction", {}),
        "report": state.get("report", {}),
        "comparison": state.get("comparison", {}),
        "history": state.get("history", {}),
        "signal_quality": state.get("signal_quality", {}),
        "confidence": state.get("confidence", {}),
        "trend": state.get("trend", {}),
        "explainability": state.get("explainability", {}),
        "risk": state.get("risk", {}),
        "recommendation": state.get("recommendation", {}),
        "final_answer": state.get("final_answer", ""),
        "errors": state.get("errors", []),
        "warnings": state.get("warnings", []),
    }
    return {"response_payload": payload}

def build_stage5_graph():
    builder = StateGraph(Stage5State)

    builder.add_node("initialize_step", initialize_node)
    builder.add_node("prediction_step", prediction_node)
    builder.add_node("report_step", report_node)
    builder.add_node("comparison_step", comparison_node)
    builder.add_node("history_step", history_node)
    builder.add_node("signal_quality_step", signal_quality_node)
    builder.add_node("confidence_step", confidence_node)
    builder.add_node("trend_step", trend_node)
    builder.add_node("explainability_step", explainability_node)
    builder.add_node("risk_step", risk_node)
    builder.add_node("recommendation_step", recommendation_node)
    builder.add_node("answer_step", answer_node)
    builder.add_node("finalize_step", finalize_node)

    builder.add_edge(START, "initialize_step")
    builder.add_edge("initialize_step", "prediction_step")
    builder.add_edge("prediction_step", "report_step")
    builder.add_edge("report_step", "comparison_step")
    builder.add_edge("comparison_step", "history_step")
    builder.add_edge("history_step", "signal_quality_step")
    builder.add_edge("signal_quality_step", "confidence_step")
    builder.add_edge("confidence_step", "trend_step")
    builder.add_edge("trend_step", "explainability_step")
    builder.add_edge("explainability_step", "risk_step")
    builder.add_edge("risk_step", "recommendation_step")
    builder.add_edge("recommendation_step", "answer_step")
    builder.add_edge("answer_step", "finalize_step")
    builder.add_edge("finalize_step", END)

    return builder.compile()

stage5_graph = build_stage5_graph()