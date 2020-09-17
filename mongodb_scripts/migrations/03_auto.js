// 2020-2021 season updates

db = db.getSiblingDB('fox_cub');

bundesliga = db.tournament_model.findOne({"name": "Bundesliga"})
bundesliga2 = db.tournament_model.findOne({"name": "Bundesliga 2"})
epl = db.tournament_model.findOne({"name": "Premier League England"})
championship = db.tournament_model.findOne({"name": "EFL Championship"})

bundesiga_2_20_21 = db.tournament.insertOne({ name: "Bundesliga 2 2020/2021", tournament_model: bundesliga2._id.valueOf(), pinnacle_id: 1843 }).insertedId;
// deactivate fixture update on Bundesliga 2 2019/2020
db.tournament.update({ name: "Bundesliga 2 2019/2020" }, { $set: { pinnacle_id: -1 } });

bundesiga20_21 = db.tournament.insertOne({ name: "Bundesliga 2020/2021", tournament_model: bundesliga._id.valueOf(), pinnacle_id: 1842 }).insertedId;
// deactivate fixture update on Bundesliga  2019/2020
db.tournament.update({ name: "Bundesliga 2019/2020" }, { $set: { pinnacle_id: -1 } });

epl20_21 = db.tournament.insertOne({ name: "Premier League England 2020/2021", tournament_model: epl._id.valueOf(), pinnacle_id: 1980 }).insertedId;
// deactivate fixture update on Premier League England 2019/2020
db.tournament.update({ name: "Premier League England 2019/2020" }, { $set: { pinnacle_id: -1 } });

championship20_21 = db.tournament.insertOne({ name: "EFL Championship 2020/2021", tournament_model: championship._id.valueOf(), pinnacle_id: 1977 }).insertedId;
// deactivate fixture update on EFL Championship 2019/2020
db.tournament.update({ name: "EFL Championship 2019/2020" }, { $set: { pinnacle_id: -1 } });


// English Championship
db.team.update({name: "Stoke City"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Cardiff City"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Middlesbrough"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Swansea City"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Derby County"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Sheffield Wednesday"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Nottingham Forest"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Reading"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Huddersfield Town"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Brentford"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Queens Park Rangers"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Bristol City"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Birmingham City"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Blackburn Rovers"}, { $push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Millwall"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Preston North End"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Barnsley"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Luton Town"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Watford"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Bournemouth"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Norwich City"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Rotherham United"}, {$push: {tournaments: championship20_21.valueOf()}}, { upsert: false })
db.team.insert({name: "Coventry", infogol_id: 340, news_feed: [], market_value: 0 , tournaments: [championship20_21.valueOf()], pinnacle_name: ["Coventry"]});
db.team.insert({name: "Wycombe", infogol_id: 887, news_feed: [], market_value: 0 , tournaments: [championship20_21.valueOf()], pinnacle_name: ["Wycombe"]});


// Premier League England
db.team.update({name: "Manchester City"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Liverpool"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Chelsea"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Manchester United"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Tottenham Hotspur"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Arsenal"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Everton"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Leicester City"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "West Ham United"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Southampton"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Aston Villa"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Crystal Palace"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Wolverhampton"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Burnley"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Brighton"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Newcastle United"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Sheffield United"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Fulham"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Leeds United"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });
db.team.update({name: "West Bromwich Albion"}, {$push: {tournaments: epl20_21.valueOf()}}, { upsert: false });


//Bundesliga
db.team.update({name: "Bayern Munich"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Borussia Dortmund"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Bayer 04 Leverkusen"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "RB Leipzig"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "FC Schalke 04"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "TSG 1899 Hoffenheim"}, { $push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Borussia Mönchengladbach"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "VfL Wolfsburg"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Eintracht Frankfurt"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Hertha BSC"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Werder Bremen"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Mainz 05"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "FC Augsburg"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "SC Freiburg"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "FC Koln"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Union Berlin"}, {$push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Stuttgart"}, {$set : {infogol_id: 338}, $push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Arminia Bielefeld"}, {$set : {infogol_id: 960}, $push: {tournaments: bundesiga20_21.valueOf()}}, { upsert: false });


//Bundesliga 2
db.team.update({name: "Karlsruher SC"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "FC Heidenheim"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Hamburger SV"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "SV Darmstadt 98"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Arminia Bielefeld"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Holstein Kiel"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "St Pauli"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Hannover 96"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Nurnberg"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Osnabruck"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Bochum"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "SV Sandhausen 1916"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Erzgebirge Aue"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Jahn Regensburg"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Greuther Furth"}, {$push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "SC Paderborn 07"}, {$set : {fivethirtyeight_name: "SC Paderborn"}, $push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.update({name: "Fortuna Düsseldorf"}, {$set : {fivethirtyeight_name: "Fortuna Düsseldorf"}, $push: {tournaments: bundesiga_2_20_21.valueOf()}}, { upsert: false });
db.team.insert({name: "Wurzburger Kickers", fivethirtyeight_name: "Wurzburger Kickers", news_feed: [], market_value: 0 , tournaments: [bundesiga_2_20_21.valueOf()], pinnacle_name: ["Wurzburger Kickers"]});
db.team.insert({name: "Eintracht Braunschweig", fivethirtyeight_name: "Eintracht Braunschweig", news_feed: [], market_value: 0 , tournaments: [bundesiga_2_20_21.valueOf()], pinnacle_name: ["Eintracht Braunschweig"]});
