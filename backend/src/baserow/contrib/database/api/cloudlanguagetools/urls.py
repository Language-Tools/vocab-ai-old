from django.urls import re_path

from .views import CloudLanguageToolsLanguageDataView


app_name = "baserow.contrib.database.api.cloudlanguagetools"

urlpatterns = [
    re_path(r"language_data/$", CloudLanguageToolsLanguageDataView.as_view(), name="list"),
]
