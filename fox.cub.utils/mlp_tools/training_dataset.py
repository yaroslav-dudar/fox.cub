"""Provide tools to generating csv dataset for Deeplearning4j."""

import csv
import sys
import traceback
import random
import argparse

from utils import *
from games import BaseGame
from dataset import DatasetAggregator, ModelType, FeatureVector
from mlp_tools.settings import CONFIG


class TrainDataset:

    def __init__(self, group_by: str, model_type: ModelType,
                 is_reshuffle: bool, is_live: bool):
        """
        Args:
            group_by: define how to group teams inside a season
            model_type: output model
        """
        self.model_type = model_type
        self.group_by = Group(group_by)
        self.is_reshuffle = is_reshuffle
        self.is_live = is_live


    def filter_by_month(self, min_month, max_month):
        def func(game: BaseGame):
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
            Away team attack,
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

    def dataset_v3(self, feature: FeatureVector,
                   minute: int, htg: int, atg: int):
        """
            League avg goals,
            Home team attack,
            Home team defence,
            Away team attack,
            Away team defence,
            Home team score
            Away team score,
            Minute of play
        """

        return [
            feature.get_avg_goals(),
            feature.attack_strength_home_team,
            feature.defence_strength_home_team,
            feature.attack_strength_away_team,
            feature.defence_strength_away_team,
            htg,
            atg,
            minute
        ]

    def dataset_v4(self, feature: FeatureVector):
        """
            League avg goals,
            Home team attack,
            Home team defence,
            Away team attack,
            Away team defence,
            Home advantage
        """

        return [
            feature.get_avg_goals(),
            feature.attack_strength_home_team,
            feature.defence_strength_home_team,
            feature.attack_strength_away_team,
            feature.defence_strength_away_team,
            feature.home_advantage
        ]

    def dataset_v5(self, feature: FeatureVector):
        """
            Home Expected Points
            Away Expected Points
        """

        return [
            feature.exp_points_home_team,
            feature.exp_points_away_team
        ]


    def prepare_data_group(self, games, dataset):
        if self.is_live:
            return self.prepare_in_paly(games, dataset)
        else:
            return self.prepare_pre_game(games, dataset)


    def prepare_pre_game(self, games, dataset):
        data_group = []
        label_def = self.model_type.get_label_def(dataset.obs_class)
        for game in games:
            if self.is_reshuffle: _, game = game.reshuffle()
            label_class, features = dataset.prepare_observation(game,
                                                                label_def)

            if not features: continue
            data_group.append([label_class] + self.dataset_v5(features))

        return data_group


    def prepare_series(self, games_serie, dataset):
        data_group = []
        label_def = self.model_type.get_label_def(dataset.obs_class)

        if self.is_reshuffle:
            is_changed, game = games_serie[0].reshuffle()
        else:
            is_changed, game = False, games_serie[0]
        _, features = dataset.prepare_observation(game, None)

        label_class = label_def(games_serie, is_changed)
        if not features or label_class < 0 : return data_group

        data_group.append([label_class] + self.dataset_v5(features))
        return data_group


    def prepare_in_paly(self, games, dataset):
        data_group = []
        timestamps = [5*i for i in range(1,20)]
        label_def = self.model_type.get_label_def(dataset.obs_class)

        for game in games:
            if not self.in_play_validate(game): continue

            for minute in timestamps:
                if self.is_reshuffle: _, game = game.reshuffle()
                label_class, features = dataset.prepare_observation(game,
                                                                    label_def)

                if not features: continue

                htg, atg = self.get_in_play_score(game, minute)
                data_group.append([label_class] +\
                                  self.dataset_v3(features, minute, htg, atg))

        return data_group


    def in_play_validate(self, game):
        if game.FTHG != 0 and game.HomeGoalsTiming == '':
            return False

        if game.FTAG != 0 and game.AwayGoalsTiming == '':
            return False

        return True


    def get_in_play_score(self, game: BaseGame, minute: int):
        home = game.HomeGoalsTiming.split(' ')
        away = game.AwayGoalsTiming.split(' ')

        if home[0] != '':
            htg = sum(int(g) <= minute for g in home)
        else:
            htg = 0

        if away[0] != '':
            atg = sum(int(g) <= minute for g in away)
        else:
            atg = 0

        return htg, atg


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
            elif self.group_by == Group.Series:
                groups = season.get_groups()

                for group in groups:
                    group_games = season.get_group_games(group)
                    # ignore series with less than 2 games and more than 3
                    if len(group_games) not in [2,3]: continue
                    output_dataset.extend(self.prepare_series(group_games,
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
    parser.add_argument('-live', default=False, action='store_true',
                        help='Generate dataset for in-play model.')
    parser.add_argument('-out', default="out.csv", type=str,
                        help='Output csv file with training data')
    parser.add_argument('-reshuffle', default=False, action='store_true',
                        help='Reshuffling home and away teams between each other')
    parser.add_argument('-seasons', default=100, type=int,
                        help='Amount of seasons to use to generate training dataset')
    return parser.parse_args()


if __name__ == '__main__':
    result_dataset = []
    args = parse_args()

    dataset = CONFIG[args.datasetName]
    model_type = ModelType(args.datasetType)
    train_dataset = TrainDataset(args.groupBy,
                                 model_type,
                                 args.reshuffle,
                                 args.live)

    reverse = True if args.seasons < 0 else False
    seasons_num = abs(args.seasons)

    for d in dataset[model_type]:
        seasons = Season.get_seasons(d.observations,
                                     reverse=reverse)
        print("Seasons: ", seasons[:seasons_num])
        result_dataset.extend(train_dataset.execute(d, seasons[:seasons_num]))

    train_dataset.to_csv(args.out, result_dataset)
