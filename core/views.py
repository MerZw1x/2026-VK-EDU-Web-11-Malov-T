from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from core.forms import LoginForm, SignupForm, ProfileForm

class SiteLoginView(LoginView):
    template_name = "core/login.html"
    authentication_form = LoginForm
    extra_context = {"title": "Вход"}

class SiteLogoutView(LogoutView):
    next_page = "questions:index"

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("questions:index")
    else:
        form = SignupForm()

    return render(
        request,
        "core/signup.html",
        {"title": "Регистрация", "form": form},
    )

@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            instance=request.user.profile,
        )
        if form.is_valid():
            form.save()
            return redirect("core:profile")
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(
        request,
        "core/profile.html",
        {"title": "Профиль", "form": form},
    )
