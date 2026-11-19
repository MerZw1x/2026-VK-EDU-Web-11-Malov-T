from django import forms
from django.db import transaction

import re

from .models import Answer, AnswerLike, Question, QuestionLike, Tag

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


class QuestionVoteForm(forms.Form):
    value = forms.TypedChoiceField(
        choices=((1, "Лайк"), (-1, "Дизлайк")),
        coerce=int,
    )

    def __init__(self, *args, user, question, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.question = question

    def clean(self):
        cleaned_data = super().clean()
        value = cleaned_data.get("value")
        if value is None:
            return cleaned_data
        previous = QuestionLike.objects.filter(
            user=self.user, question=self.question,
        ).first()
        if previous is not None and previous.value == value:
            raise forms.ValidationError("Вы уже поставили такую оценку.")
        return cleaned_data

    @transaction.atomic
    def save(self):
        question = Question.objects.select_for_update().get(pk=self.question.pk)
        value = self.cleaned_data["value"]
        previous = QuestionLike.objects.filter(
            user=self.user, question=question,
        ).first()
        old_value = previous.value if previous is not None else 0
        if old_value == value:
            raise forms.ValidationError("Вы уже поставили такую оценку.")
        QuestionLike.objects.update_or_create(
            user=self.user,
            question=question,
            defaults={"value": value},
        )
        question.rating += value - old_value
        question.save(update_fields=["rating"])
        return question


class AnswerVoteForm(forms.Form):
    value = forms.TypedChoiceField(
        choices=((1, "Лайк"), (-1, "Дизлайк")),
        coerce=int,
    )

    def __init__(self, *args, user, answer, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.answer = answer

    def clean(self):
        cleaned_data = super().clean()
        value = cleaned_data.get("value")
        if value is None:
            return cleaned_data
        previous = AnswerLike.objects.filter(
            user=self.user, answer=self.answer,
        ).first()
        if previous is not None and previous.value == value:
            raise forms.ValidationError("Вы уже поставили такую оценку.")
        return cleaned_data

    @transaction.atomic
    def save(self):
        answer = Answer.objects.select_for_update().get(pk=self.answer.pk)
        value = self.cleaned_data["value"]
        previous = AnswerLike.objects.filter(
            user=self.user, answer=answer,
        ).first()
        old_value = previous.value if previous is not None else 0
        if old_value == value:
            raise forms.ValidationError("Вы уже поставили такую оценку.")
        AnswerLike.objects.update_or_create(
            user=self.user,
            answer=answer,
            defaults={"value": value},
        )
        answer.rating += value - old_value
        answer.save(update_fields=["rating"])
        return answer

