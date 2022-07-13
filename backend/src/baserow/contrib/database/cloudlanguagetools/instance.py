import cloudlanguagetools.servicemanager


def get_servicemanager():
    manager = cloudlanguagetools.servicemanager.ServiceManager()
    manager.configure_default()
    return manager