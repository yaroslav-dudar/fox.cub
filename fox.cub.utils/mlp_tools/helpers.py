import os
import random

from enum import Enum
from typing import List
from dataclasses import dataclass
from collections import defaultdict
from statistics import mean

from utils import (join_path,
                   readfile,
                   get_season_teams,
                   get_team_scores,
                   get_seasons,
                   filter_by_season,
                   collect_stats)

DATA_FOLDER = os.environ.get('DATA_FOLDER', '')


@dataclass
class FeatureVector:
    """ Store features for particular game """

    avg_goals_home_team: float
    avg_goals_away_team: float

    league_strength_home_team: int
    league_strength_away_team: int
    attack_strength_home_team: float
    attack_strength_away_team: float
    defence_strength_home_team: float
    defence_strength_away_team: float

    def get_avg_goals(self):
        return (self.avg_goals_home_team +\
                self.avg_goals_away_team) / 2

    def reshuffle(self):
        """ Alert home team to away and away to home """

        if bool(random.getrandbits(1)):
            self.avg_goals_home_team, self.avg_goals_away_team =\
                self.avg_goals_away_team, self.avg_goals_home_team

            self.league_strength_home_team, self.league_strength_away_team =\
                self.league_strength_away_team, self.league_strength_home_team

            self.attack_strength_home_team, self.attack_strength_away_team =\
                self.attack_strength_away_team, self.attack_strength_home_team

            self.defence_strength_home_team, self.defence_strength_away_team =\
                self.defence_strength_away_team, self.defence_strength_home_team


class ModelType(Enum):

    Btts = "btts"
    Total = "totals"
    Score = "scoreline"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

    def get_label_def(self):
        labels = {
            ModelType.Btts: ObservationDataset.btts,
            ModelType.Total: ObservationDataset.totals,
            ModelType.Score: ObservationDataset.scoreline
        }
        return labels[self]


class BaseDataset:
    def __init__(self, dataset_path, meta: dict = None):
        self._dataset_path = dataset_path
        self._data = None
        self.meta = meta if meta else {}

    @property
    def path(self):
        return self._dataset_path

    @property
    def data(self):
        if self._data:
            return self._data

        self._data = readfile(join_path(DATA_FOLDER,
                                        self._dataset_path))
        return self._data


class FeatureDataset:
    """ Collection of datasets responsible for calculating
    feature vector for each game observation """

    def __init__(self, datasets: List[BaseDataset]):
        self._datasets = datasets
        self._seasons = defaultdict(dict)
        self.is_ready = False

    def start(self, clean_after = True):
        """ Collect features for each season/team from input collection """

        for dataset in self._datasets:
            dataset_stats = collect_stats(dataset.data)
            dataset_seasons = get_seasons(dataset.data)

            for season in dataset_seasons:
                self.setup_season(dataset, season)

        if clean_after: self._datasets = None
        self.is_ready = True

    def setup_season(self, dataset, season):
        season_data = filter_by_season(dataset.data, season)
        dataset_stats = collect_stats(season_data)

        for team in get_season_teams(season_data):
            team_stats = get_team_scores(season_data, team)
            self.collect_team_features(team,
                                       dataset_stats,
                                       season,
                                       team_stats,
                                       dataset.meta.get('strength', 0))

    def get_feature_vector(self, game):
        """ Return feature vector for an input game.
        Return None if at least one team not exists in dataset"""

        try:
            home = self._seasons[game['Season']][game['HomeTeam']]
            away = self._seasons[game['Season']][game['AwayTeam']]
        except KeyError:
            return None

        return FeatureVector(
            avg_goals_home_team=home['league_avg'],
            avg_goals_away_team=away['league_avg'],
            league_strength_home_team=home['league_strength'],
            league_strength_away_team=away['league_strength'],
            attack_strength_home_team=home['attack_strength'],
            attack_strength_away_team=away['attack_strength'],
            defence_strength_home_team=home['defence_strength'],
            defence_strength_away_team=away['defence_strength'])

    def collect_team_features(self, team, dataset_stats, season,
                              team_stats, league_strength):

        self._seasons[season][team] = {
            'attack_strength': mean(team_stats['scored_xg']),
            'defence_strength': mean(team_stats['conceded_xg']),
            'league_strength': league_strength,
            'league_avg': (dataset_stats['avgScoredHome'] +\
                           dataset_stats['avgScoredAway'])
        }


class ObservationDataset(BaseDataset):
    """ Represents football history data.
    Used to generate training datasets """

    @staticmethod
    def scoreline(home_goals, away_goals):
        diff = int(home_goals) - int(away_goals)

        if diff > 2: return 3
        if diff < -2: return 6
        if diff == -1: return 4
        if diff == -2: return 5
        return diff

    @staticmethod
    def btts(home_goals, away_goals):
        return 1 if int(home_goals) and int(away_goals) else 0

    @staticmethod
    def totals(home_goals, away_goals):
        return int(home_goals) + int(away_goals)


class DatasetAggregator:
    """ Combine football game observation and feature datasets.
    Allow to calculate feture vector and label value
    for each observation
    """

    def __init__(self, obs_dataset: ObservationDataset,
                 feat_dataset: FeatureDataset = None):

        self.obs_dataset = obs_dataset

        if not feat_dataset:
            # use the same dataset for features if not provided
            datasets = [BaseDataset(obs_dataset.path)]
            feat_dataset = FeatureDataset(datasets)

        self.feat_dataset = feat_dataset

    def prepare_observation(self, game, label_class_def):
        """ Return label class and feature vector """

        if not self.feat_dataset.is_ready:
            # prepare features dataset on demand
            self.feat_dataset.start()

        label = label_class_def(game['FTHG'], game['FTAG'])
        features = self.feat_dataset.get_feature_vector(game)

        return label, features

    @property
    def observations(self):
        return self.obs_dataset.data

    def __repr__(self):
        return "DatasetAggregator(observations_path=%s)" % self.obs_dataset.path
