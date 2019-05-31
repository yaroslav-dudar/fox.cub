import json

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL

class FoxCub:

    CHUNK_SIZE = 1024 * 16 # 16KB
    http = HTTPClient.from_url("http://localhost:8888", concurrency=10)
    results = []

    def __init__(self, tournament_id):
        self.test_model_url = URL('/api/v1/test/stats?tournament_id=%s' % tournament_id)

    def get_stats(self, home_team, away_team, tournament):

        data = {
            "firstBatch": [{
                "tournament_avg": [tournament],
                "home_team": [home_team],
                "away_team": [away_team]
            }]
        }

        response = self.http.post(self.test_model_url.request_uri, body=json.dumps(data))
        self.results.append(self.read_json(response))

    def read_json(self, response):
        data = response.read(self.CHUNK_SIZE).decode("utf-8")
        return json.loads(data)

    def close(self):
        self.http.close()
