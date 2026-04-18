from __future__ import annotations

from typing import Any, Dict, List

from .models import EEGUpload, PredictionResult, AgentConversation
from .inference import predict_from_edf
from .report_builder import build_prediction_report
from .compare_reports import compare_with_previous


UNCERTAIN_LOW = 0.35
UNCERTAIN_HIGH = 0.65
DELTA_ALERT_THRESHOLD = 0.20


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_upload(upload_id: int) -> EEGUpload:
    return EEGUpload.objects.get(id=upload_id)


def _serialize_prediction_obj(pred: PredictionResult) -> Dict[str, Any]:
    return {
        "predicted_label": pred.predicted_label,
        "prediction_int": pred.prediction_int,
        "probability": float(pred.probability),
        "features_summary": pred.features_json or {},
        "created_at": pred.created_at.isoformat(),
    }


def get_upload_meta(upload_id: int) -> Dict[str, Any]:
    upload = _get_upload(upload_id)
    return {
        "upload_id": upload.id,
        "original_name": upload.original_name,
        "status": upload.status,
        "uploaded_at": upload.uploaded_at.isoformat(),
        "file_path": upload.file.path,
    }


def ensure_prediction(upload_id: int) -> Dict[str, Any]:
    """
    Keeps your current ML pipeline as the core.
    If prediction already exists, reuse it.
    If not, run your existing EDF -> feature extraction -> RF prediction pipeline.
    """
    upload = _get_upload(upload_id)

    try:
        pred = upload.prediction
        return _serialize_prediction_obj(pred)
    except PredictionResult.DoesNotExist:
        result = predict_from_edf(upload.file.path)

        pred = PredictionResult.objects.create(
            upload=upload,
            predicted_label=result["label"],
            prediction_int=result["prediction"],
            probability=result["probability"],
            features_json=result["summary"],
        )

        upload.status = "processed"
        upload.save(update_fields=["status"])

        return _serialize_prediction_obj(pred)


def get_report_data(upload_id: int) -> Dict[str, Any]:
    upload = _get_upload(upload_id)
    pred_dict = ensure_prediction(upload_id)

    # Reload object if it was just created.
    pred_obj = upload.prediction
    report = build_prediction_report(upload, pred_obj)

    # Add a little extra stage-4 metadata without changing your original core report logic.
    report["stage4_context"] = {
        "report_type": "grounded_eeg_prediction_report",
        "uses_existing_model": True,
        "clinical_note": "This is a model-supported system output, not a final clinical diagnosis.",
    }
    report["prediction_snapshot"] = pred_dict
    return report


def get_comparison_data(upload_id: int) -> Dict[str, Any]:
    # Ensure current upload has prediction before comparison
    ensure_prediction(upload_id)

    comparison = compare_with_previous(upload_id)

    if "message" in comparison:
        return {
            "has_comparison": False,
            "message": comparison["message"],
        }

    probability_delta = _safe_float(comparison.get("current_probability")) - _safe_float(
        comparison.get("previous_probability")
    )

    comparison["has_comparison"] = True
    comparison["probability_delta"] = probability_delta
    return comparison


def get_history_data(upload_id: int, max_items: int = 5) -> Dict[str, Any]:
    upload = _get_upload(upload_id)

    recent_conversations = (
        AgentConversation.objects.filter(upload=upload)
        .order_by("-created_at")[:max_items]
    )

    recent_uploads = (
        EEGUpload.objects.filter(uploaded_at__lte=upload.uploaded_at)
        .order_by("-uploaded_at")[:max_items]
    )

    return {
        "recent_conversations": [
            {
                "question": item.question,
                "answer": item.answer,
                "created_at": item.created_at.isoformat(),
            }
            for item in recent_conversations
        ],
        "recent_uploads": [
            {
                "upload_id": item.id,
                "original_name": item.original_name,
                "status": item.status,
                "uploaded_at": item.uploaded_at.isoformat(),
            }
            for item in recent_uploads
        ],
    }


def classify_question_intent(question: str) -> str:
    q = (question or "").strip().lower()

    if not q:
        return "general"

    if any(word in q for word in ["compare", "previous", "change", "difference", "trend"]):
        return "compare"
    if any(word in q for word in ["report", "summary", "explain", "details"]):
        return "report"
    if any(word in q for word in ["prediction", "mdd", "healthy", "depress", "probability"]):
        return "prediction"
    if any(word in q for word in ["history", "past", "conversation"]):
        return "history"

    return "general"


