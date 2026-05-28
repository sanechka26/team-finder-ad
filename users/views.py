from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from common.constants import PAGE_SIZE
from common.pagination import paginate
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

    pg = paginate(request, qs, per_page=PAGE_SIZE, extra_params={"filter": active_filter or ""})
    return render(
        request,
        "users/participants.html",
        {
            "participants": qs,
            "page_obj": pg.page_obj,
            "active_filter": active_filter,
            "query_prefix": pg.query_prefix,
        },
    )


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect(reverse("projects:list"))
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect(reverse("projects:list"))
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse("projects:list"))


@require_GET
def user_details(request, user_id: int):
    user = get_object_or_404(
        User.objects.prefetch_related("owned_projects", "participated_projects"),
        pk=user_id,
    )
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect(reverse("users:details", kwargs={"user_id": request.user.id}))
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password(request):
    form = ChangePasswordForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        form.save()
        # Keep session by re-login
        login(request, request.user)
        return redirect(reverse("users:details", kwargs={"user_id": request.user.id}))
    return render(request, "users/change_password.html", {"form": form})

