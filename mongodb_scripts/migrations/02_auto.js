db = db.getSiblingDB('fox_cub');

var emptyBinart = new BinData(0,"AQAAAAEBAAVlbl9VSwAAAAAAAAhv");
db.tournament_model.insert({ name: "Bundesliga 2", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart });


mls = db.tournament_model.findOne({"name": "MLS"})
db.tournament.insert({ name: "Bundesliga 2 2019/2020", tournament_model: bundesliga2._id.valueOf(), pinnacle_id: 1843 });
db.tournament.insert({ name: "MLS 2020", tournament_model: mls._id.valueOf(), pinnacle_id: 2663 });
// deactivate fixture update on MLS 2019
db.tournament.update({ name: "MLS 2019" }, { $set: { pinnacle_id: -1 } });

bundesiga2_19_20 = db.tournament.findOne({"name": "Bundesliga 2 2019/2020"});
mls_20 = db.tournament.findOne({"name": "MLS 2020"});

db.team.update({name: "Houston Dynamo"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "DC United"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Los Angeles FC"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "New York Red Bulls"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "L.A. Galaxy"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Chicago"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Seattle"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Philadelphia"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Columbus"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Toronto"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "FC Dallas"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Montreal"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Minnesota United"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Orlando City"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "New England"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "New York City FC"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Atlanta United"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Colorado"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Portland"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "FC Cincinnati"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Vancouver"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Salt Lake"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "San Jose"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Kansas City"}, {$push: {tournaments: mls_20._id.valueOf()}}, { upsert: false });

db.team.insertMany( [
    { name: "Inter Miami", news_feed: [], market_value: 0 , tournaments: [mls_20._id.valueOf()], fivethirtyeight_name: "Inter Miami CF", pinnacle_name: ["Inter Miami"]},
    { name: "Nashville SC", news_feed: [], market_value: 0 , tournaments: [mls_20._id.valueOf()], fivethirtyeight_name: "Nashville SC", pinnacle_name: ["Nashville SC"]},
])

db.team.insertMany( [
    // Bundesliga 2
    { name: "Wehen Wiesbaden", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "SV Wehen Wiesbaden", pinnacle_name: ["Wehen Wiesbaden"]},
    { name: "Stuttgart", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "VfB Stuttgart", pinnacle_name: ["Stuttgart"]},
    { name: "Dynamo Dresden", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Dynamo Dresden", pinnacle_name: ["Dynamo Dresden"]},
    { name: "Karlsruher SC", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Karlsruher SC", pinnacle_name: ["Karlsruher SC"]},
    { name: "FC Heidenheim", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "1. FC Heidenheim 1846", pinnacle_name: ["FC Heidenheim"]},
    { name: "Hamburger SV", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Hamburg SV", pinnacle_name: ["Hamburger SV"]},
    { name: "SV Darmstadt 98", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "SV Darmstadt 98", pinnacle_name: ["SV Darmstadt 98"]},
    { name: "Arminia Bielefeld", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Arminia Bielefeld", pinnacle_name: ["Arminia Bielefeld"]},
    { name: "Holstein Kiel", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Holstein Kiel", pinnacle_name: ["Holstein Kiel"]},
    { name: "St Pauli", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "FC St. Pauli", pinnacle_name: ["St Pauli"]},
    { name: "Hannover 96", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Hannover 96", pinnacle_name: ["Hannover 96"]},
    { name: "Nurnberg", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "1. FC Nürnberg", pinnacle_name: ["Nurnberg"]},
    { name: "Osnabruck", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "VfL Osnabruck", pinnacle_name: ["Osnabruck"]},
    { name: "Bochum", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "VfL Bochum", pinnacle_name: ["Bochum"]},
    { name: "SV Sandhausen 1916", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "SV Sandhausen", pinnacle_name: ["SV Sandhausen 1916"]},
    { name: "Erzgebirge Aue", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Erzgebirge Aue", pinnacle_name: ["Erzgebirge Aue"]},
    { name: "Jahn Regensburg", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Jahn Regensburg", pinnacle_name: ["Jahn Regensburg"]},
    { name: "Greuther Furth", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "SpVgg Greuther Fürth", pinnacle_name: ["Greuther Furth"]}
    ])
