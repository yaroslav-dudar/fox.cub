import scrapy
from scrapy.exceptions import DropItem

import re
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from typing import List
from datetime import datetime


class Match(scrapy.Item):
    Date = scrapy.Field()
    HomeTeam = scrapy.Field()
    AwayTeam = scrapy.Field()
    FTHG = scrapy.Field()
    FTAG = scrapy.Field()
    Map = scrapy.Field()
    Event = scrapy.Field()
    Season = scrapy.Field()
    Id = scrapy.Field()
    Url = scrapy.Field()
    Group = scrapy.Field()


@dataclass
class CSGOTeam:
    _id: int
    name: str

class HLTVDataset:
    """ http://spys.one/en/ """
    url_pattern = "https://www.hltv.org/stats/teams/matches/{0}/{1}?matchType=BigEvents"

    def __init__(self, teams: List[CSGOTeam]):
        self.current = 0
        self.teams = teams


    def __iter__(self):
        return self

    def __next__(self):
        if self.current < len(self.teams):
            url = self.get_url()
            team = self.get_team_name()
            self.current += 1
            return url, team

        raise StopIteration

    def get_url(self):
        team = self.teams[self.current]
        return self.url_pattern.format(team._id, team.name)

    def get_team_name(self):
        return self.teams[self.current].name


class DuplicatesPipeline:

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['Id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['Id'])
            return item


top_teams = HLTVDataset([CSGOTeam(10578, "Infamous"),
                         CSGOTeam(10330, "Supremacy"),
                         CSGOTeam(8008, "Grayhound"),
                         CSGOTeam(4863, "TYLOO"),
                         CSGOTeam(6211, "Renegades"),
                         CSGOTeam(5929, "Space%20Soldiers"),
                         CSGOTeam(6665, "Astralis"),
                         CSGOTeam(8513, "Windigo"),
                         CSGOTeam(7533, "North"),
                         CSGOTeam(4411, "NiP"),
                         CSGOTeam(7092, "5POWER"),
                         CSGOTeam(5995, "G2"),
                         CSGOTeam(6667, "FaZe"),
                         CSGOTeam(5310, "HellRaisers"),
                         CSGOTeam(5973, "Liquid"),
                         CSGOTeam(6134, "Kinguin"),
                         CSGOTeam(6947, "TeamOne"),
                         CSGOTeam(7532, "BIG"),
                         CSGOTeam(4494, "mousesports"),
                         CSGOTeam(5422, "Dignitas"),
                         CSGOTeam(6290, "Luminosity"),
                         CSGOTeam(6902, "GODSENT"),
                         CSGOTeam(4991, "fnatic"),
                         CSGOTeam(6137, "SK"),
                         CSGOTeam(7865, "HAVU"),
                         CSGOTeam(6615, "OpTic"),
                         CSGOTeam(6978, "Singularity"),
                         CSGOTeam(8120, "AVANGAR"),
                         CSGOTeam(6010, "Chiefs"),
                         CSGOTeam(5991, "Envy"),
                         CSGOTeam(4608, "Natus%20Vincere"),
                         CSGOTeam(5752, "Cloud9"),
                         CSGOTeam(7175, "Heroic"),
                         CSGOTeam(5378, "Virtus.pro"),
                         CSGOTeam(5988, "FlipSid3"),
                         CSGOTeam(4688, "Epsilon"),
                         CSGOTeam(8637, "Sprout"),
                         CSGOTeam(4869, "ENCE"),
                         CSGOTeam(5974, "CLG"),
                         CSGOTeam(8135, "forZe"),
                         CSGOTeam(5395, "PENTA"),
                         CSGOTeam(6673, "NRG"),
                         CSGOTeam(4674, "LDLC"),
                         CSGOTeam(5005, "Complexity"),
                         CSGOTeam(8068, "AGO"),
                         CSGOTeam(7898, "pro100"),
                         CSGOTeam(7020, "Spirit"),
                         CSGOTeam(6896, "PRIDE"),
                         CSGOTeam(4602, "Tricked"),
                         CSGOTeam(6651, "Gambit"),
                         CSGOTeam(7969, "Nemiga"),
                         CSGOTeam(4501, "ALTERNATE%20aTTaX"),
                         CSGOTeam(9215, "MIBR"),
                         CSGOTeam(8474, "100%20Thieves"),
                         CSGOTeam(10399, "Evil%20Geniuses"),
                         CSGOTeam(7354, "MVP%20PK"),
                         CSGOTeam(7606, "ViCi")])


class HLTVSpider(scrapy.Spider):
    name = 'hltv'

    dataset = top_teams
    proxy = "61.220.204.25:3128"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'ITEM_PIPELINES': {
            'hltv.DuplicatesPipeline': 300,
        }
    }

    def start_requests(self):
        for url, team in self.dataset:
            yield scrapy.Request(url=url,
                                 callback=self.parse_table,
                                 meta={'proxy': self.proxy, 'team': team})

    def get_season_year(self, date):
        return date.split('/')[-1]

    def convert_date(self, datetime_str: str):
        return datetime.strptime(datetime_str, '%d/%m/%y').strftime('%d/%m/%Y')

    def get_group(self, match):
        teams = [match['HomeTeam'], match['AwayTeam']]
        teams.sort()
        group = teams[0] + teams[1] + match['Date']
        return hash(group)

    def parse_table(self, response):
        games = response.css('table.stats-table tbody tr')

        for game in games:
            match = Match()

            match['Date'] = self.convert_date(game.css('td.time a::text').extract_first())

            match['HomeTeam'] = response.meta.get('team')
            match['AwayTeam'] = game.xpath('(.//td)[4]/a/text()').extract_first()
            match['FTHG'], match['FTAG'] = game.css('td.gtSmartphone-only span.statsDetail::text').\
                                                     extract_first().\
                                                     replace(' ', '').\
                                                     split("-")

            match['Url'] = game.css('td.time a::attr(href)').extract_first()
            match['Id'] = game.css('td.time a::attr(href)').extract_first().split('/')[4]
            match['Map'] = game.css('td.statsMapPlayed span::text').extract_first()
            match['Event'] = game.xpath('(.//td)[2]/a/@title').extract_first()
            match['Season'] = self.get_season_year(match['Date'])
            match['Group'] = self.get_group(match)

            yield match

