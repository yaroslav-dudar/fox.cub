import pymongo

class Odds:

    @classmethod
    def init(cls, db_client):
        cls.db_client = db_client

    @staticmethod
    def insert(document):
        db_client.odds.insert(document)

    @staticmethod
    def insert_many(documents):
        db_client.fixtures.insert_many(documents)

    @staticmethod
    def get_document(fixture_id, date, spreads, moneyline, totals):
        return {
            "fixture_id": fixture_id, "date": date,
            "spreads": spreads, "moneyline": moneyline,
            "totals": totals,
        }


class Fixtures:

    def __init__(self, db_client):
        self.collection = db_client["fixtures"]

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


    def get_document(self, home_name, away_name, date, tournament_name,
        home_id=None, away_id=None, tournament_id=None):

        return {
            "home_name": home_name, "away_name": away_name,
            "date": date, "tournament_id": tournament_id,
            "tournament_name": tournament_name,
            "home_id": home_id, "away_id": away_id
        }
