import logging
import redis
import json
import cloudlanguagetools.servicemanager

from django.conf import settings

logger = logging.getLogger(__name__)

clt_instance = cloudlanguagetools.servicemanager.ServiceManager() 
clt_instance.configure_default()

redis_url = settings.REDIS_URL
logger.info(f'connecting to {redis_url}')
redis_client = redis.Redis.from_url( redis_url )

def get_servicemanager():
    return clt_instance

def get_language_list():
    redis_key = 'cloudlanguagetools:language_data:language_list'
    return json.loads(redis_client.get(redis_key))

def get_translation_options():
    redis_key = 'cloudlanguagetools:language_data:translation_options'
    return json.loads(redis_client.get(redis_key))

def get_transliteration_options():
    redis_key = 'cloudlanguagetools:language_data:transliteration_options'
    return json.loads(redis_client.get(redis_key))

