import os
import json
import time
import logging
import functools

import schedule

from pymongo import MongoClient

from sdk import (
    BusTramSdk,
    SdkRequestError,
    TramSdk,
)


def init_sdks(api_key_file):
    with open(api_key_file) as f:
        api_key = json.load(f)['api_key']
    return BusTramSdk(api_key), TramSdk(api_key)


def get_to_mongo(mongo_db, bustram_sdk, tram_sdk):
    try:
        buses = bustram_sdk.buses()
        trams = tram_sdk.trams()
    except SdkRequestError as e:
        logging.getLogger(__name__).error(e)
    else:
        mongo_db.trams.insert_many(trams)
        mongo_db.buses.insert_many(buses)


def main():
    bustram_sdk, tram_sdk = init_sdks('api_key.json')
    mongo_client = MongoClient(
        'mongodb://pdrpy:{0}@192.166.219.242:27447/pdrpy_db'.format(
            os.environ.get('MONGO_PASSWORD'),
        ),
    )
    mongo_db = mongo_client.pdrpy_db
    job = functools.partial(get_to_mongo, mongo_db, bustram_sdk, tram_sdk)
    schedule.every(0.1).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if '__main__' == __name__:
    main()
