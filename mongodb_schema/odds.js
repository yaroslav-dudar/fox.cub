db = db.getSiblingDB('fox_cub');

db.createCollection("odds", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: [ "fixture_id", "date", "spreads", "moneyline", "totals"],
            properties: {
                fixture_id: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                date: {
                    bsonType: "date",
                    description: "must be a date and is required"
                },
                moneyline: {
                    bsonType: "object",
                    description: "must be a object and is required"
                },
                spreads: {
                    bsonType: "array",
                    description: "must be a array and is required"
                },
                totals: {
                    bsonType: "array",
                    description: "must be a array and is required"
                },
            }
        }
    }
})
