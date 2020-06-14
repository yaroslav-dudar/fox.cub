# -*- coding: utf-8 -*-
"""Convert dataset file to fox.cub.gui сompatible format.

This module receive data file with games.
Fetch team/player results and create new JSON file
"""

import os
import sys
import time
import json
import argparse
from enum import Enum
from statistics import mean
from datetime import datetime

from utils import Season
from games import BaseGame
from dataset import DatasetAggregator

from testing.settings import CONFIG
from testing.slave import SlaveFoxCubTest
from testing.searchers import SingleTeamPattern

class FoxCubConverter:

    def __init__(self):
        self.parse_args() # call it first

    def str2datetime(self, value):
        if isinstance(value, datetime):
            return value

        try:
            value = datetime.strptime(value, BaseGame.date_format)
        except (ValueError, TypeError) as e:
            raise argparse.ArgumentTypeError(
                "Date should be in %s format" % BaseGame.date_format)

        return value

    def out_file_name(self):
        return "{}.json".format(self.args.team)


    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-seasons', default=100, type=int,
                            help='Amount of seasons to include in result set.')
        parser.add_argument('-team', default=100, type=str, required=True,
                            help='Target team. Resulting dataset will include games with current team')
        parser.add_argument('-dataset', required=True, type=str,
                            help='Path to the file with games that should be parsed' +\
                                 ' or name of dataset inside settings.py')
        parser.add_argument('-venueFilter', required=True, type=str,
                            help='Venue filter pattern.')

        parser.add_argument('-start', default=datetime.min, type=self.str2datetime,
                            help='Find games from this date. 1/1/1 by default')
        parser.add_argument('-end', default=datetime.now(), type=self.str2datetime,
                            help='Find games to this date. By default today')
        self.args = parser.parse_args()


    def start(self, dataset: DatasetAggregator):
        reverse = True if self.args.seasons < 0 else False
        seasons_num = abs(self.args.seasons)

        patterns = [SingleTeamPattern]
        patterns[0].selected_team = self.args.team

        result_dataset = []
        for season in Season.get_seasons(dataset.observations,
                                         reverse)[:seasons_num]:

            subdataset = dataset.split(season)[0]
            slave = SlaveFoxCubTest(None,
                                    100000,
                                    patterns,
                                    self.args.start,
                                    self.args.end)

            games, (teams_1, teams_2) = slave.build_pipeline(subdataset, season)
            games, _, _ = slave.filter_results(games, teams_1, teams_2)

            filtered_games = list(filter(self.filter_game, games))
            result_dataset.extend([self.get_result(g) for g in filtered_games])

        self.to_json(result_dataset)

    def get_result(self, game: BaseGame):
        venue = "home" if game.HomeTeam == self.args.team else "away"
        opponent = game.HomeTeam if venue == "away" else game.AwayTeam
        score_for = game.FTAG if venue == "away" else game.FTHG
        score_against = game.FTHG if venue == "away" else game.FTAG

        return {
            "venue": venue,
            "team": self.get_team_obj(self.args.team),
            "opponent": self.get_team_obj(opponent),
            "score_for": score_for,
            "score_against": score_against,
            "points_for": game.get_team_points(self.args.team),
            "points_against": game.get_team_points(opponent),
            "date": game.date_as_timestamp()
        }

    def filter_game(self, game):
        return self.args.start <=\
            game.date_as_datetime() <= self.args.end and\
            (self.args.team in [game.HomeTeam, game.AwayTeam])

    def to_json(self, data):
        with open(self.out_file_name(), 'w+') as outfile:
            json.dump(data, outfile)

    def get_team_obj(self, team):
        oid = hash(team)
        return [{"_id":{"$oid": oid}, "name": team}]

if __name__ == '__main__':
    converter = FoxCubConverter()
    dataset = CONFIG[converter.args.dataset]

    start_at = time.time()
    converter.start(dataset)
    print("Execution time: {}".format(time.time() - start_at))
