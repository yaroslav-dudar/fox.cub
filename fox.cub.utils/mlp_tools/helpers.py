import os
from enum import Enum

from utils import join_path, readfile

DATA_FOLDER = os.environ['DATA_FOLDER']


class ModelType(Enum):

    Btts = "btts"
    Total = "totals"
    Score = "scoreline"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

    def get_output_def(self):
        maps = {
            ModelType.Btts: TrainDataset.btts,
            ModelType.Total: TrainDataset.totals,
            ModelType.Score: TrainDataset.scoreline
        }
        return maps[self]


class TrainDataset:

    def __init__(self, trainDatasetPath,
                 statDatasetPaths: list = None):

        self._statDataset, self._trainDataset = [], None

        self._trainDatasetPath = trainDatasetPath
        if not statDatasetPaths:
            self._statDatasetPaths = [trainDatasetPath]
        else:
            self._statDatasetPaths = statDatasetPaths

    @property
    def trainDataset(self):
        if not self._trainDataset:
            self._trainDataset = readfile(join_path(
                                          DATA_FOLDER,
                                          self._trainDatasetPath))
        return self._trainDataset

    @property
    def statDataset(self):
        if self._statDataset:
            return self._statDataset

        for _path in self._statDatasetPaths:
            data = readfile(join_path(DATA_FOLDER, _path))
            self._statDataset.append(data)

        return self._statDataset

    @staticmethod
    def scoreline(home_goals, away_goals):
        diff = home_goals - away_goals

        if diff > 2: return 3
        if diff < -2: return 6
        if diff == -1: return 4
        if diff == -2: return 5
        return diff

    @staticmethod
    def btts(home_goals, away_goals):
        return 1 if home_goals and away_goals else 0

    @staticmethod
    def totals(home_goals, away_goals):
        return home_goals + away_goals


PLAYOFF = [
    TrainDataset('cups/scotland_fa_cup.json',
                 ['leagues/scotland_premiership.json']),
    TrainDataset('cups/fa_cup.json',
                 ['leagues/epl.json', 'leagues/efl_championship.json']),
    TrainDataset('cups/league_cup.json',
                 ['leagues/epl.json', 'leagues/efl_championship.json']),
    TrainDataset('cups/dfb_pokal.json',
                 ['leagues/bundesliga.json', 'leagues/bundesliga2.json']),
    TrainDataset('cups/coupe_de_france.json',
                 ['leagues/france_ligue1.json', 'leagues/france_ligue2.json']),
    TrainDataset('cups/copa_de_ligue.json',
                 ['leagues/france_ligue1.json', 'leagues/france_ligue2.json']),
    TrainDataset('cups/copa_del_rey.json',
                 ['leagues/laliga.json', 'leagues/segunda.json']),
    TrainDataset('cups/copa_italia.json',
                 ['leagues/serie_a.json', 'leagues/serie_b.json']),
    TrainDataset('cups/taga_de_portugal.json',
                 ['leagues/portugal_liga.json']),
]

INT_FINAL = [
    TrainDataset('international/africa_cup.json'),
    TrainDataset('international/asia_cup.json'),
    TrainDataset('international/copa_america.json'),
    TrainDataset('international/eu_championship.json'),
    TrainDataset('international/world_cup.json'),
    TrainDataset('international/gold_cup.json')
]

INT_QUALIFICATION = [
    TrainDataset('international/europe_qual.json'),
    TrainDataset('international/africa_qual.json'),
    TrainDataset('international/asia_qual.json'),
    TrainDataset('international/southamerica_qualific.json')
]

MLS = [TrainDataset('leagues/mls.json')]
CHAMPIONSHIP = [TrainDataset('leagues/efl_championship.json')]
BUNDESLIGA = [TrainDataset('leagues/bundesliga.json')]

CONFIG = {
    'epl': {
        ModelType.Score: [TrainDataset('leagues/epl.json')],
        ModelType.Total: [
            TrainDataset('eradivisie.json'),
            TrainDataset('epl.json'),
            TrainDataset('laliga.json'),
            TrainDataset('bundesliga.json')
        ],
        ModelType.Btts: [
            TrainDataset('eradivisie.json'),
            TrainDataset('epl.json'),
            TrainDataset('laliga.json'),
            TrainDataset('bundesliga.json')
        ]
    },
    'international_final': {
        ModelType.Score: INT_FINAL,
        ModelType.Total: INT_FINAL,
        ModelType.Btts: INT_FINAL
    },
    "international_qualification": {
        ModelType.Score: INT_QUALIFICATION,
        ModelType.Total: INT_QUALIFICATION,
        ModelType.Btts: INT_QUALIFICATION
    },
    'mls': {
        ModelType.Score: MLS,
        ModelType.Total: MLS,
        ModelType.Btts: MLS
    },
    "playoff": {
        ModelType.Score: PLAYOFF,
        ModelType.Total: PLAYOFF,
        ModelType.Btts: PLAYOFF
    },
    "bundesliga": {
        ModelType.Score: BUNDESLIGA,
        ModelType.Total: BUNDESLIGA,
        ModelType.Btts: BUNDESLIGA
    }
}
