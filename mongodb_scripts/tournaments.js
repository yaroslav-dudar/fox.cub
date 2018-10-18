db = db.getSiblingDB('fox_cub');

db.tournament.insertMany( [
    { name: "Premier League England" },
    { name: "EFL Championship" },
    { name: "Bundesliga" }
]);
