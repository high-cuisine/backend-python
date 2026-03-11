from time import time

from django.conf import settings
from django.http import QueryDict
from django.utils.functional import classproperty


def to_int(value, default=None):
    try:
        value = str(value).replace(',', '.')
        return int(float(value))
    except (ValueError, TypeError):
        return default


def site_url(path: str, **kwargs) -> str:
    query_string = ''
    if kwargs:
        q = QueryDict('', mutable=True)
        for k, v in kwargs.items():
            if v is not None and v != '':
                q[k] = v
        query_string = '?' + q.urlencode()
    return settings.BASE_URL + path + query_string


class Memoized(object):
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl

    def __call__(self, func):
        def _memoized(*args, **kwargs):
            self.func = func
            current_time = time()
            cache_key = tuple(map(hash, args))
            try:
                value, last_update = self.cache[cache_key]
                age = current_time - last_update
                if age > self.ttl:
                    raise AttributeError

                return value

            except (KeyError, AttributeError):
                value = self.func(*args, **kwargs)
                self.cache[cache_key] = (value, current_time)
                return value

            except TypeError:
                return self.func(*args, **kwargs)

        return _memoized


class cached_classproperty(classproperty):
    def get_result_field_name(self):
        return self.fget.__name__ + "_property_result" if self.fget else None

    def __get__(self, instance, cls=None):
        result_field_name = self.get_result_field_name()

        if hasattr(cls, result_field_name):
            return getattr(cls, result_field_name)

        if not cls or not result_field_name:
            return self.fget(cls)

        setattr(cls, result_field_name, self.fget(cls))
        return getattr(cls, result_field_name)
