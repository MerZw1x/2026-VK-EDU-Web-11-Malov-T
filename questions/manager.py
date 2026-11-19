from django.db import models


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(questions_count=models.Count("questions")).order_by(
            "-questions_count", "id",
        )


class TagManager(models.Manager.from_queryset(TagQuerySet)):
    pass


class QuestionQuerySet(models.QuerySet):
    def with_user_vote(self, user):
        from .models import QuestionLike

        votes = QuestionLike.objects.filter(user=user) if user.is_authenticated else QuestionLike.objects.none()
        return self.prefetch_related(models.Prefetch("likes", queryset=votes, to_attr="user_votes"))

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
    def with_user_vote(self, user):
        from .models import AnswerLike

        votes = AnswerLike.objects.filter(user=user) if user.is_authenticated else AnswerLike.objects.none()
        return self.prefetch_related(models.Prefetch("likes", queryset=votes, to_attr="user_votes"))

    def before(self, answer):
        earlier = models.Q(created_at__lt=answer.created_at) | models.Q(
            created_at=answer.created_at, pk__lt=answer.pk,
        )
        if answer.is_correct:
            return self.filter(is_correct=True).filter(earlier)
        return self.filter(models.Q(is_correct=True) | earlier)

    def for_question(self, question_id):
        return self.filter(question_id=question_id)

    def ordered(self):
        return self.order_by("-is_correct", "created_at", "id")

    def with_author(self):
        return self.select_related("author__profile")

class AnswerManager(models.Manager.from_queryset(AnswerQuerySet)):
    pass
