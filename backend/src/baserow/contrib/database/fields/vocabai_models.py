from django.db import models

from baserow.contrib.database.fields.models import Field


# after making changes, run
# ./dev.sh run backend manage makemigrations
# ./dev.sh run backend manage migrate

# undoing a migration:
# ./dev.sh run backend manage migrate database 0071

class TranslationField(Field):
    source_field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        help_text="The field to translate.",
        null=True,
        blank=True,
        related_name='+'
    )    