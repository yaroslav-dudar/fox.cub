db.game_stats.aggregate( [
  {
    $facet: {
      "league_avg": [
        { $match: {"tournament": "5b8a36a335b9d3a022e66887", "venue": "home"}},
        {
          $bucket: {
            groupBy: "$_id",
            boundaries: [0, 150],
            default: "Other",
            output: {
              "avgScoredHome": { $avg: "$goals_for"},
              "avgScoredAway": { $avg: "$goals_against"},
            }
          }
        }
      ],
      "away_team_avg": [
        { $match: {"tournament": "5b8a36a335b9d3a022e66887", "team": "5bae42e42ba2728fc776882f"}},
        {
          $bucket: {
            groupBy: "$_id",
            boundaries: [0, 150],
            default: "Other",
            output: {
              "scored": {$push: "$goals_for"},
              "conceded": {$push: "$goals_against"}
            }
          }
        }
      ],
      "home_team_avg": [
        { $match: {"tournament": "5b8a36a335b9d3a022e66887", "team": "5bae42e42ba2728fc7768830"}},
        {
          $bucket: {
            groupBy: "$_id",
            boundaries: [0, 150],
            default: "Other",
            output: {
              "scored": {$push: "$goals_for"},
              "conceded": {$push: "$goals_against"}
            }
          }
        }
      ]
    }
  }
])

db.game_stats.aggregate( [
    {
        $match: {"team": "5bae42e42ba2728fc7768838", "tournament": "5b8a36a335b9d3a022e66887"}
    },
    {
        "$addFields": {
            "team": { "$toObjectId": "$team" },
            "opponent": { "$toObjectId": "$opponent" }
        }
    },
    {
        $lookup: {
            from: "team",
            localField: "team",
            foreignField: "_id",
            as: "team"
        }
    },
    {
        $lookup: {
            from: "team",
            localField: "opponent",
            foreignField: "_id",
            as: "opponent"
        }
    }
])
