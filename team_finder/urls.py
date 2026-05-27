from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import include, path, reverse

urlpatterns = [
    path("", lambda request: redirect(reverse("projects:list"), permanent=False)),
    path("admin/", admin.site.urls),
    path("projects/", include(("projects.urls", "projects"), namespace="projects")),
    path("users/", include(("users.urls", "users"), namespace="users")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
