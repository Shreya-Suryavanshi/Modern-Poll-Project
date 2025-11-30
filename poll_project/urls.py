from django.contrib import admin
from django.urls import path
from pollapp.views import (
    usignup, ulogin, home, create, view, result, ulogout,
    create_category, dashboard, vote_ajax
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("usignup/", usignup, name="usignup"),
    path("ulogin/", ulogin, name="ulogin"),
    path("ulogout/", ulogout, name="ulogout"),
    path("create/", create, name="create"),
    path("create-category/", create_category, name="create_category"),
    path("dashboard/", dashboard, name="dashboard"),
    path("view/<int:poll_id>/", view, name="view"),
    path("result/<int:poll_id>/", result, name="result"),
    path("api/vote/<int:poll_id>/", vote_ajax, name="vote_ajax"),
]
