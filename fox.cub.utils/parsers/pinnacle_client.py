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
from models import Fixtures, Odds, MongoClient


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


class PinnacleApi:

    CHUNK_SIZE = 1024 * 16 # 16KB
    http = HTTPClient.from_url('https://api.pinnacle.com',
                               concurrency=10)
    results = []

    odds_v1 = '/v1/odds?sportId={0}&leagueIds={1}&oddsFormat={2}'
    fixtures_v1 = '/v1/fixtures?sportId={0}&leagueIds={1}'

    # Pinnacle football id
    SPORT_ID = '29'
    LEAGUES = '1872, 2639'

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.auth_headers = { 'Authorization' : 'Basic %s' %  self.get_base_auth() }

        self.fixture = Fixtures()
        self.odds = Odds()


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
                    document = self.fixture.get_document(
                        ev['id'], ev['home'], ev['away'],
                        self.parse_date(ev['starts']),
                        league['name'])

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
                    full_game = ev['periods'][0]
                    document = self.odds.get_document(
                        ev['id'], datetime.utcnow(),
                        full_game['spreads'],
                        full_game['moneyline'],
                        full_game['totals'])

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
