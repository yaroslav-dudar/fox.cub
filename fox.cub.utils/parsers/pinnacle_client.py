"""Fetch sport fixtures and their odds using Pinaccle API."""

from gevent import monkey
monkey.patch_all()

import json
import ssl
import sys
import functools
from collections import namedtuple

from base64 import b64encode
from datetime import datetime

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL
from geventhttpclient.connectionpool import SSLConnectionPool
import gevent.pool
import pymongo

from models import (
    Fixture as FixtureModel, Odds, Tournament,
    Team, MongoClient, Pinnacle)


def _create_tcp_socket(self, family, socktype, protocol):
    """ Use ssl.SSLContext instead of gevent.ssl context"""
    sock = super(SSLConnectionPool, self)._create_tcp_socket(
        family, socktype, protocol)

    if self.ssl_context_factory is None:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cafile='/etc/ssl/certs/ca-certificates.crt')
        return context.wrap_socket(sock, server_hostname=self._host)
    else:
        return self.ssl_context_factory().wrap_socket(sock, **self.ssl_options)

# Monkey patch original tcp socket method to fix SSL handshake issue
SSLConnectionPool._create_tcp_socket = _create_tcp_socket


class League:

    def __init__(self, t_id, teams, name = None):
        self.t_id = t_id
        self.teams = teams
        self.name = name


# Pinnacle Fixture object schema
fixture_fields = ["id", "home", "away", "starts", "liveStatus",
                  "status", "parlayRestriction", "altTeaser",
                  "resultingUnit", "rotNum", "parentId"]
Fixture = namedtuple(
    'Fixture', fixture_fields, defaults=(None,) * len(fixture_fields))
# Pinnacle Odds object schema
event_fields = ["id", "periods"]
Event = namedtuple('Event', event_fields, defaults=(None,) * len(event_fields))
# Pinnacle Period object schema
period_fields = ["lineId", "number", "cutoff", "maxSpread", "maxMoneyline",
                 "maxTotal", "maxTeamTotal", "status",
                 "spreads", "moneyline", "totals", "teamTotal"]
Period = namedtuple('Period', period_fields, defaults=(None,) * len(period_fields))

