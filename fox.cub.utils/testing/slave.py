# -*- coding: utf-8 -*-
"""Provide tools to test Fox.Cub MLP artificial neural network.

Send API requests to Fox.Cub system and collect statistical
model results with actual results.
"""

from utils import *
from testing.helpers import TestSessionResult, StrongWithWeekPattern

class SlaveFoxCubTest:

    str_to_datetime = lambda self, g: datetime.strptime(g['Date'], '%d/%m/%Y')

    def __init__(self, tournament, pattern = None):
        # setup http client
        self.fox_cub_client = FoxCub(tournament)
        # search teams by pattern, find games only with this teams
        # and ignore the rest games in testing dataset
        if pattern:
            self.team_pattern = pattern
        else:
            self.team_pattern = StrongWithWeekPattern


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

        results = TestSessionResult()
        scoring_table = get_season_table(stats_dataset, metric='scored')
        cons_table = get_season_table(stats_dataset, metric='conceded')

        teams_1, teams_2 = self.team_pattern(stats_dataset).get_teams()

        for t in teams_1:
            # save team1 stats
            results.scored_1.append(
                scoring_table[t] / get_team_games(stats_dataset, t))
            results.conceded_1.append(
                cons_table[t] / get_team_games(stats_dataset, t))

        for t in teams_2:
            # save team2 stats
            results.scored_2.append(
                scoring_table[t] / get_team_games(stats_dataset, t))
            results.conceded_2.append(
                cons_table[t] / get_team_games(stats_dataset, t))

        skip_games = len(test_dataset) * 0.0
        sorted_games = sorted(test_dataset, key=self.str_to_datetime)
        process_games = sorted_games[:]

        games = list(filter(lambda g:
            (g['HomeTeam'] in teams_2 and g['AwayTeam'] in teams_1) or
            (g['HomeTeam'] in teams_1 and g['AwayTeam'] in teams_2),
            process_games))

        session_id = test_fox_cub(games,
                                  stats_dataset,
                                  self.fox_cub_client,
                                  True)

        for i, g in enumerate(games):
            results.totals_2_5.append(is_total_under(g, total=2.5))
            results.totals_3_5.append(is_total_under(g, total=3.5))
            results.btts.append(float(g['FTHG']) > 0 and float(g['FTAG']) > 0)

            self.process_results(results, g,
                                 self.fox_cub_client.results[session_id][i],
                                 teams_1)
            results.model_results.append(
                self.fox_cub_client.results[session_id][i])

        self.fox_cub_client.clear_results(session_id)
        return results


    @staticmethod
    def process_results(results, game, fox_cub_res, teams_1):
        """ Determine Team1 and Team2 for actual and model results"""
        if game['HomeTeam'] in teams_1:
            results.actual_results_team1.\
                append(float(game['FTHG']) - float(game['FTAG']))
            results.actual_results_team2.\
                append(float(game['FTAG']) - float(game['FTHG']))
        else:
            results.actual_results_team2.\
                append(float(game['FTHG']) - float(game['FTAG']))
            results.actual_results_team1.\
                append(float(game['FTAG']) - float(game['FTHG']))

        if fox_cub_res['HomeTeam'] in teams_1:
            fox_cub_res['Team1'] = "Home"
            fox_cub_res['Team2'] = "Away"
        else:
            fox_cub_res['Team1'] = "Away"
            fox_cub_res['Team2'] = "Home"