def assess_escalation(prediction: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    probability = _safe_float(prediction.get("probability"))
    predicted_label = prediction.get("predicted_label", "Unknown")

    reasons: List[str] = []
    risk_level = "low"
    should_flag = False

    if UNCERTAIN_LOW <= probability <= UNCERTAIN_HIGH:
        should_flag = True
        risk_level = "medium"
        reasons.append(
            f"Model probability {probability:.4f} is in the uncertainty band "
            f"({UNCERTAIN_LOW:.2f}-{UNCERTAIN_HIGH:.2f})."
        )

    if predicted_label == "MDD" and probability > 0.80:
        risk_level = "high"
        should_flag = True
        reasons.append(
            f"Predicted label is MDD with high probability ({probability:.4f})."
        )

    if comparison.get("has_comparison"):
        prev_label = comparison.get("previous_label")
        curr_label = comparison.get("current_label")
        prob_delta = abs(_safe_float(comparison.get("probability_delta")))

        if prev_label and curr_label and prev_label != curr_label:
            should_flag = True
            risk_level = "high" if risk_level != "high" else risk_level
            reasons.append(
                f"Label changed from {prev_label} to {curr_label} compared with the previous processed upload."
            )

        if prob_delta >= DELTA_ALERT_THRESHOLD:
            should_flag = True
            if risk_level == "low":
                risk_level = "medium"
            reasons.append(
                f"Probability changed significantly by {prob_delta:.4f} compared with the previous processed upload."
            )

    if not reasons:
        reasons.append("No escalation trigger fired from the current Stage 4 rules.")

    return {
        "should_flag_for_review": should_flag,
        "risk_level": risk_level,
        "reasons": reasons,
    }


def build_grounded_answer(
    question: str,
    intent: str,
    prediction: Dict[str, Any],
    comparison: Dict[str, Any],
    report: Dict[str, Any],
    history: Dict[str, Any],
    escalation: Dict[str, Any],
) -> str:
    predicted_label = prediction.get("predicted_label", "Unknown")
    probability = _safe_float(prediction.get("probability"))
    features_summary = prediction.get("features_summary", {})

    if intent == "prediction":
        return (
            f"Based on your existing NeuroShield prediction pipeline, the current upload is "
            f"classified as {predicted_label} with probability {probability:.4f}. "
            f"This is a model-supported output and not a final clinical diagnosis."
        )

    if intent == "report":
        return (
            f"Report summary: upload {report.get('upload_id')} for file '{report.get('file_name')}' "
            f"has status '{report.get('status')}', predicted label '{report.get('predicted_label')}', "
            f"and probability {float(report.get('probability', 0.0)):.4f}. "
            f"Feature summary includes count={features_summary.get('feature_count', 'NA')}, "
            f"mean={_safe_float(features_summary.get('feature_mean')):.6f}, "
            f"std={_safe_float(features_summary.get('feature_std')):.6f}, "
            f"min={_safe_float(features_summary.get('feature_min')):.6f}, "
            f"max={_safe_float(features_summary.get('feature_max')):.6f}."
        )

    if intent == "compare":
        if not comparison.get("has_comparison"):
            return comparison.get("message", "No previous processed upload found for comparison.")

        return (
            f"Compared with previous upload {comparison.get('previous_upload_id')}, "
            f"the current label is {comparison.get('current_label')} and the previous label was "
            f"{comparison.get('previous_label')}. Probability changed from "
            f"{_safe_float(comparison.get('previous_probability')):.4f} to "
            f"{_safe_float(comparison.get('current_probability')):.4f}. "
            f"Mean feature delta is {_safe_float(comparison.get('delta_feature_mean')):.6f}. "
            f"Stage 4 review flag is set to {escalation.get('should_flag_for_review')}."
        )

    if intent == "history":
        convo_count = len(history.get("recent_conversations", []))
        upload_count = len(history.get("recent_uploads", []))
        return (
            f"I found {convo_count} recent conversation records and {upload_count} recent upload records "
            f"available for grounded context for this upload."
        )

    return (
        f"I can answer grounded questions about prediction, report summary, comparison with previous uploads, "
        f"and stored conversation history for upload {report.get('upload_id')}. "
        f"Current model label is {predicted_label} with probability {probability:.4f}. "
        f"Review flag: {escalation.get('should_flag_for_review')}."
    )


def persist_stage4_conversation(upload_id: int, question: str, answer: str) -> None:
    upload = _get_upload(upload_id)
    AgentConversation.objects.create(
        upload=upload,
        question=f"[STAGE4] {question}",
        answer=answer,
    )