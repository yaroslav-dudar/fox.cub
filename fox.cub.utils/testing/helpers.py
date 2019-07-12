# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import functools

from utils import *

class TestSessionResult():

    def __init__(self, teams_1: list = None, teams_2: list = None):
        self.totals_2_5, self.totals_3_5 = [], []
        self.actual_results_team1, self.actual_results_team2 = [], []
        self.model_results = []
        self.scored_1, self.conceded_1 = [], []
        self.scored_2, self.conceded_2 = [], []
        self.btts = []

        self.teams_1, self.teams_2 = teams_1, teams_2

    def __iadd__(self, other_session):
        self.totals_2_5 += other_session.totals_2_5
        self.totals_3_5 += other_session.totals_3_5

        self.actual_results_team1 += other_session.actual_results_team1
        self.actual_results_team2 += other_session.actual_results_team2

        self.scored_1 += other_session.scored_1
        self.conceded_1 += other_session.conceded_1

        self.scored_2 += other_session.scored_2
        self.conceded_2 += other_session.conceded_2
        self.model_results += other_session.model_results
        self.btts += other_session.btts

        return self

    def cleanup(self):
        self.totals_2_5, self.totals_3_5 = [], []
        self.actual_results_team1, self.actual_results_team2 = [], []
        self.model_results = []
        self.scored_1, self.conceded_1 = [], []
        self.scored_2, self.conceded_2 = [], []
        self.btts = []

    def set_scoring_results(self, results):
        scoring_table = get_season_table(results, metric='scored')
        cons_table = get_season_table(results, metric='conceded')

        for t in self.teams_1:
            number_of_games = get_team_games(results, t)
            self.scored_1.append(scoring_table[t] / number_of_games)
            self.conceded_1.append(cons_table[t] / number_of_games)

        for t in self.teams_2:
            number_of_games = get_team_games(results, t)
            self.scored_2.append(scoring_table[t] / number_of_games)
            self.conceded_2.append(cons_table[t] / number_of_games)

    def set_actual_results(self, game):
        if game['HomeTeam'] in self.teams_1:
            self.actual_results_team1.\
                append(float(game['FTHG']) - float(game['FTAG']))
            self.actual_results_team2.\
                append(float(game['FTAG']) - float(game['FTHG']))
        else:
            self.actual_results_team2.\
                append(float(game['FTHG']) - float(game['FTAG']))
            self.actual_results_team1.\
                append(float(game['FTAG']) - float(game['FTHG']))

        self.btts.append(float(game['FTHG']) > 0 and float(game['FTAG']) > 0)

    def set_model_results(self, prediction):
        if prediction['HomeTeam'] in self.teams_1:
            prediction['Team1'] = "Home"
            prediction['Team2'] = "Away"
        else:
            prediction['Team1'] = "Away"
            prediction['Team2'] = "Home"

        self.model_results.append(prediction)


class BasePattern(metaclass=ABCMeta):

    def __init__(self, dataset: list):
        self.dataset = dataset


    def __init_subclass__(cls):
        required_class_variables = ["team_1", "team_2"]

        for var in required_class_variables:
            if not hasattr(cls, var):
                raise NotImplementedError(
                    f'Class {cls} lacks required `{var}` class attribute'
                )

    @abstractmethod
    def get_games(self):
        return NotImplemented


class ScoringPattern(BasePattern, metaclass=ABCMeta):
    str_to_datetime = lambda self, g: datetime.strptime(g['Date'], '%d/%m/%Y')

    @abstractmethod
    def team_1(self) -> dict:
        pass


    @abstractmethod
    def team_2(self) -> dict:
        pass


    def get_filter(self, filter_by, table):
        return lambda t: filter_by['min'] <= table[t] / \
            get_team_games(self.dataset, t) <= filter_by['max']


    def get_games(self, dataset: list = None):
        """ Detecting games with team_1 and team_2 only. """
        teams_1, teams_2 = self.get_teams()

        if not dataset: dataset = self.dataset
        sorted_dateset = sorted(dataset, key=self.str_to_datetime)

        return list(filter(lambda g:
            (g['HomeTeam'] in teams_2 and g['AwayTeam'] in teams_1) or
            (g['HomeTeam'] in teams_1 and g['AwayTeam'] in teams_2),
            sorted_dateset))


    @functools.lru_cache(maxsize=None)
    def get_teams(self):
        scoring_table = get_season_table(self.dataset, metric='scored')
        cons_table = get_season_table(self.dataset, metric='conceded')

        # search teams that match team_1 pattern
        scoring_teams_1 = filter(
            self.get_filter(
                self.team_1['attack'], scoring_table),
            scoring_table.keys())

        defending_teams_1 = filter(
            self.get_filter(
                self.team_1['defence'], cons_table),
            cons_table.keys())

        # search teams that match team_2 pattern
        scoring_teams_2 = filter(
            self.get_filter(
                self.team_2['attack'], scoring_table),
            scoring_table.keys())

        defending_teams_2 = filter(
            self.get_filter(
                self.team_2['defence'], cons_table),
            cons_table.keys())

        teams_1 = set(scoring_teams_1) & set(defending_teams_1)
        teams_2 = set(scoring_teams_2) & set(defending_teams_2)

        return teams_1, teams_2


class StrongWithWeakPattern(ScoringPattern):

    @property
    def team_1(self):
        return {
            'attack': { 'min': 1.3, 'max': 3.5 },
            'defence': { 'min': 0.3, 'max': 1.3 }
        }

    @property
    def team_2(self):
        return {
            'attack': { 'min': 0.5, 'max': 1.3 },
            'defence': { 'min': 1.3, 'max': 2.5 }
        }
