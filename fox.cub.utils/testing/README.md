Fox.Cub model testing
=====================

Send requests to the fox.cub core system, collect results and allow to compare model results vs actual (real world) results

## Command line arguments

<pre>positional arguments:
    - dataFolder         Path to the testing data folder.
    - venueFilter        Venue filter pattern

optional arguments:
    - slaves             Amount of slaves to use in a test
    - patterns           Teams searching pattern(s). Use `,` separator to combine multiple paterns
    - games              Amount of games to test for each season
</pre>

## Examples
Test only midweek games between strong-strong teams:

	PYTHONPATH=../. python master.py -dataFolder /home/etc/data -pattern MidweekGames,StrongWithStrong -games 1000 -venueFilter AllTested games: 1075
<br>