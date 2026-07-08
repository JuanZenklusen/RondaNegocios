from crispy_forms.helper import FormHelper
from django import forms
from django.forms import inlineformset_factory

from .models import Company, Need, Product, Service
from .validators import format_cuit, normalize_cuit, validate_cuit


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "razon_social",
            "nombre_fantasia",
            "cuit",
            "rubro",
            "description",
            "logo",
            "website",
            "email",
            "phone",
            "linkedin",
            "instagram",
            "facebook",
            "address",
            "city",
            "province",
            "country",
            "employees_count",
            "production_capacity",
            "certifications",
            "is_public",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "production_capacity": forms.Textarea(attrs={"rows": 2}),
            "certifications": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # el <form> y los formsets los pone el template
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean_cuit(self):
        cuit = self.cleaned_data.get("cuit", "")
        if not cuit or not normalize_cuit(cuit):
            return None  # blanco -> None, para no romper el unique
        validate_cuit(cuit)
        return format_cuit(cuit)


class _BaseChildForm(forms.ModelForm):
    """Aplica clases de Bootstrap a los formsets hijos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control form-control-sm")


ProductForm = forms.modelform_factory(Product, fields=["name", "description"], form=_BaseChildForm)
ServiceForm = forms.modelform_factory(Service, fields=["name", "description"], form=_BaseChildForm)
NeedForm = forms.modelform_factory(Need, fields=["description"], form=_BaseChildForm)


ProductFormSet = inlineformset_factory(Company, Product, form=ProductForm, extra=1, can_delete=True)
ServiceFormSet = inlineformset_factory(Company, Service, form=ServiceForm, extra=1, can_delete=True)
NeedFormSet = inlineformset_factory(Company, Need, form=NeedForm, extra=1, can_delete=True)
