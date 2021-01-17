""" Pymongo repository """

import json
from dataclasses import asdict

from .base import BaseModel
from domain import FootballMatch, BaseMatch

from bson.objectid import ObjectId

class MatchRepository(metaclass=BaseModel):
    collection = "matches"

    @classmethod
    def search(cls, attr, value) -> FootballMatch:
        if attr == '_id':
            value = ObjectId(value)

        items = cls.db_session.find({ attr: value })
        return [FootballMatch(**i) for i in items]

    @classmethod
    def insert(cls, m: FootballMatch):
        return cls.db_session.insert_one(asdict(m))

    @classmethod
    def delete(cls, _id: int):
        return cls.db_session.remove({"_id": ObjectId(_id)})

    @staticmethod
    def from_file(filepath, domain: BaseMatch):
        """ Create list of matches from input file. """
        matches = []
        with open(filepath, 'r') as _file:
            data = json.load(_file)
            for match in data:
                try:
                    matches.append(domain(**match))
                except ValueError as err:
                    print(err)

        return matches
