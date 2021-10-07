from django import forms


class FillupForm(forms.Form):
    # vehicle =
    distance = forms.FloatField(label="Total odometer")
    price = forms.DecimalField(
        label="Price per unit", decimal_places=3, max_digits=5)
    amount = forms.FloatField(label="Total filled up amount")
