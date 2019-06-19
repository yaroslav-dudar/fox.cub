"""Provide tools to generating csv dataset for Deeplearning4j."""

import csv
import sys
import traceback
import random

from enum import Enum
from datetime import datetime

from utils import *

class Group(Enum):

    Disable = 0
    Group = 1


def game_scoreline(home_goals, away_goals):
    diff = home_goals - away_goals

    if diff > 2: return 3
    if diff < -2: return 6
    if diff == -1: return 4
    if diff == -2: return 5
    return diff


def game_btts(home_goals, away_goals):
    return 1 if home_goals and away_goals else 0


def game_totals(home_goals, away_goals):
    return home_goals + away_goals


def individual_totals(goals):
    return goals


def filter_by_month(min_month, max_month):
    def func(game):
        game_date = datetime.strptime(game['Date'], '%d/%m/%Y')
        return game_date.month <= max_month and game_date.month >= min_month

    return func


def get_team_stats(stats_data_list, team):
    for idx, stats in enumerate(stats_data_list[:1]):
        try:
            team_scores = get_team_scores(stats, team)
        except Exception as e:
            print(e)
            return None

        if team_scores['scored_xg']:
            try:
                season_totals = get_totals(stats)
            except Exception as e:
                traceback.print_exc()
                raise SystemExit("Something went wrong!")

            return [
                season_totals['avgScoredHome'] + season_totals['avgScoredAway'],
                team_scores['scored_xg'], team_scores['conceded_xg'], idx
            ]

    return None


def reshuffle_teams(game, home_team, away_team):
    """ Alert home team to away and away to home """

    if bool(random.getrandbits(1)):
        home_team, away_team = away_team, home_team
        game['FTHG'], game['FTAG'] = game['FTAG'], game['FTHG']

    return home_team, away_team, game


def dataset_v1(home_team, away_team):
    """
        League avg goals,
        Home team attack,
        Home team defence,
        Away Team attack,
        Away team defence
    """

    return [
        home_team[0],
        sum(home_team[1])/len(home_team[1]),
        sum(home_team[2])/len(home_team[2]),
        sum(away_team[1])/len(away_team[1]),
        sum(away_team[2])/len(away_team[2])
    ]


def dataset_v2(home_team, away_team):
    """
        Home team League avg goals,
        Away team League avg goals,
        Home team division [0 - higher 1 - lower],
        Away team division [0 - higher 1 - lower],
        Home team attack,
        Home team defence,
        Away Team attack,
        Away team defence
    """

    return [
        home_team[0], away_team[0],
        home_team[3], away_team[3],
        sum(home_team[1])/len(home_team[1]),
        sum(home_team[2])/len(home_team[2]),
        sum(away_team[1])/len(away_team[1]),
        sum(away_team[2])/len(away_team[2])
    ]


def prepare_data_group(games, stats, output_method, is_neutral=False):
    data_group = []

    for i, g in enumerate(games):
        home_team = get_team_stats(stats, g['HomeTeam'])
        away_team = get_team_stats(stats, g['AwayTeam'])

        if is_neutral:
            g, home_team, away_team = reshuffle_teams(
                g, home_team, away_team, game)

        if not home_team or not away_team: continue

        data_group.append([
            output_method(int(g['FTHG']), int(g['FTAG']))] +\
            dataset_v1(home_team, away_team)
        )

    return data_group

def prepare_dataset(input_dataset, stats_dataset,
    seasons, group_by):

    """Generate dataset for Fox.Cub statistical model

    Args:
        input_dataset: games to analyse and put in output dataset
        stats_dataset: dataset used to get teams statistics.
            In some cases input_dataset and stats_dataset may be equal
        seasons: list of seasons we need to put to the output dataset
        group_by: define how to group teams inside a season
    """

    dataset = []
    print("Preparing dataset ...")

    for season in seasons:
        scored, conceded = {}, {}

        input_games = filter_by_season(input_dataset, str(season))
        stats_data = [filter_by_season(stats, str(season)) for stats in stats_dataset]

        if not input_games: continue

        games_in_season = len(get_season_teams(input_games))*2 - 2

        sorted_games = sorted(input_games, key=lambda g: datetime.strptime(g['Date'], '%d/%m/%Y'))
        #sorted_games = list(filter(filter_by_month(1, 7) , sorted_games))

        if group_by == Group.Disable:
            dataset.extend(
                prepare_data_group(sorted_games, stats_data, game_scoreline)
            )
        elif group_by == Group.Group:
            groups = get_groups(input_dataset)

            for group in groups:
                if group == -1: continue

                data_group = filter_by_group(input_games, group)
                stats_group = [filter_by_group(s, group) for s in stats_data]

                group_games = sorted(data_group, key=lambda g: datetime.strptime(g['Date'], '%d/%m/%Y'))

                dataset.extend(
                    prepare_data_group(group_games, stats_data, game_scoreline)
                )

    return dataset


