"""Pymongo wrapper with object models and operations with them."""

import atexit
from datetime import datetime

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
        # clean-up DB resources
        atexit.register(MongoClient.conn.close)


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
            { "home_id": document["home_id"],
              "away_id": document["away_id"]
            },
            {
                '$addToSet': {'external_ids': document['external_id']},
                '$set': {
                    'home_name': document['home_name'],
                    'away_name': document['away_name'],
                    'tournament_name': document['tournament_name'],
                    "tournament_id": document['tournament_id'],
                    'home_id': document['home_id'],
                    'away_id': document['away_id'],
                    'date': document['date']
                }
            }, upsert=True
        )


    def get_document(self, fixture_id, home_name,
        away_name, date, tournament_name,
        home_id=None, away_id=None, tournament_id=None):

        return {
            "external_id": fixture_id,
            "home_name": home_name, "away_name": away_name,
            "date": date, "tournament_id": tournament_id,
            "tournament_name": tournament_name,
            "home_id": home_id, "away_id": away_id
        }

    def get_id(self, home_id, away_id, date: datetime):
        """ Non-rigid date filter """
        where = 'return this.date.getDay() == {0}'.format(date.day)
        fixture = self.collection.find_one({'$where' : where,
                                            "home_id" : home_id,
                                            "away_id": away_id})

        return None if not fixture else str(fixture['_id'])

class StatsModel:
    def __init__(self):
        self.collection = MongoClient.db["tournament_model"]

    def update(self, model_id, model_type, model_content):
        self.collection.update(
            {'_id': ObjectId(model_id)},
            {"$set": {model_type: model_content}},
            upsert=False
        )


class Tournaments:

    def __init__(self):
        self.collection = MongoClient.db["tournament"]

    def get(self, t_name, t_attr='name'):
        tournament_id = self.collection.find_one({t_attr: t_name})
        return tournament_id


class Teams:

    def __init__(self):
        self.collection = MongoClient.db["team"]

    def get_id(self, t_name, t_attr, t_list=None):
        if not t_list:
            team = self.collection.find_one({t_attr: t_name})
            return team
        else:
            t_filt = filter(lambda t: t[t_attr] == t_name , t_list)
            team = next(t_filt, None)
            return None if not team else str(team['_id'])

    def find(self, t_id):
        return list(self.collection.find({"tournaments": t_id}))
