from django.contrib import admin
from django.urls import path
from monitoring import views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("records/", views.records, name="records"),
    path("alerts/", views.alerts, name="alerts"),
    path("analyze/", views.analyze, name="analyze"),
]
