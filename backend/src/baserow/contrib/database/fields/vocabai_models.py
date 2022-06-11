from django.db import models

from baserow.contrib.database.fields.models import Field


# after making changes, run
# ./dev.sh run backend manage makemigrations
# ./dev.sh run backend manage migrate

# undoing a migration:
# ./dev.sh run backend manage migrate database 0071

class TranslationField(Field):
    source_field = models.CharField(
        max_length=255,
        blank=False,
        default="",
        help_text="field to translate",
    )