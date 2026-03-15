from django.urls import path

from ml.stage5.stage5_api import (
    stage5_analyze,
    stage5_report,
    stage5_compare,
    stage5_chat,
)

urlpatterns = [
    path("analyze/<int:upload_id>/", stage5_analyze, name="stage5-analyze"),
    path("report/<int:upload_id>/", stage5_report, name="stage5-report"),
    path("compare/<int:upload_id>/", stage5_compare, name="stage5-compare"),
    path("chat/<int:upload_id>/", stage5_chat, name="stage5-chat"),
]