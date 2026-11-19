from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from .models import Answer, Question, Tag
from .forms import AnswerForm, AnswerVoteForm, QuestionForm, QuestionVoteForm

from .pagination import paginate


def question_vote(request, question_id):
    if request.method != "POST":
        response = JsonResponse({"error": "Разрешён только метод POST."}, status=405)
        response["Allow"] = "POST"
        return response
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Войдите, чтобы голосовать."}, status=401)
    question = Question.objects.filter(pk=question_id).first()
    if question is None:
        return JsonResponse({"error": "Вопрос не найден."}, status=404)
    form = QuestionVoteForm(request.POST, user=request.user, question=question)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    try:
        question = form.save()
    except ValidationError as error:
        form.add_error(None, error)
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    except Question.DoesNotExist:
        return JsonResponse({"error": "Вопрос не найден."}, status=404)
    return JsonResponse({
        "rating": question.rating,
        "vote_state": "liked" if form.cleaned_data["value"] == 1 else "disliked",
    })

def answer_vote(request, answer_id):
    if request.method != "POST":
        response = JsonResponse({"error": "Разрешён только метод POST."}, status=405)
        response["Allow"] = "POST"
        return response
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Войдите, чтобы голосовать."}, status=401)
    answer = Answer.objects.filter(pk=answer_id).first()
    if answer is None:
        return JsonResponse({"error": "Ответ не найден."}, status=404)
    form = AnswerVoteForm(request.POST, user=request.user, answer=answer)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    try:
        answer = form.save()
    except ValidationError as error:
        form.add_error(None, error)
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    except Answer.DoesNotExist:
        return JsonResponse({"error": "Ответ не найден."}, status=404)
    return JsonResponse({
        "rating": answer.rating,
        "vote_state": "liked" if form.cleaned_data["value"] == 1 else "disliked",
    })


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
    page = paginate(queryset.with_user_vote(request.user), request)
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
    question = get_object_or_404(Question.objects.with_card_data().with_user_vote(request.user), pk=question_id)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(question.get_absolute_url())
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(author=request.user, question=question)
            return redirect(answer)
    else:
        form = AnswerForm()
    page = paginate(Answer.objects.for_question(question.pk).ordered().with_author().with_user_vote(request.user), request)
    return render(request, "questions/question.html", {
        "title": question.title,
        "question": question,
        "answers": page,
        "answers_count": question.answers_count,
        "page_obj": page,
        "form": form,
    })
