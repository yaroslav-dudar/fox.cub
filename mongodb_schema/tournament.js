db = db.getSiblingDB('fox_cub');

db.createCollection("tournament", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: [ "name" ],
            properties: {
                name: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                stats: {
                    bsonType: "object",
                    description: "must be an object"
                },
            }
        }
    }
})
 