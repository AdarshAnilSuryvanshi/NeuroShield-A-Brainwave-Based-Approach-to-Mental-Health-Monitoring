


import pickle
import numpy as np

MODEL_PATH = "ml/artifacts/random_forest_model.pkl"

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


def predict_from_features(features):

    prediction = model.predict(features)[0]

    probability = model.predict_proba(features)[0][1]

    label = "MDD" if prediction == 1 else "Healthy"

    return {
        "label": label,
        "probability": float(probability),
        "prediction": int(prediction)
    }