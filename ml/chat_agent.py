from .models import EEGUpload, PredictionResult, AgentConversation
from .report_builder import build_prediction_report
from .compare_reports import compare_with_previous


def answer_question(upload_id, question):
    upload = EEGUpload.objects.get(id=upload_id)
    pred = upload.prediction

    q = question.lower()

    if "depress" in q or "healthy" in q or "prediction" in q or "mdd" in q:
        answer = (
            f"Based on the uploaded EDF file, the model prediction is "
            f"{pred.predicted_label} with probability {pred.probability:.4f}. "
            f"This is a model prediction, not a final clinical diagnosis."
        )

    elif "summary" in q or "feature" in q or "data" in q:
        report = build_prediction_report(upload, pred)
        fs = report["features_summary"]
        answer = (
            f"Feature summary for upload {upload.id}: "
            f"count={fs['feature_count']}, "
            f"mean={fs['feature_mean']:.6f}, "
            f"std={fs['feature_std']:.6f}, "
            f"min={fs['feature_min']:.6f}, "
            f"max={fs['feature_max']:.6f}."
        )

    elif "compare" in q or "previous" in q:
        comparison = compare_with_previous(upload_id)
        if "message" in comparison:
            answer = comparison["message"]
        else:
            answer = (
                f"Compared with previous upload {comparison['previous_upload_id']}, "
                f"current label is {comparison['current_label']} "
                f"and previous label was {comparison['previous_label']}. "
                f"Probability changed from {comparison['previous_probability']:.4f} "
                f"to {comparison['current_probability']:.4f}. "
                f"Mean feature delta is {comparison['delta_feature_mean']:.6f}."
            )

    else:
        answer = (
            "I can answer questions about prediction, feature summary, "
            "and comparison with previous uploaded EEG files."
        )

    AgentConversation.objects.create(
        upload=upload,
        question=question,
        answer=answer,
    )

    return answer