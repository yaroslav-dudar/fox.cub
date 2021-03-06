db = db.getSiblingDB('fox_cub');

db.createCollection("game_stats", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: [ "team", "opponent", "date", "venue", "goals_for", "goals_against", "xG_for", "xG_against", "tournament" ],
         properties: {
            team: {
               bsonType: "string",
               description: "must be an id of a team collection and is required"
            },
            opponent: {
               bsonType: "string",
               description: "must be an id of a team collection and is required"
            },
            tournament: {
                bsonType: "string",
                description: "must be an id of a tournament collection and is required"
            },
            date: {
               bsonType: "int",
               minimum: 0,
               description: "must be an unix timestamp and is required"
            },
            venue: {
               enum: [ "home", "away" ],
               description: "can only be one of the enum values and is required"
            },
            goals_for: {
               bsonType: [ "int" ],
               minimum: 0,
               description: "must be a int and is required"
            },
            goals_against: {
                bsonType: [ "int" ],
                minimum: 0,
                description: "must be a int and is required"
            },
            xG_for: {
                bsonType: [ "double" ],
                minimum: 0,
                description: "must be a double and is required"
            },
            xG_against: {
                bsonType: [ "double" ],
                minimum: 0,
                description: "must be a double and is required"
            }
         }
      }
   }
})
