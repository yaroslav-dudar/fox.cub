db = db.getSiblingDB('fox_cub');

db.createCollection("game_odds", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: [ "home_team", "away_team", "odds", "tournament", "event_date" ],
            properties: {
                home_team: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                away_team: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                odds: {
                    bsonType: "array",
                    description: "must be a array and is required"
                },
                event_date: {
                    bsonType: "date",
                    description: "must be a date and is required"
                },
                tournament: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
            }
        }
    }
})
 