import logging
import redis
import json
import cloudlanguagetools.servicemanager

from django.conf import settings

logger = logging.getLogger(__name__)

clt_instance = cloudlanguagetools.servicemanager.ServiceManager() 
clt_instance.configure_default()

# clt_language_data = None

def get_servicemanager():
    return clt_instance

def get_language_data():
    # return clt_language_data

    redis_url = settings.REDIS_URL
    logger.info(f'connecting to {redis_url}')
    r = redis.Redis.from_url( redis_url )

    clt_language_data = r.get('clt:language_data')

    r.close()

    return json.loads(clt_language_data)
