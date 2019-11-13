export const TournamentMixin = {
    methods: {
        /**
         * Return teams points per game from a specific tournament
         * @return {number}
         */
        getTeamPPG(ppg_table, team_id, tournament_id, metric = "ppg") {
            var filtered = ppg_table[tournament_id]
                .filter(team => team.team_id == team_id);

            if (filtered.length > 0) return filtered[0][metric];
            return 0;
        }
    }
}

export default {
    TournamentMixin
};
