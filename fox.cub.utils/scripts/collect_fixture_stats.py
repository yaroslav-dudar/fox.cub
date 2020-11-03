# -*- coding: utf-8 -*-
"""
This module collect actual fixtures within given window
and update statistics
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

from utils import str2datetime, init_logger
from models import (
    Fixture as FixtureModel, Odds, Tournament,
    Team, MongoClient, Pinnacle)


str2datetime.TIME_FORMAT = "%d/%m/%Y %H:%M:%S"
START_TIME_DEFAULT = datetime.utcnow() - timedelta(days=1)
END_TIME_DEFAULT = datetime.utcnow() + timedelta(days=3)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-start', default=START_TIME_DEFAULT, type=str2datetime,
                        help='Collect stats for fixtures from this date. Ignored data transfered via stdin')
    parser.add_argument('-end', default=END_TIME_DEFAULT, type=str2datetime,
                        help='Collect stats for fixtures to this date. Ignored data transfered via stdin')
    return parser.parse_args()


def modify_fixture_stats(fixture: dict, odds: list):
    """ Receive list of odds with different external ids.
        Find odds belongs to a single fixture and find open/close line"""

    find_odds = lambda o: o['_id'] in fixture['external_ids']
    fixture_odds = []
    for line in filter(find_odds, odds):
        fixture_odds.extend([line['open'], line['close']])

    if len(fixture_odds) < 2: return False

    fixture_odds.sort(key=lambda o: o['date'])
    fixture['open'] = fixture_odds[0]
    fixture['close'] = fixture_odds[-1]
    print(fixture, fixture_odds)
    print("="*50)
    return True


if __name__ == '__main__':
    start_at = time.time()

    args = parse_args()
    logger = init_logger()
    io_ops = select.select([sys.stdin], [], [], 2)

    if io_ops[0]:
        stdin = io_ops[0][0].buffer.read()
        input_data = pickle.loads(stdin)
        ids = [f['fixture_id'] for f in input_data.odds]
        fixtures = FixtureModel.get_by_ext_id(ids)
    else:
        logger.warning("No stdin received, staring script in time range mode.")
        fixtures = FixtureModel.get_in_range(args.start, args.end)

    ext_ids = [f['external_ids'] for f in fixtures]
    flatten_ids = list(itertools.chain.from_iterable(ext_ids))

    odds = Odds.get_line_diff(flatten_ids)
    for f in fixtures:
        modify_fixture_stats(f, odds)

    fixtures_with_stats = filter(lambda f: f.get('open') and f.get('close'),
                                 fixtures)

    #res = FixtureModel.bulk_write_stats(list(fixtures_with_stats))
    logger.info("Stats collection finished: {}. Execution time: {}"
        .format(res.bulk_api_result, time.time() - start_at))


class Notification:

    def compare_moneyline(self, old_line: dict, new_line: dict):
        pass

    def compare_totals(self, old_line: dict, new_line: dict):
        pass

    def compare(self, old_line: dict, new_line: dict):
        old_keys = old_line.keys()
        new_keys = new_line.keys()
        assert old_keys == new_keys



