class UserProfile:
    def __init__(
        self,
        investment_goal,
        risk_tolerance,
        time_horizon,
        investing_styles=None,
        preferred_sectors=None,
        excluded_sectors=None,
        growth_preference=3,
        stability_preference=3,
        valuation_preference=3,
        dividend_preference=3,
        company_sizes=None,
        experience_level="beginner"
    ):
        self.investment_goal = investment_goal
        self.risk_tolerance = risk_tolerance
        self.time_horizon = time_horizon
        self.investing_styles = investing_styles or []
        self.preferred_sectors = preferred_sectors or []
        self.excluded_sectors = excluded_sectors or []
        self.growth_preference = growth_preference
        self.stability_preference = stability_preference
        self.valuation_preference = valuation_preference
        self.dividend_preference = dividend_preference
        self.company_sizes = company_sizes or []
        self.experience_level = experience_level

    def to_dict(self):
        return self.__dict__