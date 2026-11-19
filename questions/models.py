from django.conf import settings
from django.db import models
from django.urls import reverse

from .manager import AnswerManager, QuestionManager, TagManager
from .pagination import PER_PAGE


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Код для URL")
    objects = TagManager()
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
    
    def __str__(self):
        return f"Тег #{self.id}: {self.name}"

class Question(models.Model):
    author = models.ForeignKey (
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="questions",
        verbose_name="Автор",
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    text = models.TextField(max_length=10000, verbose_name="Текст вопроса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")

    tags = models.ManyToManyField(
        Tag,
        related_name="questions",
        blank=True,
        verbose_name="Теги"
    )

    objects = QuestionManager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

        indexes = [  # noqa: RUF012
            models.Index(fields=["-created_at", "-id"], name="question_new_idx"),
            models.Index(fields=["-rating", "-id"], name="question_hot_idx"),
        ]

    
    def __str__(self):
        return f"Вопрос #{self.id}; Заголовок: {self.title}"

    def get_absolute_url(self):
        return reverse("questions:detail", kwargs={"question_id": self.pk})

    @property
    def vote_state(self):
        votes = getattr(self, "user_votes", [])
        if not votes:
            return ""
        return "liked" if votes[0].value == 1 else "disliked"


class Answer(models.Model):
    author = models.ForeignKey (
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="answers",
        verbose_name="Автор",
        null=True,
        blank=True
    )

    question = models.ForeignKey (
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )

    text = models.TextField(max_length=5000, verbose_name="Текст ответа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    is_correct = models.BooleanField("Правильный ответ", default=False)

    objects = AnswerManager()

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
    
    def __str__(self):
        return f"Ответ #{self.id} на вопрос #{self.question_id}"

    def get_absolute_url(self):
        preceding = Answer.objects.for_question(self.question_id).before(self).count()
        page_number = preceding // PER_PAGE + 1
        url = reverse("questions:detail", kwargs={"question_id": self.question_id})
        return f"{url}?page={page_number}#answer-{self.pk}"

    @property
    def vote_state(self):
        votes = getattr(self, "user_votes", [])
        if not votes:
            return ""
        return "liked" if votes[0].value == 1 else "disliked"

class QuestionLike(models.Model):
    user = models.ForeignKey (
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_like",
        verbose_name="Пользователь",
    )

    question = models.ForeignKey (
        Question,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Вопрос",
    )

    value = models.SmallIntegerField(
        verbose_name="Оценка",
        choices=[(1, "Лайк"), (-1, "Дизлайк")]
    )

    class Meta:
        verbose_name = "Лайк на вопрос"
        verbose_name_plural = "Лайки на вопрос"

        unique_together = [("user", "question")]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(value__in=[-1, 1]),
                name="question_like_value_valid",
            ),
        ]   

class AnswerLike(models.Model):
    user = models.ForeignKey (
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answer_like",
        verbose_name="Пользователь",
    )

    answer = models.ForeignKey (
        Answer,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Ответ",
    )

    value = models.SmallIntegerField(
        verbose_name="Оценка",
        choices=[(1, "Лайк"), (-1, "Дизлайк")]
    )

    class Meta:
        verbose_name = "Лайк на ответ"
        verbose_name_plural = "Лайки на ответ"

        unique_together = [("user", "answer")]
    
        constraints = [
            models.CheckConstraint(
                condition=models.Q(value__in=[-1, 1]),
                name="answer_like_value_valid",
            ),
        ]   

