db = db.getSiblingDB('fox_cub');

db.createCollection("team", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: [ "name", "news_feed", "market_value", "tournaments" ],
            properties: {
                name: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                news_feed: {
                    bsonType: "array",
                    description: "must be a array and is required"
                },
                market_value: {
                    bsonType: "double",
                    minimum: 0,
                    description: "must be a double and is required"
                },
                tournaments: {
                    bsonType: "array",
                    description: "must be a array and is required"
                },
            }
        }
    }
})
 