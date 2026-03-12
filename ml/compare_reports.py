from .models import EEGUpload


def compare_with_previous(upload_id):
    current_upload = EEGUpload.objects.get(id=upload_id)
    current_pred = current_upload.prediction

    previous_upload = (
        EEGUpload.objects
        .filter(status="processed", uploaded_at__lt=current_upload.uploaded_at)
        .order_by("-uploaded_at")
        .first()
    )

    if not previous_upload:
        return {
            "message": "No previous processed upload found for comparison."
        }

    previous_pred = previous_upload.prediction

    c = current_pred.features_json
    p = previous_pred.features_json

    result = {
        "current_upload_id": current_upload.id,
        "previous_upload_id": previous_upload.id,
        "current_label": current_pred.predicted_label,
        "previous_label": previous_pred.predicted_label,
        "current_probability": current_pred.probability,
        "previous_probability": previous_pred.probability,
        "delta_feature_mean": c["feature_mean"] - p["feature_mean"],
        "delta_feature_std": c["feature_std"] - p["feature_std"],
        "delta_feature_max": c["feature_max"] - p["feature_max"],
        "delta_feature_min": c["feature_min"] - p["feature_min"],
    }

    return result