from datetime import datetime
from collections import OrderedDict
from enum import Enum
from typing import List

import json
import os
import time
import uuid
import functools

from collections import namedtuple

from fox_cub_client import FoxCub
import gevent.pool

game_fields = ["FTAG", "FTHG", "HTHG", "HTAG", "Group",
               "HomeGoalsTiming", "AwayGoalsTiming",
               "Season", "Date", "AwayTeam", "HomeTeam"]
_GameTuple = namedtuple('GameTuple', game_fields, defaults=(None,) * len(game_fields))

class Game(_GameTuple):
    FLOAT_FIELDS = game_fields[:5]

    def __new__(cls, *args, **kwargs):
        obj = super(Game, cls)

        new_args = [float(val) if cls.is_float(field, val) else val
            for field, val in zip(obj.__thisclass__._fields, args)]

        new_kwargs = {field: float(val) if cls.is_float(field, val) else val
            for field, val in kwargs.items()}

        return obj.__new__(cls, *new_args, **new_kwargs)

    @classmethod
    def is_float(cls, field, val):
        return field in cls.FLOAT_FIELDS and val is not None

    def is_total_under(self, total=2.5):
        return self.FTHG + self.FTAG < total

    def get_team_points(self, team):
        if self.FTAG == self.FTHG:
            return 1
        if self.HomeTeam == team:
            return 3 if self.FTHG > self.FTAG else 0
        if self.AwayTeam == team:
            return 3 if self.FTAG > self.FTHG else 0

    def get_team_goals(self, team, is_score):
        """ Send batch of games to Fox.Cub

        Args:
            team: team name to seatch
            is_score: if True return team goals for if False goals agains
        """
        if self.HomeTeam == team:
            return self.FTHG if is_score else self.FTAG
        if self.AwayTeam == team:
            return self.FTAG if is_score else self.FTHG

    def date_as_datetime(self):
        return self.to_datetime(self.Date)

    @classmethod
    def from_file(cls, filepath):
        """ Create list of games using input file. """
        games = []
        with open(filepath, 'r') as f:
            for g in json.load(f):
                try:
                    games.append(cls(**g))
                except ValueError:
                    pass

        return games

    @staticmethod
    def to_datetime(str_date, date_format='%d/%m/%Y'):
        return datetime.strptime(str_date, date_format)


class Season:

    def __init__(self, games: List[Game]):
        self.games = games

    def get_teams(self):
        return list(set([g.AwayTeam for g in self.games]))

    def is_empty(self):
        return len(self.games) == 0

    @staticmethod
    def get_seasons(games: List[Game], reverse=False):
        """ Get list of seasons in asc/desc order"""
        seasons = list(set([g.Season for g in games]))
        seasons.sort(reverse=reverse)
        return seasons

    def get_groups(self):
        return list(set([g.Group for g in self.games]))

    def get_team_games(self, team):
        games = filter(lambda g: g.AwayTeam == team or\
                       g.HomeTeam == team, self.games)
        return len(list(games))

    def get_table(self, metric='points'):
        teams = self.get_teams()
        table = {}
        for t in teams:
            games = filter(lambda g: t in [g.HomeTeam, g.AwayTeam], self.games)
            count = 0
            for g in games:
                if metric == 'points':
                    count += g.get_team_points(t)
                elif metric == 'scored':
                    count += g.get_team_goals(t, True)
                elif metric == 'conceded':
                    count += g.get_team_goals(t, False)

            table[t] = count

        return OrderedDict(sorted(table.items(), key=lambda t: t[1], reverse=True))

    @functools.lru_cache(maxsize=32)
    def get_team_scores(self, team, include_home=True, include_away=True):
        if include_away:
            away_games = list(filter(lambda g: team == g.AwayTeam, self.games))
        else:
            away_games = []

        if include_home:
            home_games = list(filter(lambda g: team == g.HomeTeam, self.games))
        else:
            home_games = []

        scored = [g.FTAG for g in away_games] + [g.FTHG for g in home_games]
        conceded = [g.FTHG for g in away_games] + [g.FTAG for g in home_games]
        return { "scored_xg": scored, "conceded_xg": conceded }

    def get_team_results(self, team):
        games = self.get_team_scores(team)
        return list(map(float.__sub__,
                        games['scored_xg'],
                        games['conceded_xg']))

    @staticmethod
    def get(games: List[Game], season: str = None):
        """ Get Season entity. """
        if season:
            season_games = filter(lambda g: g.Season == season, games)
        else:
            season_games = games

        return Season(list(season_games))

    def get_group_games(self, group):
        return list(filter(lambda g: g.Group == group, self.games))

    @classmethod
    def filter_games(cls, games: List[Game], before):
        before = cls.to_datetime(before)
        return tuple(filter(
            lambda g: g.date_as_datetime() < before, games))

    def get_multiteam_games(self, teams):
        teams = set(teams)
        games = list(filter(lambda g: teams.intersection(set([g.HomeTeam,
                                                              g.AwayTeam])),
                                                              self.games))
        return games

    def get_teams_by_table_pos(self, min_place, max_place):
        return list(get_season_table(self.games).keys())[min_place-1:max_place-1]

    @staticmethod
    def collect_stats(games: List[Game], date_min = None, date_max = None):
        """ Collecting general statistics for batch of games """
        if not games: games = self.games

        under2_5 = len(list(filter(lambda g: g.is_total_under(), games)))
        under3_5 = len(list(filter(lambda g: g.is_total_under(3.5), games)))
        under1_5 = len(list(filter(lambda g: g.is_total_under(1.5), games)))

        home_score = sum([g.FTHG for g in games])
        away_score = sum([g.FTAG for g in games])

        home_wins = sum(1 for _ in filter(lambda g: g.FTHG > g.FTAG, games))
        away_wins = sum(1 for _ in filter(lambda g: g.FTHG < g.FTAG, games))
        draws = sum(1 for _ in filter(lambda g: g.FTHG == g.FTAG, games))

        return {
            'under2.5': float(under2_5) / len(games),
            'under3.5': float(under3_5) / len(games),
            'under1.5': float(under1_5) / len(games),
            'avgScoredHome': float(home_score) / len(games),
            'avgScoredAway': float(away_score) / len(games),
            "home_wins": float(home_wins) / len(games),
            "away_wins": float(away_wins) / len(games),
            "draws": float(draws) / len(games),
        }


class Group(Enum):
    Disable = 'Off'
    Group = 'Group'


def get_mean_line(data):
    return [sum(data[0:i+1])/(i+1) for i in range(len(data))]

def test_fox_cub(games_to_test, dataset, client):
    pool = gevent.pool.Pool(1024)
    # unique testing id
    session_id = str(uuid.uuid4())

    for game in games_to_test:
        _, features = dataset.prepare_observation(game)

        home_team_season = dataset.get_team_stats(game.HomeTeam,
                                                  game.Season)['season']
        away_team_season = dataset.get_team_stats(game.AwayTeam,
                                                  game.Season)['season']

        home_team_res = home_team_season.get_team_scores(game.HomeTeam)
        away_team_res = away_team_season.get_team_scores(game.AwayTeam)

        season_avg = {
            "avgScoredHome": features.avg_goals_home_team/2,
            "avgScoredAway": features.avg_goals_away_team/2
        }
        pool.spawn(client.get_stats, home_team_res, away_team_res,
                   season_avg, game.HomeTeam, game.AwayTeam, session_id)

    pool.join()
    return session_id


def join_path(base_path, file_path):
    return os.path.join(base_path, *file_path.split('/'))
