import json

from collections import defaultdict

import requests


class BusTramSdkRequestError(Exception):
    pass


class BusTramSdk:
    API_BASE_URL = 'https://api.um.warszawa.pl/api/action/busestrams_get/'
    API_RESOURCE_ID = 'f2e5503e-927d-4ad3-9500-4ab9e55deb59'

    def __init__(self, api_key):
        self._api_key = api_key

    @classmethod
    def key_from_json(cls, fname, key="api_key"):
        with open(fname) as f:
            api_key = json.load(f)[key]
        return cls(api_key)

    def trams(self, line=None, brigade=None):
        return self._request(type_=2, line=line, brigade=brigade)

    def buses(self, line=None, brigade=None):
        return self._request(type_=1, line=line, brigade=brigade)

    def all(self, brigade=None):
        return dict(
            buses=self.buses(brigade=brigade),
            trams=self.trams(brigade=brigade),
        )

    def _request(self, type_, line, brigade):
        params = defaultdict(str)
        params['type'] = type_
        if line is not None:
            params['line'] = line
        if brigade is not None:
            params['brigade'] = brigade
        params.update({
            'resource_id': self.API_RESOURCE_ID,
            'apikey': self._api_key,
        })
        response = requests.post(self.API_BASE_URL, params=params)
        result = response.json()['result']
        if isinstance(result, str):
            raise BusTramSdkRequestError()
        return result
