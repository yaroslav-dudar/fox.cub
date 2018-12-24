import scrapy
from collections import defaultdict

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


class SoccerPunterSpider(scrapy.Spider):
    name = 'soccerpunter'

    championship = ["/England/Championship-{0}-{1}".format(year, year+1)
        for year in range(1993, 2018)]

    epl = ["/England/Premier-League-{0}-{1}".format(year, year+1)
        for year in range(1965, 2018)]

    bundesliga = ["/Germany/Bundesliga-{0}-{1}".format(year, year+1)
        for year in range(1963, 2018)]

    bundesliga2 = ["/Germany/2.-Bundesliga-{0}-{1}".format(year, year+1)
        for year in range(1993, 2018)]

    efl_league1 = ["/England/League-One-{0}-{1}".format(year, year+1)
        for year in range(1993, 2018)]

    laliga = ["/Spain/La-Liga-{0}-{1}".format(year, year+1)
        for year in range(1993, 2018)]

    serie_a = ["/Italy/Serie-A-{0}-{1}".format(year, year+1)
        for year in range(1993, 2018)]

    tournaments = serie_a
    base_url = "https://www.soccerpunter.com/soccer-statistics"

    h_timings = defaultdict(list)
    a_timings = defaultdict(list)

    GAME_CODE = "G"

    proxy = "131.108.6.118:50435"

    def start_requests(self):
        urls = [self.base_url + t + "/results" for t in self.tournaments]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': self.proxy})

    def parse(self, response):
        games = response.css("table.roundsResultDisplay")
        season = self.get_season_year(response)

        matches = {}

        for g in games.css("tr[data-match]:not([data-code])"):
            self.parse_game_details(g, matches)

        for g in games.css("tr[data-match][data-code]"):
            self.parse_events(g, matches)

        for k,v in matches.items():
            v['HomeGoalsTiming'] = ' '.join(self.h_timings[k])
            v['AwayGoalsTiming'] = ' '.join(self.a_timings[k])
            v['Season'] = season
            yield v


    def parse_events(self, game, matches):
        match_id = game.css("::attr(data-match)").extract_first()
        match = matches[match_id]

        ev_type = game.css("::attr(data-code)").extract_first()
        if ev_type == self.GAME_CODE:
            home = game.css("td.evHome span.event_minute::text").extract_first()
            away = game.css("td.evAway span.event_minute::text").extract_first()

            if home: self.h_timings[match_id].append(self.get_goal_timing(home))
            if away: self.a_timings[match_id].append(self.get_goal_timing(away))

    def parse_game_details(self, game, matches):
        is_game_finished = game.css("td.score div.score:not([data-timestamp])").\
            extract_first()
        if not is_game_finished:
            # ignore not finished games
            return

        match_id = game.css("::attr(data-match)").extract_first()
        match = Match()

        home_team = game.css(".teamHome a.teamLink::text").extract()
        away_team = game.css(".teamAway a.teamLink::text").extract()
        match['HomeTeam'] = ''.join([i for i in home_team]).strip()
        match['AwayTeam'] = ''.join([i for i in away_team]).strip()
        match['FTHG'], match['FTAG'] = game.css("td.score div.score::text").\
            extract_first().replace(' ', '').split("-")
        half_time_score = game.css("div.halfTimeScore::text").extract_first()

        match['HTHG'], match['HTAG'] = half_time_score.replace(' ', '').split("-") if half_time_score else [None, None]
        match['Date'] = game.css("a.dateLink::text").extract_first().strip()
        matches[match_id] = match

    def get_goal_timing(self, goal):
        goal = goal.replace("'", "")
        return str(eval(goal)) if '+' in goal else goal

    def get_season_year(self, response):
        season = response.css("select.sbar_season option[selected]::text").\
            extract_first()
        return season.split('/')[0]
