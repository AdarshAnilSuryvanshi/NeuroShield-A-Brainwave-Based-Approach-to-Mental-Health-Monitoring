from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("predictions.urls")),
    path("ml/", include("ml.urls")),
   # path("ml/stage4/", include("ml.stage4_urls")), 
    path("ml/stage5/", include("ml.stage5.stage5_urls")),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)