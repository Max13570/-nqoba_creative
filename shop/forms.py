import re

from django import forms
from django.utils import timezone

from .models import Enquiry, Order, Service

PHONE_PATTERN = re.compile(r'^\+?[\d\s\-()]{7,20}$')


class OrderForm(forms.ModelForm):
    """Customer order form. `website` is a hidden spam trap."""

    website = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = [
            'customer_name',
            'whatsapp',
            'email',
            'service',
            'quantity',
            'deadline',
            'details',
        ]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'details': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['service'].empty_label = 'Choose a service'

        self.fields['deadline'].widget.attrs['min'] = timezone.localdate().isoformat()
        self.fields['quantity'].widget.attrs.update({'min': 1, 'max': 1000})

    def clean_whatsapp(self):
        value = self.cleaned_data['whatsapp'].strip()

        if not PHONE_PATTERN.match(value):
            raise forms.ValidationError(
                'Enter a valid phone number, for example +268 7833 6238.'
            )

        return value

    def clean_quantity(self):
        value = self.cleaned_data['quantity']

        if value < 1 or value > 1000:
            raise forms.ValidationError('Quantity must be between 1 and 1000.')

        return value

    def clean_deadline(self):
        value = self.cleaned_data['deadline']

        if value < timezone.localdate():
            raise forms.ValidationError('The deadline cannot be in the past.')

        return value

    def clean_details(self):
        value = self.cleaned_data['details'].strip()

        if len(value) < 10:
            raise forms.ValidationError(
                'Please describe what you need in a little more detail.'
            )

        return value


class EnquiryForm(forms.ModelForm):
    """Contact page form. `website` is a hidden spam trap."""

    website = forms.CharField(required=False)

    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'phone', 'service', 'budget', 'message']

    def clean_phone(self):
        value = self.cleaned_data['phone'].strip()

        if not PHONE_PATTERN.match(value):
            raise forms.ValidationError(
                'Enter a valid phone number, for example +268 7833 6238.'
            )

        return value

    def clean_message(self):
        value = self.cleaned_data['message'].strip()

        if len(value) < 10:
            raise forms.ValidationError(
                'Please tell us a little more about your project.'
            )

        return value
