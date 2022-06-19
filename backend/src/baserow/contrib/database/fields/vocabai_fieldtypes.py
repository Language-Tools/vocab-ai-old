from django.db import models
from django.core.exceptions import ValidationError
from baserow.contrib.database.fields.field_cache import FieldCache

from rest_framework import serializers

from baserow.contrib.database.fields.registries import FieldType
from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.views.handler import ViewHandler

from .vocabai_models import TranslationField

from .tasks import run_cloudlanguagetoools

import logging
logger = logging.getLogger(__name__)


class TranslationTextField(models.TextField):
    requires_refresh_after_update = True

class TranslationFieldType(FieldType):
    type = "translation"
    model_class = TranslationField
    allowed_fields = ['source_field']
    serializer_field_names = ['source_field']

    can_be_primary_field = False

    def prepare_value_for_db(self, instance, value):
        return value

    def get_serializer_field(self, instance, **kwargs):
        return serializers.CharField(
            **{
                "required": False,
                "allow_null": True,
                "allow_blank": True,
                **kwargs,
            }        
        )

    def get_model_field(self, instance, **kwargs):
        return TranslationTextField(
            default=None,
            blank=True, 
            null=True, 
            **kwargs
        )

    def get_field_dependencies(self, field_instance: Field, field_lookup_cache: FieldCache):
        # logger.info(f'get_field_dependencies')
        table_model = field_lookup_cache.get_model(field_instance.table)
        candidates = [field for field in table_model._meta.fields if field.name == field_instance.source_field]
        if len(candidates) != 1:
            raise Exception(f'could not find {field_instance.source_field} in table {table_model}')
        field = candidates[0]
        result = [field.verbose_name]
        logger.info(f'result: {result}')
        return result


    def row_of_dependency_updated(
        self,
        field,
        starting_row,
        update_collector,
        via_path_to_starting_table,
    ):
        logger.info(f'row_of_dependency_updated, row: {starting_row} vars: {vars(starting_row)}')
        source_value = getattr(starting_row, field.source_field)

        # add translation logic here:
        # translated_value = 'translation: ' + source_value

        # logger.info(f'starting_row: {starting_row} vars: {vars(starting_row)}')

        table_id = field.table.id
        row_id = starting_row.id
        field_id = f'field_{field.id}'
        run_cloudlanguagetoools.delay(source_value, table_id, row_id, field_id)

        # update_collector.add_field_with_pending_update_statement(
        #     field,
        #     translated_value,
        #     via_path_to_starting_table=via_path_to_starting_table,
        # )        

        super().row_of_dependency_updated(
            field,
            starting_row,
            update_collector,
            via_path_to_starting_table,
        )        

