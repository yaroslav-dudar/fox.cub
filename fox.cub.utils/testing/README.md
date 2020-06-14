Fox.Cub model testing
=====================

Send requests to the fox.cub core system, collect results and allow to compare model results vs actual (real world) results

## Command line arguments

<pre>required arguments:
    - testDataset        Dataset name from settings.py
    - venueFilter        Venue filter pattern
    - tournamentId       Selecting MLP model based on DB tournament id

optional arguments:
    - slaves             Amount of slaves to use in a test
    - patterns           Teams searching pattern(s) class. Use `,` separator to combine multiple paterns
    - games              Amount of games to test for each season
    - seasons            Amount of seasons to test in current session
    - groupBy            Group pattern for teams inside a season
</pre>

## Examples
Test only midweek games between strong-strong teams:

	PYTHONPATH=../. python master.py -dataFolder /home/etc/data -patterns testing.searchers.MidweekGames,testing.searchers.StrongWithStrong -games -16 -venueFilter Team1Home -seasons 10 -tournamentId 5ca22044b8fa4a20ff05e731 -groupBy Off
<br>

Fox.Cub converter
=====================

Generate dataset file in fox.cub.gui сompatible format.

## Command line arguments

<pre>required arguments:
    - testDataset        Dataset name from settings.py
    - venueFilter        Venue filter pattern
    - tournamentId       Selecting MLP model based on DB tournament id

optional arguments:
    - slaves             Amount of slaves to use in a test
    - patterns           Teams searching pattern(s) class. Use `,` separator to combine multiple paterns
    - games              Amount of games to test for each season
    - seasons            Amount of seasons to test in current session
    - groupBy            Group pattern for teams inside a season
</pre>

## Examples
Generate dataset for last season for team Sprout:

	PYTHONPATH=../. DATA_FOLDER=/home/ydudar/dev/historical_data python converter.py -dataset cs_go -venueFilter All -seasons -1  -start 01/03/2020 -team Sprout
<br>