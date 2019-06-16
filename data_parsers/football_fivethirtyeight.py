import csv
import os
import urllib.request

import pymongo
import datetime
from datetime import timezone

from config import Config

class FivethirtyeightParser:

    leagues = []

    DATE_FORMAT = "%Y-%m-%d"
    DATA_FOLDER = "data"
    DATA_SOURCE = "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv"

    def __init__(self):

        self.global_conf = Config()
        self.config = self.global_conf['fivethirtyeight_parser']
        self.db_conf = self.global_conf['database']

        self.client = pymongo.MongoClient(
            self.db_conf['host'],
            self.db_conf['port']
        )
        self.db = self.client[self.db_conf['db_name']]

        self.games = list(self.db[self.db_conf['collections']['game']].find())
        self.teams = list(self.db[self.db_conf['collections']['team']].find())
        print(self.teams)


    def download(self):
        """
            Download csv file with games stats from
            https://github.com/fivethirtyeight/data/tree/master/soccer-spi
        """

        self.download_to = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), self.DATA_FOLDER
        )
        self.file_path = os.path.join(self.download_to, 'spi_matches.csv')

        print("Download file: {0}. Save to: {1}".format(self.DATA_SOURCE, self.file_path))
        urllib.request.urlretrieve(self.DATA_SOURCE, self.file_path)

    def upload(self, tournament):
        """ Parse input file and upload data to DB. """

        tournament_id = str(self.db[self.db_conf['collections']['tournament']].\
            find_one({"name": tournament})["_id"])

        with open(self.file_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')

            fields = next(reader)
            print(fields)
            self.XG_HOME = fields.index("xg1")
            self.XG_AWAY = fields.index("xg2")

            self.HOME_GOALS = fields.index("score1")
            self.AWAY_GOALS = fields.index("score2")

            self.HOME_TEAM = fields.index("team1")
            self.AWAY_TEAM = fields.index("team2")

            self.LEAGUE = fields.index("league")
            self.DATE = fields.index("date")

            for row in reader:
                if row[self.LEAGUE] == self.config['tournaments_list'][tournament] and \
                    row[self.DATE].startswith('2019') and self.is_game_has_info(row):

                    home_game = self.get_game_id(row[self.HOME_TEAM], row[self.AWAY_TEAM], 'home')
                    if not home_game:
                        self.add_game(
                            row[self.HOME_TEAM], row[self.AWAY_TEAM],
                            row[self.DATE], tournament_id, 'home',
                            row[self.HOME_GOALS], row[self.AWAY_GOALS],
                            row[self.XG_HOME], row[self.XG_AWAY])

                    away_game = self.get_game_id(row[self.AWAY_TEAM], row[self.HOME_TEAM], 'away')
                    if not away_game:
                        self.add_game(
                            row[self.AWAY_TEAM], row[self.HOME_TEAM],
                            row[self.DATE], tournament_id, 'away',
                            row[self.AWAY_GOALS], row[self.HOME_GOALS],
                            row[self.XG_AWAY], row[self.XG_HOME])


    def get_team_by_name(self, name):
        """ Get team from DB by name """
        return next(filter(lambda t: t.get(self.config["find_team_by"]) == name, self.teams))


    def is_game_finished(self, game_date):
        """ Check if a given date was passed """
        today = datetime.date.today()
        game = datetime.datetime.strptime(game_date, self.DATE_FORMAT).date()
        return today > game


    def is_game_has_info(self, game_row):
        """ Verify that game has stats data """
        return game_row[self.XG_AWAY] and game_row[self.XG_HOME]


    def get_game_id(self, team_name, opponent_name, venue):
        """ Get game from db by home team, away team """
        team_id = str(self.get_team_by_name(team_name)['_id'])
        opponent_id = str(self.get_team_by_name(opponent_name)['_id'])

        game = self.db[self.db_conf['collections']['game']].\
            find_one({
                'team': team_id,
                'opponent': opponent_id,
                'venue': venue
            })

        return game['_id'] if game else None


    def get_time(self, date_str):
        """ Convert string datetime to utc timestamp """
        date = datetime.datetime.strptime(date_str, self.DATE_FORMAT)
        return int(date.replace(tzinfo=timezone.utc).timestamp())


    def add_game(self, team, opponent, date, tournament_id, venue,
        goals_for, goals_against, xg_for, xg_against):
        """ Put game data to DB """

        team_id = str(self.get_team_by_name(team)['_id'])
        opponent_id = str(self.get_team_by_name(opponent)['_id'])

        game_data = {
            "team": team_id,
            "opponent": opponent_id,
            "tournament": tournament_id,
            "date": self.get_time(date),
            "venue": venue,
            "goals_for": int(goals_for),
            "goals_against": int(goals_against),
            "xG_for": float(xg_for),
            "xG_against": float(xg_against)
        }

        print(game_data)
        self.db[self.db_conf['collections']['game']].insert_one(game_data)


if __name__ == "__main__":
    parser = FivethirtyeightParser()
    parser.download()

    for tournament in parser.config['tournaments_list']:
        parser.upload(tournament)

    parser.client.close()