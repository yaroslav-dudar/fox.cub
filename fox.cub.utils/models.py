"""Pymongo wrapper with object models and operations with them."""

import atexit
from datetime import datetime

import pymongo
from bson.objectid import ObjectId

from config import Config

class Connection:
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        if not isinstance(value, pymongo.MongoClient):
            raise ValueError("Should be MongoDB instance only")

        instance.__dict__[self.name] = value

    def __get__(self, instance, owner):
        if not instance:
            return None

        return instance.__dict__.get(self.name)


class BaseModel(type):
    def __new__(cls, name, bases, attr):
        attr['client'] = MongoClient(Config()['database'])
        return super(BaseModel, cls).__new__(cls, name, bases, attr)


class MongoClient:
    """ Global MongoDB connector """
    conn = Connection()
    db = None
    _obj = None

    def __new__(cls, *args, **kwargs):
        if cls._obj:
            # prevent to create multiple db connections
            return cls._obj
        else:
            cls._obj = super(MongoClient, cls).__new__(cls)
            return cls._obj

    def __init__(self, db_config):
        self.conn = pymongo.MongoClient(
            db_config['host'],
            db_config['port']
        )
        MongoClient.db = self.conn[db_config['db_name']]
        # clean-up DB resources
        atexit.register(self.conn.close)


class Odds(metaclass=BaseModel):

    def __init__(self):
        self.collection = self.client.db["odds"]

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


class Fixtures(metaclass=BaseModel):

    def __init__(self):
        self.collection = self.client.db["fixtures"]

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

class StatsModel(metaclass=BaseModel):
    def __init__(self):
        self.collection = self.client.db["tournament_model"]

    def update(self, model_id, model_type, model_content):
        self.collection.update(
            {'_id': ObjectId(model_id)},
            {"$set": {model_type: model_content}},
            upsert=False
        )


class Tournaments(metaclass=BaseModel):

    def __init__(self):
        self.collection = self.client.db["tournament"]

    def get(self, t_name, t_attr='name'):
        tournament_id = self.collection.find_one({t_attr: t_name})
        return tournament_id


class Teams(metaclass=BaseModel):

    def __init__(self):
        self.collection = self.client.db["team"]

    def get_id(self, t_name, t_attr, t_list=None, is_iterable=True):
        """ Searching team id using t_attr field
        Args:
            t_name (str): team name to search
            t_attr (str): attr used in search
            t_list (list): list of preloaded teams
            is_iterable (bool): is t_attr field array
        """

        if not t_list:
            team = self.collection.find_one({t_attr: t_name})
            return team
        else:
            if not is_iterable:
                t_filt = filter(lambda t: t[t_attr] == t_name , t_list)
            else:
                t_filt = filter(lambda t: t_name in t[t_attr], t_list)

            team = next(t_filt, None)
            return None if not team else str(team['_id'])

    def find(self, t_id):
        return list(self.collection.find({"tournaments": t_id}))
