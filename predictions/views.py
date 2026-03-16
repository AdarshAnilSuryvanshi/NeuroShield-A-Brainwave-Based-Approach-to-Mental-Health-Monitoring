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
"""
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from .forms import EDFUploadForm

from ml.models import EEGUpload, PredictionResult
from ml.inference import predict_from_edf


def index(request):
    result = None
    upload_id = None
    error = None
    form = EDFUploadForm()

    if request.method == "POST":
        form = EDFUploadForm(request.POST, request.FILES)

        if form.is_valid():
            edf_file = request.FILES.get("edf_file")

            if not edf_file:
                error = "No EDF file was uploaded."
            else:
                upload = EEGUpload.objects.create(
                    file=edf_file,
                    original_name=edf_file.name,
                    status="uploaded",
                )

                try:
                    pred = predict_from_edf(upload.file.path)

                    PredictionResult.objects.update_or_create(
                        upload=upload,
                        defaults={
                            "predicted_label": pred["label"],
                            "prediction_int": pred["prediction"],
                            "probability": pred["probability"],
                            "features_json": pred["summary"],
                        }
                    )

                    upload.status = "processed"
                    upload.save()

                    upload_id = upload.id
                    result = {
                        "label": pred["label"],
                        "probability": pred["probability"],
                        "prediction": pred["prediction"],
                        "summary": pred["summary"],
                    }

                except Exception as e:
                    upload.status = "failed"
                    upload.save()
                    error = str(e)

    return render(
        request,
        "predictions/index.html",
        {
            "form": form,
            "result": result,
            "upload_id": upload_id,
            "error": error,
        },
    )


@csrf_exempt
def api_register(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    email = data.get("email", "").strip()
    name = data.get("name", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return JsonResponse({"error": "email and password required"}, status=400)

    UserModel = get_user_model()
    if UserModel.objects.filter(email=email).exists():
        return JsonResponse({"error": "User already exists"}, status=400)

    user = UserModel.objects.create_user(username=email, email=email, password=password, first_name=name)
    return JsonResponse({"user": {"email": user.email, "name": user.first_name}})


@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return JsonResponse({"error": "email and password required"}, status=400)

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    return JsonResponse({"user": {"email": user.email, "name": user.first_name}})


@csrf_exempt
def api_upload_eeg(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    edf_file = request.FILES.get("edf_file")
    if not edf_file:
        return JsonResponse({"error": "No edf_file provided"}, status=400)

    upload = EEGUpload.objects.create(
        file=edf_file,
        original_name=edf_file.name,
        status="uploaded",
    )

    try:
        pred = predict_from_edf(upload.file.path)
        PredictionResult.objects.update_or_create(
            upload=upload,
            defaults={
                "predicted_label": pred["label"],
                "prediction_int": pred["prediction"],
                "probability": pred["probability"],
                "features_json": pred["summary"],
            },
        )
        upload.status = "processed"
        upload.save()

        return JsonResponse({
            "upload_id": upload.id,
            "file_name": upload.original_name,
            "status": upload.status,
            "predicted_label": pred["label"],
            "prediction": pred["prediction"],
            "probability": pred["probability"],
            "summary": pred["summary"],
        })
    except Exception as e:
        upload.status = "failed"
        upload.save()
        return JsonResponse({"error": str(e)}, status=500)


def api_dashboard(request, user_id=None):
    uploads = EEGUpload.objects.order_by("-uploaded_at")[:20]
    data = [
        {
            "id": u.id,
            "file_name": u.original_name,
            "status": u.status,
            "predicted_label": getattr(u.prediction, "predicted_label", None),
            "probability": getattr(u.prediction, "probability", None),
            "uploaded_at": u.uploaded_at.isoformat(),
        }
        for u in uploads
    ]
    return JsonResponse({"uploads": data})


def api_uploads(request):
    uploads = EEGUpload.objects.order_by("-uploaded_at")[:100]
    data = [
        {
            "id": u.id,
            "file_name": u.original_name,
            "status": u.status,
            "predicted_label": getattr(u.prediction, "predicted_label", None),
            "probability": getattr(u.prediction, "probability", None),
            "uploaded_at": u.uploaded_at.isoformat(),
        }
        for u in uploads
    ]
    return JsonResponse(data, safe=False)