class PinnacleApi:

    CHUNK_SIZE = 1024 * 16 # 16KB
    http = HTTPClient.from_url('https://api.pinnacle.com',
                               concurrency=10)

    odds_v1 = '/v1/odds?sportId={0}&leagueIds={1}&oddsFormat={2}'
    fixtures_v1 = '/v1/fixtures?sportId={0}&leagueIds={1}'

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.leagues_list, self.last_since_id = {}, {}
        self.init_data()


    LEAGUES       = property(lambda self: '1977, 1980, 2663, 1842, 2635')
    SPORT_ID      = property(lambda self: '29')
    FIND_TEAM_BY  = property(lambda self: 'pinnacle_name')
    FIND_TOURN_BY = property(lambda self: 'pinnacle_id')

    @property
    def auth_headers(self) -> dict:
        return {
            'Authorization' : 'Basic %s' %
            self.get_base_auth(self.username, self.password)
        }


    @functools.lru_cache(maxsize=32)
    def get_base_auth(self, username, password) -> str:
        return b64encode("{0}:{1}".format(
                         username,
                         password
                         ).encode()).decode("ascii")


    def get_fixture(self, sport_id, leagues_ids):
        req = URL(self.fixtures_v1.format(sport_id, leagues_ids))
        since = self.last_since_id.get('last_fixture')
        if since: req['since'] = since

        response = self.http.get(req.request_uri, headers=self.auth_headers)
        data = self.read_json(response)

        fixtures_list = []
        if not data: return fixtures_list

        try:
            for (league, ev) in self.get_event_pairs(data):
                ev = Fixture(**ev)
                if not self.is_main_fixture(ev) or\
                    self.is_live_bet(ev): continue

                home_id, away_id, tournament_id = self.\
                    get_fixture_ids(league['id'], ev)

                document = FixtureModel.get_document(
                    ev.id, ev.home, ev.away,
                    self.parse_date(ev.starts),
                    league['name'], home_id, away_id,
                    tournament_id)

                fixtures_list.append(document)
        except KeyError:
            raise Exception(
                "Error occured during processing fixtures." +
                " Pinnacle response: {}".format(data))

        # save since ID
        self.last_since_id['last_fixture'] = data['last']
        return fixtures_list


    def get_odds(self, sport_id, leagues_ids, oddsFormat="Decimal"):
        req = URL(self.odds_v1.format(sport_id, leagues_ids, oddsFormat))
        since = self.last_since_id.get('last_odds')
        if since: req['since'] = since

        response = self.http.get(req.request_uri, headers=self.auth_headers)
        data = self.read_json(response)

        odds_list = []
        if not data: return odds_list

        try:
            for (_, ev) in self.get_event_pairs(data, "leagues"):
                event = Event(**ev)
                period = self.get_full_game_period(event)
                if not period: continue
                # ignore special odds
                if not all([period.spreads,
                            period.moneyline,
                            period.totals]): continue

                document = Odds.get_document(event.id,
                                                  datetime.utcnow(),
                                                  period.spreads,
                                                  period.moneyline,
                                                  period.totals)

                odds_list.append(document)
        except KeyError:
            raise Exception(
                "Error occured during processing odds." +
                " Pinnacle response: {}".format(data))

        # save since ID
        self.last_since_id['last_odds'] = data['last']
        return odds_list


    def read_json(self, response) -> dict:
        data = ''
        while True:
            chunk = response.read(self.CHUNK_SIZE).decode("utf-8")
            if chunk == '':
                break

            data += chunk

        print(data)
        # NOTE: return empty object if no data
        return json.loads(data) if data else {}


    @functools.lru_cache(maxsize=128)
    def parse_date(self, str_date) -> datetime:
        """ Transform date string to datetime object
        Args:
            str_date (str): Event date in format {year-day-monthTHours:Minutes:Seconds}
        """
        date = datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%SZ')
        return date


    def close(self):
        self.http.close()


    def init_data(self):
        # upload tournaments and teams from DB
        for l in self.LEAGUES.split(','):
            l_id = int(l.strip())
            tournament = Tournament.get(l_id, self.FIND_TOURN_BY)

            if not tournament:
                self.leagues_list[l_id] = None
            else:
                t_id = str(tournament['_id'])
                self.leagues_list[l_id] = League(t_id, Team.find(t_id))

        # upload latest fixture and odds since ID
        self.last_since_id = Pinnacle.get()


    def get_fixture_ids(self, league_id, fixture: Fixture):
        """ Fetch Fox.Cub DB ids (home, away, tournament) for a given fixture
        Args:
            league_id (str): Pinnacle League Id
            fixture (dict): Pinnacle Fixture
        """
        home_id, away_id, tournament_id = None, None, None
        tournament = self.leagues_list[league_id]

        if tournament:
            tournament_id = tournament.t_id
            home_id = Team.get_id(
                fixture.home,
                self.FIND_TEAM_BY,
                tournament.teams)
            away_id = Team.get_id(
                fixture.away,
                self.FIND_TEAM_BY,
                tournament.teams)

        return home_id, away_id, tournament_id


    def is_main_fixture(self, fixture: Fixture):
        return True if not fixture.parentId else False

    def is_live_bet(self, fixture: Fixture):
        return True if fixture.liveStatus == 1 else False

    def get_event_pairs(self, data: dict, league_attr: str = "league"):
        """ Returns generator with league, event pairs.
        Args:
            data (dict): Pinnacle API response
            league_attr (str): Path to leagues dict
        """

        return ((le, ev) for le in data[league_attr]
                for ev in le['events'])

    def get_full_game_period(self, event: Event) -> Period:
        """ Finding full game period.
        Args:
            event (Event): Pinnacle odds to find period
        """

        for period in event.periods:
            p = Period(**period)
            if p.number == 0:
                return p

        # not found full game period
        return None

    def update_last_requests(self):
        document = Pinnacle.get_document(self.last_since_id['last_fixture'],
                                         self.last_since_id['last_odds'])
        Pinnacle.insert(document)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        raise Exception("Please, put your Pinnacle credentials!")

    user_id = sys.argv[1]
    user_pwd = sys.argv[2]

    pinnacle = PinnacleApi(user_id, user_pwd)
    pool = gevent.pool.Pool(20)

    fixtures = pool.spawn(pinnacle.get_fixture,
                          pinnacle.SPORT_ID,
                          pinnacle.LEAGUES)

    odds = pool.spawn(pinnacle.get_odds,
                      pinnacle.SPORT_ID,
                      pinnacle.LEAGUES)
    pool.join()

    for fixture in fixtures.value:
        FixtureModel.add(fixture)

    if odds.value:
        Odds.insert_many(odds.value)

    pinnacle.update_last_requests()
    pinnacle.close()
