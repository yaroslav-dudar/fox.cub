db = db.getSiblingDB('fox_cub');

db.createCollection("tournament_model", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["name", "scoreline", "totals", "btts" ],
            properties: {
                name: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                scoreline: {
                    bsonType: "binData",
                    description: "must be a binary data and is required"
                },
                totals: {
                    bsonType: "binData",
                    description: "must be a binary data and is required"
                },
                btts: {
                    bsonType: "binData",
                    description: "must be a binary data and is required"
                },
                scorelineLive: {
                    bsonType: "binData",
                    description: "must be a binary data"
                },
                totalsLive: {
                    bsonType: "binData",
                    description: "must be a binary data"
                },
                bttsLive: {
                    bsonType: "binData",
                    description: "must be a binary data"
                },
            }
        }
    }
})
