from dataset import (
    DatasetAggregator,
    EObservationDataset,
    ObservationDataset,
    FeatureDataset,
    BaseDataset,
    ModelType)

EPL = [DatasetAggregator(ObservationDataset('leagues/epl.json'))]
MLS = [DatasetAggregator(ObservationDataset('leagues/mls.json'))]
CHAMPIONSHIP = [DatasetAggregator(ObservationDataset('leagues/efl_championship.json'))]
BUNDESLIGA = [DatasetAggregator(ObservationDataset('leagues/bundesliga.json'))]
BUNDESLIGA2 = [DatasetAggregator(ObservationDataset('leagues/bundesliga2.json'))]
LA_LIGA = [DatasetAggregator(ObservationDataset('leagues/laliga.json'))]

INT_FINAL = [
    DatasetAggregator(ObservationDataset('international/africa_cup.json')),
    DatasetAggregator(ObservationDataset('international/asia_cup.json')),
    DatasetAggregator(ObservationDataset('international/copa_america.json')),
    DatasetAggregator(ObservationDataset('international/eu_championship.json')),
    DatasetAggregator(ObservationDataset('international/world_cup.json')),
    DatasetAggregator(ObservationDataset('international/gold_cup.json'))
]

CSGO = [DatasetAggregator(EObservationDataset('esport/csgo_big_events.json'))]

GENERAL = [
    DatasetAggregator(ObservationDataset('leagues/j1_league.json')),
    DatasetAggregator(ObservationDataset('leagues/turkey_1lig.json')),
    DatasetAggregator(ObservationDataset('leagues/laliga.json')),
    DatasetAggregator(ObservationDataset('leagues/allsvenskan.json')),
    DatasetAggregator(ObservationDataset('leagues/bundesliga2.json')),
    DatasetAggregator(ObservationDataset('leagues/epl.json')),
    DatasetAggregator(ObservationDataset('leagues/efl_championship.json')),
    DatasetAggregator(ObservationDataset('leagues/den_1div.json')),
]

INT_QUALIFICATION = [
    DatasetAggregator(ObservationDataset('international/europe_qual.json')),
    DatasetAggregator(ObservationDataset('international/africa_qual.json')),
    DatasetAggregator(ObservationDataset('international/asia_qual.json')),
    DatasetAggregator(ObservationDataset('international/southamerica_qual.json'))
]

PLAYOFF = [
    DatasetAggregator(
        ObservationDataset('cups/scotland_fa_cup.json'),
        FeatureDataset([
            BaseDataset.from_file('leagues/scotland_premiership.json', {'strength': 0})
            ])
    ),
    DatasetAggregator(
        ObservationDataset('cups/fa_cup.json'),
        FeatureDataset([
            BaseDataset.from_file('leagues/epl.json', {'strength': 0}),
            BaseDataset.from_file('leagues/efl_championship.json', {'strength': 1})
            ])
    ),
    DatasetAggregator(
        ObservationDataset('cups/league_cup.json'),
        FeatureDataset([
            BaseDataset.from_file('leagues/epl.json', {'strength': 0}),
            BaseDataset.from_file('leagues/efl_championship.json', {'strength': 1})
            ])
    ),
    DatasetAggregator(
        ObservationDataset('cups/dfb_pokal.json'),
        FeatureDataset([
            BaseDataset.from_file('leagues/bundesliga.json', {'strength': 0}),
            BaseDataset.from_file('leagues/bundesliga2.json', {'strength': 1})
            ])
    ),
    DatasetAggregator(
        ObservationDataset('cups/coupe_de_france.json'),
        FeatureDataset([
            BaseDataset.from_file('leagues/france_ligue1.json', {'strength': 0}),
            BaseDataset.from_file('leagues/france_ligue2.json', {'strength': 1})
            ])
    ),
    DatasetAggregator(
        ObservationDataset('cups/copa_de_ligue.json'),
        FeatureDataset([
            BaseDataset.from_file('leagues/france_ligue1.json', {'strength': 0}),
            BaseDataset.from_file('leagues/france_ligue2.json', {'strength': 1})
            ])
    ),
    DatasetAggregator(
        ObservationDataset('cups/copa_del_rey.json'),
        FeatureDataset([
            BaseDataset.from_file('leagues/laliga.json', {'strength': 0}),
            BaseDataset.from_file('leagues/segunda.json', {'strength': 1})
            ])
    ),
    DatasetAggregator(
        ObservationDataset('cups/copa_italia.json'),
        FeatureDataset([
            BaseDataset.from_file('leagues/serie_a.json', {'strength': 0}),
            BaseDataset.from_file('leagues/serie_b.json', {'strength': 1})
            ])
    ),
    DatasetAggregator(
        ObservationDataset('cups/taga_de_portugal.json'),
        FeatureDataset([
            BaseDataset.from_file('leagues/portugal_liga.json', {'strength': 0})
            ])
    )
]

CONFIG = {
    'epl': {
        ModelType.Score: EPL,
        ModelType.Total: EPL,
        ModelType.Btts: EPL
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
    },
    "championship": {
        ModelType.Score: CHAMPIONSHIP,
        ModelType.Total: CHAMPIONSHIP,
        ModelType.Btts: CHAMPIONSHIP
    },
    "bundesliga2": {
        ModelType.Score: BUNDESLIGA2,
        ModelType.Total: BUNDESLIGA2,
        ModelType.Btts: BUNDESLIGA2
    },
    "laliga": {
        ModelType.Score: LA_LIGA,
        ModelType.Total: LA_LIGA,
        ModelType.Btts: LA_LIGA
    },
    "general": {
        ModelType.Score: GENERAL,
        ModelType.Total: GENERAL,
        ModelType.Btts: GENERAL
    },
    'csgo': {
        ModelType.Score: CSGO,
        ModelType.Total: CSGO,
        ModelType.Btts: CSGO
    }
}
