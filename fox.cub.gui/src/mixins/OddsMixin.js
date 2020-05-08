export const OddsMixin = {
    methods: {
        getOptimalTotalPoints() {
            if (this.odds.length < 0 || !this.odds[0]) return;
            return this.odds[0].totals[0].points;
        },
        getTotalSeries(total = "over") {
            let optimal_points = this.getOptimalTotalPoints();

            return this.odds.map(g => {
                var totals = g.totals.find(t => t.points == optimal_points);
                totals = totals ? totals : g.totals[0];
                return [Date.parse(g.date.$date), totals[total]];
            })
        },
        getMoneylineSeries(moneyline = "home") {
            return this.odds.map(g => [
                Date.parse(g.date.$date),
                g.moneyline[moneyline]
            ]);
        },
    }
}

export default {
    OddsMixin
};
