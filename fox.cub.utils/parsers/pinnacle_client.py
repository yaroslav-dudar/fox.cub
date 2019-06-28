import json
import ssl
import sys
from base64 import b64encode
from datetime import datetime

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL
from geventhttpclient.connectionpool import SSLConnectionPool
import gevent.pool
import pymongo

from config import Config
from models import Fixtures, Odds, Tournaments, Teams, MongoClient


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

    def __init__(self, t_id, teams):
        self.t_id = t_id
        self.teams = teams


class PinnacleApi:

    CHUNK_SIZE = 1024 * 16 # 16KB
    http = HTTPClient.from_url('https://api.pinnacle.com',
                               concurrency=10)
    results = []

    odds_v1 = '/v1/odds?sportId={0}&leagueIds={1}&oddsFormat={2}'
    fixtures_v1 = '/v1/fixtures?sportId={0}&leagueIds={1}'

    # Pinnacle football id
    SPORT_ID = '29'
    LEAGUES = '1872, 1718, 2663'

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.auth_headers = { 'Authorization' : 'Basic %s' %  self.get_base_auth() }

        self.fixture = Fixtures()
        self.odds = Odds()
        self.tournaments = Tournaments()
        self.teams = Teams()

        self.leagues_list = {}
        self.init_data()


    def get_base_auth(self):
        return b64encode("{0}:{1}".format(self.username, self.password).encode()).decode("ascii")


    def get_fixture(self, sport_id, leagues_ids, since=None):
        req = URL(self.fixtures_v1.format(sport_id, leagues_ids))
        response = self.http.get(req.request_uri, headers=self.auth_headers)
        data = self.read_json(response)

        fixtures_list = []
        try:
            for league in data['league']:
                for ev in league['events']:
                    home_id, away_id, tournament_id = self.get_fixture_ids(league['id'], ev)

                    document = self.fixture.get_document(
                        ev['id'], ev['home'], ev['away'],
                        self.parse_date(ev['starts']),
                        league['name'], home_id, away_id,
                        tournament_id)

                    fixtures_list.append(document)
        except KeyError:
            raise Exception(
                "Error occured during processing fixtures. Pinnacle response: {}".format(data))

        return fixtures_list


    def get_odds(self, sport_id, leagues_ids, oddsFormat="Decimal"):
        req = URL(self.odds_v1.format(sport_id, leagues_ids, oddsFormat))
        response = self.http.get(req.request_uri, headers=self.auth_headers)
        data = self.read_json(response)

        odds_list = []
        try:
            for league in data['leagues']:
                for ev in league['events']:
                    full_game_odds = ev['periods'][0]
                    spreads, moneyline, totals = self.parse_odds(full_game_odds)

                    # ignore special odds
                    if not all([spreads, moneyline, totals]): continue

                    document = self.odds.get_document(
                        ev['id'], datetime.utcnow(),
                        spreads, moneyline, totals)

                    odds_list.append(document)
        except KeyError:
            raise Exception(
                "Error occured during processing odds. Pinnacle response: {}".format(data))

        return odds_list


    def read_json(self, response):
        data = ''
        while True:
            chunk = response.read(self.CHUNK_SIZE).decode("utf-8")
            if chunk == '':
                break

            data += chunk

        return json.loads(data)


    def parse_date(self, str_date):
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
            tournament = self.tournaments.get(l_id, "pinnacle_id")

            if not tournament:
                self.leagues_list[l_id] = None
            else:
                t_id = str(tournament['_id'])
                self.leagues_list[l_id] = League(t_id, self.teams.find(t_id))


    def get_fixture_ids(self, league_id, fixture):
        """ Fetch Fox.Cub DB ids (home, away, tournament) for a given fixture
        Args:
            league_id (str): Pinnacle League Id
            fixture (dict): Pinnacle Fixture
        """
        home_id, away_id, tournament_id = None, None, None
        tournament = self.leagues_list[league_id]

        if tournament:
            tournament_id = tournament.t_id
            home_id = self.teams.get_id(fixture['home'], 'name', tournament.teams)
            away_id = self.teams.get_id(fixture['away'], 'name', tournament.teams)

        return home_id, away_id, tournament_id


    def parse_odds(self, game_odds):
        spreads = game_odds.get('spreads')
        moneyline = game_odds.get('moneyline')
        totals = game_odds.get('totals')

        return spreads, moneyline, totals


if __name__ == '__main__':

    if len(sys.argv) < 3:
        raise Exception("Please, put your Pinnacle credentials!")

    user_id = sys.argv[1]
    user_pwd = sys.argv[2]


    # create database connection
    client = MongoClient(Config()['database'])

    pinnacle = PinnacleApi(user_id, user_pwd)
    pool = gevent.pool.Pool(20)
    fixtures = pool.spawn(pinnacle.get_fixture, pinnacle.SPORT_ID, pinnacle.LEAGUES)
    odds = pool.spawn(pinnacle.get_odds, pinnacle.SPORT_ID, pinnacle.LEAGUES)

    pool.join()

    for fixture in fixtures.value:
        pinnacle.fixture.add(fixture)

    pinnacle.odds.insert_many(odds.value)

    client.conn.close()
    pinnacle.close()
