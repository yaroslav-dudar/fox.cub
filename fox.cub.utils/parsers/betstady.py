import scrapy

import re
from collections import defaultdict

class BetStadyDataset:

    url_pattern = "https://www.betstudy.com/soccer-stats/c/{0}/{1}/d/results/{2}/"

    def __init__(self, region: str, division: str, seasons: list):
        self.current = 0
        self.region = region
        self.division = division
        self.seasons = seasons

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < len(self.seasons):
            url = self.get_url()
            self.current += 1
            return url

        raise StopIteration

    def get_url(self):
        return self.url_pattern.format(self.region,
                                       self.division,
                                       self.seasons[self.current])


class Match(scrapy.Item):
    Date = scrapy.Field()
    HomeTeam = scrapy.Field()
    AwayTeam = scrapy.Field()
    FTHG = scrapy.Field()
    FTAG = scrapy.Field()
    HTHG = scrapy.Field()
    HTAG = scrapy.Field()
    HomeGoalsTiming = scrapy.Field()
    AwayGoalsTiming = scrapy.Field()
    Season = scrapy.Field()
    Group = scrapy.Field()


class BetStadySpider(scrapy.Spider):
    name = 'betstady'

    belgium_b = BetStadyDataset("belgium", "second-division",
                                ["{0}-{1}".format(year, year+1)
                                for year in range(2005, 2019)])


    a_league = BetStadyDataset("australia", "a-league",
                               ["{0}-{1}".format(year, year+1)
                               for year in range(2005, 2019)])


    poland_1liga = BetStadyDataset("poland", "i-liga",
                                  ["{0}-{1}".format(year, year+1)
                                  for year in range(2005, 2019)])


    ekstraklasa = BetStadyDataset("poland", "ekstraklasa",
                                  ["{0}-{1}".format(year, year+1)
                                  for year in range(2005, 2019)])

    ukr_premier_league = BetStadyDataset("ukraine", "premier-league",
                                         ["{0}-{1}".format(year, year+1)
                                         for year in range(2005, 2019)])


    dataset = ukr_premier_league
    proxy = "200.105.215.18:33630"

    def start_requests(self):
        for url in self.dataset:
            yield scrapy.Request(url=url,
                                 callback=self.parse_table,
                                 meta={'proxy': self.proxy})

    def get_season_year(self, url):
        season = url.rsplit('/', 2)[-2]
        return season.split('-')[0]

    def parse_table(self, response):
        games = response.css('table.schedule-table tr')
        season = self.get_season_year(response.request.url)

        for game in games:
            fields = game.css('td')
            if len(fields) < 4:
                continue

            match = Match()
            match['Season'] = season
            match['Group'] = -1
            match['HomeGoalsTiming'], match['AwayGoalsTiming'] = '', ''
            match['HTHG'], match['HTAG'] = None, None

            match['Date'] = fields[0].css('::text').extract_first().\
                                      replace(".", "/")
            match['HomeTeam'] = fields[1].css('a::text').extract_first()
            match['AwayTeam'] = fields[3].css('a::text').extract_first()
            match['FTHG'], match['FTAG'] = fields[2].css('strong::text').\
                                                     extract_first().\
                                                     replace(' ', '').\
                                                     split("-")

            yield match

