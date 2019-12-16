# -*- coding: utf-8 -*-
"""Provide tools to test Fox.Cub MLP artificial neural network.

Send API requests to Fox.Cub system and collect statistical
model results with actual results.
"""

from utils import *
from dataset import DatasetAggregator, ObservationDataset
from testing.helpers import TestSessionResult
from testing.searchers import BasePattern

from typing import List, Tuple


class SlaveFoxCubTest:

    def __init__(self, tournament, games: List[Game], patterns: BasePattern):
        # setup http client
        self.fox_cub_client = FoxCub(tournament)
        # amount of games to test. negative value means take them from the end
        self.games_to_test = games
        # search teams by pattern(s), find games only with this teams
        # and ignore the rest games in testing dataset
        assert len(patterns) > 0
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
        results.league_goals_avg.append(
            dataset.get_season(season).league_avg)

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
        teams_1, teams_2 = None, None

        for pattern in self.team_patterns:
            last_pattern = pattern(dataset, season)
            games = last_pattern.get_games(self.games_to_test, games)

            if not teams_1 and not teams_2:
                teams_1, teams_2 = last_pattern.get_teams()
            else:
                teams_1, teams_2 = self.intersection((teams_1, teams_2),
                                                     last_pattern.get_teams())

        return games, (teams_1, teams_2)

    def intersection(self, tuple1: Tuple[set, set],
                     tuple2: Tuple[set, set]) -> Tuple[set, set]:

        intersection_result1 = tuple1[0] & tuple2[0]
        intersection_result2 = tuple1[1] & tuple2[1]
        return intersection_result1, intersection_result2
