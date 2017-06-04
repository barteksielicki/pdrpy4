import os
import functools

from sanic_cors import CORS
from sanic import Sanic
from motor.motor_asyncio import AsyncIOMotorClient

sanic_config = {
    'MONGO_HOST': '192.166.219.242',
    'MONGO_PORT': 27447,
    'MONGO_USER': 'pdrpy',
    'MONGO_DB_NAME': 'pdrpy_db',
}


def init_app(config=None):
    app = Sanic(__name__)
    app.config.update(config or {})
    app.db = functools.partial(
        _get_db,
        host=app.config.get('MONGO_HOST'),
        port=app.config.get('MONGO_PORT'),
        user=app.config.get('MONGO_USER'),
        passwd=app.config.get('MONGO_PASSWD'),
        db_name=app.config.get('MONGO_DB_NAME'),
    )
    CORS(app)
    return app


def _get_db(
    host='localhost',
    port=27017,
    user=None,
    passwd=None,
    db_name=None,
):
    user = user or os.environ.get('MONGO_USER', 'pdrpy')
    passwd = passwd or os.environ.get('MONGO_PASSWD', 'only_python<3')
    db_name = db_name or os.environ.get('MONGO_DB_NAME', 'pdrpy_db')
    aio_mongo_client = AsyncIOMotorClient(
        f"mongodb://{user}:{passwd}@{host}:{port}/{db_name}",
    )
    return aio_mongo_client[db_name]


app = init_app(sanic_config)
