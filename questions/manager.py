from django.db import models


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(questions_count=models.Count("questions")).order_by(
            "-questions_count", "id",
        )


class TagManager(models.Manager.from_queryset(TagQuerySet)):
    pass


class QuestionQuerySet(models.QuerySet):
    def new(self):
        return self.order_by("-created_at", "-id")

    def best(self):
        return self.order_by("-rating", "-id")

    def by_tag(self, slug):
        return self.filter(tags__slug=slug)
    
    def with_card_data(self):
        return (
            self.select_related("author__profile")
            .prefetch_related("tags")
            .annotate(answers_count=models.Count("answers"))
        )

class QuestionManager(models.Manager.from_queryset(QuestionQuerySet)):
    pass

class AnswerQuerySet(models.QuerySet):
    def for_question(self, question_id):
        return self.filter(question_id=question_id)

    def ordered(self):
        return self.order_by("-is_correct", "created_at", "id")

    def with_author(self):
        return self.select_related("author__profile")

class AnswerManager(models.Manager.from_queryset(AnswerQuerySet)):
    pass
