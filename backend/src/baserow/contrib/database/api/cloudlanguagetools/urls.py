from django.urls import re_path

from .views import CloudLanguageToolsLanguageList, CloudLanguageToolsTranslationOptions, CloudLanguageToolsTransliterationOptions, CloudLanguageToolsTranslationServices


app_name = "baserow.contrib.database.api.cloudlanguagetools"

urlpatterns = [
    re_path(r"language_list/$", CloudLanguageToolsLanguageList.as_view(), name="list"),
    re_path(r"translation_options/$", CloudLanguageToolsTranslationOptions.as_view(), name="list"),
    re_path(r"transliteration_options/$", CloudLanguageToolsTransliterationOptions.as_view(), name="list"),
    re_path(r"translation_services/(?P<source_language>[a-z_]+)/(?P<target_language>[a-z_]+)/$", CloudLanguageToolsTranslationServices.as_view(), name="list"),
]
