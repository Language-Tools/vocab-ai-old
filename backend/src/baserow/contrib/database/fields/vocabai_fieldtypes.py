from django.db import models
from django.core.exceptions import ValidationError

from rest_framework import serializers

from baserow.contrib.database.fields.registries import FieldType

from .vocabai_models import TranslationField


class TranslationFieldType(FieldType):
    type = "translation"
    model_class = TranslationField
    allowed_fields = ['source_field']
    serializer_field_names = ['source_field']

    def prepare_value_for_db(self, instance, value):
        return value

    def get_serializer_field(self, instance, **kwargs):
        return serializers.CharField(
            **{
                "required": True,
                "allow_null": False,
                "allow_blank": False,
                **kwargs,
            }        
        )

    def get_model_field(self, instance, **kwargs):
        return models.TextField(
            default=None,
            blank=False, 
            null=False, 
            **kwargs
        )