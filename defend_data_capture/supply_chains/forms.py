from django import forms
from .widgets import HintedDisclosingRadioSelect
from .models import StrategicActionUpdate, RAGRatingHints


class MonthlyUpdateInfoForm(forms.ModelForm):
    class Meta:
        model = StrategicActionUpdate
        fields = ['content',]
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'govuk-textarea',
            })
        }


class MonthlyUpdateStatusForm(forms.ModelForm):
    class Meta:
        model = StrategicActionUpdate
        fields = ['implementation_rag_rating', 'reason_for_delays']
        widgets = {
            'implementation_rag_rating': HintedDisclosingRadioSelect(attrs={
                    'class': 'govuk-radios__input',
                    'data-aria-controls': "{id}-disclosure"
                },
                hints=RAGRatingHints,
                disclosures = {
                    'RED': 'Have a banana!'
                }
            )
        }
