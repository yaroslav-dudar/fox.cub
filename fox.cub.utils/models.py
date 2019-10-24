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

        if attr.get("capped_settings"):
            cls.setup_capped_collection(attr)

        attr['db_context'] = attr['client'].db[attr["collection"]]
        return super().__new__(cls, name, bases, attr)


    @classmethod
    def setup_capped_collection(cls, attr):
        settings = attr.get("capped_settings")
        try:
            attr['client'].db.create_collection(attr["collection"],
                                                    capped=settings["capped"],
                                                    size=settings["size"],
                                                    max=settings["max"])
        except pymongo.errors.CollectionInvalid:
            stats = attr['client'].db.command('collStats',
                                              attr["collection"])
            # verifing that collection is capped
            if not stats.get('capped'):
                raise RuntimeError('{} should be capped collection'.\
                                format(stats['ns']))

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
        auth_config = {}
        if db_config.get("authMechanism") == "SCRAM-SHA-1":
            auth_config['authMechanism'] = db_config["authMechanism"]
            auth_config['authSource'] = db_config["authSource"]
            auth_config['username'] = db_config["username"]
            auth_config['password'] = db_config["password"]

        self.conn = pymongo.MongoClient(
            host=db_config['host'],
            port=db_config['port'],
            **auth_config
        )
        MongoClient.db = self.conn[db_config['db_name']]
        # clean-up DB resources
        atexit.register(self.conn.close)


class Odds(metaclass=BaseModel):

    collection = "odds"

    @classmethod
    def insert(cls, document):
        cls.db_context.insert(document)

    @classmethod
    def insert_many(cls, documents):
        cls.db_context.insert_many(documents)

    @classmethod
    def get_document(cls, fixture_id, date, spreads, moneyline, totals):
        return {
            "fixture_id": fixture_id, "date": date,
            "spreads": spreads, "moneyline": moneyline,
            "totals": totals,
        }


class Fixture(metaclass=BaseModel):
    collection = "fixtures"

    @classmethod
    def add(cls, document):
        """ Insert fixture record if it not existed before """

        if document["home_id"] and document["away_id"]:
            query = {
                "home_id": document["home_id"],
                "away_id": document["away_id"]
            }
        else:
            query = {
                "home_name": document["home_name"],
                "away_name": document["away_name"]
            }

        cls.db_context.update(
            query,
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

    @classmethod
    def get_document(cls, fixture_id, home_name,
        away_name, date, tournament_name,
        home_id=None, away_id=None, tournament_id=None):

        return {
            "external_id": fixture_id,
            "home_name": home_name, "away_name": away_name,
            "date": date, "tournament_id": tournament_id,
            "tournament_name": tournament_name,
            "home_id": home_id, "away_id": away_id
        }

    @classmethod
    def get_id(self, home_id, away_id, date: datetime):
        """ Non-rigid date filter """
        where = 'return this.date.getDay() == {0}'.format(date.day)
        fixture = cls.db_context.find_one({'$where' : where,
                                            "home_id" : home_id,
                                            "away_id": away_id})

        return None if not fixture else str(fixture['_id'])

class StatsModel(metaclass=BaseModel):
    collection = "tournament_model"

    @classmethod
    def update(cls, model_id, model_type, model_content):
        cls.db_context.update(
            {'_id': ObjectId(model_id)},
            {"$set": {model_type: model_content}},
            upsert=False
        )


class Tournament(metaclass=BaseModel):
    collection = "tournament"

    @classmethod
    def get(cls, t_name, t_attr='name'):
        tournament = cls.db_context.find_one({t_attr: t_name})
        return tournament

    @classmethod
    def get_many(cls, t_name_list: list, t_attr='name'):
        tournaments = list(cls.db_context.find(
            {t_attr: {"$in": t_name_list}}))
        return tournaments

class Team(metaclass=BaseModel):

    collection = "team"

    @classmethod
    def get_id(cls, t_name, t_attr, t_list=None, is_iterable=True):
        """ Searching team id using t_attr field
        Args:
            t_name (str): team name to search
            t_attr (str): attr used in search
            t_list (list): list of preloaded teams
            is_iterable (bool): is t_attr field array
        """

        if not t_list:
            team = cls.db_context.find_one({t_attr: t_name})
            return team
        else:
            if not is_iterable:
                t_filt = filter(lambda t: t[t_attr] == t_name , t_list)
            else:
                t_filt = filter(lambda t: t_name in t[t_attr], t_list)

            team = next(t_filt, None)
            return None if not team else str(team['_id'])

    @classmethod
    def find(cls, t_id):
        """ Searching team id by tournament
        Args:
            t_id (list): tournament ids
        """
        return list(cls.db_context.find({"tournaments": t_id}))

    @classmethod
    def find_all(cls):
        return list(cls.db_context.find({}))


class Pinnacle(metaclass=BaseModel):
    collection = "pinnacle"
    capped_settings = {
        "capped": True,
        "size": 100000,
        "max": 1
    }

    @classmethod
    def get(cls):
        return cls.db_context.find_one({}) or {}

    @classmethod
    def insert(cls, document):
        cls.db_context.insert(document)

    @classmethod
    def get_document(self, last_fixture, last_odds):
        return {
            "last_fixture": last_fixture,
            "last_odds": last_odds,
        }


class Game(metaclass=BaseModel):

    collection = "game_stats"

    @classmethod
    def insert(cls, document):
        cls.db_context.insert_one(document)

    @classmethod
    def get_document(self, team, opponent,
                     tournament, date, venue,
                     goals_for, goals_against,
                     xg_for, xg_against):
        return {
            "team": team,
            "opponent": opponent,
            "tournament": tournament,
            "date": date,
            "venue": venue,
            "goals_for": int(goals_for),
            "goals_against": int(goals_against),
            "xG_for": float(xg_for),
            "xG_against": float(xg_against)
        }

    @classmethod
    def find_one(cls, team, opponent, tournament, venue):
        return cls.db_context.find_one(
            cls.find_query(team, opponent, tournament, venue))

    @classmethod
    def find_query(cls, team, opponent, tournament, venue):
        return {
            'team': team,
            'opponent': opponent,
            'venue': venue,
            'tournament': tournament
        }

    @classmethod
    def find_all(cls, tournament):
        return cls.db_context.find({ 'tournament': tournament })

    @classmethod
    def update(cls, game_id, with_data):
        return cls.db_context.update({'_id': game_id},
                                     {'$set': with_data},
                                     upsert=False)

    @classmethod
    def upsert(cls, query, with_data):
        return cls.db_context.update(query,
                                     {'$set': with_data},
                                     upsert=True)
