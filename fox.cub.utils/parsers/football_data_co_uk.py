
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urljoin
import urllib.request

from functools import reduce
from datetime import datetime

import os
import csv
import time

import pymongo

from config import Config

class Downloader:

    DATA_FOLDER = "data"

    def __init__(self):
        self.global_conf = Config()
        self.config = self.global_conf['data_co_uk_parser']
        self.db_conf = self.global_conf['database']

        self.client = pymongo.MongoClient(
            self.db_conf['host'],
            self.db_conf['port']
        )
        self.db = self.client[self.db_conf['db_name']]

        self.download_to = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), self.DATA_FOLDER
        )

        self.date_format_1 = "%d/%m/%y"
        self.date_format_2 = "%d/%m/%Y"

        self.db_data = []

    def get_filename(self, url):
        """ Fetch file name from URL """
        return url.split("/")[-1]

    def download(self):
        """ Download csv files with statistics from football-data.co.uk """

        for _, t_url in self.config['tournaments_list'].items():
            file_path = os.path.join(self.download_to, self.get_filename(t_url))
            print("Download file: %s" % t_url)
            urllib.request.urlretrieve(t_url, file_path)

    def get_db_data(self):
        """ Fetch current data from DB """

        for tournament in self.config['tournaments_list']:
            tournament_id = str(self.db[self.db_conf['collections']['tournament']].\
                find_one({"name": tournament})["_id"])
            self.db_data.extend(list(self.db[self.db_conf['collections']['game']].\
                find({"tournament": tournament_id})))

    def is_exists(self, tournament_id, date, team_id):
        """ Check if given data already exists in DB """

        for row in self.db_data:
            if row["tournament"] == tournament_id and\
                row["date"] == date and row["team"] == team_id:

                return True

        return False

    def upload(self, tournament):
        """ Move data from csv to DB """

        filename = self.get_filename(
            self.config['tournaments_list'][tournament]
        )
        filepath = os.path.join(self.download_to, filename)
        teams = list(self.client.fox_cub.team.find())

        # get tournament id from DB
        tournament_id = str(self.db[self.db_conf['collections']['tournament']].\
            find_one({"name": tournament})["_id"])

        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')

            fields = next(reader)

            home_team = fields.index("HomeTeam")
            away_team = fields.index("AwayTeam")

            home_goals = fields.index("FTHG")
            away_goals = fields.index("FTAG")

            game_date = fields.index("Date")

            documents = []
            for row in reader:
                try:
                    team = next(filter(lambda t: t[self.config['find_team_by']] == row[home_team], teams))
                    opponent = next(filter(lambda t: t[self.config['find_team_by']] == row[away_team], teams))
                except StopIteration:
                    continue

                try:
                    # check if goals data present
                    int(row[home_goals])
                    int(row[away_goals])
                except:
                    continue

                team_id = str(team["_id"])
                opponent_id = str(opponent["_id"])

                try:
                    date = int(time.mktime(
                        time.strptime(row[game_date], self.date_format_1)
                    ))
                except ValueError:
                    date = int(time.mktime(
                        time.strptime(row[game_date], self.date_format_2)
                    ))

                if not self.is_exists(tournament_id, date, team_id):
                    # home team
                    documents.append({
                        "team": team_id,
                        "opponent": opponent_id,
                        "tournament": tournament_id,
                        "date": date,
                        "venue": "home",
                        "goals_for": int(row[home_goals]),
                        "goals_against": int(row[away_goals]),
                        "xG_for": 1.0,
                        "xG_against": 1.0
                    })

                if not self.is_exists(tournament_id, date, opponent_id):
                    # away team
                    documents.append({
                        "team": opponent_id,
                        "opponent": team_id,
                        "tournament": tournament_id,
                        "date": date,
                        "venue": "away",
                        "goals_for": int(row[away_goals]),
                        "goals_against": int(row[home_goals]),
                        "xG_for": 1.0,
                        "xG_against": 1.0
                    })

                print(row[home_team], row[home_goals], "-", row[away_goals], row[away_team])

            try:
                if documents:
                    self.db[self.db_conf['collections']['game']].insert_many(documents)
                else:
                    print("No fresh data!")
            except Exception as err:
                print(err.details)


if __name__ == "__main__":
    d = Downloader()
    d.get_db_data()
    d.download()

    for tournament in d.config['tournaments_list']:
        print("===", tournament, "===")
        d.upload(tournament)

    d.client.close()
