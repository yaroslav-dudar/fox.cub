from datetime import datetime
from collections import OrderedDict
from enum import Enum

import json
import os
import time
import uuid
import functools

from fox_cub_client import FoxCub
import gevent.pool

def readfile(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def get_seasons(data, reverse=False):
    """ Get list of seasons in asc/desc order"""
    seasons = list(set([game['Season'] for game in data]))
    seasons.sort(reverse=reverse)
    return seasons

def get_groups(data):
    groups = set([game['Group'] for game in data])
    return list(groups)

def get_season_teams(data):
    home_teams = set([game['AwayTeam'] for game in data])
    return list(home_teams)

def get_team_games(data, team):
    games = filter(lambda g: g['AwayTeam'] == team or g['HomeTeam'] == team, data)
    return len(list(games))

def get_season_table(data, metric='points'):
    teams = get_season_teams(data)
    table = {}
    for t in teams:
        games = filter(lambda g: t in [g['HomeTeam'], g['AwayTeam']], data)
        count = 0
        for g in games:
            if metric == 'points':
                count += get_team_points(g, t)
            elif metric == 'scored':
                count += get_team_goals(g, t, True)
            elif metric == 'conceded':
                count += get_team_goals(g, t, False)

        table[t] = count

    return OrderedDict(sorted(table.items(), key=lambda t: t[1], reverse=True))

def get_team_points(game, team):
    if game['FTAG'] == game['FTHG']:
        return 1
    if game['HomeTeam'] == team:
        return 3 if game['FTHG'] > game['FTAG'] else 0
    if game['AwayTeam'] == team:
        return 3 if game['FTAG'] > game['FTHG'] else 0

def get_team_goals(game, team, is_team_score):
    if game['HomeTeam'] == team:
        return int(game['FTHG']) if is_team_score else int(game['FTAG'])
    if game['AwayTeam'] == team:
        return int(game['FTAG']) if is_team_score else int(game['FTHG'])

def collect_stats(data, date_min=None, date_max=None):
    under2_5 = len(list(filter(is_total_under, data)))
    under3_5 = len(list(filter(lambda g: is_total_under(g, 3.5), data)))
    under1_5 = len(list(filter(lambda g: is_total_under(g, 1.5), data)))

    home_score = sum([int(g['FTHG']) for g in data])
    away_score = sum([int(g['FTAG']) for g in data])

    home_wins = sum(1 for _ in filter(lambda g: int(g['FTHG']) > int(g['FTAG']), data))
    away_wins = sum(1 for _ in filter(lambda g: int(g['FTHG']) < int(g['FTAG']), data))
    draws = sum(1 for _ in filter(lambda g: int(g['FTHG']) == int(g['FTAG']), data))

    return {
        'under2.5': float(under2_5) / len(data),
        'under3.5': float(under3_5) / len(data),
        'under1.5': float(under1_5) / len(data),
        'avgScoredHome': float(home_score) / len(data),
        'avgScoredAway': float(away_score) / len(data),
        "home_wins": float(home_wins) / len(data),
        "away_wins": float(away_wins) / len(data),
        "draws": float(draws) / len(data),
    }

def get_teams_from(data, min_place, max_place):
    return list(get_season_table(data).keys())[min_place-1:max_place-1]

def get_games_for(data, teams):
    teams = set(teams)
    games = list(filter(lambda g: teams.intersection(set([g['HomeTeam'], g['AwayTeam']])), data))
    return games

def filter_games(games, before):
    before = datetime.strptime(before, '%d/%m/%Y')
    return tuple(filter(
        lambda g: datetime.strptime(g['Date'], '%d/%m/%Y') < before,
        games
        )
    )

def is_total_under(game, total=2.5):
    return float(game['FTHG']) + float(game['FTAG']) < total

def filter_by_season(data, season):
    """ Get games from a season. Verify that game ended successfully. """
    return list(filter(lambda g: g['Season'] == season, data))

def filter_by_group(data, group):
    return list(filter(lambda g: g['Group'] == group, data))

def filter_by_date(data, date_min, date_max, date_format="%d/%m/%Y"):
    date_min = time.strptime(date_min, "%d/%m/%Y")
    date_max = time.strptime(date_max, "%d/%m/%Y")

    foo = lambda g: date_min < time.strptime(g['Date'], "%d/%m/%Y") < date_max
    return list(filter(foo, data))

def get_mean_line(data):
    return [sum(data[0:i+1])/(i+1) for i in range(len(data))]

def get_team_scores(data, team, include_home=True, include_away=True):
    if include_away:
        away_games = list(filter(lambda g: team == g['AwayTeam'], data))
    else:
        away_games = []

    if include_home:
        home_games = list(filter(lambda g: team == g['HomeTeam'], data))
    else:
        home_games = []

    scored = [float(g["FTAG"]) for g in away_games] + [float(g["FTHG"]) for g in home_games]
    conceded = [float(g["FTHG"]) for g in away_games] + [float(g["FTAG"]) for g in home_games]
    return { "scored_xg": scored, "conceded_xg": conceded }

def test_fox_cub(games_to_test, season_data, client, countAllSeason = False):
    pool = gevent.pool.Pool(1024)
    session_id = str(uuid.uuid4())

    if countAllSeason:
        games_before = tuple(season_data)
        season_avg = collect_stats(games_before)

    for game in games_to_test:
        if not countAllSeason:
            games_before = filter_games(season_data, game['Date'])
            season_avg = collect_stats(games_before)

        home_team = get_team_scores(games_before, game['HomeTeam'])
        away_team = get_team_scores(games_before, game['AwayTeam'])
        pool.spawn(client.get_stats, home_team, away_team, season_avg,
                   game['HomeTeam'], game['AwayTeam'], session_id)

    pool.join()
    return session_id


def get_team_results(team, data):
    games = get_team_scores(data, team)
    return list(map(float.__sub__, games['scored_xg'], games['conceded_xg']))

def join_path(base_path, file_path):
    return os.path.join(base_path, *file_path.split('/'))


class Group(Enum):
    Disable = 'Off'
    Group = 'Group'
