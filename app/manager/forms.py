from django.core.validators import RegexValidator
from django.forms import Form, CharField, TextInput


class NewPeerForm(Form):
    name_re = '^[A-Za-z0-9]{1,32}$'
    name = CharField(max_length=32, widget=TextInput(attrs={
        'placeholder': 'Name',
        'class': 'form-control',
        'maxlength': '32',
        'pattern': name_re,
    }), required=True, validators=[RegexValidator(name_re)])

    public_key_re = '^[A-Za-z0-9+/]{43}=$'
    public_key = CharField(max_length=44, widget=TextInput(attrs={
        'placeholder': 'Public Key',
        'class': 'form-control',
        'maxlength': '44',
        'pattern': public_key_re,
    }), required=True, validators=[RegexValidator(public_key_re)])
