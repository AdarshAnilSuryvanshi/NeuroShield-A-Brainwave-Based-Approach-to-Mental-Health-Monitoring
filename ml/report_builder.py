def build_prediction_report(upload_obj, prediction_obj):
    return {
        "upload_id": upload_obj.id,
        "file_name": upload_obj.original_name,
        "status": upload_obj.status,
        "predicted_label": prediction_obj.predicted_label,
        "prediction_int": prediction_obj.prediction_int,
        "probability": prediction_obj.probability,
        "features_summary": prediction_obj.features_json,
        "created_at": prediction_obj.created_at.isoformat(),
    }