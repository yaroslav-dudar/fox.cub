
export var Venue = Object.freeze({"home": 0, "away": 1});
export var SoccerMetrics = Object.freeze({"goals": "goals", "xG": "xG"});

export default class Game {
    constructor(id, score_for, score_against, venue, team_name,
                opponent_name, team_id, opponent_id, timestamp,
                team_data, opponent_data, tournament) {

        this.id = id;
        this.score_for = score_for;
        this.score_against = score_against;
        this.team_name = team_name
        this.opponent_name = opponent_name;
        this.team_id = team_id
        this.opponent_id = opponent_id;
        this.team_data = team_data; // team secondary data
        this.opponent_data = opponent_data; // opponent secondary data
        this.selected = true; // selected by default
        this.timestamp = timestamp;
        this.venue = venue;
        this.tournament = tournament;
        this.team_points = this.getPoints(this.score_for, this.score_against);
        this.opponent_points = this.getPoints(this.score_against, this.score_for)
    }

    static asWyscout(raw_wyscout_fields, wyscout_data) {
        /**
         * Convert raw wyscout data to list of Game objects
         */

        var team_data = wyscout_data
            .filter((r,i) => i % 2 == 0)
            .reverse();

        var opponent_data = wyscout_data
            .filter((r,i) => i % 2 == 1)
            .reverse();

        var wyscout_fields = Game.findWyscoutFields(raw_wyscout_fields);
        return team_data.map((_, i) => {
            let team_meta = Game.getWyscoutMetadata(team_data[i],
                                                    wyscout_fields);
            let opponent_meta = Game.getWyscoutMetadata(opponent_data[i],
                                                        wyscout_fields);

            return new Game(
                i,
                team_meta["Goals"],
                opponent_meta["Goals"],
                Game.getWyscoutVenue(team_meta),
                team_meta["Team"],
                opponent_meta["Team"],
                null,
                null,
                Date.parse(team_meta["Date"]),
                team_meta,
                opponent_meta,
                team_meta["Competition"]
            )
        });
    }

    static asFoxcub(fox_cub_data) {

        return fox_cub_data.map((game, i) => {

            var {team_meta, opponent_meta} = Game.getFoxCubMetadata(game);

            return new Game(
                i,
                game.score_for || game.goals_for,
                game.score_against || game.goals_against,
                Venue[game.venue],
                game.team[0]["name"],
                game.opponent[0]["name"],
                game.team[0]["_id"]["$oid"],
                game.opponent[0]["_id"]["$oid"],
                game.date*1000,
                team_meta,
                opponent_meta,
                game.tournament
            )
        });
    }

    static getWyscoutVenue(team_data) {
        return team_data["Match"].startsWith(team_data["Team"])
            ? Venue.home: Venue.away;
    }

    static findWyscoutFields(raw_fields) {
        /**
         * Parse Wyscout export data file and recognize attributes set
         */
        var fields = []

        raw_fields.forEach(field => {
            if (field == null) return;
            var sub_fields = field.split("/");

            if (sub_fields.length == 1)
                fields.push(sub_fields[0]);
            else if (sub_fields.length == 2) {
                fields.push(sub_fields[0]);
                fields.push(`${sub_fields[1]} ${sub_fields[0]}`);
                fields.push(`${sub_fields[1]} ${sub_fields[0]} %`);
            }
            else if (sub_fields.length == 4) {
                fields.push(sub_fields[0]);
                fields.push(`${sub_fields[1]} ${sub_fields[0]}`);
                fields.push(`${sub_fields[2]} ${sub_fields[0]}`);
                fields.push(`${sub_fields[3]} ${sub_fields[0]}`);
            }
        });

        return fields;
    }

    static getWyscoutMetadata(single_row_data, fields) {
        var metadata = {}
        fields.forEach((f, i) => {
            metadata[f] = single_row_data[i];
        })

        return metadata;
    }

    static getFoxCubMetadata(data) {
        var team_suffix = "_for";
        var opponent_suffix = "_against";

        var all_fields = Object.keys(data);
        var team_fields = all_fields.filter(
            field => field.endsWith(team_suffix))
        var opponent_fields = all_fields.filter(
            field => field.endsWith(opponent_suffix));

        var team_meta = {}, opponent_meta = {};

        team_fields.forEach(
            f => team_meta[f.replace(team_suffix, "")] = data[f]);
        opponent_fields.forEach(
            f => opponent_meta[f.replace(opponent_suffix, "")] = data[f]);

        return { team_meta, opponent_meta }
    }

    getPoints(team1_score, team2_score) {
        /**
         * Get amount of points earned by team1 against team2
         */
        if (team1_score > team2_score) {
            return 3;
        } else if (team1_score == team2_score) {
            return 1;
        } else {
            return 0;
        }
    }

}
