# -*- coding: utf-8 -*-
"""
This module collect actual fixtures within given window
and update statistics. Generate notifications to show recent changes
and market movements
"""

from gevent import monkey
monkey.patch_all()

import gevent.pool
import pymongo
import sys
import pickle
import select

import argparse
from datetime import datetime, timedelta
import time
import itertools
from typing import Optional

from utils import str2datetime, init_logger, SharedDataObj
from scripts.notificator import Notificator
from messenger import BaseMessenger, messenger_factory

from models import (
    Fixture as FixtureModel, Odds, Tournament,
    Team, MongoClient, Pinnacle, Notification)


logger = init_logger()
str2datetime.TIME_FORMAT = "%d/%m/%Y %H:%M:%S"
START_TIME_DEFAULT = datetime.utcnow() - timedelta(days=1)
END_TIME_DEFAULT = datetime.utcnow() + timedelta(days=3)


def flatten_list(lst: list):
    return list(itertools.chain.from_iterable(lst))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-start', default=START_TIME_DEFAULT, type=str2datetime,
                        help='Collect stats for fixtures from this date. Ignored data transfered via stdin')
    parser.add_argument('-end', default=END_TIME_DEFAULT, type=str2datetime,
                        help='Collect stats for fixtures to this date. Ignored data transfered via stdin')
    parser.add_argument('-test', default=False, action='store_true',
                        help='Disable write to DB.')
    parser.add_argument('-messenger', default=None, type=messenger_factory,
                        help='Enable messenger notifications')
    return parser.parse_args()


def read_stdin() -> Optional[SharedDataObj]:
    """ Read stdin and parse it as python SharedDataObj object """
    io_ops = select.select([sys.stdin], [], [], 2)

    if io_ops[0]:
        stdin = io_ops[0][0].buffer.read()
        return pickle.loads(stdin)

    return None


class FixtureDelta:

    def __init__(self, fixture):
        self.fixture = fixture
        self.odds = []

    def add_line(self, line):
        self.odds.extend([line['open'], line['close']])


class DeltaProcessor:

    def __init__(self, start, end,
                 messenger: Optional[BaseMessenger],
                 shared_data: Optional[SharedDataObj]):
        self.start = start
        self.end = end
        self.shared_data = shared_data
        self.notificator = Notificator()
        self.init_data()
        self.messenger = messenger


    def init_data(self):
        if self.shared_data:
            ids = [f['fixture_id'] for f in self.shared_data.odds]
            # find fixtures which odds are changed
            self.fixtures = FixtureModel.get_by_ext_id(ids)
            # new fixtures
            self.new_fixtures = self.shared_data.fixtures
        else:
            logger.warning("No stdin received, staring script in time range mode.")
            self.fixtures = FixtureModel.get_in_range(self.start, self.end)

        self.get_odds_diff()


    def modify_fixture_stats(self):
        """ Update open/close lines in fixtures """

        fixtures_odds = {tuple(f['external_ids']): FixtureDelta(f)
                         for f in self.fixtures}
        res_fixtures = []
        ids = list(fixtures_odds.keys())
        for line in self.odds_diff:
            result = next((i for i in ids if line["_id"] in i), None)
            if result:
                fixtures_odds[result].add_line(line)

        for delta in fixtures_odds.values():
            if len(delta.odds) < 2: continue

            delta.odds.sort(key=lambda o: o['date'])
            delta.fixture['open'] = delta.odds[0]
            delta.fixture['close'] = delta.odds[-1]
            res_fixtures.append(delta.fixture)

        return res_fixtures


    def write_fixtures(self, fixtures: list):
        return FixtureModel.bulk_write(fixtures,
                                       FixtureModel.BULK_WRITE_ALLOWED)


    def get_odds_diff(self):
        """ Find open/close line for fixtures which odds are moved """
        ext_ids = [f['external_ids'] for f in self.fixtures]
        flatten_ids = flatten_list(ext_ids)
        self.odds_diff = Odds.get_line_diff(flatten_ids)


    def generate_notification(self, fixture):
        fixture_notifications = self.notificator.\
            process_new_odds(fixture, fixture['close'])

        if fixture_notifications:
            fixture['notification'] = fixture_notifications[0]

        for n in fixture_notifications:
            logger.info(n['text'])

            if self.messenger:
                self.messenger.send_message(n['text'])


if __name__ == '__main__':
    start_at = time.time()
    args = parse_args()
    shared_data = read_stdin()

    processor = DeltaProcessor(args.start, args.end,
                               args.messenger, shared_data)
    fixtures = processor.modify_fixture_stats()
    for f in fixtures:
        processor.generate_notification(f)

    res = processor.write_fixtures(fixtures)
    logger.info("Stats collection finished: {}. Execution time: {}"
        .format(res.bulk_api_result, time.time() - start_at))
