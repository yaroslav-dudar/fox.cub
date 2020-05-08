# -*- coding: utf-8 -*-

from enum import Enum
import importlib
from typing import List

from utils import *
from games import BaseGame


class FormatType(Enum):
    Score = "score"
    Points = "points"


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

    LIST_FIELDS = ['totals_2_5', 'totals_3_5', 'actual_results_team1',
                   'actual_results_team2', 'model_results', 'scored_1',
                   'conceded_1', 'scored_2', 'conceded_2', 'test_scored_1',
                   'test_conceded_1', 'test_scored_2', 'test_conceded_2',
                   'points_1', 'points_2', 'test_points_1', 'test_points_2',
                   'home_scored', 'away_scored', 'league_goals_avg', 'btts',
                   'team_1_games', 'team_2_games']

    def __init__(self, teams_1: list = None, teams_2: list = None):
        self.teams_1, self.teams_2 = teams_1, teams_2
        for f in self.LIST_FIELDS:
            setattr(self, f, [])


    def __iadd__(self, other_session):
        for f in self.LIST_FIELDS:
            new_value = getattr(self, f) + getattr(other_session, f)
            setattr(self, f, new_value)

        return self

    def cleanup(self):
        for f in self.LIST_FIELDS:
            setattr(self, f, [])

    def set_scoring_results(self, season: Season):
        scoring_table = season.get_table(metric='scored')
        cons_table = season.get_table(metric='conceded')
        points_table = season.get_table(metric='points')

        for t in self.teams_1:
            try:
                self.scored_1.append(scoring_table[t])
                self.conceded_1.append(cons_table[t])
                self.points_1.append(points_table[t])
                self.team_1_games.append(season.get_team_games(t))
            except KeyError:
                pass

        for t in self.teams_2:
            try:
                self.scored_2.append(scoring_table[t])
                self.conceded_2.append(cons_table[t])
                self.points_2.append(points_table[t])
                self.team_2_games.append(season.get_team_games(t))
            except KeyError:
                pass

    def set_test_scoring_results(self, games: List[BaseGame]):
        for g in games:
            try:
                if g.AwayTeam in self.teams_1 and g.HomeTeam in self.teams_2:
                    self.test_scored_1.append(g.FTAG)
                    self.test_conceded_1.append(g.FTHG)
                    self.test_scored_2.append(g.FTHG)
                    self.test_conceded_2.append(g.FTAG)

                    self.test_points_1.append(g.get_team_points(g.AwayTeam))
                    self.test_points_2.append(g.get_team_points(g.HomeTeam))
                elif g.AwayTeam in self.teams_2 and g.HomeTeam in self.teams_1:
                    self.test_scored_2.append(g.FTAG)
                    self.test_conceded_2.append(g.FTHG)
                    self.test_scored_1.append(g.FTHG)
                    self.test_conceded_1.append(g.FTAG)

                    self.test_points_2.append(g.get_team_points(g.AwayTeam))
                    self.test_points_1.append(g.get_team_points(g.HomeTeam))
            except TypeError:
                pass


    def set_actual_results(self, game: BaseGame):
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
        self.home_scored.append(game.FTHG)
        self.away_scored.append(game.FTAG)

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
