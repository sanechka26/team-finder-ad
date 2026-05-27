from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from projects.models import Project

from .forms import ChangePasswordForm, LoginForm, ProfileEditForm, RegisterForm
from .models import User


@require_GET
def user_list(request):
    qs = User.objects.all().order_by("id")
    active_filter = None

    raw_filter = request.GET.get("filter")
    if raw_filter and request.user.is_authenticated:
        # Support both spec keys and template keys.
        mapping = {
            "favorites_authors": "owners-of-favorite-projects",
            "my_projects_authors": "owners-of-participating-projects",
            "liked_my_projects": "interested-in-my-projects",
            "my_projects_participants": "participants-of-my-projects",
        }
        active_filter = mapping.get(raw_filter, raw_filter)

        if active_filter == "owners-of-favorite-projects":
            owner_ids = request.user.favorites.values_list("owner_id", flat=True).distinct()
            qs = qs.filter(id__in=owner_ids)
        elif active_filter == "owners-of-participating-projects":
            owner_ids = (
                Project.objects.filter(participants=request.user)
                .values_list("owner_id", flat=True)
                .distinct()
            )
            qs = qs.filter(id__in=owner_ids)
        elif active_filter == "interested-in-my-projects":
            my_project_ids = Project.objects.filter(owner=request.user).values_list("id", flat=True)
            qs = qs.filter(favorites__id__in=my_project_ids).distinct()
        elif active_filter == "participants-of-my-projects":
            my_project_ids = Project.objects.filter(owner=request.user).values_list("id", flat=True)
            qs = qs.filter(participated_projects__id__in=my_project_ids).distinct()

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_prefix = ""
    if active_filter:
        query_prefix = f"filter={active_filter}&"
    return render(
        request,
        "users/participants.html",
        {
            "participants": qs,
            "page_obj": page_obj,
            "active_filter": active_filter,
            "query_prefix": query_prefix,
        },
    )


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/projects/list/")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect("/projects/list/")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


@require_GET
def user_details(request, user_id: int):
    user = (
        User.objects.prefetch_related("owned_projects", "participated_projects")
        .filter(pk=user_id)
        .first()
    )
    if not user:
        raise Http404
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f"/users/{request.user.id}/")
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Keep session by re-login
            login(request, request.user)
            return redirect(f"/users/{request.user.id}/")
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, "users/change_password.html", {"form": form})

