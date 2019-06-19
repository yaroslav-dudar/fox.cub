db = db.getSiblingDB('fox_cub');

db.createCollection("fixtures", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: [ "home_name", "away_name", "date", "tournament_name", "tournament_id", "home_id", "away_id" ],
            properties: {
                home_name: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                away_name: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                date: {
                    bsonType: "date",
                    description: "must be a date and is required"
                },
                tournament_name: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                tournament_id: {
                    anyOf: [{ bsonType: "string" }, { bsonType: "null" }]
                },
                home_id: {
                    anyOf: [{ bsonType: "string" }, { bsonType: "null" }]
                },
                away_id: {
                    anyOf: [{ bsonType: "string" }, { bsonType: "null" }]
                },
            }
        }
    }
})
