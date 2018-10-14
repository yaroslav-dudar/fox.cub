
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

from bson.objectid import ObjectId

DEFUALT_LEAGUES = ['Premier League England', 'EFL Championship', 'Bundesliga']

class Downloader:

    team_name = "football_co_uk_name"

    def __init__(self, season='1819', leagues=DEFUALT_LEAGUES):
        self.file_names = {
            DEFUALT_LEAGUES[0]: 'E0.csv',
            DEFUALT_LEAGUES[1]: 'E1.csv',
            DEFUALT_LEAGUES[2]: 'D1.csv',
        }

        self.url = 'http://www.football-data.co.uk/mmz4281/'

        self.season = season + "/"
        self.leagues = leagues

        self.download_to = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'data'
        )

        self.date_format = "%d/%m/%y"
        self.client = pymongo.MongoClient("localhost", 27017)

        self.db_data = []

    def download(self):
        """ Download csv files with statistics from football-data.co.uk """

        for league in self.leagues:
            file_name = self.file_names[league]
            file_path = os.path.join(self.download_to, file_name)
            file_url = reduce(urljoin, [self.url, self.season, file_name])
            print("Download file: %s" % file_url)
            urllib.request.urlretrieve(file_url, file_path)

    def get_db_data(self):
        """ Fetch current data from DB """

        for tournament in DEFUALT_LEAGUES:
            tournament_id = str(self.client.fox_cub.tournament.\
                find_one({"name": tournament})["_id"])
            self.db_data.extend(list(self.client.fox_cub.game_stats.\
                find({"tournament": tournament_id})))

    def is_exists(self, tournament_id, date, team_id):
        """ Check if given data already exists in DB """

        for row in self.db_data:
            if row["tournament"] == tournament_id and\
                row["date"] == date and row["team"] == team_id:

                return True
        
        return False

    def upload(self, tournament=DEFUALT_LEAGUES[0]):
        """ Move data from csv to DB """

        filename = self.file_names[tournament]
        filepath = os.path.join(self.download_to, filename)
        teams = list(self.client.fox_cub.team.find())

        # get tournament id from DB
        tournament_id = str(self.client.fox_cub.tournament.\
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
                    team = next(filter(lambda t: t[self.team_name] == row[home_team], teams))
                    opponent = next(filter(lambda t: t[self.team_name] == row[away_team], teams))
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
                date = int(time.mktime(
                    time.strptime(row[game_date], self.date_format)
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
                    self.client.fox_cub.game_stats.insert_many(documents)
                else:
                    print("No fresh data!")
            except Exception as err:
                print(err.details)


if __name__ == "__main__":
    d = Downloader()
    d.get_db_data()
    d.download()

    for tournament in DEFUALT_LEAGUES:
        print("===", tournament, "===")
        d.upload(tournament)

    d.client.close()
