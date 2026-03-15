from __future__ import annotations

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ml.models import EEGUpload
from ml.stage5.stage5_graph import stage5_graph
from ml.stage5.stage5_core import persist_stage5_conversation


def run_stage5(mode: str, upload_id: int, question: str = "") -> dict:
    state = {
        "mode": mode,
        "upload_id": upload_id,
        "question": question,
        "errors": [],
        "warnings": [],
    }
    result = stage5_graph.invoke(state)
    return result["response_payload"]


@csrf_exempt
def stage5_analyze(request, upload_id: int):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        EEGUpload.objects.get(id=upload_id)
        payload = run_stage5("analyze", upload_id)
        return JsonResponse(payload, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def stage5_report(request, upload_id: int):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    try:
        EEGUpload.objects.get(id=upload_id)
        payload = run_stage5("report", upload_id)
        return JsonResponse(payload, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def stage5_compare(request, upload_id: int):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    try:
        EEGUpload.objects.get(id=upload_id)
        payload = run_stage5("compare", upload_id)
        return JsonResponse(payload, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def stage5_chat(request, upload_id: int):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        EEGUpload.objects.get(id=upload_id)

        body = json.loads(request.body.decode("utf-8"))
        question = body.get("question", "").strip()

        if not question:
            return JsonResponse({"error": "Question is required"}, status=400)

        payload = run_stage5("chat", upload_id, question)

        persist_stage5_conversation(
            upload_id=upload_id,
            question=question,
            answer=payload.get("final_answer", ""),
        )

        return JsonResponse(payload, status=200)

    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)