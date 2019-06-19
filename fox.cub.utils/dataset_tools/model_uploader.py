"""Help to upload statistical models to MongoDB."""

import pymongo

from bson.objectid import ObjectId

from config import Config

import sys
from enum import Enum


class ModelType(Enum):

    Btts = "btts"
    Total = "totals"
    Score = "scoreline"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


if __name__ == '__main__':

    if len(sys.argv) < 4:
        raise Exception("Please, specify\n1. path to the model dump file\n2. model id\n3. " +\
            "model type")

    model_file = sys.argv[1]
    model_id = sys.argv[2]
    model_type = sys.argv[3]

    if not ModelType.has_value(model_type):
        raise Exception("Model type not supported. Available types: [btts, scoreline, totals]")

    db_conf = Config()['database']

    client = pymongo.MongoClient(
        db_conf['host'],
        db_conf['port']
    )
    db = client[db_conf['db_name']]

    with open(model_file, mode='rb') as file:
        model_content = file.read()

    db[db_conf['collections']['stats_model']].update(
        {'_id': ObjectId(model_id)},
        {"$set": {model_type: model_content}},
        upsert=False
    )

    client.close()
