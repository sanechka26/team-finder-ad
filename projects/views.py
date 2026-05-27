from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import ProjectForm
from .models import Project


@require_GET
def project_list(request):
    qs = Project.objects.select_related("owner").prefetch_related("participants").order_by("-created_at")
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_prefix = ""
    return render(
        request,
        "projects/project_list.html",
        {"projects": qs, "page_obj": page_obj, "query_prefix": query_prefix},
    )


@require_GET
def project_details(request, project_id: int):
    project = (
        Project.objects.select_related("owner")
        .prefetch_related("participants", "owner__favorites")
        .filter(pk=project_id)
        .first()
    )
    if not project:
        raise Http404
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id: int):
    project = get_object_or_404(Project, pk=project_id)
    if not (request.user.is_staff or project.owner_id == request.user.id):
        raise Http404
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@require_POST
@login_required
def complete_project(request, project_id: int):
    project = get_object_or_404(Project, pk=project_id)
    if not (request.user.is_staff or project.owner_id == request.user.id):
        return JsonResponse({"status": "error"}, status=403)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=400)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@require_POST
@login_required
def toggle_participate(request, project_id: int):
    project = get_object_or_404(Project.objects.prefetch_related("participants"), pk=project_id)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@require_POST
@login_required
def toggle_favorite(request, project_id: int):
    project = get_object_or_404(Project, pk=project_id)
    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@require_GET
@login_required
def favorite_projects(request):
    qs = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    return render(request, "projects/favorite_projects.html", {"projects": qs})

