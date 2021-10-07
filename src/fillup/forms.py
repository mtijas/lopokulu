from django.forms import ModelForm
from .models.fillups import Fillup


class FillupForm(ModelForm):
    class Meta:
        model = Fillup
        fields = ['price', 'amount', 'distance', 'vehicle']
