from __future__ import annotations

from typing import Dict, Any

from .stage4_state import Stage4State
from .stage4_tools import (
    get_upload_meta,
    ensure_prediction,
    get_comparison_data,
    get_report_data,
    get_history_data,
    classify_question_intent,
    assess_escalation,
    build_grounded_answer,
)


def initialize_node(state: Stage4State) -> Dict[str, Any]:
    upload_id = state["upload_id"]

    return {
        "upload_meta": get_upload_meta(upload_id),
        "errors": state.get("errors", []),
        "warnings": state.get("warnings", []),
    }


def ensure_prediction_node(state: Stage4State) -> Dict[str, Any]:
    prediction = ensure_prediction(state["upload_id"])
    return {"prediction": prediction}


def comparison_node(state: Stage4State) -> Dict[str, Any]:
    comparison = get_comparison_data(state["upload_id"])
    return {"comparison": comparison}


def report_node(state: Stage4State) -> Dict[str, Any]:
    report = get_report_data(state["upload_id"])
    return {"report": report}


def history_node(state: Stage4State) -> Dict[str, Any]:
    history = get_history_data(state["upload_id"])
    return {"history": history}


def intent_node(state: Stage4State) -> Dict[str, Any]:
    question = state.get("question", "")
    intent = classify_question_intent(question)
    return {"intent": intent}


def escalation_node(state: Stage4State) -> Dict[str, Any]:
    escalation = assess_escalation(
        prediction=state.get("prediction", {}),
        comparison=state.get("comparison", {}),
    )
    return {"escalation": escalation}


def answer_node(state: Stage4State) -> Dict[str, Any]:
    mode = state.get("mode", "analyze")
    question = state.get("question", "").strip()

    if mode == "chat":
        final_answer = build_grounded_answer(
            question=question,
            intent=state.get("intent", "general"),
            prediction=state.get("prediction", {}),
            comparison=state.get("comparison", {}),
            report=state.get("report", {}),
            history=state.get("history", {}),
            escalation=state.get("escalation", {}),
        )
    else:
        pred = state.get("prediction", {})
        esc = state.get("escalation", {})
        final_answer = (
            f"Stage 4 analysis complete for upload {state['upload_id']}. "
            f"Predicted label: {pred.get('predicted_label', 'Unknown')}, "
            f"probability: {float(pred.get('probability', 0.0)):.4f}, "
            f"review flag: {esc.get('should_flag_for_review')}."
        )

    return {"final_answer": final_answer}


def finalize_node(state: Stage4State) -> Dict[str, Any]:
    response_payload = {
        "mode": state.get("mode"),
        "upload_id": state.get("upload_id"),
        "upload_meta": state.get("upload_meta", {}),
        "prediction": state.get("prediction", {}),
        "comparison": state.get("comparison", {}),
        "report": state.get("report", {}),
        "history": state.get("history", {}),
        "intent": state.get("intent", ""),
        "escalation": state.get("escalation", {}),
        "final_answer": state.get("final_answer", ""),
        "errors": state.get("errors", []),
        "warnings": state.get("warnings", []),
    }
    return {"response_payload": response_payload}