from django.core.paginator import Paginator
from django.db.models import Q


def sort_queryset(queryset, request, default_sort='-created_at', allowed_fields=None):
    sort_field = request.GET.get('sort', '')
    order = request.GET.get('order', '')
    if not sort_field:
        sort_field = default_sort
        sort_field_clean = sort_field.lstrip('-')
    else:
        if sort_field.startswith('-'):
            sort_field_clean = sort_field[1:]
        else:
            sort_field_clean = sort_field
        if allowed_fields and sort_field_clean not in allowed_fields:
            sort_field = default_sort
            sort_field_clean = default_sort.lstrip('-')
        if not order:
            order = 'desc' if sort_field.startswith('-') else 'asc'
        if order == 'desc':
            if not sort_field.startswith('-'):
                sort_field = f'-{sort_field}'
        else:
            sort_field = sort_field_clean
    return queryset.order_by(sort_field), sort_field_clean, order


def paginate(queryset, request, per_page=15):
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page)
    return page_obj, paginator


def build_search_filter(queryset, request, fields):
    search = request.GET.get('search', '').strip()
    if search:
        q_objects = Q()
        for field in fields:
            q_objects |= Q(**{f'{field}__icontains': search})
        queryset = queryset.filter(q_objects)
    return queryset, search


def get_sortable_context(request, queryset, default_sort='-created_at', allowed_fields=None, search_fields=None, per_page=15):
    queryset, sort_field, order = sort_queryset(queryset, request, default_sort, allowed_fields)
    search_term = ''
    if search_fields:
        queryset, search_term = build_search_filter(queryset, request, search_fields)
    page_obj, paginator = paginate(queryset, request, per_page)
    return {
        'page_obj': page_obj,
        'paginator': paginator,
        'sort_field': sort_field,
        'sort_order': order,
        'search': search_term,
    }
