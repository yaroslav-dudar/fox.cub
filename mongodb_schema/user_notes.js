db = db.getSiblingDB('fox_cub');

db.createCollection("user_notes", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: [ "user", "ref_id", "ref_to", "note_text", "created_at", "updated_at", "note_type" ],
            properties: {
                user: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                ref_id: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                ref_to: {
                    enum: [ "team", "player", "tournament", "game" ],
                    description: "can only be one of the enum values and is required"
                },
                note_text: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                created_at: {
                    bsonType: "date",
                    description: "must be a date and is required"
                },
                updated_at: {
                    bsonType: "date",
                    description: "must be a date and is required"
                },
                note_type: {
                    enum: [ "review", "weakness", "strength", "general" ],
                    description: "can only be one of the enum values and is required"
                },
            }
        }
    }
})
 