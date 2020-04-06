import os
import random

from enum import Enum
from typing import List
from dataclasses import dataclass
from collections import defaultdict
from statistics import mean

from utils import (join_path,
                   Season)

from games import BaseGame, GameFactory

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
    home_advantage: float

    exp_points_home_team: float
    exp_points_away_team: float

    def get_avg_goals(self):
        return (self.avg_goals_home_team +\
                self.avg_goals_away_team) / 2


class BaseDataset:
    def __init__(self, dataset_path, data = None, meta: dict = None):
        self._dataset_path = dataset_path
        self._data = data
        self.meta = meta if meta else {}

    @classmethod
    def from_list(cls, games: List[BaseGame], meta: dict = None):
        return cls(None, games, meta)

    @classmethod
    def from_file(cls, path: str, meta: dict = None):
        return cls(path, None, meta)

    @property
    def path(self):
        return self._dataset_path

    @property
    def data(self):
        if self._data:
            return self._data

        self._data = BaseGame.from_file(join_path(DATA_FOLDER,
                                        self._dataset_path))
        return self._data


class FeatureDataset:
    """ Collection of datasets responsible for calculating
    feature vector for each game observation """

    def __init__(self, datasets: List[BaseDataset]):
        self._datasets = datasets
        self._stats = defaultdict(dict)
        self._seasons = defaultdict(list)
        self.is_ready = False

    def start(self, clean_after = True):
        """ Collect features for each season/team from input collection """

        for dataset in self._datasets:
            dataset_stats = Season.collect_stats(dataset.data)

            for season in Season.get_seasons(dataset.data):
                self.setup_season(dataset, season)

        if clean_after: self._datasets = None
        self.is_ready = True

    def setup_season(self, dataset, season_name):
        """ Storing team stats and seasons """
        season = Season.get(dataset.data, season_name)
        dataset_stats = Season.collect_stats(season.games)
        season.league_avg = (dataset_stats['avgScoredHome'] +\
                             dataset_stats['avgScoredAway'])
        self._seasons[season_name].append(season)

        for team in season.get_teams():
            self.collect_team_features(team,
                                       dataset_stats,
                                       season_name,
                                       season,
                                       dataset.meta.get('strength', 0))

    def get_feature_vector(self, game: BaseGame):
        """ Return feature vector for an input game.
        Return None if at least one team not exists in dataset"""

        try:
            home = self._stats[game.Season][game.HomeTeam]
            away = self._stats[game.Season][game.AwayTeam]
            home_adv = home['home_adv']/home['league_avg']
        except KeyError:
            return None

        return FeatureVector(
            avg_goals_home_team=home['league_avg'],
            avg_goals_away_team=away['league_avg'],
            home_advantage=home_adv,
            league_strength_home_team=home['league_strength'],
            league_strength_away_team=away['league_strength'],
            attack_strength_home_team=home['attack_strength'],
            attack_strength_away_team=away['attack_strength'],
            defence_strength_home_team=home['defence_strength'],
            defence_strength_away_team=away['defence_strength'],
            exp_points_home_team=home['expected_points'],
            exp_points_away_team=away['expected_points'])

    def collect_team_features(self, team, dataset_stats, season_name,
                              season, league_strength):

        team_scores = season.get_team_scores(team)
        self._stats[season_name][team] = {
            'season': season,
            'attack_strength': mean(team_scores['scored_xg']),
            'defence_strength': mean(team_scores['conceded_xg']),
            'home_adv': team_scores['home_adv'],
            'league_strength': league_strength,
            'league_avg': season.league_avg,
            'expected_points': team_scores['expected_points']
        }


class ObservationDataset(BaseDataset):
    """ Represents football history data.
    Used to generate training datasets """

    @staticmethod
    def scoreline(game):
        diff = game.FTHG - game.FTAG

        if diff > 2: return 3
        if diff < -2: return 6
        if diff == -1: return 4
        if diff == -2: return 5
        return diff

    @staticmethod
    def btts(game):
        return 1 if game.FTHG and game.FTAG else 0

    @staticmethod
    def totals(game):
        return game.FTHG + game.FTAG


