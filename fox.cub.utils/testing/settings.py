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
BUNDESLIGA3 = DatasetAggregator(ObservationDataset('leagues/bundesliga3.json'))
CHAMPIONS_LEAGUE = DatasetAggregator(ObservationDataset('international/champions_league_group.json'))
EUROPA_LEAGUE = DatasetAggregator(ObservationDataset('international/europa_league_group.json'))
COPA_LIBERTADORES = DatasetAggregator(ObservationDataset('international/copa_libertadores.json'))
LALIGA = DatasetAggregator(ObservationDataset('leagues/laliga.json'))
SEGUNDA = DatasetAggregator(ObservationDataset('leagues/segunda.json'))
SERIE_A = DatasetAggregator(ObservationDataset('leagues/serie_a.json'))
SERIE_B = DatasetAggregator(ObservationDataset('leagues/serie_b.json'))
LIGUE1 = DatasetAggregator(ObservationDataset('leagues/ligue1.json'))
LIGUE2 = DatasetAggregator(ObservationDataset('leagues/ligue2.json'))
JUPILER_LEAGUE = DatasetAggregator(ObservationDataset('leagues/jupiler.json'))
BELGIUM_B = DatasetAggregator(ObservationDataset('leagues/belgium_b.json'))
J1_LEAGUE = DatasetAggregator(ObservationDataset('leagues/j1_league.json'))
J2_LEAGUE = DatasetAggregator(ObservationDataset('leagues/j2_league.json'))
SUPER_LIG = DatasetAggregator(ObservationDataset('leagues/super_lig.json'))
TURKEY_1LEAGUE = DatasetAggregator(ObservationDataset('leagues/turkey_1lig.json'))
EREDIVISIE = DatasetAggregator(ObservationDataset('leagues/eredivisie.json'))
EERESTE_DIV = DatasetAggregator(ObservationDataset('leagues/eerste_div.json'))
DEN_SUPERLIG = DatasetAggregator(ObservationDataset('leagues/denmark_superlig.json'))
DEN_1DIV = DatasetAggregator(ObservationDataset('leagues/den_1div.json'))
A_LEAGUE = DatasetAggregator(ObservationDataset('leagues/a_league.json'))
EKSTRAKLASA = DatasetAggregator(ObservationDataset('leagues/ekstraklasa.json'))
POL_1LIGA = DatasetAggregator(ObservationDataset('leagues/poland_1liga.json'))
UKR_PRM_LEAGUE = DatasetAggregator(ObservationDataset('leagues/ukr_prm_league.json'))
A_BUNDESLIGA = DatasetAggregator(ObservationDataset('leagues/a_bundesliga.json'))
LIGANOS = DatasetAggregator(ObservationDataset('leagues/liganos.json'))
AU_1LIGA = DatasetAggregator(ObservationDataset('leagues/au_1liga.json'))
SCOTLAND_CHAMPIONSHIP = DatasetAggregator(ObservationDataset('leagues/sc_championship.json'))
SCOTLAND_PREMIERSHIP = DatasetAggregator(ObservationDataset('leagues/sc_premiership.json'))
HNL = DatasetAggregator(ObservationDataset('leagues/hnl.json'))
RPL = DatasetAggregator(ObservationDataset('leagues/rpl.json'))
FNL = DatasetAggregator(ObservationDataset('leagues/fnl.json'))
CZECH_LIGA = DatasetAggregator(ObservationDataset('leagues/czech_liga.json'))
COLOMBIA_A = DatasetAggregator(ObservationDataset('leagues/colombia_a.json'))
LIGA_MX = DatasetAggregator(ObservationDataset('leagues/liga_mx.json'))
ARG_PRIMERA = DatasetAggregator(ObservationDataset('leagues/arg_primera.json'))
CHILE_PRIMERA = DatasetAggregator(ObservationDataset('leagues/chile_primera.json'))
SERBIA_SUPER_LIGA = DatasetAggregator(ObservationDataset('leagues/serbia_super_liga.json'))
PRIMERA_B_NATIONAL = DatasetAggregator(ObservationDataset('leagues/primera_b_national.json'))
BR_SERIE_B = DatasetAggregator(ObservationDataset('leagues/br_serie_b.json'))
BR_SERIE_A = DatasetAggregator(ObservationDataset('leagues/br_serie_a.json'))
BAHRAIN_PL = DatasetAggregator(ObservationDataset('leagues/bahrain_pl.json'))
BEL_PL = DatasetAggregator(ObservationDataset('leagues/bel_pl.json'))
K_LEAGUE = DatasetAggregator(ObservationDataset('leagues/k_league.json'))
K_LEAGUE2 = DatasetAggregator(ObservationDataset('leagues/k_league2.json'))
COSTA_RICA = DatasetAggregator(ObservationDataset('leagues/costa_rica_primera.json'))
NB_1_LIGA = DatasetAggregator(ObservationDataset('leagues/nb_1_liga.json'))
Eliteserien = DatasetAggregator(ObservationDataset('leagues/eliteserien.json'))
Allsvenskan = DatasetAggregator(ObservationDataset('leagues/allsvenskan.json'))
CHINA_SUPER_LEAGUE = DatasetAggregator(ObservationDataset('leagues/china_super_league.json'))

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