epl = [
    'eradivisie.json', 'epl.json', 'laliga.json',
    'segunda.json', 'belgium_div1.json', 'portugal_liga.json',
    'bundesliga.json'
]

efl_score = ['championship.json']

mls_totals = ['bundesliga.json', 'mls.json']

mls_score = [{'input': 'mls.json', 'stats': ['mls.json']}]

mls_btts = [
    {'input': 'mls_regular.json', 'stats': ['mls_regular.json']},
]

mls_totals = [
    {'input': 'mls_regular.json', 'stats': ['mls_regular.json']},
    {'input': 'epl.json', 'stats': ['epl.json']}
]

bundesliga = ['bundesliga.json', 'bundesliga2.json', 'swiss_super_league.json', 'epl.json', 'mls.json']

club_playoffs = [
    {'input': './cups/scotland_fa_cup.json', 'stats': ['scotland_premiership.json']},
    {'input': './cups/fa_cup.json', 'stats': ['epl.json', 'championship.json', 'efl_league1.json']},
    {'input': './cups/league_cup.json', 'stats': ['epl.json', 'championship.json', 'efl_league1.json']},
    {'input': './cups/dfb_pokal.json', 'stats': ['bundesliga.json', 'bundesliga2.json', 'bundesliga3.json']},
    {'input': './cups/coupe_de_france.json', 'stats': ['france_ligue1.json', 'france_ligue2.json']},
    {'input': './cups/copa_de_ligue.json', 'stats': ['france_ligue1.json', 'france_ligue2.json']},
    {'input': './cups/copa_del_rey.json', 'stats': ['laliga.json', 'segunda.json']},
    {'input': './cups/copa_italia.json', 'stats': ['serie_a.json', 'serie_b.json']},
    #{'input': './cups/knvb_baker.json', 'stats': ['eradivisie.json', 'eereste_divicie.json']},
    {'input': './cups/taga_de_portugal.json', 'stats': ['portugal_liga.json']},
    #{'input': './cups/swiss_pokal.json', 'stats': ['swiss_super_league.json', 'swiss_chalange_league.json']},
    #{'input': './cups/austria_cup.json', 'stats': ['austria_bundesliga.json']},
]

international_qualification = [
    {'input': './international/europe_qualific.json', 'stats': ['./international/europe_qualific.json']},
    {'input': './international/africa_qualific.json', 'stats': ['./international/africa_qualific.json']},
    {'input': './international/asia_qualific.json', 'stats': ['./international/asia_qualific.json']},
    {'input': './international/sa_qualific.json', 'stats': ['./international/sa_qualific.json']},
]

international_final_stage = [
    {'input': './international/africa_cup.json', 'stats': ['./international/africa_cup.json']},
    {'input': './international/asia_cup.json', 'stats': ['./international/asia_cup.json']},
    {'input': './international/copa_america.json', 'stats': ['./international/copa_america.json']},
    {'input': './international/eu_championship.json', 'stats': ['./international/eu_championship.json']},
    {'input': './international/world_cup.json', 'stats': ['./international/world_cup.json']},
    {'input': './international/gold_cup.json', 'stats': ['./international/gold_cup.json']},
]

if __name__ == '__main__':
    output_dataset = []

    GROUP_BY = None # None or Group

    if len(sys.argv) == 1:
        raise Exception("Please, put data folder!")

    data_folder = sys.argv[1]

    for d in international_final_stage:
        input_data = readfile(join_path(data_folder, d['input']))
        stats_data = [readfile(join_path(data_folder, s)) for s in d['stats']]
        seasons = [season for season in get_seasons(input_data)]

        output_dataset.extend(prepare_dataset(input_data, stats_data, seasons, Group.Disable))

    output_file = 'output.csv'

    with open(output_file, 'w+') as out:
        wr = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        for row in output_dataset:
            wr.writerow(row)
