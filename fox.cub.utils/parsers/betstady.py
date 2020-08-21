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
                                         for year in range(2005, 2020)])

    segunda = BetStadyDataset("spain", "segunda-division",
                              ["{0}-{1}".format(year, year+1)
                              for year in range(2005, 2019)])

    a_bundesliga = BetStadyDataset("austria", "bundesliga",
                                   ["{0}-{1}".format(year, year+1)
                                   for year in range(2005, 2019)])

    au_1liga =BetStadyDataset("austria", "1.-liga",
                                   ["{0}-{1}".format(year, year+1)
                                   for year in range(2005, 2019)])


    den_1div = BetStadyDataset("denmark", "1st-division",
                               ["{0}-{1}".format(year, year+1)
                               for year in range(2005, 2019)])

    eerste_div = BetStadyDataset("netherlands", "eerste-divisie",
                                 ["{0}-{1}".format(year, year+1)
                                 for year in range(2005, 2019)])

    liganos = BetStadyDataset("portugal", "primeira-liga",
                              ["{0}-{1}".format(year, year+1)
                              for year in range(2005, 2019)])

    ger_3liga = BetStadyDataset("germany", "3.-liga",
                              ["{0}-{1}".format(year, year+1)
                              for year in range(2005, 2019)])

    j1_league = BetStadyDataset("japan", "j1-league",
                                ["{0}".format(year)
                                for year in range(2005, 2019)])

    j2_league = BetStadyDataset("japan", "j2-league",
                                ["{0}".format(year)
                                for year in range(2005, 2019)])

    allsvenskan = BetStadyDataset("sweden", "allsvenskan",
                                  ["{0}".format(year)
                                  for year in range(2005, 2019)])

    sc_championship = BetStadyDataset("scotland", "championship",
                                      ["{0}-{1}".format(year, year+1)
                                      for year in range(2005, 2019)])

    sc_premiership = BetStadyDataset("scotland", "premiership",
                                     ["{0}-{1}".format(year, year+1)
                                     for year in range(2005, 2019)])

    croatia_hnl = BetStadyDataset("croatia", "1.-hnl",
                                  ["{0}-{1}".format(year, year+1)
                                  for year in range(2005, 2019)])

    copa_libertadores = BetStadyDataset("south-america", "copa-libertadores",
                                        ["{0}".format(year)
                                        for year in range(2006, 2019)])

    rpl = BetStadyDataset("russia", "premier-league",
                          ["{0}-{1}".format(year, year+1)
                          for year in range(2011, 2019)])

    fnl = BetStadyDataset("russia", "fnl",
                          ["2018-2019","2017-2018","2016-2017",
                          "2010","2009", "2008", "2007", "2006", "2005"])

    czech_liga = BetStadyDataset("czech-republic", "czech-liga",
                          ["{0}-{1}".format(year, year+1)
                          for year in range(2005, 2019)])

    colombia_a = BetStadyDataset("colombia", "primera-a",
                                 ["{0}".format(year)
                                 for year in range(2005, 2019)])

    liga_mx = BetStadyDataset("mexico", "liga-mx",
                              ["{0}-{1}".format(year, year+1)
                              for year in range(2005, 2019)])

    arg_primera = BetStadyDataset("argentina", "primera-division",
                              ["{0}-{1}".format(year, year+1)
                              for year in range(2016, 2020)])

    chile_primera = BetStadyDataset("chile", "primera-division",
                                    ["2019","2018","2016-2017",
                                    "2012","2011"])

    serbia_super_liga = BetStadyDataset("serbia", "super-liga",
                              ["{0}-{1}".format(year, year+1)
                              for year in range(2006, 2019)])

    primera_b_national = BetStadyDataset("argentina", "prim-b-nacional",
                              ["{0}-{1}".format(year, year+1)
                              for year in range(2005, 2019)])

    br_serie_b = BetStadyDataset("brazil", "serie-b",
                              ["{0}".format(year)
                              for year in range(2005, 2019)])

    bahrain_pl = BetStadyDataset("bahrain", "premier-league",
                              ["{0}-{1}".format(year, year+1)
                              for year in range(2005, 2019)])

    bl_pl = BetStadyDataset("belarus", "premier-league",
                             ["{0}".format(year)
                             for year in range(2005, 2019)])

    k_league = BetStadyDataset("korea-republic", "k-league-classic",
                             ["{0}".format(year)
                             for year in range(2005, 2019)])

    k_league2 = BetStadyDataset("korea-republic", "k-league-challenge",
                                ["{0}".format(year)
                                for year in range(2008, 2019)])

    costa_rica_primera = BetStadyDataset("costa-rica", "primera-division",
                                         ["{0}-{1}".format(year, year+1)
                                         for year in range(2005, 2019)])

    nb_1_liga = BetStadyDataset("hungary", "nb-i",
                                ["{0}-{1}".format(year, year+1)
                                for year in range(2005, 2019)])

    dataset = ukr_premier_league
    proxy = "196.22.199.177:8080"

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

