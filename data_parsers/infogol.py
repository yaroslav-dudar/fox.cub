import scrapy
import copy
import json

from config import Config

import pymongo

from datetime import datetime
from datetime import timezone

class InfogolSpider(scrapy.Spider):
    name = 'infogol'
    proxy = "131.108.6.118:50435"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"

    mode = 'create' # update or create

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    HOME_XG = "PostMatchExpectedHomeTeamGoals"
    AWAY_XG = "PostMatchExpectedAwayTeamGoals"

    form_data = {
        "filterJson": ["AND",[
            ["CompID","eq"],
            ["MatchStatus","eq","FullTime"],
            ["OR",[["HomeTeamID","eq"],["AwayTeamID","eq"]]]]
        ],
        "objectName": "vw_MatchList",
        "orderBy[0][propertyName]": "MatchDateTime"
    }

    url = "https://www.infogolapp.com/DataRequest/ExecuteRequest?r=getTeamCompetitionResults&v={team_id}&v={comp_id}"

    def __init__(self, *a, **kw):
        super(InfogolSpider, self).__init__(*a, **kw)

        self.global_conf = Config()
        self.config = self.global_conf['infogol_parser']
        self.db_conf = self.global_conf['database']

        self.client = pymongo.MongoClient(
            self.db_conf['host'],
            self.db_conf['port']
        )
        self.db = self.client[self.db_conf['db_name']]

        self.proxy = "191.252.185.161:8090"

        self.pull_db_data()


    def pull_db_data(self):
        self.tournamemnts = list(self.db[self.db_conf['collections']['tournament']].find())
        self.games = list(self.db[self.db_conf['collections']['game']].find())
        self.teams = list(self.db[self.db_conf['collections']['team']].find())

    def get_form_data(self, team_id, comp_id):
        form = copy.deepcopy(self.form_data)
        form['filterJson'][1][0].append(comp_id)
        form['filterJson'][1][2][1][0].append(team_id)
        form['filterJson'][1][2][1][1].append(team_id)
        form['filterJson'] = str(form['filterJson'])
        return form

    def start_requests(self):
        """ Update xG for existing games """

        callback = self.parse_and_update if self.mode == 'update' else self.parse_and_add
        available_tournaments = filter(
            lambda t: t['name'] in self.config['tournaments_list'].keys(),
            self.tournamemnts)

        for t in available_tournaments:
            comp_id = self.config['tournaments_list'][t['name']]
            # get all teams in a tournament
            teams = list(filter(lambda team: str(t['_id']) in team['tournaments'], self.teams))

            # fetch results for all teams
            for team in teams:
                team_id = int(team[self.config["find_team_by"]])
                team_url = self.url.format(
                    team_id=team_id, comp_id=comp_id)

                yield scrapy.http.FormRequest(
                    url=team_url,
                    callback=callback,
                    headers={'User-Agent': self.user_agent},
                    formdata=self.get_form_data(team_id, comp_id),
                    meta={
                        'proxy': self.proxy,
                        'team_id': team_id,
                        'tournament_id': str(t['_id'])
                    }
                )


    def parse_and_add(self, response):
        """ Find all unsaved games and add then to DB """

        results = json.loads(response.body.decode("utf-8"))
        infogol_team_id = response.request.meta['team_id']
        tournament_id = response.request.meta['tournament_id']

        for res in results:
            venue = 'home' if res['HomeTeamID'] == infogol_team_id else 'away'

            if venue == 'home':
                game = self.get_game_id(res['HomeTeamID'], res['AwayTeamID'], venue)
                team_id = str(self.get_team_by_id(res['HomeTeamID'])['_id'])
                opponent_id = str(self.get_team_by_id(res['AwayTeamID'])['_id'])
                goals_for, goals_against = res['HomeTeamGoals'], res['AwayTeamGoals']
                xg_for, xg_against = res[self.HOME_XG], res[self.AWAY_XG]
            else:
                game = self.get_game_id(res['AwayTeamID'], res['HomeTeamID'], venue)
                team_id = str(self.get_team_by_id(res['AwayTeamID'])['_id'])
                opponent_id = str(self.get_team_by_id(res['HomeTeamID'])['_id'])
                goals_for, goals_against = res['AwayTeamGoals'], res['HomeTeamGoals']
                xg_for, xg_against = res[self.AWAY_XG], res[self.HOME_XG]

            # ignore result if game already exists
            if game:
                continue

            self.db[self.db_conf['collections']['game']].\
                insert_one({
                    "team": team_id,
                    "opponent": opponent_id,
                    "tournament": tournament_id,
                    "date": self.get_time(res['MatchDateTime']),
                    "venue": venue,
                    "goals_for": goals_for,
                    "goals_against": goals_against,
                    "xG_for": xg_for,
                    "xG_against": xg_against
                })


    def parse_and_update(self, response):
        """ Find all games in db and update them """

        results = json.loads(response.body.decode("utf-8"))
        team_id = response.request.meta['team_id']

        for res in results:
            venue = 'home' if res['HomeTeamID'] == team_id else 'away'
            if venue == 'home':
                game = self.get_game_id(res['HomeTeamID'], res['AwayTeamID'], venue)
                upd_with = {
                    'xG_for': res[self.HOME_XG],
                    'xG_against': res[self.AWAY_XG]
                }
            else:
                game = self.get_game_id(res['AwayTeamID'], res['HomeTeamID'], venue)
                upd_with = {
                    'xG_for': res[self.AWAY_XG],
                    'xG_against': res[self.HOME_XG]
                }

            # ignore result if game not found
            if not game:
                continue

            self.db[self.db_conf['collections']['game']].\
                update({ '_id': game }, { '$set': upd_with }, upsert=False)


    def get_team_by_id(self, id):
        return next(filter(lambda t: t.get(self.config["find_team_by"]) == id, self.teams))

    def get_game_id(self, team_infogol_id, opponent_infogol_id, venue):
        team_id = str(self.get_team_by_id(team_infogol_id)['_id'])
        opponent_id = str(self.get_team_by_id(opponent_infogol_id)['_id'])

        game = self.db[self.db_conf['collections']['game']].\
            find_one({
                'team': team_id,
                'opponent': opponent_id,
                'venue': venue
            })

        return game['_id'] if game else None

    def get_time(self, date_str):
        date = datetime.strptime(date_str, self.DATE_FORMAT)
        return int(date.replace(tzinfo=timezone.utc).timestamp())
