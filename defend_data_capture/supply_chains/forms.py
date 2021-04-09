from django import forms
from django.db.models import TextChoices
from django.forms.utils import ErrorList

from .widgets import DetailSelectMixin, HintedDetailRadioSelect
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


class AmberReasonForDelayForm(forms.ModelForm):
    class Meta:
        model = StrategicActionUpdate
        fields = ['reason_for_delays']
        labels  = {
            "reason_for_delays": "Explain potential risk"
        }
        widgets = {
            "reason_for_delays": forms.Textarea(attrs={
                "class": "govuk-textarea"
            })
        }


class RedReasonForDelayForm(AmberReasonForDelayForm):
    class YesNoChoices(TextChoices):
        YES = (True, "Yes")
        NO = (False, "No")

    will_completion_date_change = forms.ChoiceField(
        choices=YesNoChoices.choices,
        widget=forms.RadioSelect(attrs={'class': 'govuk-radios__input'}),
        label='Will the estimated completion date change?'
    )

    class Meta(AmberReasonForDelayForm.Meta):
        labels = {
            "reason_for_delays": "Explain issue"
        }


class MonthlyUpdateStatusForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if isinstance(field.widget, DetailSelectMixin):
                for key, config in field.widget.details.items():
                    try:
                        form_class = config['form_class']
                        kwargs['prefix'] = key
                        config['form'] = form_class(*args, **kwargs)
                    except KeyError:
                        pass

    class Meta:
        model = StrategicActionUpdate
        fields = ['implementation_rag_rating']
        widgets = {
            'implementation_rag_rating': HintedDetailRadioSelect(attrs={
                    'class': 'govuk-radios__input',
                    'data-aria-controls': "{id}-detail"
                },
                hints=RAGRatingHints,
                details = {
                    'RED': {
                        'template': 'supply_chains/includes/reason-for-delays.html',
                        'form_class': RedReasonForDelayForm,
                    },
                    'AMBER': {
                        'template': 'supply_chains/includes/reason-for-delays.html',
                        'form_class': AmberReasonForDelayForm,
                    },
                }
            )
        }
        labels = {
            'implementation_rag_rating': "Current delivery status"
        }


class MonthlyUpdateTimingForm(forms.ModelForm):
    class Meta:
        model = StrategicAction
        fields = ['target_completion_date']