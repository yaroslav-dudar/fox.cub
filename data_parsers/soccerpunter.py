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
        for year in range(2000, 2018)]

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

    tournaments = asia_qualification
    base_url = "https://www.soccerpunter.com/soccer-statistics"

    h_timings = defaultdict(list)
    a_timings = defaultdict(list)

    GAME_CODE = "G"
    SORT_BY_GROUP = True
    IGNORE_NON_REGULAR_SEASON = False
    GROUPS = {}

    proxy = "191.252.185.161:8090"

    def start_requests(self):
        urls = [self.base_url + t for t in self.tournaments]
        for url in urls:
            if self.SORT_BY_GROUP:
                # add group label to each game
                yield scrapy.Request(url=url, callback=self.parse_table, meta={'proxy': self.proxy})
            else:
                # parse games
                yield scrapy.Request(url=url + "/results", callback=self.parse, meta={'proxy': self.proxy})

    def parse(self, response):
        games = response.css("table.roundsResultDisplay")
        season = self.get_season_year(response)

        matches = {}

        for g in games.css("tr[data-match]:not([data-code])"):
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

    def parse_table(self, response):
        groups = {}
        all_tables = response.xpath('//table[contains(@id, "ranking")]')
        for indx, table in enumerate(all_tables):
            for team in table.css('tr td.team a.teamLink::text').extract():
                groups[team.strip()] = indx

        print(groups)
        yield scrapy.Request(
            url=response.url + "/results",
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
        return game.xpath("preceding::tr[@class='titleSpace']/td/h2/text()")[-1]\
            .extract().strip() == "Regular Season"
