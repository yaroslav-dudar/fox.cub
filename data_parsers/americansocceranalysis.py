#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json

import urllib.request
import requests

from datetime import datetime

import pymongo

import lxml.html
from config import Config

class Downloader:

    season = "2019"

    games_list = "//table[@class='tablesorter']//tr"
    game_details = ".//td[@align='center']/text()"

    useragent = 'Mozilla/5.0 (X11; Linux x86_64)' +\
        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

    html = {
        'HOME_TEAM': 1,
        'AWAY_TEAM': 5,
        'HOME_TEAM_SCORE': 2,
        'AWAY_TEAM_SCORE': 6,
        'DATE': 0,
        'HOME_TEAM_XG': 3,
        'AWAY_TEAM_XG': 7,
    }

    def __init__(self):
        self.global_conf = Config()
        self.config = self.global_conf['americansocceranalysis_parser']
        self.db_conf = self.global_conf['database']

        self.client = pymongo.MongoClient(
            self.db_conf['host'],
            self.db_conf['port']
        )
        self.db = self.client[self.db_conf['db_name']]

        self.proxy = "3.0.239.184:3128"
        self.html_result = None

    def request(self, url):
        """ Set proxy host and send request to URL """

        proxies = {
            'http': 'http://' + self.proxy,
            'https': 'http://' + self.proxy,
        }

        print(self.proxy)
        return requests.get(url, headers={'User-Agent': self.useragent}, proxies=proxies).text

    def download(self):
        """ Download html page with by game xG statistics """

        url = "https://www.americansocceranalysis.com/by-game-" + self.season
        self.html_result = self.request("https://www.americansocceranalysis.com/by-game-2019")
        print(self.html_result)

    def parse_html(self):
        html_tree = lxml.html.fromstring(self.html_result)
        games = html_tree.xpath(self.games_list)

        for game in games:
            detailed = game.xpath(self.game_details)
            if not detailed: continue
            print(detailed[self.html['HOME_TEAM']], " - ", detailed[self.html['AWAY_TEAM']])

    def add_game(self, game):
        """ Add game to DB if it is not found"""
        pass

    def get_team_by_name(self, id):
        return next(filter(lambda t: t.get(self.config["find_team_by"]) == id, self.teams))

    def get_game(self, team_name, opponent_name, venue, date):
        pass

if __name__ == "__main__":
    d = Downloader()
    d.download()
    d.parse_html()

    d.client.close()
