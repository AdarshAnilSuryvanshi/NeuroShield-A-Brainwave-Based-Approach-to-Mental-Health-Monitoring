import pickle
from pathlib import Path

from .preprocessing import extract_features_from_edf, summarize_features

MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "random_forest_model.pkl"

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


def predict_from_features(features):
    prediction = int(model.predict(features)[0])

    if hasattr(model, "predict_proba"):
        probability = float(model.predict_proba(features)[0][1])
    else:
        probability = 0.0

    label = "MDD" if prediction == 1 else "Healthy"

    return {
        "label": label,
        "probability": probability,
        "prediction": prediction,
    }


def predict_from_edf(edf_path):
    features = extract_features_from_edf(edf_path)
    pred = predict_from_features(features)
    summary = summarize_features(features)

    return {
        "label": pred["label"],
        "probability": pred["probability"],
        "prediction": pred["prediction"],
        "features": features,
        "summary": summary,
    }