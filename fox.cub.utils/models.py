"""Pymongo wrapper with object models and operations with them."""

import atexit
from datetime import datetime
from datetime import timedelta

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
            "_id": ObjectId(),
            "fixture_id": fixture_id, "date": date,
            "spreads": spreads, "moneyline": moneyline,
            "totals": totals,
        }

    @classmethod
    def get_line_diff(cls, fixture_ids: list):
        match_query = {'$match': {'fixture_id': { '$in': fixture_ids }}}
        sort_query = { '$sort': {'date': 1 } }
        group_query = {'$group': {
            '_id': "$fixture_id",
            'open': { '$first': "$$ROOT" },
            'close': { '$last': "$$ROOT" }
        }}

        return list(cls.db_context.aggregate([match_query,
                                              sort_query,
                                              group_query],
                                              allowDiskUse=True))

    @classmethod
    def remove(cls, fixture_ids: list, unremovable_ids: list):
        """
            Remove odds belongs to given fixtures
        """

        return cls.db_context.remove({
            'fixture_id': {"$in": fixture_ids},
            '_id': {'$nin': [ObjectId(i) for i in unremovable_ids]}
        })


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

        query["date"] = cls.date_query(document['date'])

        return cls.db_context.update_one(
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
            "_id": ObjectId(),
            "external_id": fixture_id,
            "home_name": home_name, "away_name": away_name,
            "date": date, "tournament_id": tournament_id,
            "tournament_name": tournament_name,
            "home_id": home_id, "away_id": away_id
        }

    @classmethod
    def get_id(cls, home_id, away_id, date: datetime):
        """ Non-rigid date filter """
        where = 'return this.date.getDay() == {0}'.format(date.day)
        fixture = cls.db_context.find_one({'$where' : where,
                                            "home_id" : home_id,
                                            "away_id": away_id})

        return None if not fixture else str(fixture['_id'])

    @classmethod
    def bulk_write_stats(cls, fixtures: list):
        requests = []
        for f in fixtures:
            upd_req = pymongo.UpdateOne(
                {'_id': f['_id']},
                {'$set': {'open': f['open'],
                          'close': f['close']}
                })
            requests.append(upd_req)

        return cls.db_context.bulk_write(requests)


    @classmethod
    def get_in_range(cls, from_date: datetime,
                     to_date: datetime,
                     is_lite_output=True):
        """ Return Fixtures within given range

        Args:
            from_date: minimum date Fixture
            to_date: max date Fixture
        """

        projection = {'_id': 1, 'external_ids': 1}
        if not is_lite_output:
            projection = {**projection, **{'open._id': 1, 'close._id': 1}}

        query = {'date' : {'$gte':from_date, '$lte':to_date}}
        return list(cls.db_context.find(query, projection))


    @classmethod
    def get_by_ext_id(cls, ext_ids: list):
        query = {'external_ids' : {'$in': ext_ids}}
        return list(cls.db_context.find(query))


    @classmethod
    def date_query(cls, date: datetime):
        """ Consider fixtures within +-10 days range as a same.
            For example initial fixture date may change, so we need to
            persist previous fixture and odds and update
            fixtture date only.
        """
        delta = timedelta(days=10)
        start_day = date - delta
        end_day = date + delta
        return { "$gt": start_day, "$lt": end_day}


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
    def find_one(cls, team, opponent, tournament, venue, date=None):
        return cls.db_context.find_one(
            cls.find_query(team, opponent, tournament, venue, date))

    @classmethod
    def find_query(cls, team, opponent, tournament, venue, date: int = None):
        q = {
            'team': team,
            'opponent': opponent,
            'venue': venue,
            'tournament': tournament
        }

        if date: q["date"] = date
        return q

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


class Notification(metaclass=BaseModel):

    collection = "notification"

    @classmethod
    def insert(cls, document):
        cls.db_context.insert_one(document)

    @classmethod
    def get_document(self, text, odds, date: datetime):
        return {
            "text": text,
            "odds": odds,
            "date": date
        }
