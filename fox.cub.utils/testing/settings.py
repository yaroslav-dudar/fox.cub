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
SEGUNDA = DatasetAggregator(ObservationDataset('leagues/segunda.json'))
SERIE_A = DatasetAggregator(ObservationDataset('leagues/serie_a.json'))
SERIE_B = DatasetAggregator(ObservationDataset('leagues/serie_b.json'))
LIGUE1 = DatasetAggregator(ObservationDataset('leagues/ligue1.json'))
LIGUE2 = DatasetAggregator(ObservationDataset('leagues/ligue2.json'))
JUPILER_LEAGUE = DatasetAggregator(ObservationDataset('leagues/jupiler.json'))
BELGIUM_B = DatasetAggregator(ObservationDataset('leagues/belgium_b.json'))
J1_LEAGUE = DatasetAggregator(ObservationDataset('leagues/j1_league.json'))
SUPER_LIG = DatasetAggregator(ObservationDataset('leagues/super_lig.json'))
TURKEY_1LEAGUE = DatasetAggregator(ObservationDataset('leagues/turkey_1lig.json'))
EREDIVISIE = DatasetAggregator(ObservationDataset('leagues/eredivisie.json'))
DEN_SUPERLIG = DatasetAggregator(ObservationDataset('leagues/denmark_superlig.json'))
A_LEAGUE = DatasetAggregator(ObservationDataset('leagues/a_league.json'))
EKSTRAKLASA = DatasetAggregator(ObservationDataset('leagues/ekstraklasa.json'))
POL_1LIGA = DatasetAggregator(ObservationDataset('leagues/poland_1liga.json'))
UKR_PRM_LEAGUE = DatasetAggregator(ObservationDataset('leagues/ukr_prm_league.json'))

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
    'segunda': SEGUNDA,
    'serie_a': SERIE_A,
    'serie_b': SERIE_B,
    'ligue1': LIGUE1,
    'ligue2': LIGUE2,
    'jupiler': JUPILER_LEAGUE,
    'belgium_b': BELGIUM_B,
    'j1_league': J1_LEAGUE,
    'super_lig': SUPER_LIG,
    'turkey_1lig': TURKEY_1LEAGUE,
    'eredivisie': EREDIVISIE,
    'denmark_superlig': DEN_SUPERLIG,
    'a_league': A_LEAGUE,
    'ekstraklasa': EKSTRAKLASA,
    'poland_1liga': POL_1LIGA,
    'ukr_prm_league': UKR_PRM_LEAGUE
}
