# -*- coding: utf-8 -*-
"""Provide tools to test Fox.Cub MLP artificial neural network.

Send API requests to Fox.Cub system and collect statistical
model results with actual results.
"""

from utils import *
from testing.helpers import (
    TestSessionResult,
    StrongWithWeakPattern,
    BasePattern)

class SlaveFoxCubTest:

    def __init__(self, tournament, games, pattern):
        # setup http client
        self.fox_cub_client = FoxCub(tournament)
        # amount of games to test from the end
        self.games_to_test = games
        # search teams by pattern, find games only with this teams
        # and ignore the rest games in testing dataset
        self.team_pattern = pattern


    def get_test_teams_by_points(self, stats_data, team1_pos_min,
                                 team1_pos_max, team2_pos_min, team2_pos_max):

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
        pattern = self.team_pattern(stats_dataset)
        teams_1, teams_2 = pattern.get_teams()

        results = TestSessionResult(teams_1, teams_2)
        results.set_scoring_results(stats_dataset)
        games = pattern.get_games(self.games_to_test, test_dataset)

        session_id = test_fox_cub(games,
                                  stats_dataset,
                                  self.fox_cub_client,
                                  True)

        for i, g in enumerate(games):
            results.totals_2_5.append(is_total_under(g, total=2.5))
            results.totals_3_5.append(is_total_under(g, total=3.5))
            results.set_actual_results(g)
            model_result = self.fox_cub_client.results[session_id][i]
            results.set_model_results(model_result)

        self.fox_cub_client.clear_results(session_id)
        return results
