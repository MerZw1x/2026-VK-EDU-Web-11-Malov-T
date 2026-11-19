from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login

from .models import Answer, Question, Tag
from .forms import AnswerForm, QuestionForm

from .pagination import paginate

@login_required
def ask(request):
    if request.method == "POST":
        form = QuestionForm(
            request.POST,
        )
        if form.is_valid():
            question = form.save(author=request.user)
            return redirect(question)
    else:
        form = QuestionForm()

    return render(
        request,
        "questions/ask.html",
        {"title": "Задать вопрос", "form": form},
    )

def _render_list(request, template_name, title, queryset):
    page = paginate(queryset, request)
    return render(request, template_name, {
        "title": title,
        "questions": page,
        "page_obj": page,
    })


def index(request):
    questions = Question.objects.new().with_card_data()
    return _render_list(request, "questions/index.html", "Новые вопросы", questions)


def hot(request):
    questions = Question.objects.best().with_card_data()
    return _render_list(request, "questions/hot.html", "Горячие вопросы", questions)


def tag(request, tag_slug):
    selected_tag = get_object_or_404(Tag, slug=tag_slug)
    questions = Question.objects.by_tag(selected_tag.slug).new().with_card_data()
    return _render_list(
        request, "questions/tag.html", f"Вопросы по тегу {selected_tag.name}", questions,
    )


def detail(request, question_id):
    question = get_object_or_404(Question.objects.with_card_data(), pk=question_id)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(question.get_absolute_url())
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(author=request.user, question=question)
            return redirect(answer)
    else:
        form = AnswerForm()
    page = paginate(Answer.objects.for_question(question.pk).ordered().with_author(), request)
    return render(request, "questions/question.html", {
        "title": question.title,
        "question": question,
        "answers": page,
        "answers_count": question.answers_count,
        "page_obj": page,
        "form": form,
    })
