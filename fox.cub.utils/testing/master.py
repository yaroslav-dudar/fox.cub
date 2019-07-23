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
from testing.helpers import TestSessionResult, VenueFilter, import_string


class Tournament(Enum):

    EPL = "5b8a36a335b9d3a022e66887"
    Championship = "5b8a36a335b9d3a022e66888"
    MLS = "5ca22044b8fa4a20ff05e731"
    International_Qualification = "5ce63f5200c0b9b3700e5a88"
    International_Final = "5ce63f5200c0b9b3700e5a87"
    Bundesliga = "5baa5789adddfaf57a803bb2"


class MasterFoxCubTest:

    def __init__(self):
        self.parse_args() # call it first
        self.executor = ProcessPoolExecutor(max_workers=self.args.slaves)

        self.futures, self.patterns = [], []
        self.results = TestSessionResult()
        self.parse_config()

    def check_pattern_path(self, value):
        if not (isinstance(value, str) and '.' in value):
            raise argparse.ArgumentTypeError(
                "%s is an invalid path to the python class" % value)
        return value

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-slaves', default=4, type=int,
                            help='Amount of slaves to use in a test.')
        parser.add_argument('-patterns', type=self.check_pattern_path,
                            default='testing.searchers.AllPattern',
                            help='Teams searching pattern(s) class.' +\
                                 ' Use `,` separator to combine multiple paterns.')
        parser.add_argument('-games', default=5000, type=int,
                            help='Amount of games to test for each season.')
        parser.add_argument('-seasons', default=100, type=int,
                            help='Amount of seasons to test in current session.')
        parser.add_argument('-testDataset', required=True, type=str,
                            help='Path to the file with teams statistics.' +\
                                 ' Usefull when stats and test datasets are not the same.')
        parser.add_argument('-statDataset', default=None, type=str,
                            help='Path to the statistics data file.')
        parser.add_argument('-venueFilter', required=True, type=str,
                            help='Venue filter pattern.')
        parser.add_argument('-tournamentId', required=True, type=str,
                            help='Selecting MLP model based on this attribute')
        parser.add_argument('-groupBy', default="Off", type=str,
                            help='Define how to group teams inside a season.')
        self.args = parser.parse_args()

    def parse_config(self):
        """ Parse passed args and to map them with python objects """
        if self.args.statDataset is None:
            # use testDataset for stats if not specified
            self.args.statDataset = self.args.testDataset

        _filt = VenueFilter(self.args.venueFilter)
        for path in self.args.patterns.split(','):
            pattern = import_string(path)
            pattern.venue_filter = _filt
            self.patterns.append(pattern)

        self.group_by = Group(self.args.groupBy)

    def test(self, test_dataset, stats_dataset):
        """ Make API calls to Fox.Cub statistical model
        and compare model results with real results.
        Using to test Fox.Cub model

        Args:
            test_dataset: games to test with Fox.Cub model
            stats_dataset: dataset used to get teams statistics.
                In some cases test_dataset and stats_dataset may be equal
        """

        slave = SlaveFoxCubTest(self.args.tournamentId, self.args.games, self.patterns)
        reverse = True if self.args.seasons < 0 else False
        stop_at = abs(self.args.seasons)

        for season in get_seasons(test_dataset, reverse)[:stop_at]:
            data_season = filter_by_season(test_dataset, str(season))
            stats_data = filter_by_season(stats_dataset, str(season))

            if self.group_by == Group.Disable:
                f = self.executor.submit(slave.test_data_batch,
                                         data_season, stats_data)
                self.futures.append(f)

            elif self.group_by == Group.Group:
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
        score = sum([res[attr] for res in self.results.model_results])
        return score / len(self.results.model_results)

    def get_fox_cub_scoreline(self, score_type, team):
        """ Get total score to win with a given handicap """
        def get_attr(result):
            return result[result[team] + " " + score_type]

        score = sum([get_attr(res) for res in self.results.model_results])
        return score / len(self.results.model_results)

    def get_actual_results(self, actual_results, handicap):
        """ Get win percentage with a given handicap """
        wins = list(filter(lambda r: r > handicap, actual_results))
        return len(wins) / len(actual_results)

    def get_percentage(self, collection, value):
        """ Calculate percentage of a given value in collection """
        return collection.count(value) / len(collection)


if __name__ == '__main__':
    tester = MasterFoxCubTest()
    test_dataset = readfile(tester.args.testDataset)
    stats_dataset = readfile(tester.args.statDataset)

    start_at = time.time()

    tester.test(test_dataset, stats_dataset)
    tester.print_test_results()
    tester.results.cleanup()
    print("Execution time: {}".format(time.time() - start_at))
