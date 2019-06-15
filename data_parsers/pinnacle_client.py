import json
from base64 import b64encode
import ssl
import http.client

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL
from geventhttpclient.connectionpool import SSLConnectionPool


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

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.auth_headers = { 'Authorization' : 'Basic %s' %  self.get_base_auth() }


    def get_base_auth(self):
        return b64encode("{0}:{1}".format(self.username, self.password).encode()).decode("ascii")


    def get_fixture(self, sport_id, leagues_ids, since=None):
        req = URL(self.fixtures_v1.format(sport_id, leagues_ids))
        response = self.http.get(req.request_uri, headers=self.auth_headers)
        data = self.read_json(response)
        return data

    def get_odds(self, sport_id, leagues_ids, oddsFormat="Decimal"):
        req = URL(self.odds_v1.format(sport_id, leagues_ids, oddsFormat))
        response = self.http.get(req.request_uri, headers=self.auth_headers)
        data = self.read_json(response)
        return data


    def read_json(self, response):
        data = response.read(self.CHUNK_SIZE).decode("utf-8")
        return json.loads(data)

    def close(self):
        self.http.close()
