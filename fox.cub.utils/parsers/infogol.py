import scrapy
import copy
import json

from datetime import datetime, timezone
from collections import namedtuple

from config import Config
from models import Team, Game, Tournament

League = namedtuple("League",
                    ["id", "teams", "games", "external_id"],
                    defaults=(None,) * 4)

class InfogolSpider(scrapy.Spider):
    name = 'infogol'
    user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    )

    mode = 'create' # update or create
    FIND_TOURN_BY = property(lambda self: 'name')
    DATE_FORMAT   = property(lambda self: "%Y-%m-%dT%H:%M:%S")

    HOME_XG = property(lambda self: 'PostMatchExpectedHomeTeamGoals')
    AWAY_XG = property(lambda self: 'PostMatchExpectedAwayTeamGoals')

    FORM_DATA = property(lambda self: {
        "filterJson": ["AND",[
            ["CompID","eq"],
            ["MatchStatus","eq","FullTime"],
            ["OR",[["HomeTeamID","eq"],["AwayTeamID","eq"]]]]
        ],
        "objectName": "vw_MatchList",
        "orderBy[0][propertyName]": "MatchDateTime"
    })

    INFOGOL_URL = property(lambda self: (
        "https://www.infogolapp.com/DataRequest/ExecuteRequest?"
        "r=getTeamResultsInCompetition&v={team_id}&v={comp_id}"
    ))

    def __init__(self, *a, **kw):
        super(InfogolSpider, self).__init__(*a, **kw)

        self.global_conf = Config()
        self.config = self.global_conf['infogol_parser']

        self.proxy = "104.236.248.219:3128"
        self.leagues_list = {}
        self.init_data()


    def init_data(self):
        for t_name in self.config['tournaments_list']:
            tournament = Tournament.get(t_name, self.FIND_TOURN_BY)
            infogol_id = self.config['tournaments_list'][t_name]

            if not tournament:
                self.leagues_list[t_name] = None
            else:
                t_id = str(tournament['_id'])
                self.leagues_list[t_name] = League(t_id,
                                                   Team.find(t_id),
                                                   Game.find_all(t_id),
                                                   infogol_id)


    def get_form_data(self, team_id, comp_id):
        form = copy.deepcopy(self.FORM_DATA)
        form['filterJson'][1][0].append(comp_id)
        form['filterJson'][1][2][1][0].append(team_id)
        form['filterJson'][1][2][1][1].append(team_id)
        form['filterJson'] = str(form['filterJson'])
        return form

    def start_requests(self):
        """ Call API request for each tournament
        and team subscribed to infogol parser
        """

        callback = self.parse_and_update if self.mode == 'update' else self.parse_and_add

        for name, tournament in self.leagues_list.items():
            # fetch results for each team in a tournament
            for team in tournament.teams:
                team_id = int(team[self.config["find_team_by"]])
                team_url = self.INFOGOL_URL.format(
                    team_id=team_id,
                    comp_id=tournament.external_id)

                yield scrapy.http.FormRequest(
                    url=team_url,
                    callback=callback,
                    headers={
                        'User-Agent': self.user_agent,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    formdata=self.get_form_data(team_id, tournament.external_id),
                    meta={
                        'proxy': self.proxy,
                        'team_id': team_id,
                        'tournament': tournament
                    }
                )


    def parse_and_add(self, response):
        """ Find all unsaved games and add then to DB """

        results = json.loads(response.body.decode("utf-8"))
        infogol_team_id = response.request.meta['team_id']
        tournament = response.request.meta['tournament']

        for res in results:
            venue = 'home' if res['HomeTeamID'] == infogol_team_id else 'away'

            if venue == 'home':
                game = self.get_game(res['HomeTeamID'],
                                        res['AwayTeamID'],
                                        venue,
                                        tournament)

                goals_for, goals_against = res['HomeTeamGoals'], res['AwayTeamGoals']
                xg_for, xg_against = res[self.HOME_XG], res[self.AWAY_XG]
            else:
                game = self.get_game(res['AwayTeamID'],
                                     res['HomeTeamID'],
                                     venue,
                                     tournament)

                goals_for, goals_against = res['AwayTeamGoals'], res['HomeTeamGoals']
                xg_for, xg_against = res[self.AWAY_XG], res[self.HOME_XG]

            # ignore result if game already exists
            if game:
                continue

            team_id, opponent_id = game['team'], game['opponent']
            game_data = Game.get_document(team_id, opponent_id,
                                          tournament.id,
                                          self.get_time(res['MatchDateTime']),
                                          venue, goals_for, goals_against,
                                          xg_for, xg_against)
            Game.insert(game_data)


    def parse_and_update(self, response):
        """ Find all games in db and update them """

        results = json.loads(response.body.decode("utf-8"))
        team_id = response.request.meta['team_id']
        tournament = response.request.meta['tournament']

        for res in results:
            venue = 'home' if res['HomeTeamID'] == team_id else 'away'
            if venue == 'home':
                game = self.get_game(res['HomeTeamID'],
                                        res['AwayTeamID'],
                                        venue,
                                        tournament)
                upd_with = {
                    'xG_for': res[self.HOME_XG],
                    'xG_against': res[self.AWAY_XG]
                }
            else:
                game = self.get_game(res['AwayTeamID'],
                                        res['HomeTeamID'],
                                        venue,
                                        tournament)
                upd_with = {
                    'xG_for': res[self.AWAY_XG],
                    'xG_against': res[self.HOME_XG]
                }

            # ignore result if game not found
            if not game:
                continue

            Game.update(str(game['_id']), upd_with)


    def get_team_by_id(self, id, tournament: League):
        return next(filter(
            lambda t: t.get(self.config["find_team_by"]) == id,
            tournament.teams)
        )


    def get_game(self, team_value, opponent_value, venue, tournament: League):
        team_id = Team.get_id(
            team_value,
            self.config["find_team_by"],
            tournament.teams,
            False)

        opponent_id = Team.get_id(
            opponent_value,
            self.config["find_team_by"],
            tournament.teams,
            False)

        game = Game.find_one(team_id, opponent_id, tournament.id, venue)
        return game if game else None


    def get_time(self, date_str):
        date = datetime.strptime(date_str, self.DATE_FORMAT)
        return int(date.replace(tzinfo=timezone.utc).timestamp())
