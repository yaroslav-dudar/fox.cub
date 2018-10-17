
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import time
import random

import urllib.request
from datetime import datetime

import pymongo
from bson.objectid import ObjectId

import lxml.html

from config import Config

DEFUALT_LEAGUES = ['Premier League England', 'EFL Championship', 'Bundesliga']

class Downloader:

    team_name = "football_1xbet_name"
    site = "https://1xbet.com/en/line/Football"

    events_list = "//div[@id='games_content']//div[contains(@class, 'c-events__item_col')]"
    team_names = ".//span[@class='c-events__teams']//span[@class='c-events__team']/text()"
    odds_list = ".//div[@class='c-bets']/a/text()"
    event_date = ".//div[contains(@class, 'c-events__time')]/span/text()"

    HOME_WIN_IDX = 0
    DRAW_IDX = 1
    AWAY_WIN_IDX = 2
    TOTAL_OVER_IDX = 6
    TOTAL_IDX = 7
    TOTAL_UNDER_IDX = 8

    now = datetime.utcnow()

    useragent = 'Mozilla/5.0 (X11; Linux x86_64)' +\
        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    proxy_list = ['58.27.244.42:41719']

    def __init__(self, leagues=DEFUALT_LEAGUES):
        self.config = Config()

        self.client = pymongo.MongoClient(
            self.config['database']['host'],
            self.config['database']['port'])

        self.league_pages = {
            DEFUALT_LEAGUES[0]: self.site + "/88637-England-Premier-League/"
        }

        self.html_pages = {}

    def get_proxy(self):
        """ Get proxy host """

        return random.choice(self.proxy_list)

    def request(self, url):
        """ Set proxy host and send request to URL """

        req = urllib.request.Request(url)
        req.add_header('User-Agent', self.useragent)

        req.set_proxy(self.get_proxy(), 'https')
        req.set_proxy(self.get_proxy(), 'http')

        resp = urllib.request.urlopen(req)
        return resp.read().decode('utf-8')

    def download(self):
        """ Download html page with odds fron 1xbet site """

        for l in self.league_pages:
            html = self.request(self.league_pages[l])
            self.html_pages[l] = html

    def get_event_date(self, str_date):
        """
        Args:
            str_date (str): Event date in format {day.month Hours:Minutes}

        """
        date = datetime.strptime(str_date, '%d.%m %H:%M')

        # get event year
        year = self.now.year+1 if date.month < self.now.month else self.now.year
        return date.replace(year=year)

    def parse_html_page(self, tournament=DEFUALT_LEAGUES[0]):
        """ Fetch events with teams and odds from html page """

        html_tree = lxml.html.fromstring(self.html_pages[tournament])
        events = html_tree.xpath(self.events_list)

        parsed_ev = []
        for ev in events:
            teams = ev.xpath(self.team_names)
            date = ev.xpath(self.event_date)[0].strip()
            odds = ev.xpath(self.odds_list)

            parsed_ev.append({
                "home_team": teams[0].strip(),
                "away_team": teams[1].strip(),
                "event_date": self.get_event_date(date),
                "odds": {
                    "home_win": float(odds[self.HOME_WIN_IDX].strip()),
                    "draw": float(odds[self.DRAW_IDX].strip()),
                    "away_win": float(odds[self.AWAY_WIN_IDX].strip()),
                    "total": float(odds[self.TOTAL_IDX].strip()),
                    "total_under": float(odds[self.TOTAL_UNDER_IDX].strip()),
                    "total_over": float(odds[self.TOTAL_OVER_IDX].strip()),
                    "scraping_date": self.now
                }
            })

        return parsed_ev

    def upload(self, tournament=DEFUALT_LEAGUES[0]):
        """ Move data from csv to DB """

        teams = list(self.client.fox_cub.team.find())

        # get tournament id from DB
        tournament_id = str(self.client.fox_cub.tournament.\
            find_one({"name": tournament})["_id"])

        for ev in self.parse_html_page(tournament):
            try:
                team = next(filter(lambda t: t[self.team_name] == ev["home_team"], teams))
                opponent = next(filter(lambda t: t[self.team_name] == ev["away_team"], teams))
            except StopIteration as e:
                continue
            
            team_id = str(team["_id"])
            opponent_id = str(opponent["_id"])

            filter_query = {
                "home_team": team_id,
                "away_team": opponent_id,
                "tournament": tournament_id,
                "event_date": ev['event_date'],
            }

            push_odds = {"$push": {"odds": ev['odds']}}
            try:
                self.client.fox_cub.game_odds.update(filter_query, push_odds, upsert=True)
            except Exception as err:
                print(err)


if __name__ == "__main__":
    d = Downloader()
    d.download()
    d.upload()

    d.client.close()
