import betfairlightweight
from betfairlightweight import filters
from betfairlightweight.resources.bettingresources import (
    MarketCatalogue, MarketBook, RunnerCatalogue)

from datetime import datetime
from itertools import zip_longest
from typing import List, Dict
from collections import defaultdict

import re
import argparse
import queue
import threading
import time

from utils import init_logger, League
from models import (
    Fixture as FixtureModel, Odds, Tournament,
    Team, MongoClient)


class BetfairMarket:

    def __init__(self, book: MarketBook, catalogue: MarketCatalogue):
        self.book = book
        self.catalogue = catalogue


class BerfairApi:

    BETFAIE_EVENT_NAME_PATTERN = property(lambda self: re.compile(r'(.+) v (.+)'))
    TEST_COMPETITION_IDS       = property(lambda self: [10932509])
    FOOTBALL_COMPETITION_IDS   = property(lambda self: [10932509, 7129730, 10020873,
                                                         2005, 81, 61, 59, 117, 141, 228])
    ESPORT_COMPETITION_IDS     = property(lambda self: [11426307, 10817924, 10797727, 11638775, 11622201])
    FIND_TOURN_BY              = property(lambda self: 'betfair_id')
    FIND_TEAM_BY               = property(lambda self: 'name')

    SPREAD_MARKET              = property(lambda self: 'Asian Handicap')
    MONEYLINE_MARKET           = property(lambda self: 'Match Odds')
    TOTALS_MARKET              = property(lambda self: 'Over/Under 2.5 Goals')

    def __init__(self, username, password, app_key):

        self.api = betfairlightweight.APIClient(username, password, app_key=app_key)
        self.api.login_interactive()

        self.leagues_list, self.last_since_id = {}, {}
        self.init_data()
        self.logger = init_logger()
        self.grouped_books = []

        self.football_filter = filters.market_filter(
            event_type_ids=[1],  # filter on just soccer
            competition_ids=self.FOOTBALL_COMPETITION_IDS,
            market_type_codes=["OVER_UNDER_25", "MATCH_ODDS", "ASIAN_HANDICAP"]
        )

        self.esports_filter = filters.market_filter(
            event_type_ids=[27454571],  # filter on esports
            competition_ids=self.ESPORT_COMPETITION_IDS,
            market_type_codes=["MATCH_ODDS"],  # filter on just odds market types
        )

        self.default_market_projection = [
            #"RUNNER_DESCRIPTION",
            "COMPETITION",
            "EVENT",
            "EVENT_TYPE",
            #"MARKET_DESCRIPTION",
            "MARKET_START_TIME",
        ]


    def init_data(self):
        # upload tournaments and teams from DB
        for l_id in self.FOOTBALL_COMPETITION_IDS:
            tournament = Tournament.get(l_id, self.FIND_TOURN_BY)

            if not tournament:
                self.leagues_list[l_id] = None
            else:
                t_id = str(tournament['_id'])
                self.leagues_list[l_id] = League(t_id, Team.find(t_id))


    def grouper(self, iterable, n, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)


    def get_runner_price(self, runner):
        """ Get runners price """
        if runner.ex.available_to_back:
            return runner.ex.available_to_back[0].price
        # price not found
        return None


    def get_event_odds(self, markets: List[BetfairMarket]):
        """ Recieve list of books for a single event and return odds object """
        moneyline, spreads, totals = None, None, None
        event_id = markets[0].catalogue.event.id

        for m in markets:
            if m.catalogue.market_name == self.SPREAD_MARKET:
                spreads = self.parse_spreads(m.book)
            elif m.catalogue.market_name == self.TOTALS_MARKET:
                totals = self.parse_totals(m.book)
            elif m.catalogue.market_name == self.MONEYLINE_MARKET:
                moneyline = self.parse_moneyline(m.book)

        return Odds.get_document(event_id,
                                 datetime.utcnow(),
                                 spreads,
                                 moneyline,
                                 totals)


    def parse_moneyline(self, book: MarketBook):
        """ Fetch 1X2 (moneyline) price from market """
        moneyline = {"home": self.get_runner_price(book.runners[0]),
                     "away": self.get_runner_price(book.runners[1]),
                    }

        if len(book.runners) > 2:
            draw_price = self.get_runner_price(book.runners[2])
        else:
            draw_price = None

        moneyline["draw"] = draw_price
        return moneyline


    def parse_spreads(self, book: MarketBook):
        """ Fetch asian handicap price from market """
        spreads, handicaps = [], [-2.5, -1.5, -1]
        # group runners by handicap
        runners = self.grouper(book.runners, 2)

        for hdp in handicaps:
            spread = self.find_spread(hdp, runners)
            if spread: spreads.append(spread)

        return spreads


    def find_spread(self, handicap: float, runners: list):
        for r in runners:
            if r[0].handicap == handicap:
                return { "hdp" : handicap,
                         "home" : self.get_runner_price(r[0]),
                         "away" : self.get_runner_price(r[1]) }


    def parse_totals(self, book: MarketBook):
        """ Fetch total goals price from market """
        totals = [{ "points" : 2.5,
                    "under"  : self.get_runner_price(book.runners[0]),
                    "over"   : self.get_runner_price(book.runners[1])  }]
        return totals


    def group_by_event(self, market_books: List[MarketBook],
                       markets: Dict[str, MarketCatalogue]):
        """ Grouping market books with market catalogue by event id"""

        groups = defaultdict(list)
        for market_book in market_books:
            catalogue = markets[market_book.market_id]
            item = BetfairMarket(market_book, catalogue)
            groups[catalogue.event.id].append(item)

        return groups


    def request_market_books(self, market_catalogue: List[MarketCatalogue]):
        """
        Fetch list of market books by a given market catalogue(s)
        Rate Limits:
        sum(Weight) * number market ids must not exceed 200 points per requests
        EX_BEST_OFFERS equals to 5 points
        """
        market_ids_block = self.grouper([i.market_id for i in market_catalogue], 40)

        market_books = []
        for market_ids in market_ids_block:
            market_books.extend(self.api.betting.list_market_book(
                market_ids=market_ids,
                price_projection=filters.price_projection(
                    price_data=filters.price_data(ex_best_offers=True)
                ),
            ))

        return market_books


    def get_odds(self, market_catalogue: List[MarketCatalogue]):
        """ Request MarketBooks via polling Betfair API"""
        markets = {m.market_id: m for m in market_catalogue}
        market_books = self.request_market_books(market_catalogue)
        market_groups = self.group_by_event(market_books, markets)

        for group in market_groups.values():
            document = self.get_event_odds(group)
            print(group[0].catalogue.json())
            print(document)
            print("="*50)


    def request_market_catalogue(self, market_projection=None, market_filter=None):
        """ Make MarketCatalogue request and fetch event data """

        if not market_projection:
            market_projection = self.default_market_projection

        if not market_filter:
            market_filter = self.football_filter

        return self.api.betting.list_market_catalogue(
            market_projection=market_projection,
            filter=market_filter,
            max_results=1000,
        )


    def get_fixture(self, market_catalogue: List[MarketCatalogue]):
        """ Fetch betfair events from a given market catalogue(s) """
        events = set()
        for ev in market_catalogue:
            if ev.event.id in events:
                continue

            events.add(ev.event.id)
            home, away = self.get_home_away_teams(ev.event.name)

            home_id, away_id, tournament_id = self.\
                get_fixture_ids(home, away, ev)

            document = FixtureModel.get_document(
                ev.event.id, home, away,
                ev.market_start_time,
                ev.competition.name, home_id, away_id,
                tournament_id)

            print(document)
            print('='*25)


    def get_home_away_teams(self, event_name):
        """ Fetching team names from betfair event name
            Example: Everton v Man U
        """
        m = self.BETFAIE_EVENT_NAME_PATTERN.match(event_name)
        try:
            return m.group(1), m.group(2)
        except IndexError:
            return None, None


    def get_fixture_ids(self, home: str, away: str, fixture: MarketCatalogue):
        """ Fetch Fox.Cub DB ids (home, away, tournament) for a given fixture
        Args:
            competition_id (int): Betfair competition Id
            fixture: Betfair MarketCatalogue object
        """

        home_id, away_id, tournament_id = None, None, None
        tournament = self.leagues_list[int(fixture.competition.id)]

        if tournament:
            tournament_id = tournament.t_id
            home_id = Team.get_id(home,
                                  self.FIND_TEAM_BY,
                                  tournament.teams)
            away_id = Team.get_id(away,
                                  self.FIND_TEAM_BY,
                                  tournament.teams)

        return home_id, away_id, tournament_id


    def create_stream(self, output_queue, market_ids):
        """ Create Betfair stream that allow to establish
            connection once and receive MarketBook updates in real time
        """
        # create stream listener
        listener = betfairlightweight.StreamListener(output_queue=output_queue)

        # create stream
        stream = self.api.streaming.create_stream(listener=listener)

        market_filter = filters.streaming_market_filter(
            market_ids=market_ids
        )
        market_data_filter = filters.streaming_market_data_filter(
            fields=["EX_BEST_OFFERS", "EX_MARKET_DEF"], ladder_levels=3
        )

        # subscribe
        streaming_unique_id = stream.subscribe_to_markets(
            market_filter=market_filter,
            market_data_filter=market_data_filter,
            conflate_ms=2000,  # send update every 1000ms
        )

        return stream

    def parse_market_change(self, msgs: List[MarketBook]):
        pass


    def start_stream(self, stream):
        """ Betfair stream, simple error handling """
        while True:
            try:
                self.logger.info("Starting Betfair stream ...")
                stream.start()
            except betfairlightweight.exceptions.SocketError as err:
                self.logger.warning(err)
                time.sleep(5.0)


    def listen_stream(self, output_queue):
        while True:
            market_books = output_queue.get()
            print(market_books)

            for market_book in market_books:
                print(
                    market_book,
                    market_book.streaming_unique_id,  # unique id of stream (returned from subscribe request)
                    market_book.streaming_update,  # json update received
                    market_book.market_definition.event_id,
                    market_book.publish_time,  # betfair publish time of update
                )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', required=True, type=str,
                        help='Betfair user ID.')
    parser.add_argument('-p', required=True, type=str,
                        help='Betfair Password')
    parser.add_argument('-k', required=True, type=str,
                        help='Betfair application key')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    betfair = BerfairApi(args.u, args.p, args.k)
    market_catalogue = betfair.\
        request_market_catalogue(None, betfair.football_filter)

    #betfair.get_fixture(market_catalogue)
    #betfair.get_odds(market_catalogue)

    stream_queue = queue.Queue()
    market_ids = [i.market_id for i in market_catalogue]
    stream = betfair.create_stream(stream_queue, market_ids)

    t = threading.Thread(target=betfair.start_stream, args=(stream,), daemon=True, )
    t.start()

    betfair.listen_stream(stream_queue)

