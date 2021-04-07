from django.forms.widgets import RadioSelect


class HintedSelectMixin:
    def __init__(self, hints=None, **kwargs):
        super().__init__(**kwargs)
        self.hints: dict = {} if hints is None else hints

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option =  super().create_option(name, value, label, selected, index, subindex, attrs)
        if value in self.hints.keys():
            option['dit_hint'] = self.hints[value]
        return option


class DisclosingSelectMixin:

    def __init__(self, disclosures=None, **kwargs):
        super().__init__(**kwargs)
        self.disclosures = {} if disclosures is None else disclosures

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option =  super().create_option(name, value, label, selected, index, subindex, attrs)
        if value in self.disclosures.keys():
            option['dit_disclosure'] = self.disclosures[value]
            try:
                option['attrs']['data-aria-controls'] = option['attrs']['data-aria-controls'].format(**option['attrs'])
            except KeyError:
                pass
        else:
            try:
                option['attrs'].pop('data-aria-controls')
            except KeyError:
                pass
        return option



class HintedRadioSelect(HintedSelectMixin, RadioSelect):
    pass


class HintedDisclosingRadioSelect(DisclosingSelectMixin, HintedSelectMixin, RadioSelect):
    pass
