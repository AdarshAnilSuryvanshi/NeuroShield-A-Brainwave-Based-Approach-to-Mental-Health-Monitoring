"""import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import EEGUpload
from .chat_agent import answer_question
from .compare_reports import compare_with_previous
from .report_builder import build_prediction_report


@csrf_exempt
def get_report(request, upload_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    try:
        upload = EEGUpload.objects.get(id=upload_id)
        report = build_prediction_report(upload, upload.prediction)
        return JsonResponse(report, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)


@csrf_exempt
def compare_report(request, upload_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    try:
        data = compare_with_previous(upload_id)
        return JsonResponse(data, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)


@csrf_exempt
def chat_with_agent(request, upload_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        question = body.get("question", "").strip()

        if not question:
            return JsonResponse({"error": "Question is required"}, status=400)

        answer = answer_question(upload_id, question)
        return JsonResponse({"upload_id": upload_id, "question": question, "answer": answer}, status=200)

    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import EEGUpload
from .chat_agent import answer_question
from .compare_reports import compare_with_previous
from .report_builder import build_prediction_report


@csrf_exempt
def get_report(request, upload_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    try:
        upload = EEGUpload.objects.get(id=upload_id)
        report = build_prediction_report(upload, upload.prediction)
        return JsonResponse(report, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def compare_report(request, upload_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    try:
        data = compare_with_previous(upload_id)
        return JsonResponse(data, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def chat_with_agent(request, upload_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        question = body.get("question", "").strip()

        if not question:
            return JsonResponse({"error": "Question is required"}, status=400)

        answer = answer_question(upload_id, question)

        return JsonResponse(
            {
                "upload_id": upload_id,
                "question": question,
                "answer": answer,
            },
            status=200,
        )

    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def visualization_data(request, upload_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    try:
        upload = EEGUpload.objects.get(id=upload_id)
        result = {
            "upload_id": upload.id,
            "file_name": upload.original_name,
            "status": upload.status,
            "uploaded_at": upload.uploaded_at.isoformat(),
            "band_power": {
                "delta": 0.47,
                "theta": 0.43,
                "alpha": 0.68,
                "beta": 0.54,
                "gamma": 0.38,
            },
            "channels": [
                {"name": "CH1", "values": [0.1, 0.3, 0.2, 0.5, 0.4]},
                {"name": "CH2", "values": [0.2, 0.4, 0.3, 0.6, 0.45]},
            ],
            "radar": [
                {"subject": "Alpha", "A": 72, "fullMark": 100},
                {"subject": "Beta", "A": 60, "fullMark": 100},
                {"subject": "Theta", "A": 58, "fullMark": 100},
                {"subject": "Delta", "A": 66, "fullMark": 100},
                {"subject": "Gamma", "A": 34, "fullMark": 100},
            ],
        }
        return JsonResponse(result, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
