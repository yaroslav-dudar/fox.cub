db = db.getSiblingDB('fox_cub');

// ------------------------
// MLS
// ------------------------
db.tournament.update({ name: "MLS 2019" }, { $set: { pinnacle_id: 2663 } });

db.team.update({name: "Houston Dynamo"}, {$set : {pinnacle_name: ["Houston Dynamo"]}}, { upsert: false });
db.team.update({name: "DC United"}, {$set : {pinnacle_name: ["D.C. United"]}}, { upsert: false });
db.team.update({name: "Los Angeles FC"}, {$set : {pinnacle_name: ["Los Angeles FC"]}}, { upsert: false });
db.team.update({name: "New York Red Bulls"}, {$set : {pinnacle_name: ["New York Red Bulls"]}}, { upsert: false });
db.team.update({name: "L.A. Galaxy"}, {$set : {pinnacle_name: ["Los Angeles Galaxy"]}}, { upsert: false });
db.team.update({name: "Chicago"}, {$set : {pinnacle_name: ["Chicago Fire"]}}, { upsert: false });
db.team.update({name: "Seattle"}, {$set : {pinnacle_name: ["Seattle Sounders"]}}, { upsert: false });
db.team.update({name: "Philadelphia"}, {$set : {pinnacle_name: ["Philadelphia Union"]}}, { upsert: false });
db.team.update({name: "Columbus"}, {$set : {pinnacle_name: ["Columbus Crew"]}}, { upsert: false });
db.team.update({name: "Toronto"}, {$set : {pinnacle_name: ["Toronto FC"]}}, { upsert: false });
db.team.update({name: "FC Dallas"}, {$set : {pinnacle_name: ["Dallas"]}}, { upsert: false });
db.team.update({name: "Montreal"}, {$set : {pinnacle_name: ["Montreal Impact"]}}, { upsert: false });
db.team.update({name: "Minnesota United"}, {$set : {pinnacle_name: ["Minnesota United"]}}, { upsert: false });
db.team.update({name: "Orlando City"}, {$set : {pinnacle_name: ["Orlando City"]}}, { upsert: false });
db.team.update({name: "New England"}, {$set : {pinnacle_name: ["New England Revolution"]}}, { upsert: false });
db.team.update({name: "New York City FC"}, {$set : {pinnacle_name: ["New York City"]}}, { upsert: false });
db.team.update({name: "Atlanta United"}, {$set : {pinnacle_name: ["Atlanta United"]}}, { upsert: false });
db.team.update({name: "Colorado"}, {$set : {pinnacle_name: ["Colorado Rapids"]}}, { upsert: false });
db.team.update({name: "Portland"}, {$set : {pinnacle_name: ["Portland Timbers"]}}, { upsert: false });
db.team.update({name: "FC Cincinnati"}, {$set : {pinnacle_name: ["FC Cincinnati"]}}, { upsert: false });
db.team.update({name: "Vancouver"}, {$set : {pinnacle_name: ["Vancouver Whitecaps"]}}, { upsert: false });
db.team.update({name: "Salt Lake"}, {$set : {pinnacle_name: ["Real Salt Lake"]}}, { upsert: false });
db.team.update({name: "San Jose"}, {$set : {pinnacle_name: ["San Jose Earthquakes"]}}, { upsert: false });
db.team.update({name: "Kansas City"}, {$set : {pinnacle_name: ["Sporting Kansas City"]}}, { upsert: false });
