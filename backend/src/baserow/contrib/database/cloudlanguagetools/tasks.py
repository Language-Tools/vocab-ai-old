from baserow.config.celery import app
import redis
import json

import logging
logger = logging.getLogger(__name__)

EXPORT_SOFT_TIME_LIMIT = 60 * 60
EXPORT_TIME_LIMIT = EXPORT_SOFT_TIME_LIMIT + 60

from baserow.contrib.database.cloudlanguagetools import instance as clt_instance
from django.conf import settings


#@app.on_after_configure.connect
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info('setup_periodic_tasks')
    
    # run every 30s
    # period = 30
    period = 3600 * 3
    sender.add_periodic_task(period, refresh_cloudlanguagetools_language_data.s(), name='cloudlanguagetools language data')
    
    # run once at startup
    refresh_cloudlanguagetools_language_data.delay()


# noinspection PyUnusedLocal
@app.task(
    bind=True,
    soft_time_limit=EXPORT_SOFT_TIME_LIMIT,
    time_limit=EXPORT_TIME_LIMIT,
)
def refresh_cloudlanguagetools_language_data(self):
    logger.info('refresh_cloudlanguagetools_language_data')
    manager = clt_instance.get_servicemanager()
    language_data = manager.get_language_data_json()

    # create redis client
    redis_url = settings.REDIS_URL
    logger.info(f'connecting to {redis_url}')
    r = redis.Redis.from_url( redis_url )

    for key, data in language_data.items():
        redis_key = f'cloudlanguagetools:language_data:{key}'
        r.set(redis_key, json.dumps(data))

    r.close()

