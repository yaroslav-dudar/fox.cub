db = db.getSiblingDB('fox_cub');

var emptyBinart = new BinData(0,"AQAAAAEBAAVlbl9VSwAAAAAAAAhv");
db.tournament_model.insert({ name: "Test", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart });


epl = db.tournament_model.findOne({"name": "Premier League England"})
championship = db.tournament_model.findOne({"name": "EFL Championship"})
bundesliga = db.tournament_model.findOne({"name": "Bundesliga"})
testing = db.tournament_model.findOne({"name": "Test"})


db.tournament.insert({ name: "Bundesliga 2019/2020", tournament_model: bundesliga._id.valueOf(), pinnacle_id: 1842 });
db.tournament.insert({ name: "EFL Championship 2019/2020", tournament_model: championship._id.valueOf(), pinnacle_id: 1977 });
db.tournament.insert({ name: "Premier League England 2019/2020", tournament_model: epl._id.valueOf(), pinnacle_id: 1980 });
db.tournament.insert({ name: "Internal Testing", tournament_model: testing._id.valueOf(), pinnacle_id: -1 });


championship19_20 = db.tournament.findOne({"name": "EFL Championship 2019/2020"})
epl19_20 = db.tournament.findOne({"name": "Premier League England 2019/2020"})

// English Championship
db.team.update({name: "Stoke City"}, {$set : {pinnacle_name: ["Stoke City"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Cardiff City"}, {$set : {pinnacle_name: ["Cardiff City"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "West Bromwich Albion"}, {$set : {pinnacle_name: ["West Brom"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Middlesbrough"}, {$set : {pinnacle_name: ["Middlesbrough"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Swansea City"}, {$set : {pinnacle_name: ["Swansea City"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Leeds United"}, {$set : {pinnacle_name: ["Leeds United"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Derby County"}, {$set : {pinnacle_name: ["Derby County"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Sheffield Wednesday"}, {$set : {pinnacle_name: ["Sheffield Wednesday"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Nottingham Forest"}, {$set : {pinnacle_name: ["Nottingham Forest"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Hull City"}, {$set : {pinnacle_name: ["Hull City"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Reading"}, {$set : {pinnacle_name: ["Reading"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Huddersfield Town"}, {$set : {pinnacle_name: ["Huddersfield Town"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Brentford"}, {$set : {pinnacle_name: ["Brentford"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Queens Park Rangers"}, {$set : {pinnacle_name: ["Queens Park Rangers"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Bristol City"}, {$set : {pinnacle_name: ["Bristol City"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Birmingham City"}, {$set : {pinnacle_name: ["Birmingham City"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Fulham"}, {$set : {pinnacle_name: ["Fulham"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Blackburn Rovers"}, {$set : {pinnacle_name: ["Blackburn Rovers"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Wigan Athletic"}, {$set : {pinnacle_name: ["Wigan Athletic"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Millwall"}, {$set : {pinnacle_name: ["Millwall"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Preston North End"}, {$set : {pinnacle_name: ["Preston"]}, $push: {tournaments: championship19_20._id.valueOf()}}, { upsert: false });
db.team.insert({name: "Barnsley", infogol_id: 33, news_feed: [], market_value: 0 , tournaments: [championship19_20._id.valueOf()], pinnacle_name: ["Barnsley"]});
db.team.insert({name: "Luton Town", infogol_id: 341, news_feed: [], market_value: 0 , tournaments: [championship19_20._id.valueOf()], pinnacle_name: ["Luton Town"]});
db.team.insert({name: "Charlton Athletic", infogol_id: 10, news_feed: [], market_value: 0 , tournaments: [championship19_20._id.valueOf()], pinnacle_name: ["Charlton Athletic"]});


// Premier League England
db.team.update({name: "Manchester City"}, {$set : {pinnacle_name: ["Manchester City"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Liverpool"}, {$set : {pinnacle_name: ["Liverpool"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Chelsea"}, {$set : {pinnacle_name: ["Chelsea"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Manchester United"}, {$set : {pinnacle_name: ["Manchester United"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Tottenham Hotspur"}, {$set : {pinnacle_name: ["Tottenham Hotspur"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Arsenal"}, {$set : {pinnacle_name: ["Arsenal"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Everton"}, {$set : {pinnacle_name: ["Everton"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Leicester City"}, {$set : {pinnacle_name: ["Leicester City"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "West Ham United"}, {$set : {pinnacle_name: ["West Ham United"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Southampton"}, {$set : {pinnacle_name: ["Southampton"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Aston Villa"}, {$set : {pinnacle_name: ["Aston Villa"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Crystal Palace"}, {$set : {pinnacle_name: ["Crystal Palace"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Wolverhampton"}, {$set : {pinnacle_name: ["Wolverhampton Wanderers"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Burnley"}, {$set : {pinnacle_name: ["Burnley"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Brighton"}, {$set : {pinnacle_name: ["Brighton and Hove Albion"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Newcastle United"}, {$set : {pinnacle_name: ["Newcastle United"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Bournemouth"}, {$set : {pinnacle_name: ["Bournemouth", "Bournemouth FC"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Watford"}, {$set : {pinnacle_name: ["Watford"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Norwich City"}, {$set : {pinnacle_name: ["Norwich City"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
db.team.update({name: "Sheffield United"}, {$set : {pinnacle_name: ["Sheffield United"]}, $push: {tournaments: epl19_20._id.valueOf()}}, { upsert: false });
