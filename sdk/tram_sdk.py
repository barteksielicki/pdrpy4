import requests

from .base_sdk import (
    BaseSdk,
    SdkRequestError,
)


class TramSdk(BaseSdk):
    API_BASE_URL = 'https://api.um.warszawa.pl/api/action/wsstore_get/'
    API_RESOURCE_ID = 'c7238cfe-8b1f-4c38-bb4a-de386db7e776'

    def trams(self, **kwargs):
        return self._request(**kwargs)

    def _request(self, **kwargs):
        response = requests.get(self.API_BASE_URL, params={
            'id': self.API_RESOURCE_ID,
            'apikey': self._api_key,
        })
        if response.status_code != 200:
            raise SdkRequestError()
        result = list()
        for tram in response.json()['result']:
            for key, value in kwargs.items():
                if tram.get(key.lower().capitalize()) != value:
                    break
            else:
                result.append(tram)
        return result
