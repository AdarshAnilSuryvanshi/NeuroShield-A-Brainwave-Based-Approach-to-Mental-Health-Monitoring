from __future__ import annotations

from typing import Any, Dict, List, Optional

from ml.models import EEGUpload, PredictionResult, AgentConversation
from ml.inference import predict_from_edf
from ml.report_builder import build_prediction_report
from ml.compare_reports import compare_with_previous


# ---------------------------
# Constants / thresholds
# ---------------------------

UNCERTAIN_LOW = 0.35
UNCERTAIN_HIGH = 0.65
HIGH_RISK_THRESHOLD = 0.80
SIGNIFICANT_DELTA = 0.20
MAX_HISTORY_ITEMS = 5


# ---------------------------
# Basic helpers
# ---------------------------

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_upload(upload_id: int) -> EEGUpload:
    return EEGUpload.objects.get(id=upload_id)


def serialize_prediction(pred: PredictionResult) -> Dict[str, Any]:
    features = pred.features_json or {}
    return {
        "predicted_label": pred.predicted_label,
        "prediction_int": pred.prediction_int,
        "probability": safe_float(pred.probability),
        "features_summary": features,
        "created_at": pred.created_at.isoformat(),
    }


def get_upload_meta(upload_id: int) -> Dict[str, Any]:
    upload = get_upload(upload_id)
    return {
        "upload_id": upload.id,
        "original_name": upload.original_name,
        "status": upload.status,
        "uploaded_at": upload.uploaded_at.isoformat(),
        "file_path": upload.file.path,
    }


# ---------------------------
# Core prediction (preserves your existing model)
# ---------------------------

def ensure_prediction(upload_id: int) -> Dict[str, Any]:
    """
    Uses your existing NeuroShield prediction pipeline.
    If prediction exists, reuse it.
    Else run predict_from_edf() and save PredictionResult.
    """
    upload = get_upload(upload_id)

    try:
        pred = upload.prediction
        return serialize_prediction(pred)
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

        return serialize_prediction(pred)


def get_report(upload_id: int) -> Dict[str, Any]:
    upload = get_upload(upload_id)
    ensure_prediction(upload_id)
    pred = upload.prediction

    report = build_prediction_report(upload, pred)
    report["stage5_context"] = {
        "system_version": "NeuroShield Stage 5",
        "uses_existing_prediction_model": True,
        "note": "This is a model-supported mental health monitoring system output, not a final clinical diagnosis.",
    }
    return report


def get_comparison(upload_id: int) -> Dict[str, Any]:
    ensure_prediction(upload_id)
    comparison = compare_with_previous(upload_id)

    if "message" in comparison:
        return {
            "has_comparison": False,
            "message": comparison["message"],
        }

    current_prob = safe_float(comparison.get("current_probability"))
    previous_prob = safe_float(comparison.get("previous_probability"))
    comparison["has_comparison"] = True
    comparison["probability_delta"] = current_prob - previous_prob
    return comparison


# ---------------------------
# History / longitudinal data
# ---------------------------

def get_recent_history(upload_id: int, max_items: int = MAX_HISTORY_ITEMS) -> Dict[str, Any]:
    upload = get_upload(upload_id)

    recent_conversations = (
        AgentConversation.objects.filter(upload=upload)
        .order_by("-created_at")[:max_items]
    )

    all_processed_uploads = (
        EEGUpload.objects.filter(status="processed", uploaded_at__lte=upload.uploaded_at)
        .order_by("uploaded_at")
    )

    timeline = []
    probabilities = []

    for item in all_processed_uploads:
        try:
            pred = item.prediction
            prob = safe_float(pred.probability)
            probabilities.append(prob)
            timeline.append({
                "upload_id": item.id,
                "uploaded_at": item.uploaded_at.isoformat(),
                "label": pred.predicted_label,
                "probability": prob,
            })
        except PredictionResult.DoesNotExist:
            continue

    return {
        "recent_conversations": [
            {
                "question": c.question,
                "answer": c.answer,
                "created_at": c.created_at.isoformat(),
            }
            for c in recent_conversations
        ],
        "timeline": timeline[-max_items:],
        "probabilities": probabilities[-max_items:],
    }


