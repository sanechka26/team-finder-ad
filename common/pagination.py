from __future__ import annotations

from dataclasses import dataclass

from django.core.paginator import Paginator


@dataclass(frozen=True)
class PaginationResult:
    page_obj: object
    query_prefix: str


def paginate(request, queryset, *, per_page: int, extra_params: dict[str, str] | None = None) -> PaginationResult:
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))
    extra_params = extra_params or {}
    query_prefix = "&".join([f"{k}={v}" for k, v in extra_params.items() if v])
    query_prefix = (query_prefix + "&") if query_prefix else ""
    return PaginationResult(page_obj=page_obj, query_prefix=query_prefix)

