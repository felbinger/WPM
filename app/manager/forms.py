from django.core.validators import RegexValidator
from django.forms import Form, CharField, TextInput


class NewPeerForm(Form):
    name = CharField(max_length=32, widget=TextInput(attrs={
        'placeholder': 'Name',
        'class': 'form-control',
        'maxlength': '32',
        'pattern': "[A-Za-z0-9]{1,32}",
    }), required=True, validators=[RegexValidator('[A-Za-z0-9]{1,32}')])

    public_key = CharField(max_length=44, widget=TextInput(attrs={
        'placeholder': 'Public Key',
        'class': 'form-control',
        'maxlength': '44',
        'readonly': 'true',
    }), required=True)
