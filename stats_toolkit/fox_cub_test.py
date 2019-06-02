"""Provide tools to test Fox.Cub MLP artificial neural network."""

from utils import *
from enum import Enum

import sys

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


class TestModel:

    totals, results = [], []
    test_model_results, real_results = [], []
    scored_1, conceded_1 = [], []
    scored_2, conceded_2 = [], []

    btts = []

    def get_test_teams_by_scoring(self, stats_data):
        # TODO: pass attack, defend stats via func params
        scoring_table = get_season_table(stats_data, metric='scored')
        cons_table = get_season_table(stats_data, metric='conceded')

        # teams1
        scoring_teams_1 = filter(
            lambda t: scoring_table[t]/get_team_games(stats_data, t) < 1.5,
            scoring_table.keys())

        defending_teams_1 = filter(
            lambda t: cons_table[t]/get_team_games(stats_data, t) < 1.5,
            cons_table.keys())

        # teams2
        scoring_teams_2 = filter(
            lambda t: scoring_table[t]/get_team_games(stats_data, t) < 1.5,
            scoring_table.keys())

        defending_teams_2 = filter(
            lambda t: cons_table[t]/get_team_games(stats_data, t) < 1.5,
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

        scoring_table = get_season_table(stats_dataset, metric='scored')
        cons_table = get_season_table(stats_dataset, metric='conceded')

        #teams_1, teams_2 = self.get_test_teams_by_scoring(stats_dataset)
        teams_1, teams_2 = self.get_test_teams_by_points(stats_dataset, 0, 24, 0, 24)

        for t in teams_1:
            # save team1 stats
            self.scored_1.append(scoring_table[t] / get_team_games(stats_dataset, t))
            self.conceded_1.append(cons_table[t] / get_team_games(stats_dataset, t))

        for t in teams_2:
            # save team2 stats
            self.scored_2.append(scoring_table[t] / get_team_games(stats_dataset, t))
            self.conceded_2.append(cons_table[t] / get_team_games(stats_dataset, t))

        skip_games = len(test_dataset) * 0.0
        sorted_games = sorted(test_dataset, key=lambda g: datetime.strptime(g['Date'], '%d/%m/%Y'))
        process_games = sorted_games[36:]

        games = list(filter(lambda g:
            (g['HomeTeam'] in teams_2 and g['AwayTeam'] in teams_1) or
            (g['HomeTeam'] in teams_1 and g['AwayTeam'] in teams_2),  process_games))

        self.test_model_results.extend(
            test_fox_cub(games, stats_dataset, self.tournament, True))

        for g in games:
            self.totals.append(is_total_under(g, total=2.5))
            self.results.append(float(g['FTHG']) - float(g['FTAG']))
            self.btts.append(float(g['FTHG']) > 0 and float(g['FTAG']) > 0)
            self.real_results.append(g)


    def test(self, test_dataset, stats_dataset, tournament, group_by=Group.Disable):
        """ Make API calls to Fox.Cub statistical model
        and compare model results with real results.
        Using to test Fox.Cub model

        Args:
            test_dataset: games to test with Fox.Cub model
            stats_dataset: dataset used to get teams statistics.
                In some cases test_dataset and stats_dataset may be equal
            group_by: define how to group teams inside a season
        """

        # setup current tournament
        self.tournament = tournament

        for season in get_seasons(test_dataset):
            data_season = filter_by_season(test_dataset, str(season))
            stats_data = filter_by_season(stats_dataset, str(season))

            if group_by == Group.Disable:
                self.test_data_batch(data_season, stats_data)

            elif group_by == Group.Group:
                groups = get_groups(test_dataset)

                for group in groups:
                    if group == -1: continue

                    data_group = filter_by_group(data_season, group)
                    stats_group = filter_by_group(stats_data, group)

                    scoring_table = get_season_table(stats_group, metric='scored')
                    cons_table = get_season_table(stats_group, metric='conceded')

                    self.test_data_batch(data_group, stats_group)


    def print_test_results(self):
        print("Tested games:", len(self.results))
        print("Scored avg team1:", sum(self.scored_1)/len(self.scored_1))
        print("Conceded avg team1:", sum(self.conceded_1)/len(self.conceded_1))
        print("Scored avg team2:", sum(self.scored_2)/len(self.scored_2))
        print("Conceded avg team2:", sum(self.conceded_2)/len(self.conceded_2))
        print('='*25)
        print("Real results Home Win:", len(list(filter(lambda r: r > 0, self.results)))/len(self.results))
        print("Real results Away Win:", len(list(filter(lambda r: r < 0, self.results)))/len(self.results))
        print("Real results Draw:", self.results.count(0)/len(self.results))
        print("Real results Total Under 2.5:", self.totals.count(True)/len(self.totals))
        print("Real results BTTS:", self.btts.count(True)/len(self.btts))
        print('='*25)
        print("Fox.cub results Home Win:", sum([res['Home Win'] for res in self.test_model_results]) / len(self.test_model_results))
        print("Fox.cub results Away Win:", sum([res['Away Win'] for res in self.test_model_results]) / len(self.test_model_results))
        print("Fox.cub results Draw:", sum([res['Draw'] for res in self.test_model_results]) / len(self.test_model_results))
        print("Fox.cub results Total Under 2.5:", sum([res['under 2.5'] for res in self.test_model_results]) / len(self.test_model_results))
        print("Fox.cub results BTTS:", sum([res['BTTS'] for res in self.test_model_results]) / len(self.test_model_results))
        print('='*25)
        print("Real results Home Win +1.5:", len(list(filter(lambda r: r > 1, self.results)))/len(self.results))
        print("Real results Home Win +2.5:", len(list(filter(lambda r: r > 2, self.results)))/len(self.results))
        print("Real results Away Win +1.5:", len(list(filter(lambda r: r < -1, self.results)))/len(self.results))
        print("Real results Away Win +2.5:", len(list(filter(lambda r: r < -2, self.results)))/len(self.results))

        print("Fox.cub results Home Win +1.5:", sum([res['Home Win +1.5'] for res in self.test_model_results]) / len(self.test_model_results))
        print("Fox.cub results Home Win +2.5:", sum([res['Home Win +2.5'] for res in self.test_model_results]) / len(self.test_model_results))
        print("Fox.cub results Away Win +1.5:", sum([res['Away Win +1.5'] for res in self.test_model_results]) / len(self.test_model_results))
        print("Fox.cub results Away Win +2.5:", sum([res['Away Win +2.5'] for res in self.test_model_results]) / len(self.test_model_results))


    def cleanup_results(self):
        self.totals, self.results = [], []
        self.test_model_results, self.real_results = [], []
        self.scored_1, self.conceded_1 = [], []
        self.scored_2, self.conceded_2 = [], []

        self.btts = []


if __name__ == '__main__':

    if len(sys.argv) == 1:
        raise Exception("Please, put data folder!")

    data_folder = sys.argv[1]

    test_dataset = readfile(join_path(data_folder, "/international/world_cup_u20.json"))
    stats_dataset = readfile(join_path(data_folder, "/international/world_cup_u20.json"))

    model_tester = TestModel()
    model_tester.test(stats_dataset, stats_dataset,
        Tournament.International_Final.value, Group.Disable)
    model_tester.print_test_results()
    model_tester.cleanup_results()