def analyze_trend(history: Dict[str, Any]) -> Dict[str, Any]:
    probs = history.get("probabilities", [])

    if len(probs) < 2:
        return {
            "has_trend": False,
            "direction": "insufficient_data",
            "trend_confidence": 0.0,
            "summary": "Not enough previous processed uploads to analyze a longitudinal trend.",
        }

    delta = probs[-1] - probs[0]

    if delta > 0.10:
        direction = "worsening"
        confidence = min(0.95, abs(delta) + 0.50)
    elif delta < -0.10:
        direction = "improving"
        confidence = min(0.95, abs(delta) + 0.50)
    else:
        direction = "stable"
        confidence = 0.65

    return {
        "has_trend": True,
        "direction": direction,
        "trend_confidence": round(confidence, 4),
        "start_probability": round(probs[0], 4),
        "latest_probability": round(probs[-1], 4),
        "probability_series": [round(x, 4) for x in probs],
        "summary": f"Risk trend appears {direction} across the available upload history.",
    }


# ---------------------------
# Stage 5 intelligence layers
# ---------------------------

def assess_signal_quality(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Approximate signal-quality-style assessment from available feature summary.
    This does NOT replace true raw-signal QC, but gives a grounded reliability estimate
    from the data you already store.
    """
    fs = prediction.get("features_summary", {}) or {}

    feature_count = int(fs.get("feature_count", 0) or 0)
    feature_std = safe_float(fs.get("feature_std"))
    feature_min = safe_float(fs.get("feature_min"))
    feature_max = safe_float(fs.get("feature_max"))

    quality_score = 0.50
    warnings: List[str] = []

    if feature_count >= 50:
        quality_score += 0.20
    else:
        warnings.append("Low feature count detected; confidence may be reduced.")

    if 0.0 < feature_std < 5.0:
        quality_score += 0.15
    else:
        warnings.append("Feature spread appears unusual.")

    if feature_max != feature_min:
        quality_score += 0.10
    else:
        warnings.append("Feature range appears collapsed or uninformative.")

    quality_score = max(0.05, min(0.98, quality_score))

    status = "good"
    if quality_score < 0.45:
        status = "poor"
    elif quality_score < 0.70:
        status = "moderate"

    artifact_warning = quality_score < 0.55

    return {
        "status": status,
        "quality_score": round(quality_score, 4),
        "artifact_warning": artifact_warning,
        "warnings": warnings,
        "note": "This is a metadata-based reliability estimate from stored feature summaries, not a full raw-signal artifact detector.",
    }


def compute_confidence(prediction: Dict[str, Any], signal_quality: Dict[str, Any]) -> Dict[str, Any]:
    probability = safe_float(prediction.get("probability"))
    quality_score = safe_float(signal_quality.get("quality_score"), 0.5)

    distance_from_uncertainty = abs(probability - 0.50) * 2.0
    confidence_score = (0.65 * distance_from_uncertainty) + (0.35 * quality_score)
    confidence_score = max(0.05, min(0.99, confidence_score))

    band = "high"
    if confidence_score < 0.45:
        band = "low"
    elif confidence_score < 0.70:
        band = "medium"

    return {
        "confidence_score": round(confidence_score, 4),
        "confidence_band": band,
        "uncertainty_band_hit": UNCERTAIN_LOW <= probability <= UNCERTAIN_HIGH,
    }


def build_explainability(prediction: Dict[str, Any]) -> Dict[str, Any]:
    fs = prediction.get("features_summary", {}) or {}

    top_factors = []
    mean_val = safe_float(fs.get("feature_mean"))
    std_val = safe_float(fs.get("feature_std"))
    min_val = safe_float(fs.get("feature_min"))
    max_val = safe_float(fs.get("feature_max"))

    if std_val > 1.0:
        top_factors.append("High feature variability was observed in the extracted EEG feature space.")
    else:
        top_factors.append("Feature variability appears relatively controlled in the extracted EEG feature space.")

    if mean_val > 0:
        top_factors.append("Overall extracted feature mean is positive, indicating a shifted aggregate feature profile.")
    else:
        top_factors.append("Overall extracted feature mean is neutral-to-negative, indicating a different aggregate feature profile.")

    if abs(max_val - min_val) > 1.0:
        top_factors.append("Feature range is broad, suggesting strong separation across extracted EEG-derived indicators.")
    else:
        top_factors.append("Feature range is relatively narrow, suggesting more compact extracted EEG-derived indicators.")

    return {
        "top_factors": top_factors[:3],
        "explanation_note": "These explanations are derived from the stored feature summary and model result, not from a separate SHAP pipeline.",
    }


def assess_risk(
    prediction: Dict[str, Any],
    comparison: Dict[str, Any],
    confidence: Dict[str, Any],
    trend: Dict[str, Any],
) -> Dict[str, Any]:
    probability = safe_float(prediction.get("probability"))
    label = prediction.get("predicted_label", "Unknown")
    confidence_band = confidence.get("confidence_band", "medium")

    reasons: List[str] = []
    risk_level = "low"
    urgent_review = False

    if label == "MDD" and probability >= HIGH_RISK_THRESHOLD:
        risk_level = "high"
        urgent_review = True
        reasons.append(f"Predicted label is MDD with high probability ({probability:.4f}).")

    if confidence_band == "low":
        if risk_level == "low":
            risk_level = "medium"
        reasons.append("Overall confidence is low; specialist review is recommended before strong conclusions.")

    if comparison.get("has_comparison"):
        delta = abs(safe_float(comparison.get("probability_delta")))
        if delta >= SIGNIFICANT_DELTA:
            if risk_level == "low":
                risk_level = "medium"
            reasons.append(f"Probability changed significantly compared with the previous processed upload ({delta:.4f}).")

        if comparison.get("previous_label") != comparison.get("current_label"):
            risk_level = "high"
            urgent_review = True
            reasons.append("Predicted label changed compared with the previous processed upload.")

    if trend.get("has_trend") and trend.get("direction") == "worsening":
        risk_level = "high"
        urgent_review = True
        reasons.append("Longitudinal probability trend suggests worsening mental-health risk over time.")

    if not reasons:
        reasons.append("No major risk escalation trigger fired from the current Stage 5 rules.")

    return {
        "risk_level": risk_level,
        "urgent_review": urgent_review,
        "reasons": reasons,
    }


def build_recommendation(
    prediction: Dict[str, Any],
    signal_quality: Dict[str, Any],
    confidence: Dict[str, Any],
    trend: Dict[str, Any],
    risk: Dict[str, Any],
) -> Dict[str, Any]:
    actions: List[str] = []

    if signal_quality.get("status") == "poor":
        actions.append("Re-check the EEG acquisition quality or repeat the recording if clinically appropriate.")

    if confidence.get("confidence_band") == "low":
        actions.append("Interpret the model output cautiously and consider specialist review.")

    if risk.get("urgent_review"):
        actions.append("Clinical review is recommended due to elevated or changing risk.")

    if trend.get("has_trend") and trend.get("direction") == "worsening":
        actions.append("Continue longitudinal monitoring and compare future uploads against this trajectory.")

    if not actions:
        actions.append("Continue routine monitoring and use the current report as a reference point.")

    return {
        "recommended_action": " ".join(actions),
        "actions": actions,
    }


# ---------------------------
# Question / answer intelligence
# ---------------------------

def classify_intent(question: str) -> str:
    q = (question or "").strip().lower()

    if not q:
        return "overview"

    # safety / crisis-like intent
    if any(word in q for word in ["suicide", "kill myself", "self harm", "hurt myself", "end my life"]):
        return "crisis"

    if any(word in q for word in ["dataset", "data", "training data", "input dataset"]):
        return "dataset"
    if any(word in q for word in ["feature", "features", "explain features"]):
        return "features"
    if any(word in q for word in ["prediction", "probability", "mdd", "healthy", "depression result"]):
        return "prediction"
    if any(word in q for word in ["compare", "difference", "previous", "change"]):
        return "comparison"
    if any(word in q for word in ["trend", "history", "timeline", "progression", "monitoring"]):
        return "trend"
    if any(word in q for word in ["confidence", "reliable", "trust", "signal quality", "artifact"]):
        return "confidence"
    if any(word in q for word in ["mental stability", "stability", "risk", "safe", "condition"]):
        return "stability"
    if any(word in q for word in ["what should i do", "next step", "recommend", "action", "how can i improve"]):
        return "recommendation"
    if any(word in q for word in ["project", "system", "how does this work", "about this project"]):
        return "project"

    return "overview"


def build_project_overview() -> str:
    return (
        "NeuroShield is an EEG-based depression detection and mental-health monitoring system. "
        "Its core uniqueness is your existing prediction pipeline: EDF input goes through feature extraction, "
        "then your trained model generates a prediction, probability, and summary. "
        "The Stage 5 layer does not replace that model. It adds signal-quality-style reliability estimation, "
        "confidence analysis, longitudinal trend analysis, risk assessment, recommendations, and a grounded assistant "
        "that answers questions from the stored project outputs."
    )


def build_crisis_message() -> str:
    return (
        "If you may be in immediate danger or thinking about hurting yourself, seek urgent help now: "
        "call your local emergency number or go to the nearest emergency department. "
        "If possible, contact a trusted family member, friend, or clinician right away and do not stay alone. "
        "This system can provide supportive information, but it is not a crisis service or a substitute for immediate professional help."
    )


def build_answer(
    question: str,
    upload_meta: Dict[str, Any],
    prediction: Dict[str, Any],
    report: Dict[str, Any],
    comparison: Dict[str, Any],
    history: Dict[str, Any],
    signal_quality: Dict[str, Any],
    confidence: Dict[str, Any],
    trend: Dict[str, Any],
    explainability: Dict[str, Any],
    risk: Dict[str, Any],
    recommendation: Dict[str, Any],
) -> str:
    intent = classify_intent(question)

    if intent == "crisis":
        return build_crisis_message()

    if intent == "project":
        return build_project_overview()

    if intent == "dataset":
        return (
            "This project analyzes EEG upload data provided to NeuroShield. "
            f"For the current upload, the file is '{upload_meta.get('original_name')}' with status "
            f"'{upload_meta.get('status')}'. The Stage 5 system answers from the stored upload, prediction, "
            "report, and history context available in your project database."
        )

    if intent == "features":
        fs = prediction.get("features_summary", {}) or {}
        return (
            f"The current prediction uses the feature summary already generated by your existing pipeline. "
            f"Feature count is {fs.get('feature_count', 'NA')}, mean is {safe_float(fs.get('feature_mean')):.6f}, "
            f"standard deviation is {safe_float(fs.get('feature_std')):.6f}, "
            f"minimum is {safe_float(fs.get('feature_min')):.6f}, and maximum is {safe_float(fs.get('feature_max')):.6f}. "
            f"Stage 5 explainability highlights: {' '.join(explainability.get('top_factors', []))}"
        )

    if intent == "prediction":
        return (
            f"The current upload is classified as {prediction.get('predicted_label', 'Unknown')} "
            f"with probability {safe_float(prediction.get('probability')):.4f}. "
            f"Overall confidence is {confidence.get('confidence_band')} "
            f"({safe_float(confidence.get('confidence_score')):.4f}). "
            f"Risk level is {risk.get('risk_level')}."
        )

    if intent == "comparison":
        if not comparison.get("has_comparison"):
            return comparison.get("message", "No previous processed upload is available for comparison.")
        return (
            f"Compared with previous upload {comparison.get('previous_upload_id')}, "
            f"the previous label was {comparison.get('previous_label')} and the current label is "
            f"{comparison.get('current_label')}. Probability changed from "
            f"{safe_float(comparison.get('previous_probability')):.4f} to "
            f"{safe_float(comparison.get('current_probability')):.4f}. "
            f"Delta is {safe_float(comparison.get('probability_delta')):.4f}."
        )

    if intent == "trend":
        return (
            f"{trend.get('summary')} "
            f"Trend confidence is {safe_float(trend.get('trend_confidence')):.4f}. "
            f"Recent probability series: {trend.get('probability_series', [])}."
        )

    if intent == "confidence":
        return (
            f"Signal-quality status is {signal_quality.get('status')} with quality score "
            f"{safe_float(signal_quality.get('quality_score')):.4f}. "
            f"Overall model confidence is {confidence.get('confidence_band')} "
            f"({safe_float(confidence.get('confidence_score')):.4f}). "
            f"Artifact warning is {signal_quality.get('artifact_warning')}."
        )

    if intent == "stability":
        return (
            f"Based on the current Stage 5 assessment, the predicted label is "
            f"{prediction.get('predicted_label', 'Unknown')} with probability "
            f"{safe_float(prediction.get('probability')):.4f}. "
            f"Risk level is {risk.get('risk_level')}. "
            f"Longitudinal trend assessment says: {trend.get('summary')}"
        )

    if intent == "recommendation":
        return recommendation.get("recommended_action", "Continue routine monitoring.")

    # overview
    return (
        f"NeuroShield Stage 5 overview for upload {upload_meta.get('upload_id')}: "
        f"label={prediction.get('predicted_label', 'Unknown')}, "
        f"probability={safe_float(prediction.get('probability')):.4f}, "
        f"signal_quality={signal_quality.get('status')}, "
        f"confidence={confidence.get('confidence_band')}, "
        f"trend={trend.get('direction')}, "
        f"risk={risk.get('risk_level')}. "
        f"Recommendation: {recommendation.get('recommended_action')}"
    )


def persist_stage5_conversation(upload_id: int, question: str, answer: str) -> None:
    upload = get_upload(upload_id)
    AgentConversation.objects.create(
        upload=upload,
        question=f"[STAGE5] {question}",
        answer=answer,
    )