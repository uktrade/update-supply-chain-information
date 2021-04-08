from django import forms
from .widgets import HintedDetailRadioSelect
from .models import StrategicActionUpdate, RAGRatingHints, StrategicAction


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
            'implementation_rag_rating': HintedDetailRadioSelect(attrs={
                    'class': 'govuk-radios__input',
                    'data-aria-controls': "{id}-detail"
                },
                hints=RAGRatingHints,
                details = {
                    'RED': {
                        'template': 'supply_chains/reason_for_delays.html',
                        'field': lambda self: self['reason_for_delays'],
                        'prefix': 'red',
                    },
                    'AMBER': {
                        'template': 'supply_chains/reason_for_delays.html',
                        'field': lambda self: self['reason_for_delays'],
                        'prefix': 'amber',
                    },
                }
            )
        }


class MonthlyUpdateTimingForm(forms.ModelForm):
    class Meta:
        model = StrategicAction
        fields = ['target_completion_date']