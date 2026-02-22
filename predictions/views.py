"""
        Version 1
from django.shortcuts import render

# Create your views here.
# predictions/views.py
from django.shortcuts import render
from .forms import FeatureInputForm
from ml.inference import parse_features_text, predict_one, EXPECTED_FEATURES


def home(request):
    form = FeatureInputForm()
    prediction_label = None
    prediction_text = None
    probability = None
    error = None
    n_received = None

    if request.method == "POST":
        form = FeatureInputForm(request.POST)
        if form.is_valid():
            features_text = form.cleaned_data["features_text"]
            try:
                features = parse_features_text(features_text)
                n_received = len(features)

                pred, prob = predict_one(features)

                prediction_label = pred
                prediction_text = "MDD" if pred == 1 else "Healthy"
                probability = prob

            except Exception as e:
                error = str(e)

    return render(
        request,
        "predictions/index.html",
        {
            "form": form,
            "prediction_label": prediction_label,
            "prediction_text": prediction_text,
            "probability": probability,
            "error": error,
            "expected_features": EXPECTED_FEATURES,
            "n_received": n_received,
        },
    )

    

        Version 2
from django.shortcuts import render
from .forms import CSVUploadForm
from ml.csv_utils import read_csv_features
from ml.inference import predict_one, EXPECTED_FEATURES


def home(request):
    form = CSVUploadForm()
    prediction_label = None
    prediction_text = None
    probability = None
    error = None
    n_received = None

    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = form.cleaned_data["csv_file"]
            try:
                features = read_csv_features(csv_file)
                n_received = len(features)

                pred, prob = predict_one(features)

                prediction_label = pred
                prediction_text = "MDD" if pred == 1 else "Healthy"
                probability = prob

            except Exception as e:
                error = str(e)

    return render(
        request,
        "predictions/index.html",
        {
            "form": form,
            "prediction_label": prediction_label,
            "prediction_text": prediction_text,
            "probability": probability,
            "error": error,
            "expected_features": EXPECTED_FEATURES,
            "n_received": n_received,
        },
    )


"""

import os
from django.shortcuts import render
from .forms import EDFUploadForm

from ml.preprocessing import extract_features_from_edf
from ml.inference import predict_from_features


UPLOAD_DIR = "uploads"


def index(request):

    result = None

    if request.method == "POST":

        form = EDFUploadForm(request.POST, request.FILES)

        if form.is_valid():

            edf_file = request.FILES["edf_file"]

            file_path = os.path.join(UPLOAD_DIR, edf_file.name)

            # Save file
            with open(file_path, "wb+") as f:
                for chunk in edf_file.chunks():
                    f.write(chunk)

            # Extract features
            features = extract_features_from_edf(file_path)

            # Predict
            result = predict_from_features(features)

    else:
        form = EDFUploadForm()

    return render(request, "predictions/index.html", {
        "form": form,
        "result": result
    })
