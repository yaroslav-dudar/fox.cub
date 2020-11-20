# -*- coding: utf-8 -*-
"""
This module creates notifications, described market changes and movement
"""

from typing import List, Dict
from models import Notification

from datetime import datetime
from enum import Enum

class NotificationType(Enum):
    SPREAD    = 'spread'
    TOTAL     = 'total'
    MONEYLINE = 'moneyline'
    FIXTURE   = 'fixture'


class LineDelta:

    def __init__(self, delta, line, line_type: NotificationType):
        self.delta = delta # line diff in #
        self.line = line # line naming
        self.line_type: NotificationType = line_type

    def __repr__(self):
        return 'LineDelta(delta={0},line={1},line_type={2})'.\
            format(self.delta, self.line, self.line_type)


class Notificator:

    threshold = 0.03 # 3%
    total_field = "under"

    def compare_moneyline(self, old_moneyline: dict, new_moneyline: dict):
        for field in old_moneyline.keys():
            delta = 1/old_moneyline[field] - 1/new_moneyline[field]

            if abs(delta) >= self.threshold:
                return [LineDelta(delta, field, NotificationType.MONEYLINE)]

        return []


    def find_total(self, totals: list, points: float):
        """ Find and return individual total line in totals list"""

        return next((t for t in totals if t['points'] == points), None)


    def compare_totals(self, old_totals: dict, new_totals: dict):
        assert len(old_totals) > 0 and len(new_totals) > 0

        for old_total in old_totals:
            new_total = self.find_total(new_totals, old_total['points'])
            if new_total:
                delta = 1/old_total[self.total_field] -\
                    1/new_total[self.total_field]

                if abs(delta) >= self.threshold:
                    return [LineDelta(delta, self.total_field, NotificationType.TOTAL)]
                else:
                    return []

        return []


    def verify(self, old_odds: dict, new_odds: dict):
        old_keys = old_odds.keys()
        new_keys = new_odds.keys()
        assert old_keys == new_keys


    def process_new_odds(self, fixture: dict, new_odds: dict,
                        prev_notification: dict = None):
        """ Process new odds for a given fixture and
        generate notification if needed """

        if prev_notification:
            old_odds = prev_notification['odds']
        else:
            old_odds = fixture['open']

        m_delta = self.compare_moneyline(old_odds["moneyline"],
                                         new_odds["moneyline"])
        t_delta = self.compare_totals(old_odds["totals"],
                                      new_odds["totals"])

        return [self.create_notification(fixture, new_odds, delta)
                for delta in m_delta + t_delta]


    def process_new_fixture(self, fixture: dict, odds: dict):
        """ Process input fixture and generate notification if needed """

        # TODO: check if notification required
        return [self.create_notification(fixture, odds)]


    def create_notification(self, fixture, odds, linedelta: LineDelta=None):
        type_text_pattern = "NOTIFICATION TYPE - [{0}]."
        fixture_text = "[{0}] {1} - {2}.".format(fixture["tournament_name"],
                                             fixture["home_name"],
                                             fixture["away_name"])
        if not linedelta:
            type_text  = type_text_pattern.format(NotificationType.FIXTURE.value)
            delta_text = ''
        else:
            type_text  = type_text_pattern.format(linedelta.line_type.value)
            delta_text = '[{0}] moved by [{1}]'.format(linedelta.line, linedelta.delta)

        text = " ".join([type_text, fixture_text, delta_text])
        return Notification.get_document(text, odds, datetime.utcnow())
