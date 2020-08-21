db = db.getSiblingDB('fox_cub');

db.createCollection("user", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: [ "username", "password", "salt" ],
            properties: {
                username: {
                    bsonType: "string",
                    description: "must be a string and is required",
                    minLength: 8,
                    maxLength: 16
                },
                password: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                salt: {
                    bsonType: "string",
                    description: "must be a string and is required",
                    minLength: 8,
                    maxLength: 16
                },
                notes: {
                    bsonType: "array",
                    description: "must be an array of objectId's",
                    items: {
                        bsonType: "objectId"
                    }
                },
                fav_fixtures: {
                    bsonType: "array",
                    description: "must be an array of objectId's",
                    items: {
                        bsonType: "objectId"
                    }
                }
            }
        }
    }
})
