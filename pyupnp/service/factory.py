from .base_service import BaseService


class Factory(object):
    registry = {}


def service(name):
    def wrapper(name=name):
        def decorator(f):
            Factory.registry[name] = f
            return f
        return decorator
    return wrapper(name)

def create_service(base_url, data):
    stype = data['serviceType']
    ctor = Factory.registry.get(stype)
    return ctor(base_url, data) if ctor else BaseService(base_url, data)

