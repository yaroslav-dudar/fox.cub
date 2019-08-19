# -*- coding: utf-8 -*-
"""Provide tools to test Fox.Cub MLP artificial neural network.

Send API requests to Fox.Cub system and collect statistical
model results with actual results.
"""

from utils import *
from dataset import DatasetAggregator
from testing.helpers import TestSessionResult
from testing.searchers import BasePattern

from typing import List


class SlaveFoxCubTest:

    def __init__(self, tournament, games: List[Game], patterns: BasePattern):
        # setup http client
        self.fox_cub_client = FoxCub(tournament)
        # amount of games to test. negative value means take them from the end
        self.games_to_test = games
        # search teams by pattern(s), find games only with this teams
        # and ignore the rest games in testing dataset
        self.team_patterns = patterns


    def test_data_batch(self, dataset: DatasetAggregator, season: str):
        """ Send batch of games to Fox.Cub

        Args:
            test_dataset: batch of games
            stats_dataset: dataset used to get teams statistics.
                In some cases test_dataset and stats_dataset may be equal
        """
        games, (teams_1, teams_2) = self.build_pipeline(dataset, season)

        testing_season = Season.get(dataset.observations, season)
        results = TestSessionResult(teams_1, teams_2)
        results.set_scoring_results(testing_season)

        session_id = test_fox_cub(games,
                                  dataset,
                                  self.fox_cub_client)

        for i, g in enumerate(games):
            results.totals_2_5.append(g.is_total_under(total=2.5))
            results.totals_3_5.append(g.is_total_under(total=3.5))
            results.set_actual_results(g)
            model_result = self.fox_cub_client.results[session_id][i]
            results.set_model_results(model_result)

        self.fox_cub_client.clear_results(session_id)
        return results


    def build_pipeline(self, dataset: DatasetAggregator, season):
        """ Apply search patterns gradually one by one """
        games = dataset.observations
        for pattern in self.team_patterns:
            last_pattern = pattern(dataset, season)
            games = last_pattern.get_games(self.games_to_test, games)

        return games, last_pattern.get_teams()

