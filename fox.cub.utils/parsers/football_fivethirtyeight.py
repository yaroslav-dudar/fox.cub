import csv
import os
import ssl
import urllib.request

import pymongo
import datetime
from datetime import timezone
from collections import namedtuple

from config import Config
from models import Team, Game, Tournament

League = namedtuple("League",
                    ["id", "teams", "games", "name", "range"],
                    defaults=(None,) * 5)

class FivethirtyeightParser:

    FIND_TOURN_BY = property(lambda self: 'name')
    DATE_FORMAT =   property(lambda self: "%Y-%m-%d")
    DATA_SOURCE =   property(lambda self: "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv")

    def __init__(self):

        self.global_conf = Config()
        self.config = self.global_conf['fivethirtyeight_parser']

        self.leagues_list = {}
        self.init_data()

        self.ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_ctx.load_verify_locations(cafile='/etc/ssl/certs/ca-certificates.crt')

        self.download_to = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "..", "data", "tmp"
        )
        self.file_path = os.path.join(self.download_to, 'spi_matches.csv')

    def init_data(self):
        # upload tournaments and teams from DB
        for t_name in self.config['tournaments_list']:
            tournament = Tournament.get(t_name, self.FIND_TOURN_BY)
            tournament_config = self.config['tournaments_list'][t_name]
            t_external_name = tournament_config['league']

            date_range = self.season_date_range(tournament_config['range'])

            if not tournament:
                self.leagues_list[t_external_name] = None
            else:
                t_id = str(tournament['_id'])
                self.leagues_list[t_external_name] = League(t_id,
                                                            Team.find(t_id),
                                                            Game.find_all(t_id),
                                                            t_name,
                                                            date_range)

    def download(self):
        """
            Download csv file with games stats from
            https://github.com/fivethirtyeight/data/tree/master/soccer-spi
        """

        print("Download file: {0}. Save to: {1}".format(self.DATA_SOURCE, self.file_path))
        with urllib.request.urlopen(self.DATA_SOURCE, context=self.ssl_ctx) as u, \
            open(self.file_path, 'wb') as f:
                f.write(u.read())


    def find_dataset_fields(self):
        """ Recognize dataset field names based on first row """
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


    def start(self):
        """ Parse input file and upload data to DB. """

        with open(self.file_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            # skip field names row
            next(reader)

            for row in reader:
                league = self.leagues_list.get(row[self.LEAGUE])
                if league and \
                    league.range['start'] < row[self.DATE] < league.range['end'] and \
                    self.is_game_has_info(row):

                    self.process_row(row, league)


    def process_row(self, row, tournament):
        home_game = self.get_game_id(row[self.HOME_TEAM],
                                     row[self.AWAY_TEAM],
                                     'home',
                                     tournament)
        if not home_game:
            self.add_game(
                row[self.HOME_TEAM], row[self.AWAY_TEAM],
                row[self.DATE], tournament, 'home',
                row[self.HOME_GOALS], row[self.AWAY_GOALS],
                row[self.XG_HOME], row[self.XG_AWAY])

        away_game = self.get_game_id(row[self.AWAY_TEAM],
                                     row[self.HOME_TEAM],
                                     'away',
                                     tournament)
        if not away_game:
            self.add_game(
                row[self.AWAY_TEAM], row[self.HOME_TEAM],
                row[self.DATE], tournament, 'away',
                row[self.AWAY_GOALS], row[self.HOME_GOALS],
                row[self.XG_AWAY], row[self.XG_HOME])


    def is_game_finished(self, game_date):
        """ Check if a given date was passed """
        today = datetime.date.today()
        game = datetime.datetime.strptime(game_date, self.DATE_FORMAT).date()
        return today > game


    def is_game_has_info(self, game_row):
        """ Verify that game has stats data """
        return game_row[self.XG_AWAY] and game_row[self.XG_HOME]


    def get_game_id(self, team_name, opponent_name, venue, tournament: League):
        """ Get game from db by home team, away team """

        team_id = Team.get_id(
            team_name,
            self.config["find_team_by"],
            tournament.teams)

        opponent_id = Team.get_id(
            opponent_name,
            self.config["find_team_by"],
            tournament.teams)

        game = Game.find_one(team_id, opponent_id, tournament.id, venue)
        return game['_id'] if game else None


    def get_time(self, date_str):
        """ Convert string datetime to utc timestamp """
        date = datetime.datetime.strptime(date_str, self.DATE_FORMAT)
        return int(date.replace(tzinfo=timezone.utc).timestamp())


    def add_game(self, team, opponent, date, tournament: League, venue,
        goals_for, goals_against, xg_for, xg_against):
        """ Put game data to DB """
        team_id = Team.get_id(
            team,
            self.config["find_team_by"],
            tournament.teams,
            False)

        opponent_id = Team.get_id(
            opponent,
            self.config["find_team_by"],
            tournament.teams,
            False)

        game_data = Game.get_document(team_id, opponent_id,
                                      tournament.id, self.get_time(date),
                                      venue, goals_for, goals_against,
                                      xg_for, xg_against)
        print(game_data)
        Game.insert(game_data)

    def season_date_range(self, _range: dict):
        """ Generate season start-end date range based on years. """
        if _range['start'] == _range['end']:
            # spring-to-autumn cycle
            return {
                "start": "%d-01-01" % _range['start'],
                "end": "%d-12-31" % _range['end'],
            }
        elif _range['start'] + 1 == _range['end']:
            # summer-to-spring cycle
            return {
                "start": "%d-07-01" % _range['start'],
                "end": "%d-06-31" % _range['end'],
            }
        else:
            raise Exception("Incorrect season range")


if __name__ == "__main__":
    parser = FivethirtyeightParser()
    parser.download()
    parser.find_dataset_fields()
    parser.start()
