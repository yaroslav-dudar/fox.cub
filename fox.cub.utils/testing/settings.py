from dataset import (
    DatasetAggregator,
    ObservationDataset,
    FeatureDataset,
    BaseDataset)

EPL = DatasetAggregator(ObservationDataset('leagues/epl.json'))
MLS = DatasetAggregator(ObservationDataset('leagues/mls.json'))
CHAMPIONSHIP = DatasetAggregator(ObservationDataset('leagues/efl_championship.json'))
LEAGUE_1 = DatasetAggregator(ObservationDataset('leagues/efl_league1.json'))
BUNDESLIGA = DatasetAggregator(ObservationDataset('leagues/bundesliga.json'))
BUNDESLIGA2 = DatasetAggregator(ObservationDataset('leagues/bundesliga2.json'))

FA_CUP = DatasetAggregator(
    ObservationDataset('cups/fa_cup.json'),
    FeatureDataset([
        BaseDataset.from_file('leagues/epl.json', {'strength': 0}),
        BaseDataset.from_file('leagues/efl_championship.json', {'strength': 1}),
        BaseDataset.from_file('leagues/efl_league1.json', {'strength': 2}),
        BaseDataset.from_file('leagues/efl_league2.json', {'strength': 3})
        ])
)

LEAGUE_CUP = DatasetAggregator(
    ObservationDataset('cups/league_cup.json'),
    FeatureDataset([
        BaseDataset.from_file('leagues/epl.json', {'strength': 0}),
        BaseDataset.from_file('leagues/efl_championship.json', {'strength': 1}),
        BaseDataset.from_file('leagues/efl_league1.json', {'strength': 2}),
        BaseDataset.from_file('leagues/efl_league2.json', {'strength': 3})
        ])
)

EU_QUALIFICATION = DatasetAggregator(ObservationDataset('international/eu_qualification.json'))

CONFIG = {
    'epl': EPL,
    'mls': MLS,
    "bundesliga": BUNDESLIGA,
    'bundesliga2': BUNDESLIGA2,
    "championship": CHAMPIONSHIP,
    "league1": LEAGUE_1,
    "fa_cup": FA_CUP,
    "league_cup": LEAGUE_CUP,
    'eu_qualific': EU_QUALIFICATION
}
