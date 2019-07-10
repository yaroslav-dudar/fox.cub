# -*- coding: utf-8 -*-

class TestSessionResult():

    def __init__(self):
        self.totals_2_5, self.totals_3_5 = [], []
        self.actual_results_team1, self.actual_results_team2 = [], []
        self.model_results = []
        self.scored_1, self.conceded_1 = [], []
        self.scored_2, self.conceded_2 = [], []
        self.btts = []

    def __iadd__(self, other_session):
        self.totals_2_5 += other_session.totals_2_5
        self.totals_3_5 += other_session.totals_3_5

        self.actual_results_team1 += other_session.actual_results_team1
        self.actual_results_team2 += other_session.actual_results_team2

        self.scored_1 += other_session.scored_1
        self.conceded_1 += other_session.conceded_1

        self.scored_2 += other_session.scored_2
        self.conceded_2 += other_session.conceded_2
        self.model_results += other_session.model_results
        self.btts += other_session.btts

        return self

    def cleanup(self):
        self.totals_2_5, self.totals_3_5 = [], []
        self.actual_results_team1, self.actual_results_team2 = [], []
        self.model_results = []
        self.scored_1, self.conceded_1 = [], []
        self.scored_2, self.conceded_2 = [], []
        self.btts = []
