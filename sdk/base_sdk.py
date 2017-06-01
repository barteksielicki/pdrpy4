import json


class SdkRequestError(Exception):
    pass


class BaseSdk:
    API_BASE_URL = None
    API_RESOURCE_ID = None

    def __init__(self, api_key):
        self._api_key = api_key

    @classmethod
    def key_from_json(cls, fname, key="api_key"):
        with open(fname) as f:
            api_key = json.load(f)[key]
        return cls(api_key)
