export const FixtureMixin = {
    methods: {
        groupByDate() {
            var dates = new Set(this.fixtures.map(f => {
                let day = this._getDay(f.date.$date);
                return day;
            }));
            dates = Array.from(dates);

            var groups = {};
            dates.map(d => groups[d] = []);
            this.fixtures.map(f => {
                let day = this._getDay(f.date.$date);
                groups[day].push(f);
            })

            return groups;
        },
        _getDay(date) {
            return date.split("T")[0];
        }
    }
}

export default {
    FixtureMixin
};
