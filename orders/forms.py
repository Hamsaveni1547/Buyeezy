# orders/forms.py
from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'state', 'postal_code', 'payment_method'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'payment_method': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'payment_method':
                field.widget.attrs['class'] = 'form-control'
            field.required = True