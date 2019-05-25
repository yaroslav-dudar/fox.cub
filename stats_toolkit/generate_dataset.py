import csv
import sys
from datetime import datetime

from utils import *

diff_list = []

def game_scoreline(home_goals, away_goals):
    diff = home_goals - away_goals

    if diff > 2:
        diff_list.append(3)
    elif diff < -2:
        diff_list.append(-3)
    else:
        diff_list.append(diff)

    if diff > 2: return 3
    if diff < -2: return 6
    if diff == -1: return 4
    if diff == -2: return 5
    return diff

def game_btts(home_goals, away_goals):
    return 1 if home_goals and away_goals else 0

def game_totals(home_goals, away_goals):
    return home_goals + away_goals

def individual_totals(goals):
    return goals

def filter_by_month(min_month, max_month):
    def func(game):
        game_date = datetime.strptime(game['Date'], '%d/%m/%Y')
        return game_date.month <= max_month and game_date.month >= min_month

    return func

def get_team_stats(stats_data_list, team):
    for idx, stats in enumerate(stats_data_list[:1]):
        try:
            team_scores = get_team_scores(stats, team)
        except Exception as e:
            print(e)
            return None

        if team_scores['scored_xg']:
            try:
                season_totals = get_totals(stats)
            except Exception as e:
                raise SystemExit(e)

            return [
                season_totals['avgScoredHome'] + season_totals['avgScoredAway'],
                team_scores['scored_xg'], team_scores['conceded_xg'], idx
            ]

    return None

def prepare_dataset(input_dataset, stats_dataset, year_from, year_to):
    """Generate dataset for Fox.Cub statistical model

    Args:
        input_dataset: games to analyse and put in output dataset
        stats_dataset: dataset used to get teams statistics.
            In some cases input_dataset and stats_dataset may be equal
        year_from: input_dataset start date
        year_to: input_dataset finish date
    """

    dataset = []
    print("Preparing dataset ...")

    for season in range(year_from, year_to):
        scored, conceded = {}, {}

        input_games = filter_by_season(input_dataset, str(season))
        stats_data = [filter_by_season(stats, str(season)) for stats in stats_dataset]

        if not input_games: continue

        games_in_season = len(get_season_teams(input_games))*2 - 2

        sorted_games = sorted(input_games, key=lambda g: datetime.strptime(g['Date'], '%d/%m/%Y'))
        #sorted_games = list(filter(filter_by_month(1, 7) , sorted_games))

        for i, g in enumerate(sorted_games):

            home_team = get_team_stats(stats_data, g['HomeTeam'])
            away_team = get_team_stats(stats_data, g['AwayTeam'])

            if not home_team or not away_team: continue

            dataset.append([
                game_totals(int(g['FTHG']), int(g['FTAG']))] +\
                [
                    home_team[0], #away_team[0],
                    #home_team[3], away_team[3],
                    sum(home_team[1])/len(home_team[1]),
                    sum(home_team[2])/len(home_team[2]),
                    sum(away_team[1])/len(away_team[1]),
                    sum(away_team[2])/len(away_team[2])
                ]
            )
    return dataset


epl = [
    'eradivisie.json', 'epl.json', 'laliga.json',
    'segunda.json', 'belgium_div1.json', 'portugal_liga.json',
    'bundesliga.json'
]
efl = [
    'efl.json'
]

mls_totals = ['bundesliga.json', 'mls.json']

mls_score = ['mls.json']

mls_btts = ['mls_regular.json', 'bundesliga.json']

bundesliga = ['bundesliga.json', 'bundesliga2.json', 'swiss.json', 'epl.json', 'mls.json']

club_playoffs = [
    {'input': './nation_cups/scotland_fa_cup.json', 'stats': ['scotland_premiership.json']},
    {'input': './nation_cups/fa_cup.json', 'stats': ['epl.json', 'championship.json', 'efl_league1.json']},
    {'input': './nation_cups/league_cup.json', 'stats': ['epl.json', 'championship.json', 'efl_league1.json']},
    {'input': './nation_cups/dfb_pokal.json', 'stats': ['bundesliga.json', 'bundesliga2.json', 'bundesliga3.json']},
    {'input': './nation_cups/coupe_de_france.json', 'stats': ['france_ligue1.json', 'france_ligue2.json']},
    {'input': './nation_cups/copa_de_ligue.json', 'stats': ['france_ligue1.json', 'france_ligue2.json']},
    {'input': './nation_cups/copa_del_rey.json', 'stats': ['laliga.json', 'segunda.json']},
    {'input': './nation_cups/copa_italia.json', 'stats': ['serie_a.json', 'serie_b.json']},
    #{'input': './nation_cups/knvb_baker.json', 'stats': ['eradivisie.json', 'eereste_divicie.json']},
    {'input': './nation_cups/taga_de_portugal.json', 'stats': ['portugal_liga.json']},
    #{'input': './nation_cups/swiss_pokal.json', 'stats': ['swiss_super_league.json', 'swiss_chalange_league.json']},
    #{'input': './nation_cups/austria_cup.json', 'stats': ['austria_bundesliga.json']},
]

if __name__ == '__main__':
    output_dataset = []

    if len(sys.argv) == 1:
        raise Exception("Please, put data folder!")

    data_folder = sys.argv[1]

    for d in club_playoffs:
        input_data = readfile("{0}/{1}".format(data_folder, d['input']))
        stats_data = [readfile("{0}/{1}".format(data_folder, s)) for s in d['stats']]

        output_dataset.extend(prepare_dataset(input_data, stats_data, 2000, 2019))

    output_file = 'output.csv'

    with open(output_file, 'w+') as out:
        wr = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        for row in output_dataset:
            wr.writerow(row)
