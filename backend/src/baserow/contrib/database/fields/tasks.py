from baserow.config.celery import app

from baserow.contrib.database.table.models import Table
from baserow.contrib.database.rows.signals import row_updated, before_row_update

import time

import logging
logger = logging.getLogger(__name__)

EXPORT_SOFT_TIME_LIMIT = 60 * 60
EXPORT_TIME_LIMIT = EXPORT_SOFT_TIME_LIMIT + 60

# noinspection PyUnusedLocal
@app.task(
    bind=True,
    soft_time_limit=EXPORT_SOFT_TIME_LIMIT,
    time_limit=EXPORT_TIME_LIMIT,
)
def run_cloudlanguagetoools(self, source_value, table_id, row_id, field_id):
    # time.sleep(3.0)
    time.sleep(0.2)
    logger.info(f'run_cloudlanguagetoools {source_value} table_id: {table_id} row_id: {row_id} field_id: {field_id}')

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

    setattr(row, field_id, f'clt {source_value}')
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
