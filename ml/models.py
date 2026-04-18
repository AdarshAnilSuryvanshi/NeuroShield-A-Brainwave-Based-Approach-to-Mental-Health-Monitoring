from django.db import models


class EEGUpload(models.Model):
    file = models.FileField(upload_to="uploads/")
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("uploaded", "Uploaded"),
            ("processed", "Processed"),
            ("failed", "Failed"),
        ],
        default="uploaded",
    )

    def __str__(self):
        return f"{self.id} - {self.original_name}"


class PredictionResult(models.Model):
    upload = models.OneToOneField(
        EEGUpload,
        on_delete=models.CASCADE,
        related_name="prediction"
    )
    predicted_label = models.CharField(max_length=50)
    prediction_int = models.IntegerField()
    probability = models.FloatField(default=0.0)
    features_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.upload.original_name} -> {self.predicted_label}"


class AgentConversation(models.Model):
    upload = models.ForeignKey(
        EEGUpload,
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
    )
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q for upload {self.upload_id}: {self.question[:50]}"