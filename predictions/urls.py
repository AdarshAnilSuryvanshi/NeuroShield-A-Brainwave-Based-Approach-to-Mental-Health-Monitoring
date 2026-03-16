from django.urls import path
from .views import (
    index,
    api_register,
    api_login,
    api_upload_eeg,
    api_dashboard,
    api_uploads,
)

urlpatterns = [
    path("api/register/", api_register, name="api-register"),
    path("api/login/", api_login, name="api-login"),
    path("api/upload/", api_upload_eeg, name="api-upload"),
    path("api/dashboard/<int:user_id>/", api_dashboard, name="api-dashboard-user"),
    path("api/dashboard/", api_dashboard, name="api-dashboard"),
    path("api/uploads/", api_uploads, name="api-uploads"),
    path("", index, name="index"),
]