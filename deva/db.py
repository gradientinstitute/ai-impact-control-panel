"""Database implementations for flask frontend."""

import sys
import pickle
import hashlib


class DB:
    """Base class with the accessors for the various bits of state."""

    def __init__(self):
        raise NotImplementedError()

    def _get(self, key):
        raise NotImplementedError()

    def _set(self, key, value):
        raise NotImplementedError()

    def _del(self, key):
        raise NotImplementedError()

    @property
    def eliciter(self):
        return self._get('eliciter')

    @eliciter.setter
    def eliciter(self, value):
        return self._set('eliciter', value)

    @eliciter.deleter
    def eliciter(self):
        return self._del('eliciter')

    @property
    def bounder(self):
        return self._get('bounder')

    @bounder.setter
    def bounder(self, value):
        return self._set('bounder', value)

    @bounder.deleter
    def bounder(self):
        return self._del('bounder')

    @property
    def logger(self):
        return self._get('logger')

    @logger.setter
    def logger(self, value):
        return self._set('logger', value)

    @logger.deleter
    def logger(self):
        return self._del('logger')


class RedisDB(DB):
    """Key-value storage with redis."""
    def __init__(self, redis_client, session):
        self.r = redis_client
        self.session = session
        try:
            self.r.ping()
        except Exception:
            print("Could not connect to Redis database")
            sys.exit(-1)

    def _get(self, key):
        id = self.session['id']
        raw = self.r.get(id + "/" + key)
        result = pickle.loads(raw)
        print(f"getting {key}:", hashlib.md5(raw).hexdigest())
        return result

    def _set(self, key, value):
        id = self.session['id']
        raw = pickle.dumps(value)
        self.r.set(id + "/" + key, raw)
        print(f"setting {key}: ", hashlib.md5(raw).hexdigest())

    def _del(self, key):
        id = self.session['id']
        self.r.delete(id + '/' + key)


class DevDB(DB):
    """Simple dict, not even serialized."""
    def __init__(self, session):
        self.session = session
        self._db = {}

    def _get(self, key):
        id = self.session['id']
        result = self._db[id + "/" + key]
        return result

    def _set(self, key, value):
        id = self.session['id']
        self._db[id + "/" + key] = value

    def _del(self, key):
        id = self.session['id']
        del self._db[id + '/' + key]
