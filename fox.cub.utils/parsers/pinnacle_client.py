"""Fetch sport fixtures and their odds using Pinaccle API."""

from gevent import monkey
monkey.patch_all()

import json
import ssl
import sys
import pickle
import functools
import argparse
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
from utils import SharedDataObj, init_logger, League


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
                 "maxTotal", "maxTeamTotal", "status", "spreadUpdatedAt",
                 "moneylineUpdatedAt", "totalUpdatedAt", "teamTotalUpdatedAt",
                 "spreads", "moneyline", "totals", "teamTotal"]
Period = namedtuple('Period', period_fields, defaults=(None,) * len(period_fields))

class PinnacleApi:

    CHUNK_SIZE = 1024 * 16 # 16KB
    http = HTTPClient.from_url('https://api.pinnacle.com',
                               concurrency=10)

    odds_v1 = '/v1/odds?sportId={0}&leagueIds={1}&oddsFormat={2}'
    fixtures_v1 = '/v1/fixtures?sportId={0}&leagueIds={1}'
    sports_v2 = '/v2/sports'
    leagues_v2 = '/v2/leagues?sportId={0}'

    def __init__(self, username, password, incremental_updates):
        self.username = username
        self.password = password
        self.incremental_updates = incremental_updates

        self.leagues_list, self.last_since_id = {}, {}
        self.init_data()
        self.logger = init_logger()


    SOCCER_LEAGUES = property(lambda self: '1766, 1728, 2157, 2242, 2333, 2421, 209349, 2360,'\
                                           ' 6417, 1977, 1980, 2663, 1842, 2635, 2627, 2630, 1843,'\
                                           ' 1957, 1913, 1792, 1891, 1844, 6416, 207551, 2374, 2592,'\
                                           ' 2386, 2196, 2436, 2081, 1880')
    SOCCER_ID      = property(lambda self: '29')
    E_SPORT_ID     = property(lambda self: '12')
    FIND_TEAM_BY   = property(lambda self: 'pinnacle_name')
    FIND_TOURN_BY  = property(lambda self: 'pinnacle_id')

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


    def get_sports(self):
        """ Returns all sports with the status
        whether they currently have lines or not. """
        req = URL(self.sports_v2)
        response = self.http.get(req.request_uri, headers=self.auth_headers)
        data = self.read_json(response)

        return data


    def get_leagues(self, sport_id):
        """ Returns all sports leagues with the status
        whether they currently have lines or not. """
        req = URL(self.leagues_v2.format(sport_id))
        response = self.http.get(req.request_uri, headers=self.auth_headers)
        data = self.read_json(response)

        return data


    def get_fixture(self, sport_id, leagues_ids):
        req = URL(self.fixtures_v1.format(sport_id, leagues_ids))
        since = self.last_since_id.get('last_fixture')
        if since: req['since'] = since

        response = self.http.get(req.request_uri, headers=self.auth_headers)
        data = self.read_json(response)

        fixtures_list, ev = [], None
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
                "Event data: {}.\nPinnacle response: {}".format(ev, data))

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
                period = self.modify_odds_moneyline(period)
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
        except TypeError:
            self.logger.error("Invalid Event: {}".format(ev))

        # save since ID
        self.last_since_id['last_odds'] = data['last']
        return odds_list


    def read_json(self, response) -> dict:
        """ Read chunked transfer encoding and parse as JSON text """
        data = ''
        while True:
            chunk = response.read(self.CHUNK_SIZE).decode("utf-8")
            if chunk == '':
                break

            data += chunk

        self.logger.debug(data)

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
        if self.incremental_updates:
            pinnacle.update_last_requests()

        self.http.close()


    def init_data(self):
        # upload tournaments and teams from DB
        for l in self.SOCCER_LEAGUES.split(','):
            l_id = int(l.strip())
            tournament = Tournament.get(l_id, self.FIND_TOURN_BY)

            if not tournament:
                self.leagues_list[l_id] = None
            else:
                t_id = str(tournament['_id'])
                self.leagues_list[l_id] = League(t_id, Team.find(t_id))

        if self.incremental_updates:
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

    def modify_odds_moneyline(self, period):
        """ Add dummy moneyline if missing. """
        if not period.moneyline:
            period = period._replace(moneyline = {"home" : 0,
                                                  "away" : 0,
                                                  "draw" : 0 })
        return period

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', required=True, type=str,
                        help='Pinnacle user ID.')
    parser.add_argument('-p', required=True, type=str,
                        help='Pinnacle Password')
    parser.add_argument('-o',  default=True, action='store_false',
                        help='Write parsing results to std out')
    parser.add_argument('-incr', default=True, action='store_false',
                        help='Disable incremental updates.')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    pinnacle = PinnacleApi(args.u, args.p, args.incr)
    pool = gevent.pool.Pool(20)
    new_fixtures = []

    fixtures = pool.spawn(pinnacle.get_fixture,
                          pinnacle.SOCCER_ID,
                          pinnacle.SOCCER_LEAGUES)

    odds = pool.spawn(pinnacle.get_odds,
                      pinnacle.SOCCER_ID,
                      pinnacle.SOCCER_LEAGUES)
    pool.join()

    for fixture in fixtures.value:
        res = FixtureModel.add(fixture)
        if res.upserted_id: new_fixtures.append(fixture)

    if odds.value:
        Odds.insert_many(odds.value)

    pinnacle.close()

    if args.o:
        output = SharedDataObj(odds.value, new_fixtures, None)
        serialized = pickle.dumps(output)
        pinnacle.logger.debug(serialized)
        sys.stdout.buffer.write(serialized)
