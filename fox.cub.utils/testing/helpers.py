# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from utils import *

class TestSessionResult():

    def __init__(self):
        self.totals_2_5, self.totals_3_5 = [], []
        self.actual_results_team1, self.actual_results_team2 = [], []
        self.model_results = []
        self.scored_1, self.conceded_1 = [], []
        self.scored_2, self.conceded_2 = [], []
        self.btts = []

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


class BasePattern(metaclass=ABCMeta):

    def __init_subclass__(cls):
        required_class_variables = ["team_1", "team_2"]

        for var in required_class_variables:
            if not hasattr(cls, var):
                raise NotImplementedError(
                    f'Class {cls} lacks required `{var}` class attribute'
                )

    @abstractmethod
    def get_teams(self):
        return NotImplemented


class ScoringPattern(BasePattern, metaclass=ABCMeta):

    team_1 = {}
    team_2 = {}

    def __init__(self, dataset):
        self.dataset = dataset


    def get_filter(self, filter_by, table):
        return lambda t: filter_by['min'] <= table[t] / \
            get_team_games(self.dataset, t) <= filter_by['max']


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


class StrongWithWeekPattern(ScoringPattern):

    team_1 = {
        'attack': { 'min': 1.3, 'max': 3.5 },
        'defence': { 'min': 0.3, 'max': 1.3 }
    }

    team_2 = {
        'attack': { 'min': 0.5, 'max': 1.3 },
        'defence': { 'min': 1.3, 'max': 2.5 }
    }
