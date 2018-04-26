# Smash Elo

This is a Python 3 project created by Wyatt Strother, also known as the smasher AHP. This Python program provides a simple interface for collecting, storing, and updaing elo ratings for results from Smash tournaments, but could also be used for generating elo ratings on any 1-on-1 game with recorded match data.

# How to

#### Requirements: 

* Python 3
* [Pychallonge](https://github.com/russ-/pychallonge) and by extension [ISO8601](https://pypi.org/project/iso8601/)

#### Settings.py:

This file defines all the default values and file_names for any league data you generate. You can also adjust constants related to your elo rating distribution such as the K_FACTOR, ELO_WIDTH and START_RATING (which also serves as the mean rating).

#### Command Line:

You can invoke the file ***get_rankings.py*** from the command line with a number of parameters to generate different outputs. By default it will generate a league using the default parameters defined by ***settings.py*** and output results to the console.

* **save** - creates a .json file to save league data
* ***.json** - specifies saved league data to update / defnes a filename to save json data to
* **html** - creates a .html file to display league data
* ***.html** - defines a flename to save html to
* ***.css** - defines a CSS stylesheet file_name for output of html
* **f** - forces league data to be re-generated from scratch
* **follow** - only pulls matches between players who are specified in the FOLLOW_FILE as dfined by ***settings.py***

#### tournaments.txt:

Each line should contain a bracket url. (At this stage, only Challonge is supported though support for Smash.GG will be added next). You can also speciy a float value to be used as a 'strength' factor that will scale the K_FACTOR applied to matches of a specific tournament.

**Example:**
'''
http://challonge.com/example1
http://challonge.com/example2 0.5
'''

#### follow.txt:

Each line should contain a single player tag written with *no spaces*.

**Example:**
'''
exampletag1
exampletag2
'''

### alts.txt:

Each line should contain the preferred player tag on the left and any alternate tags to the right, separated by spaces. *Tags listed in this file must be spelled without spaces* or they'll be read as two separate alts.

**Example:**
'''
exampletag1 alt1 alt2
exampletag2 alt3
'''

# Coming Soon..

* Support for challonge brackets
* Support for live web application with built in REST-API module.
