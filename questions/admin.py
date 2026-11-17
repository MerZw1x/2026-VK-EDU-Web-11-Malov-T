from django.contrib import admin
from django.db import models
from questions.models import Question, Tag, Answer, AnswerLike, QuestionLike

# Register your models here.
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ["author", "text", "is_correct"]
    readonly_fields = ["author"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")

class HasQuestionsFilter(admin.SimpleListFilter):
    title = "Наличие вопросов"
    parameter_name = "has_questions"

    def lookups(self, request, model_admin):
        return [("yes", "Есть вопросы"), ("no", "Нет вопросов")]

    def queryset(self, request, queryset):
        exists = models.Exists(
            Question.tags.through.objects.filter(tag_id=models.OuterRef("pk"))
        )
        if self.value() == "yes":
            return queryset.filter(exists)
        if self.value() == "no":
            return queryset.filter(~exists)
        return queryset


class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "author",
        "rating",
        "created_at",
    ]

    search_fields = [
        "title",
        "text",
        "author__username",
    ]

    list_filter = ["created_at"]

    list_select_related = ["author"]

    raw_id_fields = ["author"]          
    autocomplete_fields = ["tags"]   

    inlines = [AnswerInline]   

class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]

    search_fields = ["name", "slug"]

    list_filter = [HasQuestionsFilter]

class AnswerAdmin(admin.ModelAdmin):
    list_display = ["id", "question", "author", "is_correct", "rating"]

    search_fields = ["text", "author__username"]

    list_filter = ["is_correct", "created_at"]

    list_select_related = ["author", "question"]
    raw_id_fields = ["author", "question"] 

class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "answer", "value"]

    search_fields = ["user__username"]

    list_filter = ["value"]

    list_select_related = ["user", "answer"]
    raw_id_fields = ["user", "answer"] 

class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "question", "value"]

    search_fields = ["user__username"]

    list_filter = ["value"]

    list_select_related = ["user", "question"]
    raw_id_fields = ["user", "question"] 

admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerLike, AnswerLikeAdmin)
admin.site.register(QuestionLike, QuestionLikeAdmin)
