# -*- coding: utf-8 -*-
"""
This module cleanup deprecated odds
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
START_TIME_DEFAULT = datetime.min
END_TIME_DEFAULT = datetime.utcnow() - timedelta(weeks=8)

# TODO
# 1. Find deprecated fixtures
# 2. Find open, close lines for deprecated fixtures
# 3. Remove odds belongs to deprecated fixtures except open/close

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-start', default=START_TIME_DEFAULT, type=str2datetime,
                        help='Remove odds for fixtures from this date')
    parser.add_argument('-end', default=END_TIME_DEFAULT, type=str2datetime,
                        help='Remove odds for fixtures to this date')
    parser.add_argument('-safe', action='store_true',
                        help='Remove odds only if open/close stats collected')
    return parser.parse_args()


if __name__ == '__main__':
    start_at = time.time()

    args = parse_args()
    fixtures = FixtureModel.get_in_range(args.start,
                                         args.end,
                                         is_lite_output=False)

    ext_ids, not_remove_odds = set(), set()
    for f in fixtures:
        open_line = f.get('open', {}).get('_id')
        close_line = f.get('close', {}).get('_id')

        if args.safe and not (open_line and close_line):
            continue

        if open_line and close_line:
            not_remove_odds.update([str(open_line), str(close_line)])

        ext_ids.update(f['external_ids'])

    res = Odds.remove(list(ext_ids), not_remove_odds)
    print("Cleanup finsihed {}. Execution time: {}"
        .format(res, time.time() - start_at))
