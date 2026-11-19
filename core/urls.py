from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("login/", views.SiteLoginView.as_view(), name="login"),
    path("logout/", views.SiteLogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
]
