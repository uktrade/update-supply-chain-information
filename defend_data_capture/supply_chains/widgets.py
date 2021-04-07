from django.forms.widgets import RadioSelect


class HintedRadioSelect(RadioSelect):

    def __init__(self, attrs=None, choices=(), hints=None):
        super().__init__(attrs, choices)
        self.hints: dict = hints

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option =  super().create_option(name, value, label, selected, index, subindex, attrs)
        if value in self.hints.keys():
            option['dit_hint'] = self.hints[value]
        return option


