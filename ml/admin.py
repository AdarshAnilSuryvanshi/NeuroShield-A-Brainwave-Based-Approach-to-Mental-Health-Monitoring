from django.contrib import admin
from .models import EEGUpload, PredictionResult, AgentConversation

admin.site.register(EEGUpload)
admin.site.register(PredictionResult)
admin.site.register(AgentConversation)