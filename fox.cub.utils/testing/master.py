# -*- coding: utf-8 -*-
"""Master process responsible for spawning testing slave processes.

This module receive testing data. Divide it to pieces and delegate work to slaves.
Collect results from slaves and output overall testing results to stdout
"""

import os
import sys
import time
import argparse
from statistics import mean
from concurrent.futures import ProcessPoolExecutor, ALL_COMPLETED, wait

from utils import *
from enum import Enum
from testing.slave import SlaveFoxCubTest
from testing.helpers import TestSessionResult, pattern_factory


class Tournament(Enum):

    EPL = "5b8a36a335b9d3a022e66887"
    Championship = "5b8a36a335b9d3a022e66888"
    MLS = "5ca22044b8fa4a20ff05e731"
    International_Qualification = "5ce63f5200c0b9b3700e5a88"
    International_Final = "5ce63f5200c0b9b3700e5a87"
    Bundesliga = "5baa5789adddfaf57a803bb2"


class Group(Enum):

    Disable = 0
    Group = 1


class MasterFoxCubTest:
    def __init__(self):
        self.parse_args() # call it first
        self.executor = ProcessPoolExecutor(max_workers=self.args.slaves)
        # list of worker futures
        self.futures = []
        self.results = TestSessionResult()
        self.pattern = pattern_factory(self.args.pattern)
        print(self.pattern)


    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-slaves', default=4, type=int,
                            help='Amount of slaves to use in a test.')
        parser.add_argument('-pattern', default='AllPattern', type=str,
                            help='Teams searching pattern.')
        parser.add_argument('-games', default=5000, type=int,
                            help='Amount of games to test for each season')
        parser.add_argument('-dataFolder', required=True, type=str,
                            help='Path to the testing data folder')
        self.args = parser.parse_args()


    def test(self, test_dataset, stats_dataset,
        tournament, group_by=Group.Disable):
        """ Make API calls to Fox.Cub statistical model
        and compare model results with real results.
        Using to test Fox.Cub model

        Args:
            test_dataset: games to test with Fox.Cub model
            stats_dataset: dataset used to get teams statistics.
                In some cases test_dataset and stats_dataset may be equal
            group_by: define how to group teams inside a season
        """

        slave = SlaveFoxCubTest(tournament, self.args.games, self.pattern)

        for season in get_seasons(test_dataset):
            data_season = filter_by_season(test_dataset, str(season))
            stats_data = filter_by_season(stats_dataset, str(season))

            if group_by == Group.Disable:
                f = self.executor.submit(slave.test_data_batch,
                                         data_season, stats_data)
                self.futures.append(f)

            elif group_by == Group.Group:
                groups = get_groups(test_dataset)

                for group in groups:
                    if group == -1: continue

                    data_group = filter_by_group(data_season, group)
                    stats_group = filter_by_group(stats_data, group)

                    scoring_table = get_season_table(stats_group,
                                                     metric='scored')
                    cons_table = get_season_table(stats_group,
                                                  metric='conceded')

                    f = self.executor.submit(slave.test_data_batch,
                                             data_group, stats_group)
                    self.futures.append(f)

        wait(self.futures, return_when=ALL_COMPLETED)
        for f in self.futures:
            self.results += f.result()


    def print_test_results(self):
        print("Tested games:", len(self.results.actual_results_team1))
        print("Scored avg team1:", mean(self.results.scored_1))
        print("Conceded avg team1:", mean(self.results.conceded_1))
        print("Scored avg team2:", mean(self.results.scored_2))
        print("Conceded avg team2:", mean(self.results.conceded_2))
        print('='*25)
        print("Real results Team1 Win:", self.get_actual_results(self.results.actual_results_team1, 0))
        print("Real results Team2 Win:", self.get_actual_results(self.results.actual_results_team2, 0))
        print("Real results Draw:", self.get_percentage(self.results.actual_results_team2, 0))
        print("Real results Total Under 2.5:", self.get_percentage(self.results.totals_2_5, True))
        print("Real results Total Under 3.5:", self.get_percentage(self.results.totals_3_5, True))
        print("Real results BTTS:", self.get_percentage(self.results.btts, True))
        print('='*25)
        print("Fox.cub results Team1 Win:", self.get_fox_cub_scoreline('Win', 'Team1'))
        print("Fox.cub results Team2 Win:", self.get_fox_cub_scoreline('Win', 'Team2'))
        print("Fox.cub results Draw:", self.get_fox_cub_results('Draw'))
        print("Fox.cub results Total Under 2.5:", self.get_fox_cub_results('under 2.5'))
        print("Fox.cub results Total Under 3.5:", self.get_fox_cub_results('under 3.5'))
        print("Fox.cub results BTTS:", self.get_fox_cub_results('BTTS'))
        print('='*25)
        print("Real results Team1 Win +1.5:", self.get_actual_results(self.results.actual_results_team1, 1))
        print("Real results Team1 Win +2.5:", self.get_actual_results(self.results.actual_results_team1, 2))
        print("Real results Team2 Win +1.5:", self.get_actual_results(self.results.actual_results_team2, 1))
        print("Real results Team2 Win +2.5:", self.get_actual_results(self.results.actual_results_team2, 2))

        print("Fox.cub results Team1 Win +1.5:", self.get_fox_cub_scoreline('Win +1.5', 'Team1'))
        print("Fox.cub results Team1 Win +2.5:", self.get_fox_cub_scoreline('Win +2.5', 'Team1'))
        print("Fox.cub results Team2 Win +1.5:", self.get_fox_cub_scoreline('Win +1.5', 'Team2'))
        print("Fox.cub results Team2 Win +2.5:", self.get_fox_cub_scoreline('Win +2.5', 'Team2'))


    def get_fox_cub_results(self, attr):
        """ Get total score of a given attribute """
        return sum([res[attr] for res in self.results.model_results]) / len(self.results.model_results)


    def get_fox_cub_scoreline(self, score_type, team):
        """ Get total score to win with a given handicap """
        def get_attr(result):
            return result[result[team] + " " + score_type]

        score = sum([get_attr(res) for res in self.results.model_results])
        return score / len(self.results.model_results)


    def get_actual_results(self, actual_results, handicap):
        """ Get win percentage with a given handicap """
        return len(list(filter(lambda r: r > handicap, actual_results))) / len(actual_results)

    def get_percentage(self, collection, value):
        """ Calculate percentage of a given value in collection """
        return collection.count(value) / len(collection)


if __name__ == '__main__':
    tester = MasterFoxCubTest()
    test_dataset = readfile(join_path(tester.args.dataFolder, "leagues/mls.json"))
    stats_dataset = readfile(join_path(tester.args.dataFolder, "leagues/mls.json"))

    start_at = time.time()

    tester.test(test_dataset, stats_dataset,
        Tournament.International_Final.value, Group.Disable)
    tester.print_test_results()
    tester.results.cleanup()
    print("Execution time: {}".format(time.time() - start_at))
