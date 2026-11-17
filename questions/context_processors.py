from .models import Tag


def sidebar(request):
    return {"popular_tags": Tag.objects.popular()[:10]}