JAPAN_CUP = DatasetAggregator(ObservationDataset('cups/japan_cup.json'))

EU_QUALIFICATION = DatasetAggregator(ObservationDataset('international/eu_qualification.json'))

CSGO = DatasetAggregator(ObservationDataset('esport/csgo.json'))
DOTA2 = DatasetAggregator(ObservationDataset('esport/dota2.json'))

CONFIG = {
    'epl': EPL,
    'mls': MLS,
    "bundesliga": BUNDESLIGA,
    'bundesliga2': BUNDESLIGA2,
    'bundesliga3': BUNDESLIGA3,
    "championship": CHAMPIONSHIP,
    "league1": LEAGUE_1,
    "league2": LEAGUE_2,
    "fa_cup": FA_CUP,
    "league_cup": LEAGUE_CUP,
    'eu_qualific': EU_QUALIFICATION,
    'champions_league': CHAMPIONS_LEAGUE,
    'europa_league': EUROPA_LEAGUE,
    'copa_libertadores': COPA_LIBERTADORES,
    'laliga': LALIGA,
    'segunda': SEGUNDA,
    'serie_a': SERIE_A,
    'serie_b': SERIE_B,
    'ligue1': LIGUE1,
    'ligue2': LIGUE2,
    'jupiler': JUPILER_LEAGUE,
    'belgium_b': BELGIUM_B,
    'j1_league': J1_LEAGUE,
    'j2_league': J2_LEAGUE,
    'super_lig': SUPER_LIG,
    'turkey_1lig': TURKEY_1LEAGUE,
    'eredivisie': EREDIVISIE,
    'eerste_div': EERESTE_DIV,
    'denmark_superlig': DEN_SUPERLIG,
    'den_1div': DEN_1DIV,
    'a_league': A_LEAGUE,
    'ekstraklasa': EKSTRAKLASA,
    'poland_1liga': POL_1LIGA,
    'ukr_prm_league': UKR_PRM_LEAGUE,
    'a_bundesliga': A_BUNDESLIGA,
    'au_1liga': AU_1LIGA,
    'liganos': LIGANOS,
    'sc_premiership': SCOTLAND_PREMIERSHIP,
    'sc_championship': SCOTLAND_CHAMPIONSHIP,
    'hnl': HNL,
    'rpl': RPL,
    'fnl': FNL,
    'czech_liga': CZECH_LIGA,
    'colombia_a': COLOMBIA_A,
    'liga_mx': LIGA_MX,
    'arg_primera': ARG_PRIMERA,
    'primera_b_national': PRIMERA_B_NATIONAL,
    'chile_primera': CHILE_PRIMERA,
    'serbia_super_liga': SERBIA_SUPER_LIGA,
    'br_serie_b': BR_SERIE_B,
    'br_serie_a': BR_SERIE_A,
    'bahrain_pl': BAHRAIN_PL,
    'bel_pl': BEL_PL,
    'k_league': K_LEAGUE,
    'k_league2': K_LEAGUE2,
    'costa_rica': COSTA_RICA,
    'cs_go': CSGO,
    'dota2': DOTA2,
    'nb_1_liga': NB_1_LIGA,
    'eliteserien': Eliteserien,
    "allsvenskan": Allsvenskan,
    "china_super_league": CHINA_SUPER_LEAGUE,
    'japan_cup': JAPAN_CUP
}
