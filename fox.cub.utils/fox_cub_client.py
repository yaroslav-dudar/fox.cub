import json

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL

class FoxCub:

    CHUNK_SIZE = 1024 * 16 # 16KB
    http = HTTPClient.from_url("http://localhost:8888", concurrency=10)
    results = []

    def __init__(self, tournament_id):
        self.test_model_url = URL('/api/v1/test/stats?tournament_id=%s' % tournament_id)

    def get_stats(self, home_results,
        away_results, tournament_avg,
        home_team, away_team):

        data = {
            "firstBatch": [{
                "tournament_avg": [tournament_avg],
                "home_team": [home_results],
                "away_team": [away_results]
            }]
        }

        response = self.http.post(self.test_model_url.request_uri, body=json.dumps(data))
        data = self.read_json(response)
        data['HomeTeam'] = home_team
        data['AwayTeam'] = away_team

        self.results.append(data)

    def read_json(self, response):
        data = response.read(self.CHUNK_SIZE).decode("utf-8")
        return json.loads(data)

    def close(self):
        self.http.close()

    def clear_results(self):
        self.results = []
