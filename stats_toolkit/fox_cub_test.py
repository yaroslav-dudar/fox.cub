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

    totals_2_5, totals_3_5 = [], []
    actual_results_team1, actual_results_team2 = [], []
    model_results = []
    scored_1, conceded_1 = [], []
    scored_2, conceded_2 = [], []

    btts = []

    def get_test_teams_by_scoring(self, stats_data):
        # TODO: pass attack, defend stats via func params
        scoring_table = get_season_table(stats_data, metric='scored')
        cons_table = get_season_table(stats_data, metric='conceded')

        # teams1
        scoring_teams_1 = filter(
            lambda t: 1.1 < scoring_table[t]/get_team_games(stats_data, t) < 2.0,
            scoring_table.keys())

        defending_teams_1 = filter(
            lambda t: 0.5 < cons_table[t]/get_team_games(stats_data, t) < 1.6,
            cons_table.keys())

        # teams2
        scoring_teams_2 = filter(
            lambda t: 0.0 < scoring_table[t]/get_team_games(stats_data, t) < 1.2,
            scoring_table.keys())

        defending_teams_2 = filter(
            lambda t: 1.2 < cons_table[t]/get_team_games(stats_data, t) < 3.3,
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

        teams_1, teams_2 = self.get_test_teams_by_scoring(stats_dataset)
        #teams_1, teams_2 = self.get_test_teams_by_points(stats_dataset, 0, 24, 0, 24)

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
        process_games = sorted_games[:]

        games = list(filter(lambda g:
            (g['HomeTeam'] in teams_2 and g['AwayTeam'] in teams_1) or
            (g['HomeTeam'] in teams_1 and g['AwayTeam'] in teams_2),  process_games))

        test_fox_cub(games, stats_dataset, self.fox_cub_client, True)

        for i, g in enumerate(games):
            self.totals_2_5.append(is_total_under(g, total=2.5))
            self.totals_3_5.append(is_total_under(g, total=3.5))
            self.btts.append(float(g['FTHG']) > 0 and float(g['FTAG']) > 0)

            self.process_results(g, self.fox_cub_client.results[i], teams_1)
            self.model_results.append(self.fox_cub_client.results[i])

        self.fox_cub_client.clear_results()


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
        self.fox_cub_client = FoxCub(tournament)

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
        print("Tested games:", len(self.actual_results_team1))
        print("Scored avg team1:", sum(self.scored_1)/len(self.scored_1))
        print("Conceded avg team1:", sum(self.conceded_1)/len(self.conceded_1))
        print("Scored avg team2:", sum(self.scored_2)/len(self.scored_2))
        print("Conceded avg team2:", sum(self.conceded_2)/len(self.conceded_2))
        print('='*25)
        print("Real results Team1 Win:", self.get_actual_results(self.actual_results_team1, 0))
        print("Real results Team2 Win:", self.get_actual_results(self.actual_results_team2, 0))
        print("Real results Draw:", self.actual_results_team2.count(0)/len(self.actual_results_team2))
        print("Real results Total Under 2.5:", self.totals_2_5.count(True)/len(self.totals_2_5))
        print("Real results Total Under 3.5:", self.totals_3_5.count(True)/len(self.totals_3_5))
        print("Real results BTTS:", self.btts.count(True)/len(self.btts))
        print('='*25)
        print("Fox.cub results Team1 Win:", self.get_fox_cub_scoreline('Win', 'Team1'))
        print("Fox.cub results Team2 Win:", self.get_fox_cub_scoreline('Win', 'Team2'))
        print("Fox.cub results Draw:", self.get_fox_cub_results('Draw'))
        print("Fox.cub results Total Under 2.5:", self.get_fox_cub_results('under 2.5'))
        print("Fox.cub results Total Under 3.5:", self.get_fox_cub_results('under 3.5'))
        print("Fox.cub results BTTS:", self.get_fox_cub_results('BTTS'))
        print('='*25)
        print("Real results Team1 Win +1.5:", self.get_actual_results(self.actual_results_team1, 1))
        print("Real results Team1 Win +2.5:", self.get_actual_results(self.actual_results_team1, 2))
        print("Real results Team2 Win +1.5:", self.get_actual_results(self.actual_results_team2, 1))
        print("Real results Team2 Win +2.5:", self.get_actual_results(self.actual_results_team2, 2))

        print("Fox.cub results Team1 Win +1.5:", self.get_fox_cub_scoreline('Win +1.5', 'Team1'))
        print("Fox.cub results Team1 Win +2.5:", self.get_fox_cub_scoreline('Win +2.5', 'Team1'))
        print("Fox.cub results Team2 Win +1.5:", self.get_fox_cub_scoreline('Win +1.5', 'Team2'))
        print("Fox.cub results Team2 Win +2.5:", self.get_fox_cub_scoreline('Win +2.5', 'Team2'))


    def cleanup_results(self):
        self.totals_2_5, self.totals_3_5 = [], []
        self.actual_results_team1, self.actual_results_team2 = [], []
        self.model_results = []
        self.scored_1, self.conceded_1 = [], []
        self.scored_2, self.conceded_2 = [], []
        self.btts = []


    def get_fox_cub_results(self, attr):
        """ Get total score of a given attribute """
        return sum([res[attr] for res in self.model_results]) / len(self.model_results)


    def get_fox_cub_scoreline(self, score_type, team):
        """ Get total score to win with a given handicap """
        def get_attr(result):
            return result[result[team] + " " + score_type]

        score = sum([get_attr(res) for res in self.model_results])
        return score / len(self.model_results)


    def get_actual_results(self, actual_results, handicap):
        """ Get win percentage with a given handicap """
        return len(list(filter(lambda r: r > handicap, actual_results))) / len(actual_results)


    def process_results(self, game, fox_cub_res, teams_1):
        """ Determine Team1 and Team2 """
        if game['HomeTeam'] in teams_1:
            self.actual_results_team1.append(float(game['FTHG']) - float(game['FTAG']))
            self.actual_results_team2.append(float(game['FTAG']) - float(game['FTHG']))

            fox_cub_res['Team1'] = "Home"
            fox_cub_res['Team2'] = "Away"
        else:
            self.actual_results_team2.append(float(game['FTHG']) - float(game['FTAG']))
            self.actual_results_team1.append(float(game['FTAG']) - float(game['FTHG']))

            fox_cub_res['Team1'] = "Away"
            fox_cub_res['Team2'] = "Home"


if __name__ == '__main__':

    if len(sys.argv) == 1:
        raise Exception("Please, put data folder!")

    data_folder = sys.argv[1]

    test_dataset = readfile(join_path(data_folder, "/international/world_cup.json"))
    stats_dataset = readfile(join_path(data_folder, "/international/world_cup.json"))

    model_tester = TestModel()
    model_tester.test(stats_dataset, stats_dataset,
        Tournament.International_Final.value, Group.Disable)
    model_tester.print_test_results()
    model_tester.cleanup_results()
