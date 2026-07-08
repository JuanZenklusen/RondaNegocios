from crispy_forms.helper import FormHelper
from django import forms
from django.forms import inlineformset_factory

from .models import Activity, Event


class _DateInput(forms.DateInput):
    input_type = "date"


class _DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "name",
            "description",
            "event_type",
            "modality",
            "status",
            "start_date",
            "end_date",
            "location",
            "address",
            "cover",
            "capacity",
            "general_price",
            "is_public",
            "meeting_duration_minutes",
            "meetings_per_company",
            "tables_count",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "start_date": _DateInput(format="%Y-%m-%d"),
            "end_date": _DateInput(format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "La fecha de fin no puede ser anterior al inicio.")
        return cleaned


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["title", "activity_type", "start", "end", "room", "capacity", "is_public"]
        widgets = {
            "start": _DateTimeInput(format="%Y-%m-%dT%H:%M"),
            "end": _DateTimeInput(format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # datetime-local necesita este formato para poblar valores existentes.
        self.fields["start"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end"].input_formats = ["%Y-%m-%dT%H:%M"]
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select form-select-sm")
            else:
                field.widget.attrs.setdefault("class", "form-control form-control-sm")


ActivityFormSet = inlineformset_factory(
    Event, Activity, form=ActivityForm, extra=1, can_delete=True
)
