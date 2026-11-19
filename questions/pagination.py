from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


PER_PAGE = 10


def paginate(objects_list, request, per_page=PER_PAGE):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get("page", "1")

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(1)

    page.visible_pages = list(
        paginator.get_elided_page_range(
            page.number,
            on_each_side=2,
            on_ends=1,
        )
    )

    return page
