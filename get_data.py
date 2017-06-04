"""
Our data collected from API is stored in Mongo Database on remote server.
It needs to be cleaned a bit, and splitted into smaller chunks so it could
be effectively processed by other scripts. That's what this script is
responsible for.
"""

import os
import urllib
from datetime import datetime, timedelta

from bson.json_util import dumps
from pymongo import MongoClient

MONGO_HOST = "192.166.219.242:27447"
MONGO_DB = "pdrpy_db"
MONGO_USER = "pdrpy"
MONGO_PASSWORD = urllib.parse.quote_plus('only_python<3')
MONGO_COLLECTION = "tram_doc"

DATE_FROM = datetime(2017, 5, 4)
DATE_TO = DATE_FROM + timedelta(days=7)
DATE_CHUNK_SIZE = timedelta(hours=12)

OUTPUT_DIRECTORY = "data"


def clean_record(record):
    def sanitize(field):
        return str(field).strip()

    for f in ("brigade", "first_line"):
        record[f] = sanitize(record[f])
    for f in ("_id", "lines", "low_floor"):
        del record[f]
    record["time"] = record["time"]["$date"]
    return record


client = MongoClient("mongodb://{}:{}@{}/{}".format(
    MONGO_USER, MONGO_PASSWORD, MONGO_HOST, MONGO_DB
))
data = client[MONGO_DB][MONGO_COLLECTION]

if not os.path.exists(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)

date = DATE_FROM
while date < DATE_TO:
    print("Chunk {} to {}:".format(
        datetime.strftime(date, "%d/%m/%Y %T"),
        datetime.strftime(date + DATE_CHUNK_SIZE, "%d/%m/%Y %T")))
    print("\tProcessing... ", end="", flush=True)
    chunk_cursor = data.find({"time": {"$gte": date, "$lt": date + DATE_CHUNK_SIZE}})
    chunk = [clean_record(r) for r in chunk_cursor]
    print("Done")
    filename = os.path.join(OUTPUT_DIRECTORY, "{}_{}.json".format(
        MONGO_COLLECTION, datetime.strftime(date, "%d_%m_%Y_%H_%M")))

    print("\tSaving {}... ".format(filename), end="", flush=True)
    with open(filename, "w") as f:
        f.write(dumps(chunk))
    print("Done")
    date += DATE_CHUNK_SIZE
