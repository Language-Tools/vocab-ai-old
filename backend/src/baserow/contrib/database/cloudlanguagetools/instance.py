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

def get_translation_services_source_target_language(source_language, target_language):
    translation_options = get_translation_options()
    source_language_options = [x for x in translation_options if x['language_code'] == source_language]
    target_language_options = [x for x in translation_options if x['language_code'] == target_language]
    source_services = [x['service'] for x in source_language_options]
    target_services = [x['service'] for x in target_language_options]
    service_list = list(set(source_services).intersection(target_services))
    return service_list
