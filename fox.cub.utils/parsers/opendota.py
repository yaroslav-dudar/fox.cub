import scrapy
from scrapy.exceptions import DropItem

import re
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import List
from datetime import datetime


class Match(scrapy.Item):
    Date = scrapy.Field()
    HomeTeam = scrapy.Field() # radiant team
    AwayTeam = scrapy.Field() # dire team
    FTHG = scrapy.Field() # radiant team score
    FTAG = scrapy.Field() # dire team score
    HomeTeamId = scrapy.Field()
    AwayTeamId = scrapy.Field()
    Event = scrapy.Field()
    EventId = scrapy.Field()
    Season = scrapy.Field()
    Id = scrapy.Field()
    Group = scrapy.Field()
    Duration = scrapy.Field()
    HomeTeamWin = scrapy.Field()
    Type = scrapy.Field()


class OpenDotaSpider(scrapy.Spider):
    """ https://docs.opendota.com/#tag/pro-matches%2Fpaths%2F~1proMatches%2Fget """
    name = 'opendota'

    base_url = "https://api.opendota.com/api/proMatches"
    stop_on_match_id = 5458146682
    proxy = "83.168.86.1:8090"

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1
    }

    def __init__(self, category=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_requests = 300
        self.iter_num = 0


    def get_season_year(self, date: str):
        return date.split('/')[-1]

    def convert_date(self, ts: int):
        return datetime.utcfromtimestamp(ts).strftime('%d/%m/%Y')

    def start_requests(self):
        yield scrapy.Request(url=self.base_url,
                             callback=self.parse,
                             meta={'proxy': self.proxy})

    def parse(self, response):
        games = json.loads(response.text)
        if not games: return

        lower_match_id = float("inf")
        self.iter_num += 1

        for game in games:
            match = Match()

            match['Date'] = self.convert_date(game["start_time"])
            match['HomeTeam'], match['AwayTeam'] = game["radiant_name"], game["dire_name"]
            match['HomeTeamId'], match['AwayTeamId'] = game["radiant_team_id"], game["dire_team_id"]
            match['FTHG'], match['FTAG'] = game["radiant_score"], game["dire_score"]
            match['Duration'] = game["duration"]
            match['Id'] = game["match_id"]
            match['Season'] = self.get_season_year(match['Date'])
            match['Group'] = game["series_id"]
            match["Event"] = game["league_name"]
            match["EventId"] = game["leagueid"]
            match["HomeTeamWin"] = game["radiant_win"]
            match["Type"] = game["series_type"]

            if lower_match_id > match["Id"]:
                lower_match_id = match["Id"]

            if self.stop_on_match_id and match["Id"] < self.stop_on_match_id:
                # stop parser
                return

            if None not in [match['HomeTeam'], match['AwayTeam']]:
                yield match


        next_url = "{0}?less_than_match_id={1}".format(self.base_url,
                                                       lower_match_id)

        if self.iter_num < self.max_requests:
            yield scrapy.Request(url=next_url,
                                callback=self.parse,
                                meta={'proxy': self.proxy})

