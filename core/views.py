from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect

from core.forms import LoginForm, SignupForm

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

def profile(request):
    context = {"title": "Настройки профиля"}
    return render(request, "core/profile.html", context)
