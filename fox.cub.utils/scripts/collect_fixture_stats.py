# -*- coding: utf-8 -*-
"""
This module collect actual fixtures within given window
and update statistics
"""

from gevent import monkey
monkey.patch_all()

import gevent.pool
import pymongo

import argparse
from datetime import datetime, timedelta
import time
import itertools

from utils import str2datetime
from models import (
    Fixture as FixtureModel, Odds, Tournament,
    Team, MongoClient, Pinnacle)


str2datetime.TIME_FORMAT = "%d/%m/%Y %H:%M:%S"
START_TIME_DEFAULT = datetime.utcnow() - timedelta(days=7)
END_TIME_DEFAULT = datetime.utcnow() + timedelta(days=14)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-start', default=START_TIME_DEFAULT, type=str2datetime,
                        help='Collect stats for fixtures from this date')
    parser.add_argument('-end', default=END_TIME_DEFAULT, type=str2datetime,
                        help='Collect stats for fixtures to this date')
    return parser.parse_args()


def modify_fixture_stats(fixture: dict, odds: list):
    """Receive list of odds with different external ids.
        Find odds belongs to a single fixture and find open/close line"""

    find_odds = lambda o: o['_id'] in fixture['external_ids']
    fixture_odds = []
    for line in filter(find_odds, odds):
        fixture_odds.extend([line['open'], line['close']])

    if len(fixture_odds) < 2: return False

    fixture_odds.sort(key=lambda o: o['date'])
    f['open'] = fixture_odds[0]
    f['close'] = fixture_odds[-1]
    return True


if __name__ == '__main__':
    start_at = time.time()

    args = parse_args()
    open_fixtures = FixtureModel.get_in_range(args.start, args.end)

    ext_ids = [f['external_ids'] for f in open_fixtures]
    flatten_ids = list(itertools.chain.from_iterable(ext_ids))

    odds = Odds.get_line_diff(flatten_ids)

    for f in open_fixtures:
        modify_fixture_stats(f, odds)

    fixtures_with_stats = filter(lambda f: f.get('open') and f.get('close'),
                                 open_fixtures)

    FixtureModel.bulk_write_stats(list(fixtures_with_stats))
    print("Stats collection finished. Execution time: {}"
        .format(time.time() - start_at))
