
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

class Downloader:

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

    def __init__(self):
        self.global_conf = Config()
        self.config = self.global_conf['1xbet_parser']
        self.db_conf = self.global_conf['database']

        self.client = pymongo.MongoClient(
            self.db_conf['host'],
            self.db_conf['port']
        )
        self.db = self.client[self.db_conf['db_name']]

        self.html_pages = {}
        self.proxy = "131.108.6.118:50435"

    def request(self, url):
        """ Set proxy host and send request to URL """

        req = urllib.request.Request(url)
        req.add_header('User-Agent', self.useragent)

        print(self.proxy)
        req.set_proxy(self.proxy, 'https')
        req.set_proxy(self.proxy, 'http')

        resp = urllib.request.urlopen(req)
        return resp.read().decode('utf-8')

    def download(self):
        """ Download html page with odds fron 1xbet site """

        for l in self.config['tournaments_list']:
            html = self.request(self.config['tournaments_list'][l])
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

    def parse_html_page(self, tournament):
        """ Fetch events with teams and odds from html page """

        html_tree = lxml.html.fromstring(self.html_pages[tournament])
        events = html_tree.xpath(self.events_list)

        parsed_ev = []
        for ev in events:
            teams = ev.xpath(self.team_names)
            date = ev.xpath(self.event_date)[0].strip()
            odds = ev.xpath(self.odds_list)

            home_win = odds[self.HOME_WIN_IDX].strip()
            draw = odds[self.DRAW_IDX].strip()
            away_win = odds[self.AWAY_WIN_IDX].strip()
            total = odds[self.TOTAL_IDX].strip()
            total_under = odds[self.TOTAL_UNDER_IDX].strip()
            total_over = odds[self.TOTAL_OVER_IDX].strip()

            parsed_ev.append({
                "home_team": teams[0].strip(),
                "away_team": teams[1].strip(),
                "event_date": self.get_event_date(date),
                "odds": {
                    "home_win": float(home_win) if home_win != "-" else None,
                    "draw": float(draw) if draw != "-" else None,
                    "away_win": float(away_win) if away_win != "-" else None,
                    "total": float(total) if total != "-" else None,
                    "total_under": float(total_under) if total_under != "-" else None,
                    "total_over": float(total_over) if total_over != "-" else None,
                    "scraping_date": self.now
                }
            })

        return parsed_ev

    def upload(self, tournament):
        """
        Upload parsed data to Database

        Raises:
            ServerSelectionTimeoutError: DB server query timeout
        """

        teams = list(self.db[self.db_conf['collections']['team']].find())

        # get tournament id from DB
        tournament_id = str(self.db[self.db_conf['collections']['tournament']].\
            find_one({"name": tournament})["_id"])

        for ev in self.parse_html_page(tournament):
            try:
                team = next(filter(lambda t: t[self.config["find_team_by"]] == ev["home_team"], teams))
                opponent = next(filter(lambda t: t[self.config["find_team_by"]] == ev["away_team"], teams))
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
            print(ev['odds'])
            try:
                self.db[self.db_conf['collections']['odds']].\
                    update(filter_query, push_odds, upsert=True)
            except Exception as err:
                print(err)


if __name__ == "__main__":
    d = Downloader()
    d.download()

    for tournament in d.config['tournaments_list']:
        d.upload(tournament)

    d.client.close()
