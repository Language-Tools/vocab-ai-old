from baserow.config.celery import app

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
    time.sleep(3.0)
    logger.info(f'run_cloudlanguagetoools {source_value} table_id: {table_id} row_id: {row_id} field_id: {field_id}')