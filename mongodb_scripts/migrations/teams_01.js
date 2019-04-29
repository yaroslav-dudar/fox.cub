db = db.getSiblingDB('fox_cub');

mls = db.tournament.findOne({"name": "MLS"})

db.team.insertMany( [
    // MLS
    { name: "Houston Dynamo", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Houston Dynamo", football_1xbet_name: "Houston Dynamo"},
    { name: "DC United", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "DC United", football_1xbet_name: "D.C. United"},
    { name: "Los Angeles FC", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Los Angeles FC", football_1xbet_name: "Los Angeles"},
    { name: "New York Red Bulls", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "New York Red Bulls", football_1xbet_name: "New York Red Bulls"},
    { name: "L.A. Galaxy", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Los Angeles Galaxy", football_1xbet_name: "Los Angeles Galaxy"},
    { name: "Chicago", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Chicago Fire", football_1xbet_name: "Chicago Fire"},
    { name: "Seattle", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Seattle Sounders FC", football_1xbet_name: "Seattle Sounders"},
    { name: "Philadelphia", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Philadelphia Union", football_1xbet_name: "Philadelphia Union"},
    { name: "Columbus", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Columbus Crew", football_1xbet_name: "Columbus Crew"},
    { name: "Toronto", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Toronto FC", football_1xbet_name: "Toronto"},
    { name: "FC Dallas", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "FC Dallas", football_1xbet_name: "Dallas"},
    { name: "Montreal", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Montreal Impact", football_1xbet_name: "Montreal Impact"},
    { name: "Minnesota United", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Minnesota United FC", football_1xbet_name: "Minnesota United"},
    { name: "Orlando City", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Orlando City SC", football_1xbet_name: "Orlando City"},
    { name: "New England", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "New England Revolution", football_1xbet_name: "New England Revolution"},
    { name: "New York City FC", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "New York City FC", football_1xbet_name: "New York City"},
    { name: "Atlanta United", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Atlanta United FC", football_1xbet_name: "Atlanta United"},
    { name: "Colorado", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Colorado Rapids", football_1xbet_name: "Colorado Rapids"},
    { name: "Portland", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Portland Timbers", football_1xbet_name: "Portland Timbers"},
    { name: "FC Cincinnati", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "FC Cincinnati", football_1xbet_name: "Cincinnati"},
    { name: "Vancouver", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Vancouver Whitecaps", football_1xbet_name: "Vancouver Whitecaps"},
    { name: "Salt Lake", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Real Salt Lake", football_1xbet_name: "Real Salt Lake"},
    { name: "San Jose", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "San Jose Earthquakes", football_1xbet_name: "San Jose Earthquakes"},
    { name: "Kansas City", news_feed: [], market_value: 0 , tournaments: [mls._id.valueOf()], fivethirtyeight_name: "Sporting Kansas City", football_1xbet_name: "Sporting Kansas City"}
])
