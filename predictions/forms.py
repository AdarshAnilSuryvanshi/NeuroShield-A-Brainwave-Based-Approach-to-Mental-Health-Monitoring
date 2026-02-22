# predictions/forms.py
"""
    Version 1
from django import forms


class FeatureInputForm(forms.Form):
    features_text = forms.CharField(
        label="Input Features (comma or newline separated)",
        widget=forms.Textarea(
            attrs={
                "rows": 6,
                "placeholder": "Example:\n0.12, 0.34, 0.56, ... (total N values)\n\nOR\n0.12\n0.34\n0.56\n...",
            }
        ),
    )

    """
"""
        Version 2
from django import forms

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV file (80 features)")


"""

from django import forms


class EDFUploadForm(forms.Form):
    edf_file = forms.FileField(
        label="Upload EDF File",
        widget=forms.FileInput(attrs={"accept": ".edf"})
    )