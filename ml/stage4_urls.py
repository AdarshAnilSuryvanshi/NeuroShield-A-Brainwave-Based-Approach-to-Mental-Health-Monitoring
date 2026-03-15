from django.urls import path

from .stage4_api import (
    stage4_analyze,
    stage4_report,
    stage4_compare,
    stage4_chat,
)

urlpatterns = [
    path("analyze/<int:upload_id>/", stage4_analyze, name="stage4-analyze"),
    path("report/<int:upload_id>/", stage4_report, name="stage4-report"),
    path("compare/<int:upload_id>/", stage4_compare, name="stage4-compare"),
    path("chat/<int:upload_id>/", stage4_chat, name="stage4-chat"),
]