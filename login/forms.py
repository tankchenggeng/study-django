from django import forms
from materialsystem import models

class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["username",
                  "password",
                  ]

