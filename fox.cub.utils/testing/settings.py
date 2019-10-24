from dataset import (
    DatasetAggregator,
    ObservationDataset,
    FeatureDataset,
    BaseDataset)

EPL = DatasetAggregator(ObservationDataset('leagues/epl.json'))
MLS = DatasetAggregator(ObservationDataset('leagues/mls.json'))
CHAMPIONSHIP = DatasetAggregator(ObservationDataset('leagues/efl_championship.json'))
LEAGUE_1 = DatasetAggregator(ObservationDataset('leagues/efl_league1.json'))
LEAGUE_2 = DatasetAggregator(ObservationDataset('leagues/efl_league2.json'))
BUNDESLIGA = DatasetAggregator(ObservationDataset('leagues/bundesliga.json'))
BUNDESLIGA2 = DatasetAggregator(ObservationDataset('leagues/bundesliga2.json'))
CHAMPIONS_LEAGUE = DatasetAggregator(ObservationDataset('international/champions_league_group.json'))
EUROPA_LEAGUE = DatasetAggregator(ObservationDataset('international/europa_league_group.json'))
LALIGA = DatasetAggregator(ObservationDataset('leagues/laliga.json'))
SERIE_A = DatasetAggregator(ObservationDataset('leagues/serie_a.json'))

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
    "league2": LEAGUE_2,
    "fa_cup": FA_CUP,
    "league_cup": LEAGUE_CUP,
    'eu_qualific': EU_QUALIFICATION,
    'champions_league': CHAMPIONS_LEAGUE,
    'europa_league': EUROPA_LEAGUE,
    'laliga': LALIGA,
    'serie_a': SERIE_A
}
