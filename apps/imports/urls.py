from django.urls import path

from apps.imports.views.import_view import ImportExecuteView, ImportPreviewView

urlpatterns = [
    path("preview/", ImportPreviewView.as_view(), name="import-preview"),
    path("execute/", ImportExecuteView.as_view(), name="import-execute"),
]
