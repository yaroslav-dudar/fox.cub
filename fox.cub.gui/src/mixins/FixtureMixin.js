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
        },

        /**
         * @param {Number} dayOffset Offset in days to the current date. If < 0 give past day
         * @return {Date}
         */
        getDateOffset(dayOffset) {
            var timestamp = new Date().getTime();
            var offset = 86400000 * dayOffset;
            return new Date(timestamp + offset);
        },

        /**
         * @param {Date} date input date
         * @return {string} in yyyy-mm-dd format
         */
        dateToStr(date) {
            return date.toJSON().slice(0, 10);
        },

        /**
         * @param {Number} dayOffset
         * @return {string} in yyyy-mm-dd format
         */
        getDate(dayOffset) {
            var date = this.getDateOffset(dayOffset)
            return this.dateToStr(date);
        }
    }
}

export default {
    FixtureMixin
};
