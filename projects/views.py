from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from common.constants import PAGE_SIZE
from common.pagination import paginate
from .forms import ProjectForm
from .models import Project


@require_GET
def project_list(request):
    qs = Project.objects.select_related("owner").prefetch_related("participants").order_by("-created_at")
    pg = paginate(request, qs, per_page=PAGE_SIZE)
    return render(
        request,
        "projects/project_list.html",
        {"projects": qs, "page_obj": pg.page_obj, "query_prefix": pg.query_prefix},
    )


@require_GET
def project_details(request, project_id: int):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants", "owner__favorites"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(reverse("projects:details", kwargs={"project_id": project.id}))
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id: int):
    project = get_object_or_404(Project, pk=project_id)
    if not (request.user.is_staff or project.owner_id == request.user.id):
        raise Http404
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(reverse("projects:details", kwargs={"project_id": project.id}))
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@require_POST
@login_required
def complete_project(request, project_id: int):
    project = get_object_or_404(Project, pk=project_id)
    if not (request.user.is_staff or project.owner_id == request.user.id):
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@require_POST
@login_required
def toggle_participate(request, project_id: int):
    project = get_object_or_404(Project.objects.prefetch_related("participants"), pk=project_id)
    exists = project.participants.filter(pk=request.user.pk).exists()
    if exists:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not exists})


@require_POST
@login_required
def toggle_favorite(request, project_id: int):
    project = get_object_or_404(Project, pk=project_id)
    exists = request.user.favorites.filter(pk=project.pk).exists()
    if exists:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not exists})


@require_GET
@login_required
def favorite_projects(request):
    qs = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    return render(request, "projects/favorite_projects.html", {"projects": qs})

