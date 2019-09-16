db = db.getSiblingDB('fox_cub');

var emptyBinart = new BinData(0,"AQAAAAEBAAVlbl9VSwAAAAAAAAhv");
db.tournament_model.insert({ name: "Bundesliga 2", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart });

bundesliga2 = db.tournament_model.findOne({"name": "Bundesliga 2"})

db.tournament.insert({ name: "Bundesliga 2 2019/2020", tournament_model: bundesliga2._id.valueOf(), pinnacle_id: 1843 });

bundesiga2_19_20 = db.tournament.findOne({"name": "Bundesliga 2 2019/2020"});

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
    { name: "Nurnberg", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "1. FC N├╝rnberg", pinnacle_name: ["Nurnberg"]},
    { name: "Osnabruck", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "VfL Osnabruck", pinnacle_name: ["Osnabruck"]},
    { name: "Bochum", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "VfL Bochum", pinnacle_name: ["Bochum"]},
    { name: "SV Sandhausen 1916", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "SV Sandhausen", pinnacle_name: ["SV Sandhausen 1916"]},
    { name: "Erzgebirge Aue", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Erzgebirge Aue", pinnacle_name: ["Erzgebirge Aue"]},
    { name: "Jahn Regensburg", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "Jahn Regensburg", pinnacle_name: ["Jahn Regensburg"]},
    { name: "Greuther Furth", news_feed: [], market_value: 0 , tournaments: [bundesiga2_19_20._id.valueOf()], fivethirtyeight_name: "SpVgg Greuther F├╝rth", pinnacle_name: ["Greuther Furth"]}
    ])