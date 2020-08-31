import scrapy

import re
from collections import defaultdict
from parsers.parser_library import SoccerPunterLib

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


class SoccerPunterSpider(scrapy.Spider):
    name = 'soccerpunter'

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1
    }

    tournaments = SoccerPunterLib.eu_qual_2020

    MODES = {
        'default': {
            "base_url": "https://www.soccerpunter.com/soccer-statistics",
            "results_p": re.compile(r'$'),
            "game_class": "data-match",
            "games_path": "table.roundsResultDisplay",
            "goal_code": "G"
        },
        'europe': {
            "base_url": "https://www.soccerpunter.com",
            "results_p": re.compile(r'/season/'),
            "game_class": "data-matchid",
            "games_path": "table.competitionRanking",
            "goal_code": "goal"
        }
    }
    SELECTED_MODE = 'europe'

    h_timings = defaultdict(list)
    a_timings = defaultdict(list)

    SORT_BY_GROUP = True
    IGNORE_NON_REGULAR_SEASON = False
    REGULAR_SEASON_NAMINGS = ["Group Stage", "Regular Season"]
    GROUPS = {}

    proxy = "51.75.160.176:9999"

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.mode = self.MODES[self.SELECTED_MODE]
        self.GOAL_CODE = self.get_goal_code()

    def get_results_url(self, base_url):
        return self.mode['results_p'].sub('/results/', base_url)

    def get_game_class(self):
        return self.mode['game_class']

    def get_games_path(self):
        return self.mode['games_path']

    def get_goal_code(self):
        return self.mode['goal_code']

    def start_requests(self):
        for t in self.tournaments:
            if self.SORT_BY_GROUP:
                # add group label to each game
                group_url = self.mode['base_url'] + t
                yield scrapy.Request(url=group_url,
                                     callback=self.parse_table,
                                     meta={'proxy': self.proxy})
            else:
                # parse games
                results_url = self.get_results_url(t)
                yield scrapy.Request(url=self.mode['base_url'] + results_url,
                                     callback=self.parse,
                                     meta={'proxy': self.proxy})

    def parse(self, response):
        games = response.css(self.get_games_path())
        season = self.get_season_year(response)

        matches = {}

        for g in games.css("tr[%s]:not([data-code])" % self.get_game_class()):
            if self.IGNORE_NON_REGULAR_SEASON\
                and not self.SORT_BY_GROUP\
                and not self.is_regular_season_game(g):
                # ignore non regular season games
                continue

            self.parse_game_details(g, matches)

        for g in games.css("tr[data-match][data-code]"):
            self.parse_events(g, matches)

        for k,v in matches.items():
            v['HomeGoalsTiming'] = ' '.join(self.h_timings[k])
            v['AwayGoalsTiming'] = ' '.join(self.a_timings[k])
            v['Season'] = season

            if self.SORT_BY_GROUP:
                self.set_group_index(v, response.meta['groups'])
            yield v


    def parse_events(self, game, matches):
        match_id = game.css("::attr(data-match)").extract_first()
        try:
            match = matches[match_id]
        except KeyError:
            # ignore game
            return

        ev_type = game.css("::attr(data-code)").extract_first()
        if ev_type == self.GOAL_CODE:
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
        # extracting team names
        home_team = game.css(".teamHome a.teamLink::text").extract()
        away_team = game.css(".teamAway a.teamLink::text").extract()

        match['HomeTeam'] = ''.join([i for i in home_team]).strip()
        match['AwayTeam'] = ''.join([i for i in away_team]).strip()

        match['FTHG'], match['FTAG'] = game.css("td.score div.score::text").\
                                                 extract_first().\
                                                 replace(' ', '').split("-")

        match['HTHG'], match['HTAG'] = self.parse_half_time_score(game)
        match['Date'] = game.css("a.dateLink::text").extract_first().strip()

        if not self.is_valid_match(match):
            # ignoring games without result
            return

        matches[match_id] = match

    def parse_table(self, response):
        groups = {}
        all_tables = response.xpath('//table[contains(@id, "ranking")]')
        for indx, table in enumerate(all_tables):
            for team in table.css('tr td.team a.teamLink::text').extract():
                groups[team.strip()] = indx

        print(groups)
        yield scrapy.Request(
            url=self.get_results_url(response.url),
            callback=self.parse,
            meta={'proxy': self.proxy, 'groups': groups})

    def get_goal_timing(self, goal):
        goal = goal.replace("'", "")
        return str(eval(goal)) if '+' in goal else goal

    def get_season_year(self, response):
        season = response.css("select.sbar_season option[selected]::text").\
            extract_first()
        return season.split('/')[0]

    def set_group_index(self, item, groups):
        try:
            if groups[item['HomeTeam']] == groups[item['AwayTeam']]:
                item['Group'] = groups[item['HomeTeam']]
            else:
                item['Group'] = -1
        except KeyError:
            # team not in any group
            item['Group'] = -1

    def is_regular_season_game(self, game):
        game_title = game.xpath("preceding::tr/td/h2[@class='centerOnScore']/text()")[-1]
        return game_title.extract().strip() in self.REGULAR_SEASON_NAMINGS

    def is_valid_match(self, match):
        return match['FTHG'] and match['FTAG']

    def parse_half_time_score(self, game):
        score = game.css("div.halfTimeScore::text").\
                         extract_first()

        if not score:
            score = game.css("td[align='center']::text").\
                         extract_first()

        if score:
            goals = score.replace(' ', '').split("-")
            if len(goals) == 2: return goals

        return [None, None]
