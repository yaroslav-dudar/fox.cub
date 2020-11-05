import betfairlightweight
from betfairlightweight import filters
from betfairlightweight.resources.bettingresources import MarketCatalogue

import re
import argparse
from datetime import datetime
from itertools import zip_longest
from typing import List

from utils import init_logger, League
from models import (
    Fixture as FixtureModel, Odds, Tournament,
    Team, MongoClient)


class BerfairApi:

    BETFAIE_EVENT_NAME_PATTERN = property(lambda self: re.compile(r'(.+) v (.+)'))
    FOOTBALL_COMPETITION_IDS   = property(lambda self: [10932509, 7129730, 10020873,
                                                         2005, 81, 61, 59, 117, 141, 228])
    ESPORT_COMPETITION_IDS     = property(lambda self: [11426307, 10817924, 10797727, 11638775, 11622201])
    FIND_TOURN_BY              = property(lambda self: 'betfair_id')
    FIND_TEAM_BY               = property(lambda self: 'name')

    def __init__(self, username, password, app_key):

        self.api = betfairlightweight.APIClient(username, password, app_key=app_key)
        self.api.login_interactive()

        self.leagues_list, self.last_since_id = {}, {}
        self.init_data()
        self.logger = init_logger()

        self.football_filter = filters.market_filter(
            event_type_ids=[1],  # filter on just soccer
            competition_ids=self.FOOTBALL_COMPETITION_IDS,
            market_type_codes=["MATCH_ODDS"],  # filter on just odds market types
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

    def get_odds(self, market_catalogue: list):
        market_ids_block = self.grouper([i.market_id for i in market_catalogue], 40)
        events = {i.market_id: i.json() for i in market_catalogue}

        # sum(Weight) * number market ids must
        # not exceed 200 points per requests
        # EX_BEST_OFFERS equals to 5 points
        for market_ids in market_ids_block:
            market_books = self.api.betting.list_market_book(
                market_ids=market_ids,
                price_projection=filters.price_projection(
                    price_data=filters.price_data(ex_best_offers=True)
                ),
            )

            for market_book in market_books:
                print(events[market_book.market_id])
                # TODO: find best price
                moneyline = {"home": self.get_runner_price(market_book.runners[0]),
                             "away": self.get_runner_price(market_book.runners[1]),
                            }

                if len(market_book.runners) > 2:
                    draw_price = self.get_runner_price(market_book.runners[2])
                else:
                    draw_price = None

                moneyline["draw"] = draw_price

                document = Odds.get_document(market_book.market_id,
                                             datetime.utcnow(),
                                             None,
                                             moneyline,
                                             None)
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
        """ Fetch betfair events from a given market catalogue """

        for ev in market_catalogue:
            home, away = self.get_home_away_teams(ev.event.name)

            home_id, away_id, tournament_id = self.\
                get_fixture_ids(home, away, ev)

            document = FixtureModel.get_document(
                ev.market_id, home, away,
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
    betfair.get_fixture(market_catalogue)
    betfair.get_odds(market_catalogue)
