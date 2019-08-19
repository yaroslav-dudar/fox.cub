# -*- coding: utf-8 -*-

from enum import Enum
import importlib

from utils import *


class VenueFilter(Enum):
    ALL = 'All'
    TEAM1_HOME = 'Team1Home'
    TEAM2_HOME = 'Team2Home'


class ImmutableProperty():
    def __init__(self, value):
        self.value= value

    def __get__(self, instance, owner):
        return self.value


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

    def set_scoring_results(self, season: Season):
        scoring_table = season.get_table(metric='scored')
        cons_table = season.get_table(metric='conceded')

        for t in self.teams_1:
            number_of_games = season.get_team_games(t)
            try:
                self.scored_1.append(scoring_table[t] / number_of_games)
                self.conceded_1.append(cons_table[t] / number_of_games)
            except KeyError:
                pass

        for t in self.teams_2:
            number_of_games = season.get_team_games(t)
            try:
                self.scored_2.append(scoring_table[t] / number_of_games)
                self.conceded_2.append(cons_table[t] / number_of_games)
            except KeyError:
                pass

    def set_actual_results(self, game: Game):
        if game.HomeTeam in self.teams_1:
            self.actual_results_team1.\
                append(game.FTHG - game.FTAG)
            self.actual_results_team2.\
                append(game.FTAG - game.FTHG)
        else:
            self.actual_results_team2.\
                append(game.FTHG - game.FTAG)
            self.actual_results_team1.\
                append(game.FTAG - game.FTHG)

        self.btts.append(game.FTHG > 0 and game.FTAG > 0)

    def set_model_results(self, prediction):
        if prediction['HomeTeam'] in self.teams_1:
            prediction['Team1'] = "Home"
            prediction['Team2'] = "Away"
        else:
            prediction['Team1'] = "Away"
            prediction['Team2'] = "Home"

        self.model_results.append(prediction)


def import_string(class_path: str):
    _package,  _object = class_path.rsplit('.', 1)
    # dynamically load python class
    return getattr(importlib.import_module(_package), _object)
