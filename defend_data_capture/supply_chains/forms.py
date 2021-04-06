from django import forms
from .models import StrategicActionUpdate


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
        fields = ['implementation_rag_rating',]
        widgets = {
            'content': forms.RadioSelect(attrs={
                'class': 'govuk-radios__input',
            })
        }
