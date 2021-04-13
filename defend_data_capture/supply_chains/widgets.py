from django.forms.widgets import RadioSelect, Textarea


class GDSRadioSelect(RadioSelect):
    def __init__(self, attrs=None, choices=()):
        if attrs is None:
            attrs = {}
        if "class" not in attrs.keys():
            attrs["class"] = "govuk-radios__input"
        super().__init__(attrs, choices)


class HintedFieldMixin:
    def __init__(self, hint=None, attrs=None, **kwargs):
        attrs = kwargs.get("attrs", {})
        super().__init__(**kwargs)
        self.hint = hint


class HintedSelectMixin:
    def __init__(self, hints=None, **kwargs):
        super().__init__(**kwargs)
        self.hints: dict = {} if hints is None else hints

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        if value in self.hints.keys():
            option["dit_hint"] = self.hints[value]
        return option


class DetailSelectMixin:
    def __init__(self, details=None, **kwargs):
        super().__init__(**kwargs)
        self.details = {} if details is None else details

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        if value in self.details.keys():
            option["dit_detail"] = self.details[value]
            try:
                option["attrs"]["data-aria-controls"] = option["attrs"][
                    "data-aria-controls"
                ].format(**option["attrs"])
            except KeyError:
                pass
        else:
            try:
                option["attrs"].pop("data-aria-controls")
            except KeyError:
                pass
        return option

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["has_details"] = bool(self.details)
        # context['subwidgets'] = self.subwidgets(name, value, attrs)
        return context


class HintedRadioSelect(HintedSelectMixin, RadioSelect):
    template_name = "supply_chains/forms/widgets/gds-radio-group.html"
    option_template_name = "supply_chains/forms/widgets/gds-radio-option.html"


class HintedDetailRadioSelect(DetailSelectMixin, HintedSelectMixin, RadioSelect):
    template_name = "supply_chains/forms/widgets/gds-radio-group.html"
    option_template_name = "supply_chains/forms/widgets/gds-radio-option.html"


class DetailRadioSelect(DetailSelectMixin, RadioSelect):
    template_name = "supply_chains/forms/widgets/gds-radio-group.html"
    option_template_name = "supply_chains/forms/widgets/gds-radio-option.html"
