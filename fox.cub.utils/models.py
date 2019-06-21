"""Pymongo wrapper with object models and operations with them."""

import hashlib

import pymongo
from bson.objectid import ObjectId


class MongoClient:
    """ Global MongoDB connector """
    conn = None
    db = None

    def __new__(cls, *args, **kwargs):
        if MongoClient.conn and MongoClient.db:
            # prevent to create multiple db connections
            pass
        else:
            return super(MongoClient, cls).__new__(cls)

    def __init__(self, db_config):
        MongoClient.conn = pymongo.MongoClient(
            db_config['host'],
            db_config['port']
        )
        MongoClient.db = MongoClient.conn[db_config['db_name']]


class Odds:

    def __init__(self):
        self.collection = MongoClient.db["odds"]

    def insert(self, document):
        self.collection.insert(document)

    def insert_many(self, documents):
        self.collection.insert_many(documents)

    def get_document(self, fixture_id, date, spreads, moneyline, totals):
        return {
            "fixture_id": fixture_id, "date": date,
            "spreads": spreads, "moneyline": moneyline,
            "totals": totals,
        }


class Fixtures:

    def __init__(self):
        self.collection = MongoClient.db["fixtures"]

    def add(self, document):
        """ Insert fixture record if it not existed before """
        self.collection.update(
            {
                "date": document["date"],
                "home_name": document["home_name"],
                "away_name": document["away_name"]
            },
            { "$setOnInsert": document },
            upsert=True
        )


    def get_document(self, fixture_id, home_name,
        away_name, date, tournament_name,
        home_id=None, away_id=None, tournament_id=None):

        return {
            "_id": fixture_id,
            "home_name": home_name, "away_name": away_name,
            "date": date, "tournament_id": tournament_id,
            "tournament_name": tournament_name,
            "home_id": home_id, "away_id": away_id
        }


class StatsModel:
    def __init__(self):
        self.collection = MongoClient.db["tournament_model"]

    def update(self, model_id, model_type, model_content):
        self.collection.update(
            {'_id': ObjectId(model_id)},
            {"$set": {model_type: model_content}},
            upsert=False
        )
