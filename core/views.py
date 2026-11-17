from django.shortcuts import render


def login(request):
    return render(request, "core/login.html", {"title": "Вход"})


def signup(request):
    return render(request, "core/signup.html", {"title": "Регистрация"})


def profile(request):
    context = {"title": "Настройки профиля", "show_profile_user": True}
    return render(request, "core/profile.html", context)
