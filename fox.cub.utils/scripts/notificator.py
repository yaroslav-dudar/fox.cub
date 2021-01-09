# -*- coding: utf-8 -*-
"""
This module creates notifications, described market changes and movement
"""

from bson.codec_options import TypeCodec

from typing import List, Dict
from datetime import datetime
from enum import Enum

import models

class NotificationType(Enum):
    SPREAD    = 'spread'
    TOTAL     = 'total'
    MONEYLINE = 'moneyline'
    FIXTURE   = 'fixture'


class LineDelta:

    def __init__(self, prev_price: float, new_price: float,
                 delta: float, line: str, line_type: NotificationType):
        self.delta = round(delta * 100, 2) # line diff in %
        self.prev_price = prev_price
        self.new_price = new_price
        self.line = line # line naming
        self.line_type: NotificationType = line_type

    def __repr__(self):
        return ('LineDelta(new_price={0}, prev_price={1},' +\
               ' delta={2}, line={3}, line_type={4})').\
               format(self.new_price, self.prev_price,
                      self.delta, self.line, self.line_type)


class LineDeltaCodec(TypeCodec):
    python_type = LineDelta    # the Python type acted upon by this type codec
    bson_type = str   # the BSON type acted upon by this type codec

    def transform_python(self, value):
        """Function that transforms a custom type value into a type
        that BSON can encode."""
        return str(value)

    def transform_bson(self, value):
        """Function that transforms a vanilla BSON type value into our
        custom type."""
        return value


class Notificator:

    threshold = 0.03 # 3%
    total_field = "under"

    def compare_moneyline(self, old_moneyline: dict, new_moneyline: dict):
        for bet in old_moneyline.keys():
            delta = self.get_chance(old_moneyline, bet) -\
                    self.get_chance(new_moneyline, bet)

            if abs(delta) >= self.threshold:
                return [LineDelta(old_moneyline[bet], new_moneyline[bet],
                        delta, bet, NotificationType.MONEYLINE)]

        return []


    def get_chance(self, line, bet):
        """ Returns event probability from 0 to 1"""
        return 1/line[bet] if line[bet] else 0


    def find_total(self, totals: list, points: float):
        """ Find and return individual total line in totals list"""

        return next((t for t in totals if t['points'] == points), None)


    def compare_totals(self, old_totals: dict, new_totals: dict):
        assert len(old_totals) > 0 and len(new_totals) > 0

        for old_total in old_totals:
            new_total = self.find_total(new_totals, old_total['points'])
            if new_total:
                delta = self.get_chance(old_total, self.total_field) -\
                        self.get_chance(new_total, self.total_field)
                line_name = '{0} {1}'.format(self.total_field, old_total['points'])

                if abs(delta) >= self.threshold:
                    return [LineDelta(old_total[self.total_field],
                                      new_total[self.total_field], delta,
                                      line_name, NotificationType.TOTAL)]
                else:
                    return []

        return []


    def verify(self, old_odds: dict, new_odds: dict):
        old_keys = old_odds.keys()
        new_keys = new_odds.keys()
        assert old_keys == new_keys


    def process_new_odds(self, fixture: dict, new_odds: dict):
        """
        Process new odds for a given fixture and
        generate notification if needed. Generate diff based on prev
        notification, if not exists - use open line
        """

        if self.is_new_fixture(fixture):
            return self.process_new_fixture(fixture, fixture['open'])

        if fixture.get('notification'):
            old_odds = fixture['notification']['odds']
        else:
            old_odds = fixture['open']

        m_delta = self.compare_moneyline(old_odds["moneyline"],
                                         new_odds["moneyline"])
        t_delta = self.compare_totals(old_odds["totals"],
                                      new_odds["totals"])

        return [self.create_notification(fixture, new_odds, delta)
                for delta in m_delta + t_delta]


    def is_new_fixture(self, fixture: dict):
        """ Check if fixture has only one odd record """
        return str(fixture['open']['_id']) == str(fixture['close']['_id'])


    def process_new_fixture(self, fixture: dict, odds: dict):
        """ Process input fixture and generate notification if needed """

        # TODO: check if notification required
        return [self.create_notification(fixture, odds)]


    def create_notification(self, fixture, odds, linedelta: LineDelta=None):
        return models.Notification.get_document(linedelta, odds, datetime.utcnow())
