from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from core.models import Profile

# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 1
    max_num = 1

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

User = get_user_model()
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "nickname"]

    search_fields = [
        "user__username",
        "nickname",
    ]

    list_filter = ["user__is_active"]

    list_select_related = ["user"]
    raw_id_fields = ["user"]

admin.site.register(Profile, ProfileAdmin)
