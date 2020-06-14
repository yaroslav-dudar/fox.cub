from dataset import FeatureVector

class DatasetFormat:
    """ Output formats for training dataset """

    @staticmethod
    def dataset_v1(feature: FeatureVector):
        """
            League avg goals,
            Home team attack,
            Home team defence,
            Away Team attack,
            Away team defence
        """

        return [
            feature.get_avg_goals(),
            feature.attack_strength_home_team,
            feature.defence_strength_home_team,
            feature.attack_strength_away_team,
            feature.defence_strength_away_team,
        ]

    @staticmethod
    def dataset_v2(feature: FeatureVector):
        """
            Home team League avg goals,
            Away team League avg goals,
            Home team division [0 - higher 1 - lower],
            Away team division [0 - higher 1 - lower],
            Home team attack,
            Home team defence,
            Away team attack,
            Away team defence
        """

        return [
            feature.avg_goals_home_team,
            feature.avg_goals_away_team,
            feature.league_strength_home_team,
            feature.league_strength_away_team,
            feature.attack_strength_home_team,
            feature.defence_strength_home_team,
            feature.attack_strength_away_team,
            feature.defence_strength_away_team
        ]

    @staticmethod
    def dataset_v3(feature: FeatureVector,
                   minute: int, htg: int, atg: int):
        """
            League avg goals,
            Home team attack,
            Home team defence,
            Away team attack,
            Away team defence,
            Home team score
            Away team score,
            Minute of play
        """

        return [
            feature.get_avg_goals(),
            feature.attack_strength_home_team,
            feature.defence_strength_home_team,
            feature.attack_strength_away_team,
            feature.defence_strength_away_team,
            htg,
            atg,
            minute
        ]

    @staticmethod
    def dataset_v4(feature: FeatureVector):
        """
            League avg goals,
            Home team attack,
            Home team defence,
            Away team attack,
            Away team defence,
            Home advantage
        """

        return [
            feature.get_avg_goals(),
            feature.attack_strength_home_team,
            feature.defence_strength_home_team,
            feature.attack_strength_away_team,
            feature.defence_strength_away_team,
            feature.home_advantage
        ]

    @staticmethod
    def dataset_v5(feature: FeatureVector):
        """
            Home Expected Points
            Away Expected Points
        """

        return [
            feature.exp_points_home_team,
            feature.exp_points_away_team
        ]

    @staticmethod
    def dataset_v6(feature: FeatureVector):
        """
            Home team attack,
            Home team defence,
            Away Team attack,
            Away team defence
        """

        return [
            feature.attack_strength_home_team,
            feature.defence_strength_home_team,
            feature.attack_strength_away_team,
            feature.defence_strength_away_team,
        ]
