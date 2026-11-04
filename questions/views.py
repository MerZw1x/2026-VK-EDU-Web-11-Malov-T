from collections import Counter

from django.http import Http404
from django.shortcuts import render

from .mock_data import ANSWERS, QUESTIONS
from .pagination import paginate


def _render_question_list(request, template_name, title, questions):
    answer_counts = Counter(answer["question_id"] for answer in ANSWERS)
    questions = [
        {**question, "answers_count": answer_counts[question["id"]]}
        for question in questions
    ]
    page_obj = paginate(questions, request, per_page=2)
    return render(request, template_name, {
        "title": title,
        "questions": page_obj,
        "page_obj": page_obj,
    })


def index(request):
    return _render_question_list(request, "questions/index.html", "Новые вопросы", QUESTIONS)


def detail(request, question_id):
    question = next(
        (item for item in QUESTIONS if item["id"] == question_id),
        None,
    )
    if question is None:
        raise Http404("Вопрос не найден")

    answers = [answer for answer in ANSWERS if answer["question_id"] == question_id]
    page_obj = paginate(answers, request, per_page=3)
    context = {
        "title": question["title"],
        "question": question,
        "answers": page_obj,
        "answers_count": len(answers),
        "page_obj": page_obj,
    }
    return render(request, "questions/question.html", context)


def hot(request):
    questions = sorted(QUESTIONS, key=lambda question: question["score"], reverse=True)
    return _render_question_list(request, "questions/hot.html", "Горячие вопросы", questions)


def tag(request, tag_slug):
    questions = [question for question in QUESTIONS if tag_slug in question["tags"]]
    return _render_question_list(
        request, "questions/tag.html", f"Вопросы по тегу {tag_slug}", questions,
    )


def ask(request):
    return render(request, "questions/ask.html", {"title": "Задать вопрос"})
