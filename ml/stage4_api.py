import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import EEGUpload
from .stage4_graph import stage4_graph
from .stage4_tools import persist_stage4_conversation


def _run_stage4(mode: str, upload_id: int, question: str = "") -> dict:
    state = {
        "mode": mode,
        "upload_id": upload_id,
        "question": question,
        "errors": [],
        "warnings": [],
    }
    result = stage4_graph.invoke(state)
    return result["response_payload"]


@csrf_exempt
def stage4_analyze(request, upload_id: int):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        EEGUpload.objects.get(id=upload_id)
        payload = _run_stage4(mode="analyze", upload_id=upload_id)
        return JsonResponse(payload, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def stage4_report(request, upload_id: int):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    try:
        EEGUpload.objects.get(id=upload_id)
        payload = _run_stage4(mode="report", upload_id=upload_id)
        return JsonResponse(payload, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def stage4_compare(request, upload_id: int):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    try:
        EEGUpload.objects.get(id=upload_id)
        payload = _run_stage4(mode="compare", upload_id=upload_id)
        return JsonResponse(payload, status=200)
    except EEGUpload.DoesNotExist:
        return JsonResponse({"error": "Upload not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def stage4_chat(request, upload_id: int):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        EEGUpload.objects.get(id=upload_id)

        body = json.loads(request.body.decode("utf-8"))
        question = body.get("question", "").strip()

        if not question:
            return JsonResponse({"error": "Question is required"}, status=400)

        payload = _run_stage4(mode="chat", upload_id=upload_id, question=question)

        persist_stage4_conversation(
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