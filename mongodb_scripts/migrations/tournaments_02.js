db = db.getSiblingDB('fox_cub');

mls = db.tournament_model.findOne({"name": "MLS"})
epl = db.tournament_model.findOne({"name": "Premier League England"})
championship = db.tournament_model.findOne({"name": "EFL Championship"})
bundesliga = db.tournament_model.findOne({"name": "Bundesliga"})
national_cup = db.tournament_model.findOne({"name": "National Cup"})
international_qualification = db.tournament_model.findOne({"name": "International Cup Qualification"})
international_final = db.tournament_model.findOne({"name": "International Cup Final Stage"})
brazil = db.tournament_model.findOne({"name": "Brasileiro Serie A"})

db.tournament.update({ name: "Premier League England" }, { name: "Premier League England 2018/2019", tournament_model: epl._id.valueOf()});
db.tournament.update({ name: "EFL Championship" }, { name: "EFL Championship 2018/2019", tournament_model: championship._id.valueOf()});
db.tournament.update({ name: "Bundesliga" }, { name: "Bundesliga 2018/2019", tournament_model: bundesliga._id.valueOf()});
db.tournament.update({ name: "MLS" }, { name: "MLS 2019", tournament_model: mls._id.valueOf()});
db.tournament.update({ name: "National Cup" }, { $set: {tournament_model: national_cup._id.valueOf()}});
db.tournament.update({ name: "International Cup Final Stage" }, { $set: {tournament_model: international_final._id.valueOf()}});
db.tournament.update({ name: "International Cup Qualification"}, { $set: {tournament_model: international_qualification._id.valueOf()}});
db.tournament.update({ name: "Brasileiro Serie A" }, { name: "Brasileiro Serie A 2019", tournament_model: brazil._id.valueOf()});
