from baserow.config.celery import app

from baserow.contrib.database.table.models import Table
from baserow.contrib.database.rows.signals import row_updated, before_row_update

from baserow.contrib.database.cloudlanguagetools import instance as clt_instance

import time

import logging
logger = logging.getLogger(__name__)

EXPORT_SOFT_TIME_LIMIT = 60 * 60
EXPORT_TIME_LIMIT = EXPORT_SOFT_TIME_LIMIT + 60


# translation 
# ===========

# noinspection PyUnusedLocal
@app.task(
    bind=True,
    soft_time_limit=EXPORT_SOFT_TIME_LIMIT,
    time_limit=EXPORT_TIME_LIMIT,
)
def run_clt_translation_all_rows(self, table_id, source_language, target_language, service, source_field_id, target_field_id):
    base_queryset = Table.objects
    table = base_queryset.select_related("database__group").get(id=table_id)
    # https://docs.djangoproject.com/en/4.0/ref/models/querysets/
    table_model = table.get_model()
    for row in table_model.objects.all():
        row_id = row.id
        text = getattr(row, source_field_id)
        # logger.info(f'row: {row}')
        run_clt_translation.delay(text, source_language, target_language, service, table_id, row_id, target_field_id)

# noinspection PyUnusedLocal
@app.task(
    bind=True,
    soft_time_limit=EXPORT_SOFT_TIME_LIMIT,
    time_limit=EXPORT_TIME_LIMIT,
)
def run_clt_translation(self, text, source_language, target_language, service, table_id, row_id, target_field_id):
    logger.info(f'run_cloudlanguagetoools {text} table_id: {table_id} row_id: {row_id} field_id: {target_field_id}')

    base_queryset = Table.objects
    table = base_queryset.select_related("database__group").get(id=table_id)
    logger.info(f'table: {table}')

    # logger.info(f'table vars: {vars(table)}')
    table_model = table.get_model()
    row = table_model.objects.get(id=row_id)
    # row.refresh_from_db(fields=model.fields_requiring_refresh_after_update())
    logger.info(f'row: {row}')


    before_return = before_row_update.send(
        self,
        row=row,
        user=None,
        table=table,
        model=table_model,
        updated_field_ids=None,
    )

    translated_text = clt_instance.get_translation(text, source_language, target_language, service)

    setattr(row, target_field_id, translated_text)
    logger.info(f'updated row: {row}')
    row.save()

    row_updated.send(
        None,
        row=row,
        user=None,
        table=table,
        model=table_model,
        before_return=before_return,
        updated_field_ids=None
    )


# transliteration
# ================

# noinspection PyUnusedLocal
@app.task(
    bind=True,
    soft_time_limit=EXPORT_SOFT_TIME_LIMIT,
    time_limit=EXPORT_TIME_LIMIT,
)
def run_clt_transliteration_all_rows(self, table_id, transliteration_id, source_field_id, target_field_id):
    base_queryset = Table.objects
    table = base_queryset.select_related("database__group").get(id=table_id)
    # https://docs.djangoproject.com/en/4.0/ref/models/querysets/
    table_model = table.get_model()
    for row in table_model.objects.all():
        row_id = row.id
        text = getattr(row, source_field_id)
        # logger.info(f'row: {row}')
        run_clt_transliteration.delay(text, transliteration_id, table_id, row_id, target_field_id)

# noinspection PyUnusedLocal
@app.task(
    bind=True,
    soft_time_limit=EXPORT_SOFT_TIME_LIMIT,
    time_limit=EXPORT_TIME_LIMIT,
)
def run_clt_transliteration(self, text, transliteration_id, table_id, row_id, target_field_id):
    logger.info(f'run_clt_transliteration {text} table_id: {table_id} row_id: {row_id} field_id: {target_field_id}')

    base_queryset = Table.objects
    table = base_queryset.select_related("database__group").get(id=table_id)
    logger.info(f'table: {table}')

    # logger.info(f'table vars: {vars(table)}')
    table_model = table.get_model()
    row = table_model.objects.get(id=row_id)
    # row.refresh_from_db(fields=model.fields_requiring_refresh_after_update())
    logger.info(f'row: {row}')


    before_return = before_row_update.send(
        self,
        row=row,
        user=None,
        table=table,
        model=table_model,
        updated_field_ids=None,
    )

    result = clt_instance.get_transliteration(text, transliteration_id)

    setattr(row, target_field_id, result)
    logger.info(f'updated row: {row}')
    row.save()

    row_updated.send(
        None,
        row=row,
        user=None,
        table=table,
        model=table_model,
        before_return=before_return,
        updated_field_ids=None
    )

# dictionary lookup
# =================

# noinspection PyUnusedLocal
@app.task(
    bind=True,
    soft_time_limit=EXPORT_SOFT_TIME_LIMIT,
    time_limit=EXPORT_TIME_LIMIT,
)
def run_clt_lookup_all_rows(self, table_id, lookup_id, source_field_id, target_field_id):
    base_queryset = Table.objects
    table = base_queryset.select_related("database__group").get(id=table_id)
    # https://docs.djangoproject.com/en/4.0/ref/models/querysets/
    table_model = table.get_model()
    for row in table_model.objects.all():
        row_id = row.id
        text = getattr(row, source_field_id)
        # logger.info(f'row: {row}')
        run_clt_lookup.delay(text, lookup_id, table_id, row_id, target_field_id)

# noinspection PyUnusedLocal
@app.task(
    bind=True,
    soft_time_limit=EXPORT_SOFT_TIME_LIMIT,
    time_limit=EXPORT_TIME_LIMIT,
)
def run_clt_lookup(self, text, lookup_id, table_id, row_id, target_field_id):
    logger.info(f'run_clt_lookup {text} table_id: {table_id} row_id: {row_id} field_id: {target_field_id}')

    base_queryset = Table.objects
    table = base_queryset.select_related("database__group").get(id=table_id)
    logger.info(f'table: {table}')

    # logger.info(f'table vars: {vars(table)}')
    table_model = table.get_model()
    row = table_model.objects.get(id=row_id)
    # row.refresh_from_db(fields=model.fields_requiring_refresh_after_update())
    logger.info(f'row: {row}')


    before_return = before_row_update.send(
        self,
        row=row,
        user=None,
        table=table,
        model=table_model,
        updated_field_ids=None,
    )

    result = clt_instance.get_dictionary_lookup(text, lookup_id)

    setattr(row, target_field_id, result)
    logger.info(f'updated row: {row}')
    row.save()

    row_updated.send(
        None,
        row=row,
        user=None,
        table=table,
        model=table_model,
        before_return=before_return,
        updated_field_ids=None
    )