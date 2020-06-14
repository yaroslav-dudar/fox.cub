# -*- coding: utf-8 -*-
"""
This module collect actual fixtures within given window
and update statistics
"""

from gevent import monkey
monkey.patch_all()

import gevent.pool
import pymongo

from datetime import datetime
import time
import itertools

from models import (
    Fixture as FixtureModel, Odds, Tournament,
    Team, MongoClient, Pinnacle)


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
    open_fixtures = FixtureModel.get_not_started()

    ext_ids = [f['external_ids'] for f in open_fixtures]
    flatten_ids = list(itertools.chain.from_iterable(ext_ids))

    odds = Odds.get_line_diff(flatten_ids)

    for f in open_fixtures:
        modify_fixture_stats(f, odds)

    fixtures_with_stats = filter(lambda f: f.get('open') and f.get('close'),
                                 open_fixtures)

    FixtureModel.bulk_write_stats(list(fixtures_with_stats))
    print("Execution time: {}".format(time.time() - start_at))
