"""Provide tools to generating csv dataset for Deeplearning4j."""

import csv
import sys
import traceback
import random
import argparse
from enum import Enum
from datetime import datetime

from utils import *
from mlp_tools.helpers import CONFIG, TrainDataset, ModelType

class Group(Enum):

    Disable = 'Off'
    Group = 'Group'


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

def prepare_dataset(dataset: TrainDataset,
                    seasons: list,
                    group_by: Group,
                    model_type: ModelType):

    """Generate dataset for Fox.Cub statistical model

    Args:
        dataset: contain training and stat data
        seasons: list of seasons we need to put to the output dataset
        group_by: define how to group teams inside a season
    """

    output_def = model.get_output_def()
    output_dataset = []
    print("Preparing dataset ...")

    for season in seasons:
        scored, conceded = {}, {}

        input_games = filter_by_season(dataset.trainDataset, str(season))
        stats_data = [filter_by_season(stats, str(season)) for stats in dataset.statDataset]

        if not input_games: continue

        games_in_season = len(get_season_teams(input_games))*2 - 2

        sorted_games = sorted(input_games,
                              key=lambda g: datetime.strptime(g['Date'],
                              '%d/%m/%Y'))
        #sorted_games = list(filter(filter_by_month(1, 7) , sorted_games))

        if group_by == Group.Disable:
            output_dataset.extend(
                prepare_data_group(sorted_games,
                                   stats_data,
                                   output_def)
            )
        elif group_by == Group.Group:
            groups = get_groups(dataset.trainDataset)

            for group in groups:
                if group == -1: continue

                data_group = filter_by_group(input_games, group)
                stats_group = [filter_by_group(s, group) for s in stats_data]

                group_games = sorted(data_group,
                                     key=lambda g: datetime.strptime(g['Date'],
                                     '%d/%m/%Y'))

                output_dataset.extend(prepare_data_group(group_games,
                                                  stats_data,
                                                  output_def))

    return output_dataset


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-datasetName', required=True, type=str,
                        help='Dataset name from config.')
    parser.add_argument('-groupBy', required=True, type=str,
                        help='Grouping pattern.')
    parser.add_argument('-datasetType', required=True, type=str,
                        help='Type of generated dataset')
    return parser.parse_args()


if __name__ == '__main__':
    result_dataset = []
    args = parse_args()
    dataset = CONFIG[args.datasetName]
    model = ModelType(args.datasetType)

    for d in dataset[model]:
        seasons = [season for season in get_seasons(d.trainDataset)]
        result_dataset.extend(prepare_dataset(d,
                                             seasons[-10:],
                                             Group(args.groupBy),
                                             model))

    output_file = 'output.csv'

    with open(output_file, 'w+') as out:
        wr = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        for row in result_dataset:
            wr.writerow(row)
