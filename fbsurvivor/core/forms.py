from django import forms


class PlayerForm(forms.Form):
    username = forms.CharField(label="username", max_length=20)
    email = forms.EmailField(label="email (won't be displayed)")


class CodeForm(forms.Form):
    confirmation_code = forms.CharField(max_length=6)


class EmailForm(forms.Form):
    email = forms.EmailField(label="email")
