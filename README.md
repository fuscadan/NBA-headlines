# NBA-headlines

This project is meant as an exercise in Python generally and web scraping and machine learning specifically.  The libraries we use are BeautifulSoup4 and SciKit-Learn.  Pandas dataframes are also used incidentally.

Project outline:
================

The goal is to write a program that takes some basic data from an NBA playoff game as an input and returns a short headline for that game.  This idea was humourously suggested to me by [Jordan Bell](https://www.linkedin.com/in/jordanbell2357/).  Rather than defining a headline template (or list of templates) that we can fill in with the inputted data, we instead match the given game data with the "closest" historical playoff game, and use the headline of that historical game as our template.  As long as the definition of "distance" between two sets of game data is reasonable, this algorithm should usually give us a headline template that is appropriate for the new game.

Consider the following example.  The Toronto Raptors [recently beat](https://www.espn.com/nba/game?gameId=401129105) the Philadelphia 76ers in a close Game 7.  It turns out that last year in 2018, The Cavaliers and the Pacers [played a game](https://www.espn.com/nba/game?gameId=401029433) with similar statistics. 

The ESPN headline for the Cavs-Pacers game was 
> 7th heaven: LeBron carries Cavaliers past Pacers in Game 7

The template of this headline is 
> 7th heaven: (home_pts_leader) carries (home_team) past (away_team) in Game 7

Filling in this template with information from the Raptors-Bucks game, we end up generating the headline
> 7th heaven: Leonard carries Raptors past 76ers in Game 7

Another example: Consider [Game 1 of the 2019 Eastern Conference Finals](https://www.espn.com/nba/game?gameId=401131840), a game in which Toronto lost to the Milwaukee Bucks after collapsing in the 4th quarter.  Our algorithm generates the headline
> Bucks control Raptors, lead 1-0 after dominant 4th

The template for this headline comes from [Game 1 of the 2011 Eastern Conference Finals](https://www.espn.com/nba/game?gameId=310515004), where the winning Chicago Bulls also had a strong 4th quarter.
> Bulls control Heat, lead 1-0 after dominant 4th

In summary, our algorithm 
1. identifies the nearest neigbouring historical game and extracts its headline
2. finds and replaces old team names, scores, and so on with their new counterparts.


Usage:
======

1. Find the ESPN Game Summary page for an NBA playoff game from 2019 or later, and note its 9-digit Game ID. For example,

	> https://www.espn.com/nba/game?gameId=401131840

	has the game ID `401131840`.  Basic game information for this game will be scraped from this URL and a headline for the game will be generated.

2. Run nba_headline_generator.py with the command `-id <Game Id>`.  Optional commands are `-t` to display the template headline and template game ID, and `-m <relative path to model file>` to use a different model file other than `headline_knn.joblib`. Example:
	
	`nba_headline_generator.py -id 401131840 -t`


Main Libraries Used
-------------------

The closest historical game is found using the KNeighborsClassifier module of the SciKit-Learn library.  The training set (i.e. the collection of historical game data) is built by scraping espn.com using BeautifulSoup4.  We remark that this is a somewhat degenerate use of the KNN algorithm, since we treat each training example (historical game) as having its own unique target label (its headline).  Nevertheless, I find this project to be an informative exercise in using SciKit-Learn's .neighbors, .preprocessing, .feature_extraction, and .pipeline modules.



Effectiveness of the program
============================

We emphasize the advantage of our approach over manually defining templates for headlines.  For example, information about whether the home or the road team won is usually included in the game's headline, but there are many ways of phrasing this information.  A few examples...
> ...win at home...

> ...protect home court...

> ...win in (city name)...

> ...win on the road

> ...steal (game number)...

It would be time consuming to manually define so many variations for every feature that may or may not be mentioned in a headline, and it would be even more difficult to ensure that the resulting headline would be grammatically correct.  Our algorithm avoids these issues by using historical game headlines as templates instead of trying to define our own.

By choosing relatively high weights for important features, we make games with differing values for those features far apart.  This can guarantee, for example, that the nearest neighbour of a game where the home team won will not be a game where the home team lost.  If we use that neighbour's headline as a template for the new game, it will at least be correct about whether the home or road team won.  Features that are less likely to affect a game's headline, such as the number of points scored by the top scorer on the winning team, are given less weight.

Limitations
-----------

There are cases where our algorithm will not work well.  Imagine a recent game that happened to be closest to [an old Wizards-Raptors game from 2002](http://www.espn.com/nba/game?gameId=221030028), which had the headline
> Jordan's play as ugly as teammates' in loss to Raptors

It would be hard to use the old game's headline as a template for a headline for the new game.  There are at least two issues.
1. The name "Michael Jordan" is never identified by our web scraping program since he did not lead the Wizards in scoring, rebounding, or assists.  This means that we have no way of finding and removing or replacing "Jordan" from the old headline. 
2. Even if we scraped the full roster of each team, so that our program could recognize "Jordan" as a name that could be replaced, it is hard to imagine what criteria we would use to choose a replacement.  Jordan is mentioned in the headline soley because of his legacy in basketball.  That kind of context is hard to identify using the very basic game data that we collect.


Description of files:
=====================

The main program is **nba_headline_generator.py**.  The KNN model is trained in **knn_model.py**, and the model is stored as **headline_knn.joblib**. The next most important files are the **games.py** and **features.py** modules, where we define the classes *Game* and *Feature* respectively.  Game objects are how we model games and Feature objects are what we use to extract feature vectors for those games.  The programs **espn_id_finder.py** and **dataframe_builder.py** are short programs to gather and save raw data for offline usage.


nba_headline_generator.py
-------------------------

This program uses the model trained in knn_model.py to find a historical game that is similar to a given game.  The headline of the historical game is used as a template for the headline we generate for the new game.  Numerous find/replace operations are applied to the template to update historical team names, scores, and so on to the context of the new game.

knn_model.py
------------

This program trains a KNN model to find nearest historical game to a given new game, as measured by a custom-defined metric. This is done using SciKit-Learn's KNeighborsClassifer.  The raw training data (historical games and their headlines) are loaded from a .csv file.  For each game, a feature vector is generated and stored as a dictionary, and the game's headline is stored as its label.  All such feature vectors and labels are gathered together and stored as a lists `X` and `y` respectively.  This list `X` is preprocessed using a dictionary vectorizer and a standardizer.  Finally, a K-nearest-neighbours model is trained on `X` and `y` using `K = 1` and a weighted Minkowski metric.  Predicting the label of the new game returns the headline of the new game's nearest neighbour.

games.py
--------

This is a module that defines the *Game* class.  An instance of the Game class takes an ESPN "game ID" as a parameter.  This ID is an integer used by ESPN to identify NBA games in their website URLS. For example, a particular game in 2005 is summarized on the web page

http://www.espn.com/nba/game?gameId=250506027

The game ID of this game is `250506027` and all pages on espn.com relating to this game (pages containing play-by-play, box score, etc) include this ID in their URLs.

When a Game object is instantiated, the game summary page identified by the given game ID is scraped for basic information.  That information is stored as attributes of the Game object.

**Parameters:** Game(game_id, df_path = None)
```
  game_id - ESPN game ID given as either an integer or a string.
  df_path - file path of a .csv file containing data for the given ID. If no file path is given, the game data 
            is scraped from ESPN if possible.
```

**Attributes:**
```
  .headline - string containing the headline of the game
  .winner - string, either 'home' or 'away'
  .names - dictionary containing variants of the home and away team names
  .scores - dictionary containing the home and away team scores
  .quarters - integer number of quarters played (>4 if overtime)
  .pts - dictionary of stats of the game's point leaders
  .reb - dictionary of stats of the game's rebounding leaders
  .ast - dictionary of stats of the game's assist leaders
  .n_game - integer current game in the series
  .home_wins - int current number of wins for the home team in the series
  .away_wins - int current number of wins for the away team in the series
```

**Methods:**
```
  .to_dict - collect all attributes as a dictionary in an appropriate format to pass to a pandas dataframe as a
             row
```

features.py
-----------

This module defines the *Feature* class.  Each Feature object is a function taking a Game object to a real number, along with a weight. The function defines the value of a component of a Game's feature vector (so `k` Features correspond to the components of a feature vector of length `k`). The weight of a Feature object is used when constructing the metric for the KNN model.

**Parameters:** Feature(name, weight, value_fcn)
```
	name - (str) the name of the feature
	weight - (int) the weight of the feature, to be used when defining the metric of the nearest neighbours 
           model
	value_fcn - a function taking a Game object and returning a real number.  
```
The `value_fcn` is the defining function of the feature (e.g. the function 	computes the difference in each team's point totals, or the number of games played so far in the series, etc).

**Attributes:**
```
	.name = self.name
	.weight = self.weight
```
**Methods:**
```
	.value(Game) - applies the value_fcn of the Feature to the given Game object.
```
The features.py module also contains a function assemble_feature_vector which takes a Game object an returns its feature vector.  The feature vector is formatted as a dictionary, which can then be passed to SciKit-Learn's DictVectorizer.


The **features.py** module contains the definitions of the specific game features we use, as well as a function `assemble_feature_vector` which generates a dictionary of feature values for a given Game object.


espn_id_finder.py
-----------------

An ESPN game ID is a 9 digit integer, and there are far fewer games than there are possible IDs.  The program espn_id_finder.py generates a .txt file with a list of valid game IDs. This is done by visiting, for each team and each year, the web page containing the game schedule for that team and year.  Each game listed on such a schedule page is also a hyperlink to the corresponding summary page for that game.  The game's ID may be scraped from that hyperlink.

This is the program that generated `espn_game_ids_postseason_2003-2018.txt`.


dataframe_builder.py
--------------------

A short script that scrapes raw training data from espn.com and saves it as a .csv file, so ESPN does not need to be scraped repeatedly during development of the main program.  

This is the program that generated `raw_data.csv`.
