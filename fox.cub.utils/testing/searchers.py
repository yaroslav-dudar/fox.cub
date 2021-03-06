# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Tuple
import functools

from utils import *
from dataset import DatasetAggregator
from helpers import ImmutableProperty, VenueFilter
from testing.ranking import CsGoRank, Dota2Rank

class BasePattern(metaclass=ABCMeta):

    def __init__(self, dataset: DatasetAggregator, season: str):
        self.dataset = dataset
        self.season = season

    str_to_datetime = lambda self, g: g.date_as_datetime()

    venue_filter = VenueFilter.ALL

    def get_venue_def(self, teams_1, teams_2):
        """ Returns venue filter function """
        filters = {
            VenueFilter.ALL.value: lambda g:
                (g.HomeTeam in teams_2 and g.AwayTeam in teams_1) or
                (g.HomeTeam in teams_1 and g.AwayTeam in teams_2),
            VenueFilter.TEAM1_HOME.value: lambda g:
                (g.HomeTeam in teams_1 and g.AwayTeam in teams_2),
            VenueFilter.TEAM2_HOME.value: lambda g:
                (g.HomeTeam in teams_2 and g.AwayTeam in teams_1)
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
        if not dataset: dataset = self.dataset.observations

        sorted_dateset = sorted(dataset, reverse=is_reversed,
                                key=self.str_to_datetime)[:abs(games_to_test)]
        results = list(filter(
                    self.get_venue_def(teams_1, teams_2),
                    sorted_dateset))
        return results

    @abstractmethod
    def get_teams(self) -> Tuple[set, set]:
        """ Return 2 sets of teams. """
        return NotImplemented

    def get_filter(self, filter_by, data, field):
        return lambda t: filter_by['min'] <=  \
            data[t][field] <= filter_by['max']


class ScoringPattern(BasePattern, metaclass=ABCMeta):

    @abstractmethod
    def team_1(self) -> dict: pass

    @abstractmethod
    def team_2(self) -> dict: pass

    @abstractmethod
    def name(self) -> str: pass

    def get_filter(self, filter_by, data, field):
        return lambda t: filter_by['min'] <=  \
            data[t][field] <= filter_by['max']

    @functools.lru_cache(maxsize=None)
    def get_teams(self) -> Tuple[set, set]:
        season_data = self.dataset.get_season_stats(self.season)

        # search teams that match team_1 pattern
        scoring_teams_1 = filter(
            self.get_filter(self.team_1['attack'],
                            season_data,
                            'attack_strength'),
            season_data.keys())

        defending_teams_1 = filter(
            self.get_filter(self.team_1['defence'],
                            season_data,
                            'defence_strength'),
            season_data.keys())

        # search teams that match team_2 pattern
        scoring_teams_2 = filter(
            self.get_filter(self.team_2['attack'],
                            season_data,
                            'attack_strength'),
            season_data.keys())

        defending_teams_2 = filter(
            self.get_filter(self.team_2['defence'],
                            season_data,
                            'defence_strength'),
            season_data.keys())

        teams_1 = set(scoring_teams_1) & set(defending_teams_1)
        teams_2 = set(scoring_teams_2) & set(defending_teams_2)

        return teams_1, teams_2


class LeagueStrengthPattern(BasePattern, metaclass=ABCMeta):

    @abstractmethod
    def team_1(self) -> dict: pass

    @abstractmethod
    def team_2(self) -> dict: pass

    @abstractmethod
    def name(self) -> str: pass

    @functools.lru_cache(maxsize=None)
    def get_teams(self) -> Tuple[set, set]:
        season_data = self.dataset.get_season_stats(self.season)

        teams_1 = filter(
            self.get_filter(self.team_1['strength'],
                            season_data,
                            'league_strength'),
            season_data.keys())

        # search teams that match team_2 pattern
        teams_2 = filter(
            self.get_filter(self.team_2['strength'],
                            season_data,
                            'league_strength'),
            season_data.keys())

        return set(teams_1), set(teams_2)


class MLSConfPattern(BasePattern, metaclass=ABCMeta):

    @abstractmethod
    def team_1(self) -> dict: pass

    @abstractmethod
    def team_2(self) -> dict: pass

    @abstractmethod
    def name(self) -> str: pass

    @functools.lru_cache(maxsize=None)
    def get_teams(self) -> Tuple[set, set]:
        """ Find teams with the same conference as team_1 """

        games = filter(lambda g: g['AwayTeam'] == self.team_1 or \
            g['HomeTeam'] == self.team_1, self.dataset.observations)
        teams = defaultdict(lambda: 0)

        for g in games:
            opposition = g['HomeTeam'] if g['AwayTeam'] ==\
                self.team_1 else g['AwayTeam']
            teams[opposition] += 1

        # find teams with more then 1 game in a season
        teams_list = [t for t, g in teams.items() if g > 1] + [self.team_1]
        return set(teams_list), set(teams_list)

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
    def get_teams(self) -> Tuple[set, set]:
        teams_1, teams_2 = [], []

        for season in self.dataset.get_seasons(self.season):
            points_table = season.get_table(metric='points')
            teams_1.extend(list(points_table)[
                self.team_1['standings']['min']:
                self.team_1['standings']['max']])
            teams_2.extend(list(points_table)[
                self.team_2['standings']['min']:
                self.team_2['standings']['max']])

        return set(teams_1), set(teams_2)


class StrongWithWeakPattern(ScoringPattern):

    name = ImmutableProperty('StrongWithWeak')

    @property
    def team_1(self):
        return {
            'attack': { 'min': 1.4, 'max': 3.1 },
            'defence': { 'min': 0.0, 'max': 0.9 }
        }


    @property
    def team_2(self):
        return {
            'attack': { 'min': 1.1, 'max': 2.0 },
            'defence': { 'min': 1.0, 'max': 1.7 }
        }
        #return {
        #    'attack': { 'min': 1.4 , 'max': 2.2 },
        #    'defence': { 'min': 0.95, 'max': 1.65 }
        #}



class StrongWithStrongPattern(ScoringPattern):

    name = ImmutableProperty('StrongWithStrong')

    @property
    def team_1(self):
        return {
            'attack': { 'min': 0.0, 'max': 1.3 },
            'defence': { 'min': 1.2, 'max': 1.93 }
        }


    @property
    def team_2(self):
        return {
            'attack': { 'min': 1.55, 'max': 2.5 },
            'defence': { 'min': 0.7, 'max': 1.55 }
        }


class StrongAttVsWeakDefPattern(ScoringPattern):

    name = ImmutableProperty('StrongAttVsWeakDef')

    @property
    def team_1(self):
        return {
            'attack': { 'min': 0.8, 'max': 1.5 },
            'defence': { 'min': 0.0, 'max': 1.2 }
        }

    @property
    def team_2(self):
        return {
            'attack': { 'min': 1.0, 'max': 1.6 },
            'defence': { 'min': 0.8, 'max': 1.55 }
        }


class StrongAttVsStrongDefPattern(ScoringPattern):

    name = ImmutableProperty('StrongAttVsWeakDef')

    @property
    def team_1(self):
        return {
            'attack': { 'min': 1.0, 'max': 1.7 },
            'defence': { 'min': 1.1, 'max': 2.0 }
        }

    @property
    def team_2(self):
        return {
            'attack': { 'min': 0.8, 'max': 1.5 },
            'defence': { 'min': 0.8, 'max': 1.5 }
        }


class WeakDefWithWeakDefPattern(ScoringPattern):

    name = ImmutableProperty('WeakDefWithWeakDef')

    @property
    def team_1(self):
        return {
            'attack': { 'min':  0.8, 'max': 1.65 },
            'defence': { 'min': 0.0, 'max': 1.3 }
        }


    @property
    def team_2(self):
        return {
            'attack': { 'min':  0.0, 'max': 1.3 },
            'defence': { 'min': 1.3, 'max': 1.9 }
        }


class StrongVsAveragePattern(ScoringPattern):

    name = ImmutableProperty('StrongVsAverage')

    @property
    def team_1(self):
        return {
            'attack': { 'min':  1.9, 'max': 1.75 },
            'defence': { 'min': 0.9, 'max': 1.75 }
        }


    @property
    def team_2(self):
        return {
            'attack': { 'min':  1.3, 'max': 1.9 },
            'defence': { 'min': 1.0, 'max': 1.6 }
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
        return { 'standings': { 'min': 12, 'max': 17 } }

    @property
    def team_2(self):
        return { 'standings': { 'min': 12, 'max': 16 } }


class LeadersVsMidtablePattern(StandingsPattern):
    name  = ImmutableProperty('LeadersVsMidtable')

    @property
    def team_1(self):
        return { 'standings': { 'min': 5, 'max': 11 } }

    @property
    def team_2(self):
        return { 'standings': { 'min': 2, 'max': 5 } }


class MidtableVsDogsPattern(StandingsPattern):
    name  = ImmutableProperty('MidtableVsDogs')

    @property
    def team_1(self):
        return { 'standings': { 'min': 10, 'max': 20 } }

    @property
    def team_2(self):
        return { 'standings': { 'min': 0, 'max': 100 } }


class MidtableVsMidtablePattern(StandingsPattern):
    name  = ImmutableProperty('MidtableVsMidtable')

    @property
    def team_1(self):
        return { 'standings': { 'min': 0, 'max': 3 } }

    @property
    def team_2(self):
        return { 'standings': { 'min': 3, 'max': 6 } }


class MidweekGamesPattern(AllPattern):
    name  = ImmutableProperty('MidweekGames')

    def get_games(self, games_to_test: int, dataset: list = None):
        teams_1, teams_2 = self.get_teams()
        if not dataset: dataset = self.dataset.observations

        midweek = filter(lambda g: self.str_to_datetime(g).\
                         weekday() < 5, dataset)
        return super().get_games(games_to_test, midweek)


class EventsPattern(AllPattern):
    name  = ImmutableProperty('MidweekGames')

    def is_major_event(self, g):
        return g.Event.startswith(('ESL One', 'StarLadder ImbaTV', 'Dota Summit',
                                   'EPICENTER Major', 'MDL Chengdu Major'))

    def get_games(self, games_to_test: int, dataset: list = None):
        teams_1, teams_2 = self.get_teams()
        if not dataset: dataset = self.dataset.observations

        games = filter(lambda g: self.is_major_event(g), dataset)
        return super().get_games(games_to_test, games)


class SingleTeamPattern(AllPattern):
    name  = ImmutableProperty('SingleTeam')

    selected_team = None

    @property
    def team_1(self):
        if self.selected_team: return [self.selected_team]

        return ["FaZe"]

    @property
    def team_2(self):
        return CsGoRank.cs_mid_tier
        #return ["NiP", "Complexity", "Astralis", "ENCE", "Natus Vincere", "Spirit", "Heretics", "BIG",
        #    "G2", "FaZe", "mousesports", "fnatic", "Vitality", "MAD Lions", "GODSENT", "Dignitas"]
        #return ["OG", "Alliance", "Ninjas in Pyjamas", "Virtus.pro", "HellRaisers", "Nigma",
        #    "Team Liquid", "FlyToMoon", "Natus Vincere", "ViKin.gg", "VP.Prodigy"]
        #return ["PSG.LGD", "Vici Gaming", "INVICTUS GAMING",
        #    "Royal Never Give Up", "Team Aster", "EHOME", "CDEC "]


    @functools.lru_cache(maxsize=None)
    def get_teams(self) -> Tuple[set, set]:
        teams_1, teams_2 = self.team_1, self.team_2

        #for season in self.dataset.get_seasons(self.season):
        #    points_table = season.get_table(metric='points')
        #    #teams_2.extend(list(points_table)[0:30])

        return set(teams_1), set(teams_2)



class TopLeagueVsRestPattern(LeagueStrengthPattern):
    name  = ImmutableProperty('TopLeagueVsRest')

    @property
    def team_1(self):
        return { 'strength': { 'min': 0, 'max': 0 } }

    @property
    def team_2(self):
        return { 'strength': { 'min': 1, 'max': 2 } }
