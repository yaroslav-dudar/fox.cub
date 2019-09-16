import scrapy

import re
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
    Group = scrapy.Field()


class SoccerPunterSpider(scrapy.Spider):
    name = 'soccerpunter'

    championship = ["/England/Championship-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    epl = ["/England/Premier-League-{0}-{1}".format(year, year+1)
        for year in range(1965, 2019)]

    bundesliga = ["/Germany/Bundesliga-{0}-{1}".format(year, year+1)
        for year in range(1963, 2019)]

    bundesliga2 = ["/Germany/2.-Bundesliga-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    bundesliga3 = ["/Germany/3.-Liga-{0}-{1}".format(year, year+1)
        for year in range(2008, 2019)]

    efl_league1 = ["/England/League-One-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    efl_league2 = ["/England/League-Two-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    laliga = ["/Spain/La-Liga-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    segunda = ["/Spain/Segunda-División-{0}-{1}".format(year, year+1)
        for year in range(1996, 2019)]

    serie_a = ["/Italy/Serie-A-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    serie_b = ["/Italy/Serie-B-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    serie_c = ["/Italy/Serie-C-{0}-{1}".format(year, year+1)
        for year in range(1999, 2019)]

    france_ligue1 = ["/France/Ligue-1-{0}-{1}".format(year, year+1)
        for year in range(1994, 2019)]

    france_ligue2 = ["/France/Ligue-2-{0}-{1}".format(year, year+1)
        for year in range(1994, 2019)]

    belgium_div1 = ["/Belgium/First-Division-A-{0}-{1}".format(year, year+1)
        for year in range(1995, 2018)]

    eradivisie = ["/Netherlands/Eredivisie-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    eereste_divicie = ["/Netherlands/Eerste-Divisie-{0}-{1}".format(year, year+1)
        for year in range(1996, 2019)]

    swiss_super_league = ["/Switzerland/Super-League-{0}-{1}".format(year, year+1)
        for year in range(1994, 2019)]

    swiss_chalange_league = ["/Switzerland/Challenge-League-{0}-{1}".format(year, year+1)
        for year in range(1999, 2019)]

    slovakia_super_liga = ["/Slovakia/Super-Liga-{0}-{1}".format(year, year+1)
        for year in range(2002, 2018)]

    norway_division1 = ["/Norway/1.-Division-{0}".format(year)
        for year in range(1997, 2018)]

    denmark_division1 = ["/Denmark/1st-Division-{0}-{1}".format(year, year+1)
        for year in range(1997, 2018)]

    czech_liga = ["/Czech-Republic/Czech-Liga-{0}-{1}".format(year, year+1)
        for year in range(1994, 2018)]

    portugal_liga = ["/Portugal/Primeira-Liga-{0}-{1}".format(year, year+1)
        for year in range(1994, 2019)]

    mls = ["/USA/MLS-{0}".format(year)
        for year in range(2000, 2020)]

    austria_bundesliga = ["/Austria/Bundesliga-{0}-{1}".format(year, year+1)
        for year in range(1993, 2019)]

    scotland_premiership = ["/Scotland/Premiership-{0}-{1}".format(year, year+1)
        for year in range(1994, 2019)]

    eu_qualification = [
        "/Europe/EC-Qualification-2012-Poland-Ukraine/results",
        "/Europe/EC-Qualification-2016-France",
        "/Europe/EC-Qualification-2008-Austria-Switzerland",
        "/Europe/EC-Qualification-2004-Portugal",
        "/Europe/EC-Qualification-2000-Netherlands-Belgium",
        "/Europe/EC-Qualification-1996-England",
        "/Europe/EC-Qualification-1992-Sweden",
        "/Europe/EC-Qualification-1988-Germany",
        "/Europe/EC-Qualification-1984-France",

        "/Europe/WC-Qualification-Europe-2018-Russia",
        "/Europe/WC-Qualification-Europe-2014-Brazil",
        "/Europe/WC-Qualification-Europe-2010-South-Africa",
        "/Europe/WC-Qualification-Europe-2006-Germany",
        "/Europe/WC-Qualification-Europe-2002-Korea-Rep-Japan",
        "/Europe/WC-Qualification-Europe-1998-France",
        "/Europe/WC-Qualification-Europe-1994-USA"
    ]

    eu_championship = [
        "/Europe/European-Championship-2016-France",
        "/Europe/European-Championship-2012-Poland-Ukraine",
        "/Europe/European-Championship-2008-Austria-Switzerland",
        "/Europe/European-Championship-2004-Portugal",
        "/Europe/European-Championship-2000-Netherlands-Belgium",
        "/Europe/European-Championship-1996-England",
        "/Europe/European-Championship-1992-Sweden",
        "/Europe/European-Championship-1988-Germany",
        "/Europe/European-Championship-1984-France"
    ]

    sa_qualification = [
        "/South-America/WC-Qualification-South-America-2018-Russia",
        "/South-America/WC-Qualification-South-America-2014-Brazil",
        "/South-America/WC-Qualification-South-America-2010-South-Africa",
        "/South-America/WC-Qualification-South-America-2006-Germany",
        "/South-America/WC-Qualification-South-America-2002-Korea-Rep-Japan"
    ]

    copa_america = [
        "/South-America/Copa-America-2016-USA",
        "/South-America/Copa-America-2015-Chile",
        "/South-America/Copa-America-2011-Argentina",
        "/South-America/Copa-America-2007-Venezuela",
        "/South-America/Copa-America-2004-Peru",
        "/South-America/Copa-America-2001-Colombia",
        "/South-America/Copa-America-1999-Paraguay",
        "/South-America/Copa-America-1997-Bolivia",
        "/South-America/Copa-America-1995-Uruguay"
    ]

    africa_qualification = [
        "/Africa/WC-Qualification-Africa-2018-Russia",
        "/Africa/WC-Qualification-Africa-2014-Brazil",
        "/Africa/WC-Qualification-Africa-2010-South-Africa",
        "/Africa/WC-Qualification-Africa-2006-Germany",
        "/Africa/WC-Qualification-Africa-2002-Korea-Rep-Japan"
    ]

    africa_cup = [
        "/Africa/Africa-Cup-of-Nations-2017-Gabon",
        "/Africa/Africa-Cup-of-Nations-2015-Equatorial-Guinea",
        "/Africa/Africa-Cup-of-Nations-2013-South-Africa",
        "/Africa/Africa-Cup-of-Nations-2012-Equatorial-Guinea-Gabon",
        "/Africa/Africa-Cup-of-Nations-2010-Angola",
        "/Africa/Africa-Cup-of-Nations-2008-Ghana",
        "/Africa/Africa-Cup-of-Nations-2006-Egypt",
        "/Africa/Africa-Cup-of-Nations-2004-Tunisia",
        "/Africa/Africa-Cup-of-Nations-2002-Mali",
        "/Africa/Africa-Cup-of-Nations-2000-Ghana-Nigeria",
        "/Africa/Africa-Cup-of-Nations-1998-Burkina-Faso"
    ]

    asia_qualification = [
        "/Asia/Asian-Cup-Qualification-2019-UAE",
        "/Asia/Asian-Cup-Qualification-2015-Australia",

        "/Asia/WC-Qualification-Asia-2018-Russia",
        "/Asia/WC-Qualification-Asia-2014-Brazil",
        "/Asia/WC-Qualification-Asia-2010-South-Africa",
        "/Asia/WC-Qualification-Asia-2006-Germany",
        "/Asia/WC-Qualification-Asia-2002-Korea-Rep-Japan"
    ]

    asia_cup = [
        "/Asia/AFC-Asian-Cup-2019-UAE",
        "/Asia/AFC-Asian-Cup-2015-Australia",
        "/Asia/AFC-Asian-Cup-2011-Qatar",
        "/Asia/AFC-Asian-Cup-2007-Indonesia---Malaysia---Thailand---Vietnam",
        "/Asia/AFC-Asian-Cup-2004-China"
    ]

    gold_cup = [
        "/N-C-America/CONCACAF-Gold-Cup-2017-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2015-USA-Canada",
        "/N-C-America/CONCACAF-Gold-Cup-2013-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2011-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2009-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2007-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2005-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2003-USA-Mexico",
        "/N-C-America/CONCACAF-Gold-Cup-2002-USA",
        "/N-C-America/CONCACAF-Gold-Cup-2000-USA",
        "/N-C-America/CONCACAF-Gold-Cup-1998-USA",
        "/N-C-America/CONCACAF-Gold-Cup-1996-USA",
        "/N-C-America/CONCACAF-Gold-Cup-1993-USA-Mexico",
        "/N-C-America/CONCACAF-Gold-Cup-1991-USA"
    ]

    world_cup = [
        "/World/World-Cup-2018-Russia",
        "/World/World-Cup-2014-Brazil",
        "/World/World-Cup-2010-South-Africa",
        "/World/World-Cup-2006-Germany",
        "/World/World-Cup-2002-Korea-Rep-Japan",
        "/World/World-Cup-1998-France",
        "/World/World-Cup-1994-USA",
        "/World/World-Cup-1990-Italy",
        "/World/World-Cup-1986-Mexico",
        "/World/World-Cup-1982-Spain"
    ]

    world_cup_u20 = [
        "/World/U20-World-Cup-2019-Poland",
        "/World/U20-World-Cup-2017-Korea-Republic",
        "/World/U20-World-Cup-2015-New-Zealand",
        "/World/U20-World-Cup-2013-Turkey",
        "/World/U20-World-Cup-2011-Colombia",
        "/World/U20-World-Cup-2009-Egypt",
        "/World/U20-World-Cup-2007-Canada",
        "/World/U20-World-Cup-2005-Netherlands",
    ]

    uefa_u21 = [
        "/Europe/UEFA-U21-Championship-2019-Italy",
        "/Europe/UEFA-U21-Championship-2017-Poland",
        "/Europe/UEFA-U21-Championship-2015-Czech-Republic",
        "/Europe/UEFA-U21-Championship-2013-Israel",
        "/Europe/UEFA-U21-Championship-2011-Denmark",
        "/Europe/UEFA-U21-Championship-2009-Sweden",
        "/Europe/UEFA-U21-Championship-2007-Netherlands",
        "/Europe/UEFA-U21-Championship-2006-Portugal"
    ]

    uefa_u19 = [
        "/Europe/UEFA-U19-Championship-2019-Armenia",
        "/Europe/UEFA-U19-Championship-2018-Finland",
        "/Europe/UEFA-U19-Championship-2017-Georgia",
        "/Europe/UEFA-U19-Championship-2016-Germany",
        "/Europe/UEFA-U19-Championship-2015-Greece",
        "/Europe/UEFA-U19-Championship-2014-Hungary",
        "/Europe/UEFA-U19-Championship-2013-Lithuania",
        "/Europe/UEFA-U19-Championship-2012-Estonia",
        "/Europe/UEFA-U19-Championship-2011-Romania",
        "/Europe/UEFA-U19-Championship-2010-France",
    ]

    fa_cup = ["/England/FA-Cup-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    dfb_pokal = ["/Germany/DFB-Pokal-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    copa_del_rey = ["/Spain/Copa-del-Rey-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    scotland_fa_cup = ["/Scotland/FA-Cup-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    coupe_de_france = ["/France/Coupe-de-France-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    copa_italia = ["/Italy/Coppa-Italia-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    knvb_baker = ["/Netherlands/KNVB-Beker-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    taga_de_portugal = ["/Portugal/Taça-de-Portugal-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    austria_cup = ["/Austria/Cup-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    swiss_pokal = ["/Switzerland/Schweizer-Pokal-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    copa_de_ligue = ["/France/Coupe-de-la-Ligue-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    league_cup = ["/England/League-Cup-{0}-{1}".format(year, year+1)
        for year in range(2004, 2019)]

    open_cup = ["/USA/US-Open-Cup-{0}".format(year)
        for year in range(2007, 2019)]

    champions_league = [
        "/season/12950/Europe-Champions-League-2018-2019",
        "/season/7907/Europe-Champions-League-2017-2018",
        "/season/718/Europe-Champions-League-2016-2017",
        "/season/5321/Europe-Champions-League-2015-2016",
        "/season/5322/Europe-Champions-League-2014-2015",
        "/season/5315/Europe-Champions-League-2013-2014",
        "/season/5318/Europe-Champions-League-2012-2013",
        "/season/5313/Europe-Champions-League-2011-2012",
        "/season/5312/Europe-Champions-League-2010-2011",
        "/season/5311/Europe-Champions-League-2009-2010",
        "/season/5310/Europe-Champions-League-2008-2009",
        "/season/5309/Europe-Champions-League-2007-2008",
        "/season/5308/Europe-Champions-League-2006-2007",
        "/season/5307/Europe-Champions-League-2005-2006"
    ]

    europa_league = [
        "/season/12945/Europe-Europa-League-2018-2019",
        "/season/7908/Europe-Europa-League-2017-2018",
        "/season/719/Europe-Europa-League-2016-2017",
        "/season/5337/Europe-Europa-League-2015-2016",
        "/season/5335/Europe-Europa-League-2014-2015",
        "/season/5334/Europe-Europa-League-2013-2014",
        "/season/5333/Europe-Europa-League-2012-2013",
        "/season/5332/Europe-Europa-League-2011-2012",
        "/season/5331/Europe-Europa-League-2010-2011",
        "/season/5330/Europe-Europa-League-2009-2010",
        "/season/5329/Europe-Europa-League-2008-2009",
        "/season/5328/Europe-Europa-League-2007-2008",
        "/season/5327/Europe-Europa-League-2006-2007",
        "/season/5326/Europe-Europa-League-2005-2006"
    ]

    tournaments = europa_league

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

    proxy = "104.236.248.219:3128"

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
        game_title = game.xpath("preceding::tr[@class='titleSpace']/td/h2/text()")[-1]
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
