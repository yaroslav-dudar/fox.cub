from datetime import datetime
from collections import OrderedDict, defaultdict
from enum import Enum
from typing import List
from statistics import mean

import os
import time
import uuid
import functools
import logging
import sys

from games import BaseGame
from fox_cub_client import FoxCub
import gevent.pool


class Season:

    def __init__(self, games: List[BaseGame]):
        self.games = games

    def get_teams(self, games: List[BaseGame] = None):
        games = self.games if not games else games
        teams = set()
        for g in games:
            teams.add(g.AwayTeam)
            teams.add(g.HomeTeam)
        return list(teams)

    def is_empty(self):
        return len(self.games) == 0

    @staticmethod
    def get_seasons(games: List[BaseGame], reverse=False):
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

    @functools.lru_cache(maxsize=6)
    def get_table(self, metric='points'):
        table = defaultdict(lambda: 0)
        for g in self.games:
            if metric == 'points':
                table[g.HomeTeam] += g.get_team_points(g.HomeTeam)
                table[g.AwayTeam] += g.get_team_points(g.AwayTeam)
            elif metric == 'scored':
                table[g.HomeTeam] += g.get_team_goals(g.HomeTeam, True)
                table[g.AwayTeam] += g.get_team_goals(g.AwayTeam, True)
            elif metric == 'conceded':
                table[g.HomeTeam] += g.get_team_goals(g.HomeTeam, False)
                table[g.AwayTeam] += g.get_team_goals(g.AwayTeam, False)

        return OrderedDict(sorted(table.items(), key=lambda t: t[1], reverse=True))

    def get_group_tables(self, metric='points'):
        groups = {}
        print(self.get_groups())
        for group in self.get_groups():
            table = {}
            group_games = self.get_group_games(group)
            teams = self.get_teams()

            for t in teams:
                games = filter(lambda g: t in [g.HomeTeam, g.AwayTeam], group_games)
                count = 0
                for g in games:
                    if metric == 'points':
                        count += g.get_team_points(t)
                    elif metric == 'scored':
                        count += g.get_team_goals(t, True)
                    elif metric == 'conceded':
                        count += g.get_team_goals(t, False)

                table[t] = count

            groups[group] = OrderedDict(sorted(table.items(),
                                               key=lambda t: t[1],
                                               reverse=True))

        return groups

    @functools.lru_cache(maxsize=512)
    def get_team_scores(self, team, include_home=True, include_away=True):
        """ Deprecated. Slow and unoptimized method """
        if include_away:
            away_games = list(filter(lambda g: team == g.AwayTeam, self.games))
        else:
            away_games = []

        if include_home:
            home_games = list(filter(lambda g: team == g.HomeTeam, self.games))
        else:
            home_games = []

        scored_h = [g.FTHG for g in home_games]
        scored_a = [g.FTAG for g in away_games]

        conceded_h = [g.FTAG for g in home_games]
        conceded_a = [g.FTHG for g in away_games]

        try:
            mean_gd = mean(scored_h + scored_a) - mean(conceded_h + conceded_a)
            home_gd = mean(scored_h) - mean(conceded_h)
            home_adv = home_gd - mean_gd
        except Exception:
            home_adv = 0

        return {
            "scored_xg": scored_h + scored_a,
            "conceded_xg": conceded_h + conceded_a,
            "home_adv": home_adv,
            "expected_points": self.get_table(metric='points')[team] /
                               len(home_games + away_games)
        }

    def get_list_team_scores(self):
        """ Calculate team stats for each team in a season """
        scores = defaultdict(lambda: {
            "scored_xg": [],
            "conceded_xg": [],
            "home_adv": 0,
            "expected_points": 0
        })

        for g in self.games:
            scores[g.HomeTeam]["scored_xg"].append(g.FTHG)
            scores[g.HomeTeam]["conceded_xg"].append(g.FTAG)
            scores[g.AwayTeam]["scored_xg"].append(g.FTAG)
            scores[g.AwayTeam]["conceded_xg"].append(g.FTHG)

        for team in scores.keys():
            scores[team]["expected_points"] = (self.get_table(metric='points')[team] /
                                               len(scores[team]["scored_xg"]))

        return scores


    def get_team_results(self, team):
        games = self.get_team_scores(team)
        return list(map(float.__sub__,
                        games['scored_xg'],
                        games['conceded_xg']))

    @staticmethod
    def get(games: List[BaseGame], season: str = None):
        """ Get Season entity. """
        if season:
            season_games = filter(lambda g: g.Season == season, games)
        else:
            season_games = games

        return Season(list(season_games))

    @functools.lru_cache(maxsize=64)
    def get_group_games(self, group):
        return list(filter(lambda g: g.Group == group, self.games))

    @classmethod
    def filter_games(cls, games: List[BaseGame], before):
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
    def collect_stats(games: List[BaseGame], date_min = None, date_max = None):
        """ Collecting general statistics for batch of games """
        if not games: games = self.games

        under2_5 = len(list(filter(lambda g: g.is_total_under(), games)))
        under3_5 = len(list(filter(lambda g: g.is_total_under(3.5), games)))
        under1_5 = len(list(filter(lambda g: g.is_total_under(1.5), games)))

        home_score = sum([g.FTHG for g in games])
        away_score = sum([g.FTAG for g in games])

        home_wins = sum(1 for _ in filter(lambda g: g.is_home_win(), games))
        away_wins = sum(1 for _ in filter(lambda g: g.is_away_win(), games))
        draws = sum(1 for _ in filter(lambda g: g.is_draw(), games))

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
    Series = "Series"


class SharedDataObj:

    def __init__(self, odds, fixtures, games):
        self.odds = odds
        self.fixtures = fixtures
        self.games = games


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


def singledispatchmethod(func):
    """ singledispatchmethod for python 3.7.
    Use only with staticmethod or classmethod """
    dispatcher = functools.singledispatch(func)
    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[0].__class__).__func__(*args, **kw)
    wrapper.register = dispatcher.register
    functools.update_wrapper(wrapper, func)
    return wrapper


def str2datetime(value):
    if isinstance(value, datetime):
        return value

    try:
        value = datetime.strptime(value, str2datetime.TIME_FORMAT)
    except (ValueError, TypeError) as e:
        raise argparse.ArgumentTypeError(
            "Date should be in %s format" % str2datetime.TIME_FORMAT)

    return value

str2datetime.TIME_FORMAT = BaseGame.date_format


class LoggerWriter:
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def init_logger():
    logger_dir = os.path.dirname(os.path.realpath(__file__))
    logger = logging.getLogger('fox_cub')
    logger.setLevel(logging.INFO)
    # disable redirect logging to stdout stream
    logger.propagate = False
    fh = logging.FileHandler(os.path.join(logger_dir, 'fox_cub.log'))

    formatter = logging.Formatter('%(asctime)s - %(pathname)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)

    # redirecting stderr to logger
    err_fp = LoggerWriter(logger, logging.ERROR)
    sys.stderr = err_fp

    return logger
