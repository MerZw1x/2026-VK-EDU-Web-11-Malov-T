from django.urls import path

from . import views

app_name = "questions"

urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("tag/<slug:tag_slug>/", views.tag, name="tag"),
    path("question/<int:question_id>/", views.detail, name="detail"),
    path("question/<int:question_id>/vote/", views.question_vote, name="question_vote"),
    path("answer/<int:answer_id>/vote/", views.answer_vote, name="answer_vote"),
    path("ask/", views.ask, name="ask"),
]
