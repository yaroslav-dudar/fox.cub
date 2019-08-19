"""Provide tools to generating csv dataset for Deeplearning4j."""

import csv
import sys
import traceback
import random
import argparse

from utils import *
from dataset import DatasetAggregator, ModelType, FeatureVector
from mlp_tools.settings import CONFIG


class TrainDataset:

    def __init__(self, group_by: str, model_type: ModelType,
                 is_reshuffle: bool):
        """
        Args:
            group_by: define how to group teams inside a season
            model_type: output model
        """
        self.label_def = model_type.get_label_def()
        self.group_by = Group(group_by)
        self.is_reshuffle = is_reshuffle


    def filter_by_month(self, min_month, max_month):
        def func(game: Game):
            game_date = game.date_as_datetime()
            return (game_date.month <= max_month and \
                    game_date.month >= min_month)

        return func


    def dataset_v1(self, feature: FeatureVector):
        """
            League avg goals,
            Home team attack,
            Home team defence,
            Away Team attack,
            Away team defence
        """

        return [
            feature.get_avg_goals(),
            feature.attack_strength_home_team,
            feature.defence_strength_home_team,
            feature.attack_strength_away_team,
            feature.defence_strength_away_team,
        ]


    def dataset_v2(self, feature: FeatureVector):
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
            feature.avg_goals_home_team,
            feature.avg_goals_away_team,
            feature.league_strength_home_team,
            feature.league_strength_away_team,
            feature.attack_strength_home_team,
            feature.defence_strength_home_team,
            feature.attack_strength_away_team,
            feature.defence_strength_away_team
        ]


    def prepare_data_group(self, games, dataset):
        data_group = []

        for game in games:
            label_class, features = dataset.prepare_observation(game,
                                                               self.label_def)

            if not features: continue
            if self.is_reshuffle: features.reshuffle()
            data_group.append([label_class] + self.dataset_v1(features))

        return data_group


    def sort_by_date(self, games):
        return sorted(games,
                      key=lambda g: g.date_as_datetime())


    def execute(self, dataset: DatasetAggregator, seasons: list):
        """Generate dataset for Fox.Cub statistical model

        Args:
            dataset: contain training and stat data
            seasons: list of seasons we need to put to the output dataset
        """
        output_dataset = []
        print("Preparing dataset {%s} ..." % dataset)

        for season_name in seasons:
            season = Season.get(dataset.observations, season_name)
            # ignore current season if no appropriate games
            if season.is_empty(): continue

            if self.group_by == Group.Disable:
                output_dataset.extend(
                    self.prepare_data_group(self.sort_by_date(season.games),
                                            dataset)
                )
            elif self.group_by == Group.Group:
                groups = get_groups(dataset.observations)

                for group in groups:
                    # ignore non group games (e.g playoff games)
                    if group == -1: continue

                    data_group = season.get_group_games(group)
                    group_games = self.sort_by_date(data_group)
                    output_dataset.extend(self.prepare_data_group(group_games,
                                                                  dataset))

        return output_dataset


    def to_csv(self, out_file, data):
        with open(out_file, 'w+') as out:
            wr = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
            for row in data:
                wr.writerow(row)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-datasetName', required=True, type=str,
                        help='Dataset name from config.')
    parser.add_argument('-groupBy', required=True, type=str,
                        help='Grouping pattern.')
    parser.add_argument('-datasetType', required=True, type=str,
                        help='Type of generated dataset')
    parser.add_argument('-out', default="out.csv", type=str,
                        help='Output csv file with training data')
    parser.add_argument('-reshuffle', default=False, type=bool,
                        help='Reshuffling home and away teams between each other')
    parser.add_argument('-seasons', default=100, type=int,
                        help='Amount of seasons to use to generate training dataset')
    return parser.parse_args()


if __name__ == '__main__':
    result_dataset = []
    args = parse_args()

    dataset = CONFIG[args.datasetName]
    model_type = ModelType(args.datasetType)
    train_dataset = TrainDataset(args.groupBy, model_type, args.reshuffle)

    reverse = True if args.seasons < 0 else False
    seasons_num = abs(args.seasons)

    for d in dataset[model_type]:
        seasons = Season.get_seasons(d.observations)
        result_dataset.extend(train_dataset.execute(d, seasons[:seasons_num]))

    train_dataset.to_csv(args.out, result_dataset)
