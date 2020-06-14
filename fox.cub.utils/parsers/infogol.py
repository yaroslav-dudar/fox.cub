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

    custom_settings = {
        'DOWNLOAD_DELAY': 2
    }

    def __init__(self, *a, **kw):
        super(InfogolSpider, self).__init__(*a, **kw)

        self.global_conf = Config()
        self.config = self.global_conf['infogol_parser']

        self.proxy = "83.168.86.1:8090"
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

    def get_team_id(self, tournament, external_id):
        teams = filter(lambda t: t[self.config["find_team_by"]] == external_id,
                      tournament.teams)
        return str(next(teams)['_id'])

    def start_requests(self):
        """ Call API request for each tournament
        and team subscribed to infogol parser
        """

        for name, tournament in self.leagues_list.items():
            # fetch results for each team in a tournament
            for team in tournament.teams:
                team_id = int(team[self.config["find_team_by"]])
                team_url = self.INFOGOL_URL.format(
                    team_id=team_id,
                    comp_id=tournament.external_id)

                yield scrapy.http.FormRequest(
                    url=team_url,
                    callback=self.parse_and_add,
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
                goals_for, goals_against = res['HomeTeamGoals'], res['AwayTeamGoals']
                xg_for, xg_against = res[self.HOME_XG], res[self.AWAY_XG]
                team_id = self.get_team_id(tournament, res['HomeTeamID'])
                opponent_id = self.get_team_id(tournament, res['AwayTeamID'])
                query = Game.find_query(team_id, opponent_id, tournament.id, venue)
            else:
                goals_for, goals_against = res['AwayTeamGoals'], res['HomeTeamGoals']
                xg_for, xg_against = res[self.AWAY_XG], res[self.HOME_XG]
                team_id = self.get_team_id(tournament, res['AwayTeamID'])
                opponent_id = self.get_team_id(tournament, res['HomeTeamID'])
                query = Game.find_query(team_id, opponent_id, tournament.id, venue)

            upd_data = Game.get_document(team_id, opponent_id,
                                          tournament.id,
                                          self.get_time(res['MatchDateTime']),
                                          venue, goals_for, goals_against,
                                          xg_for, xg_against)

            Game.upsert(query, upd_data)


    def get_team_by_id(self, id, tournament: League):
        return next(filter(
            lambda t: t.get(self.config["find_team_by"]) == id,
            tournament.teams)
        )


    def get_time(self, date_str):
        date = datetime.strptime(date_str, self.DATE_FORMAT)
        return int(date.replace(tzinfo=timezone.utc).timestamp())
