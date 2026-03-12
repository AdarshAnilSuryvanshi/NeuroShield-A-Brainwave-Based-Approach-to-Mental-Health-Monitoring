from django.urls import path
from .views import get_report, compare_report, chat_with_agent

urlpatterns = [
    path("report/<int:upload_id>/", get_report, name="ml-report"),
    path("compare/<int:upload_id>/", compare_report, name="ml-compare"),
    path("chat/<int:upload_id>/", chat_with_agent, name="ml-chat"),
]