# -*- coding: utf-8 -*-
"""Provide tools to test Fox.Cub MLP artificial neural network.

Send API requests to Fox.Cub system and collect statistical
model results with actual results.
"""

from utils import *
from testing.helpers import TestSessionResult
from testing.searchers import BasePattern


class SlaveFoxCubTest:

    def __init__(self, tournament, games, patterns: BasePattern):
        # setup http client
        self.fox_cub_client = FoxCub(tournament)
        # amount of games to test. negative value means take them from the end
        self.games_to_test = games
        # search teams by pattern(s), find games only with this teams
        # and ignore the rest games in testing dataset
        self.team_patterns = patterns


    def test_data_batch(self, test_dataset, stats_dataset):
        """ Send batch of games to Fox.Cub

        Args:
            test_dataset: batch of games
            stats_dataset: dataset used to get teams statistics.
                In some cases test_dataset and stats_dataset may be equal
        """
        games, (teams_1, teams_2) = self.build_pipeline(
            test_dataset, stats_dataset)

        results = TestSessionResult(teams_1, teams_2)
        results.set_scoring_results(stats_dataset)

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


    def build_pipeline(self, test_dataset, stats_dataset):
        """ Apply search patterns gradually one by one """
        games = test_dataset
        for pattern in self.team_patterns:
            last_pattern = pattern(stats_dataset)
            games = last_pattern.get_games(self.games_to_test, games)

        return games, last_pattern.get_teams()

