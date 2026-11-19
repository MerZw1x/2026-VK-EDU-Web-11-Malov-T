from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Profile

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["password"].widget.attrs["class"] = "form-control"

class SignupForm(UserCreationForm):
    email = forms.EmailField(label="Почта")
    nickname = forms.CharField(label="Никнейм", max_length=40)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "nickname")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for v in self.fields.values():
            v.widget.attrs["class"] = "form-control"

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                nickname=self.cleaned_data["nickname"],
            )

        return user
