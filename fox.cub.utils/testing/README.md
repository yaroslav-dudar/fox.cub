Fox.Cub model testing
=====================

Send requests to the fox.cub core system, collect results and allow to compare model results vs actual (real world) results

## Command line arguments

<pre>required arguments:
    - testDataset        Path to the file with games that should be tested
    - venueFilter        Venue filter pattern
    - tournamentId       Selecting MLP model based on DB tournament id

optional arguments:
    - statDataset        Path to the file with teams statistics. Using testDataset for stats if not specified
    - slaves             Amount of slaves to use in a test
    - patterns           Teams searching pattern(s). Use `,` separator to combine multiple paterns
    - games              Amount of games to test for each season
    - seasons            Amount of seasons to test in current session
    - groupBy            Group pattern for teams inside a season
</pre>

## Examples
Test only midweek games between strong-strong teams:

	PYTHONPATH=../. python master.py -dataFolder /home/etc/data -patterns MidweekGames,StrongWithStrong -games -16 -venueFilter Team1Home -seasons 10 -tournamentId 5ca22044b8fa4a20ff05e731 -groupBy Off
<br>