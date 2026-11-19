from django import forms
from django.db import transaction

import re

from .models import Answer, Question, Tag

class QuestionForm(forms.ModelForm):
    tags = forms.CharField(label="Теги", required=False, max_length=100, help_text="Через запятую, не больше 3 тегов.")
    class Meta:
        model = Question
        fields = ("title", "text", "tags")
        widgets = {
            "text": forms.Textarea(attrs={"rows": 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_tags(self):
        raw_tags = self.cleaned_data.get("tags", "")
        seen = set()
        result = []
        for tag in raw_tags.split(","):
            tag = tag.strip().lower()
            if not tag:
                continue
            if tag in seen:
                continue
            if len(tag) > 50:
                raise forms.ValidationError(f"Тег '{tag}' длиннее 50 символов")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", tag):
                raise forms.ValidationError(
                    f"Тег '{tag}' содержит недопустимые символы "
                    "Разрешены латиница, цифры и дефис (не в начале/конце и не подряд)"
                )
            seen.add(tag)
            result.append(tag)

        if len(result) > 3:
            raise forms.ValidationError("Не больше 3 уникальных тегов")

        return result

    @transaction.atomic
    def save(self, author):
        question = super().save(commit=False)
        question.author = author
        question.save()

        tag_objs = []
        for name in self.cleaned_data.get("tags", []):
            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={"slug": name},
            )
            tag_objs.append(tag)

        question.tags.set(tag_objs)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 6,
                "class": "form-control answer-form__textarea",
                "placeholder": "Напишите ваш ответ...",
                "aria-describedby": "answer-help",
            }),
        }

    def save(self, author, question):
        answer = super().save(commit=False)
        answer.author = author
        answer.question = question
        answer.save()
        return answer

