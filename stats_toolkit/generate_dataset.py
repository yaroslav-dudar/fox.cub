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

def filter_by_date(max_day, max_month):
    def func(game):
        game_date = datetime.strptime(game['Date'], '%d/%m/%Y')
        return game_date.month <= max_month and game_date.day <= max_day

    return func

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
        stats_data = filter_by_season(stats_dataset, str(season))

        if not input_games: continue

        try:
            season_totals = get_totals(stats_data)
        except Exception as e:
            print(e)
            continue

        avg_goals_per_game = season_totals['avgScoredHome'] +\
            season_totals['avgScoredAway']

        games_in_season = len(get_season_teams(input_games))*2 - 2

        sorted_games = sorted(input_games, key=lambda g: datetime.strptime(g['Date'], '%d/%m/%Y'))

        for i, g in enumerate(sorted_games):

            home_team = get_team_scores(stats_data, g['HomeTeam'])
            away_team = get_team_scores(stats_data, g['AwayTeam'])

            if not home_team['conceded_xg'] or not away_team['scored_xg']: continue

            dataset.append([
                game_scoreline(int(g['FTHG']), int(g['FTAG']))] +\
                [
                    avg_goals_per_game,
                    sum(home_team['scored_xg'])/len(home_team['scored_xg']),
                    sum(home_team['conceded_xg'])/len(home_team['conceded_xg']),
                    sum(away_team['scored_xg'])/len(away_team['scored_xg']),
                    sum(away_team['conceded_xg'])/len(away_team['conceded_xg'])
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
    {'input': '../fa_cup.json', 'stats': 'efl.json'},
    {'input': '../fa_cup.json', 'stats': 'epl.json'},
    {'input': '../dfb_pokal.json', 'stats': 'bundesliga.json'},
    {'input': '../dfb_pokal.json', 'stats': 'bundesliga2.json'},
    {'input': '../copa_del_rey.json', 'stats': 'laliga.json'},
]

if __name__ == '__main__':
    output_dataset = []

    if len(sys.argv) == 1:
        raise Exception("Please, put data folder!")

    data_folder = sys.argv[1]

    for d in club_playoffs:
        input_data = readfile("{0}/{1}".format(data_folder, d['input']))
        stats_data = readfile("{0}/{1}".format(data_folder, d['stats']))

        output_dataset.extend(prepare_dataset(input_data, stats_data, 2000, 2018))

    output_file = 'output.csv'

    with open(output_file, 'w+') as out:
        wr = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        for row in output_dataset:
            wr.writerow(row)
