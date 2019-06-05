db = db.getSiblingDB('fox_cub');

var emptyBinart = new BinData(0,"AQAAAAEBAAVlbl9VSwAAAAAAAAhv");

db.tournament_model.insertMany([
    { name: "Premier League England", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart },
    { name: "EFL Championship", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart },
    { name: "Bundesliga", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart },
    { name: "National Cup", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart },
    { name: "International Cup Qualification", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart },
    { name: "International Cup Final Stage", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart },
    { name: "Brasileiro Serie A", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart },
    { name: "MLS", scoreline: emptyBinart, btts: emptyBinart, totals: emptyBinart }
]);
