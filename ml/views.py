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