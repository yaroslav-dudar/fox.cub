"""Help to upload statistical models to MongoDB."""

import pymongo

from bson.objectid import ObjectId

from config import Config

import sys

if __name__ == '__main__':

    if len(sys.argv) < 4:
        raise Exception("Please, specify\n1. path to the model dump file\n2. model id\n3. " +\
            "model type [btts, scoreline, totals]!")

    model_file = sys.argv[1]
    model_id = sys.argv[2]
    model_type = sys.argv[3]

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
