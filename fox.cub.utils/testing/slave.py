# -*- coding: utf-8 -*-
"""Provide tools to test Fox.Cub MLP artificial neural network.

Send API requests to Fox.Cub system and collect statistical
model results with actual results.
"""


import sys
import time

from utils import *
from testing.helpers import TestSessionResult

import sys


class SlaveFoxCubTest:

    str_to_datetime = lambda self, g: datetime.strptime(g['Date'], '%d/%m/%Y')

    def __init__(self, tournament):
        # setup http client
        self.fox_cub_client = FoxCub(tournament)


    def get_test_teams_by_scoring(self, stats_data):
        # TODO: pass attack, defend stats via func params
        scoring_table = get_season_table(stats_data, metric='scored')
        cons_table = get_season_table(stats_data, metric='conceded')

        # teams1
        scoring_teams_1 = filter(
            lambda t: 1.1 < scoring_table[t]/get_team_games(stats_data, t) < 3.5,
            scoring_table.keys())

        defending_teams_1 = filter(
            lambda t: 0.1 < cons_table[t]/get_team_games(stats_data, t) < 3.2,
            cons_table.keys())

        # teams2
        scoring_teams_2 = filter(
            lambda t: 0.3 < scoring_table[t]/get_team_games(stats_data, t) < 3.35,
            scoring_table.keys())

        defending_teams_2 = filter(
            lambda t: 0.9 < cons_table[t]/get_team_games(stats_data, t) < 3.2,
            cons_table.keys())

        teams_1 = set(scoring_teams_1) & set(defending_teams_1)
        teams_2 = set(scoring_teams_2) & set(defending_teams_2)

        return teams_1, teams_2


    def get_test_teams_by_points(self, stats_data,
        team1_pos_min, team1_pos_max,
        team2_pos_min, team2_pos_max):

        points_table = get_season_table(stats_data, metric='points')
        teams_1 = list(points_table)[team1_pos_min:team1_pos_max]
        teams_2 = list(points_table)[team2_pos_min:team2_pos_max]

        return teams_1, teams_2


    def test_data_batch(self, test_dataset, stats_dataset):
        """ Send batch of games to Fox.Cub

        Args:
            test_dataset: batch of games
            stats_dataset: dataset used to get teams statistics.
                In some cases test_dataset and stats_dataset may be equal
        """

        namespace = TestSessionResult()
        scoring_table = get_season_table(stats_dataset, metric='scored')
        cons_table = get_season_table(stats_dataset, metric='conceded')

        teams_1, teams_2 = self.get_test_teams_by_scoring(stats_dataset)
        #teams_1, teams_2 = self.get_test_teams_by_points(stats_dataset, 0, 24, 0, 24)

        for t in teams_1:
            # save team1 stats
            namespace.scored_1.append(scoring_table[t] / get_team_games(stats_dataset, t))
            namespace.conceded_1.append(cons_table[t] / get_team_games(stats_dataset, t))

        for t in teams_2:
            # save team2 stats
            namespace.scored_2.append(scoring_table[t] / get_team_games(stats_dataset, t))
            namespace.conceded_2.append(cons_table[t] / get_team_games(stats_dataset, t))

        skip_games = len(test_dataset) * 0.0
        sorted_games = sorted(test_dataset, key=self.str_to_datetime)
        process_games = sorted_games[:]

        games = list(filter(lambda g:
            (g['HomeTeam'] in teams_2 and g['AwayTeam'] in teams_1) or
            (g['HomeTeam'] in teams_1 and g['AwayTeam'] in teams_2),  process_games))

        session_id = test_fox_cub(games, stats_dataset, self.fox_cub_client, True)

        for i, g in enumerate(games):
            namespace.totals_2_5.append(is_total_under(g, total=2.5))
            namespace.totals_3_5.append(is_total_under(g, total=3.5))
            namespace.btts.append(float(g['FTHG']) > 0 and float(g['FTAG']) > 0)

            self.process_results(namespace, g, self.fox_cub_client.results[session_id][i], teams_1)
            namespace.model_results.append(self.fox_cub_client.results[session_id][i])

        self.fox_cub_client.clear_results(session_id)

        return {
            'totals_2_5': namespace.totals_2_5,
            'totals_3_5': namespace.totals_3_5,
            'btts': namespace.btts,
            'actual_results_team1': namespace.actual_results_team1,
            'actual_results_team2': namespace.actual_results_team2,
            'model_results': namespace.model_results,
            'scored_1': namespace.scored_1,
            'scored_2': namespace.scored_2,
            'conceded_1': namespace.conceded_1,
            'conceded_2': namespace.conceded_2
        }


    @staticmethod
    def process_results(namespace, game, fox_cub_res, teams_1):
        """ Determine Team1 and Team2 for actual and model results"""
        if game['HomeTeam'] in teams_1:
            namespace.actual_results_team1.append(float(game['FTHG']) - float(game['FTAG']))
            namespace.actual_results_team2.append(float(game['FTAG']) - float(game['FTHG']))
        else:
            namespace.actual_results_team2.append(float(game['FTHG']) - float(game['FTAG']))
            namespace.actual_results_team1.append(float(game['FTAG']) - float(game['FTHG']))

        if fox_cub_res['HomeTeam'] in teams_1:
            fox_cub_res['Team1'] = "Home"
            fox_cub_res['Team2'] = "Away"
        else:
            fox_cub_res['Team1'] = "Away"
            fox_cub_res['Team2'] = "Home"


    def _namespace():
        return {

        }
        totals_2_5, totals_3_5 = [], []
        actual_results_team1, actual_results_team2 = [], []
        model_results = []
        scored_1, conceded_1 = [], []
        scored_2, conceded_2 = [], []

        btts = []