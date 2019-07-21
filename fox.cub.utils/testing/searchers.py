# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from collections import defaultdict
import functools

from utils import *
from helpers import ImmutableProperty, VenueFilter

class BasePattern(metaclass=ABCMeta):

    def __init__(self, dataset: list):
        self.dataset = dataset

    str_to_datetime = lambda self, g: datetime.strptime(g['Date'], '%d/%m/%Y')

    venue_filter = VenueFilter.ALL

    def get_venue_def(self, teams_1, teams_2):
        """ Returns venue filter function """
        filters = {
            VenueFilter.ALL.value: lambda g:
                (g['HomeTeam'] in teams_2 and g['AwayTeam'] in teams_1) or
                (g['HomeTeam'] in teams_1 and g['AwayTeam'] in teams_2),
            VenueFilter.TEAM1_HOME.value: lambda g:
                (g['HomeTeam'] in teams_1 and g['AwayTeam'] in teams_2),
            VenueFilter.TEAM2_HOME.value: lambda g:
                (g['HomeTeam'] in teams_2 and g['AwayTeam'] in teams_1)
        }

        return filters[self.venue_filter.value]

    def __init_subclass__(cls):
        required_class_variables = ["team_1", "team_2", "name"]

        for var in required_class_variables:
            if not hasattr(cls, var):
                raise NotImplementedError(
                    f'Class {cls} lacks required `{var}` class attribute'
                )

    def get_games(self, games_to_test: int, dataset: list = None):
        """ Detecting games with team_1 and team_2 only. """
        teams_1, teams_2 = self.get_teams()
        is_reversed = True if games_to_test < 0 else False
        if not dataset: dataset = self.dataset

        sorted_dateset = sorted(dataset, reverse=is_reversed,
                                key=self.str_to_datetime)[:abs(games_to_test)]

        return list(filter(
                    self.get_venue_def(teams_1, teams_2),
                    sorted_dateset))

    @abstractmethod
    def get_teams(self):
        return NotImplemented


class ScoringPattern(BasePattern, metaclass=ABCMeta):

    @abstractmethod
    def team_1(self) -> dict:
        pass

    @abstractmethod
    def team_2(self) -> dict:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    def get_filter(self, filter_by, table):
        return lambda t: filter_by['min'] <= table[t] / \
            get_team_games(self.dataset, t) <= filter_by['max']

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

    name = ImmutableProperty('StrongWithWeak')

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
            'defence': { 'min': 1.4, 'max': 2.7 }
        }


class StrongWithStrongPattern(ScoringPattern):

    name = ImmutableProperty('StrongWithStrong')

    @property
    def team_1(self):
        return {
            'attack': { 'min': 1.4, 'max': 3.45 },
            'defence': { 'min': 0.5, 'max': 1.35 }
        }

    @property
    def team_2(self):
        return {
            'attack': { 'min': 1.4, 'max': 3.45 },
            'defence': { 'min': 0.5, 'max': 1.35 }
        }


class AllPattern(ScoringPattern):

    name  = ImmutableProperty('All')

    @property
    def team_1(self):
        return {
            'attack': { 'min': 0.1, 'max': 5 },
            'defence': { 'min': 0.1, 'max': 5 }
        }

    @property
    def team_2(self):
        return {
            'attack': { 'min': 0.1, 'max': 5 },
            'defence': { 'min': 0.1, 'max': 5 }
        }


class MLSConfPattern(BasePattern, metaclass=ABCMeta):

    @abstractmethod
    def team_1(self) -> dict: pass

    @abstractmethod
    def team_2(self) -> dict: pass

    @abstractmethod
    def name(self) -> str: pass

    @functools.lru_cache(maxsize=None)
    def get_teams(self):
        """ Find teams with the same conference as team_1 """

        games = filter(lambda g: g['AwayTeam'] == self.team_1 or \
            g['HomeTeam'] == self.team_1, self.dataset)
        teams = defaultdict(lambda: 0)

        for g in games:
            opposition = g['HomeTeam'] if g['AwayTeam'] ==\
                self.team_1 else g['AwayTeam']
            teams[opposition] += 1

        # find teams with more then 1 game in a season
        teams_list = [t for t, g in teams.items() if g > 1] + [self.team_1]
        return teams_list, teams_list

    def contains(self, game):
        return self.team_1 in (game['HomeTeam'], game['AwayTeam'])


class StandingsPattern(BasePattern, metaclass=ABCMeta):
    @abstractmethod
    def team_1(self) -> dict: pass

    @abstractmethod
    def team_2(self) -> dict: pass

    @abstractmethod
    def name(self) -> str: pass

    @functools.lru_cache(maxsize=None)
    def get_teams(self):
        points_table = get_season_table(self.dataset, metric='points')
        teams_1 = list(points_table)[
            self.team_1['standings']['min']:
            self.team_1['standings']['max']]
        teams_2 = list(points_table)[
            self.team_2['standings']['min']:
            self.team_2['standings']['max']]

        return teams_1, teams_2


class MLSEastConfPattern(MLSConfPattern):

    name  = ImmutableProperty('MLSEastConf')
    team_1 = property(lambda self: 'DC United')
    team_2 = property(lambda self: self.team_1)


class MLSWestConfPattern(MLSConfPattern):

    name  = ImmutableProperty('MLSWestConf')
    team_1 = property(lambda self: 'LA Lakers')
    team_2 = property(lambda self: self.team_1)


class LeadersVsDogsPattern(StandingsPattern):
    name  = ImmutableProperty('LeadersVsDogs')

    @property
    def team_1(self):
        return { 'standings': { 'min': 0, 'max': 6 } }

    @property
    def team_2(self):
        return { 'standings': { 'min': 15, 'max': 25 } }


class LeadersVsMidtablePattern(StandingsPattern):
    name  = ImmutableProperty('LeadersVsMidtable')

    @property
    def team_1(self):
        return { 'standings': { 'min': 0, 'max': 6 } }

    @property
    def team_2(self):
        return { 'standings': { 'min': 6, 'max': 14 } }


class MidweekGamesPattern(AllPattern):
    name  = ImmutableProperty('MidweekGames')

    def get_games(self, games_to_test: int, dataset: list = None):
        teams_1, teams_2 = self.get_teams()
        if not dataset: dataset = self.dataset

        midweek = filter(lambda g: self.str_to_datetime(g).\
                         weekday() < 5, dataset)
        return super().get_games(games_to_test, midweek)