class EObservationDataset(BaseDataset):
    """ Represents esport history data.
    Used to generate training datasets """

    @staticmethod
    def scoreline(game: BaseGame, is_changed=False):

        if game.is_home_win(): return 1
        if game.is_away_win(): return 2
        return 0

    @staticmethod
    def btts(game, is_changed=False):
        return 1 if game.FTHG and game.FTAG else 0

    @staticmethod
    def totals(self, games_serie, is_changed=False):
        return 0 if len(games_serie) == 2 else 1

    def __scoreline(games_serie, is_changed=False):
        home, away = 0, 0
        for game in games_serie:
            if game.is_home_win():
                home += 1
            elif game.is_away_win():
                away += 1

        if not is_changed:
            if home - away == 1:
                return 0
            elif home - away == 2:
                return 1
            if home - away == -1:
                return 2
            elif home - away == -2:
                return 3
        else:
            if home - away == 1:
                return 2
            elif home - away == 2:
                return 3
            if home - away == -1:
                return 0
            elif home - away == -2:
                return 1

        return -1


class DatasetAggregator:
    """ Combine football game observation and feature datasets.
    Allow to calculate feature vector and label value
    for each observation
    """

    def __init__(self, obs_dataset: BaseDataset,
                 feat_dataset: FeatureDataset = None):

        self.obs_dataset = obs_dataset
        self.obs_class = obs_dataset.__class__

        if not feat_dataset:
            # use the same dataset for features if not provided
            datasets = [BaseDataset(obs_dataset.path)]
            feat_dataset = FeatureDataset(datasets)

        self.feat_dataset = feat_dataset

    def prepare_observation(self, game, label_class_def = None):
        """ Return label class and feature vector """
        self.check_features()

        label = label_class_def(game) if label_class_def else None
        features = self.feat_dataset.get_feature_vector(game)

        return label, features

    @property
    def observations(self):
        return self.obs_dataset.data

    def split(self, season_name, split_by_group = False):
        """ Generate subdataset(s) for a given season and groups"""
        output_sets = []
        season = Season.get(self.observations, season_name)

        if not split_by_group:
            obs_set = self.obs_class.from_list(season.games,
                                                   self.obs_dataset.meta)
            return [DatasetAggregator(obs_set, self.feat_dataset)]

        for group in season.get_groups():
            if group == -1: continue

            obs_set = self.obs_class.from_list(season.get_group_games(group),
                                                   self.obs_dataset.meta)
            output_sets.append(DatasetAggregator(obs_set, self.feat_dataset))

        return output_sets

    def get_team_stats(self, team, season) -> dict:
        """ Returns team stats in a season. """
        self.check_features()
        return self.feat_dataset._stats[season][team]

    def get_season_stats(self, season) -> dict:
        """ Returns stats for every team in a season. """
        self.check_features()
        return self.feat_dataset._stats[season]

    def get_seasons(self, season) -> Season:
        """ Returns list of seasons with a given name """
        self.check_features()
        return self.feat_dataset._seasons[season]

    def get_season_goals_avg(self, season):
        return mean([s.league_avg for s in self.get_seasons(season)])

    def check_features(self):
        if not self.feat_dataset.is_ready:
            # prepare features dataset on demand
            self.feat_dataset.start()

    def __repr__(self):
        return "DatasetAggregator(observations_path=%s)" % self.obs_dataset.path


class ModelType(Enum):

    Btts = "btts"
    Total = "totals"
    Score = "scoreline"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

    def get_label_def(self, obs_class: BaseDataset):
        labels = {
            ModelType.Btts: obs_class.btts,
            ModelType.Total: obs_class.totals,
            ModelType.Score: obs_class.scoreline
        }
        return labels[self]
