# -*- coding: utf-8 -*-
"""
Created on Mon May 20 18:44:07 2019

@author: danie
"""

'''
    Defines the 'Feature' object. Each Feature object is a function taking
    a Game object to a real number, along with a weight. The function defines
    the value of a component of a Game's feature vector (so k Features
    correspond to the components of a feature vector of length k). The weight
    of a Feature object is used when constructing the metric for the KNN model.
    
    Parameters: Feature(self, name, weight, value_fcn)
        name = string name of the feature
        weight = int weight given to the feature when defining the model's 
            metric
        value_fcn = function that takes a Game object and returns a real number
            representing the value of the Feature for the given Game
    
    Methods:
        .name - returns the 'name' string
        .weight - returns the 'weight' int
        .value_fnc(game) - applies the value_fcn to the Game object 'game'
    
    Class methods:
        .getinstances - returns the set of all instances of the Feature class. 
            This is taken from the example found at:
                
            http://effbot.org/pyfaq/how-do-i-get-a-list-of-all-instances-of-a-given-class.htm
'''

import weakref

class Feature:
    
    _instances = []
    
    def __init__(self,name,weight,value_fcn):
        self._instances.append(weakref.ref(self))
        self.name = name
        self.weight = weight
        self.value_fcn = value_fcn
    
    def value(self,game):
        return self.value_fcn(game)

    @classmethod
    def getinstances(cls):
        #dead = set()
        feature_list = []
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                feature_list.append(obj)
            else:
                cls._instances.remove(ref)
        return feature_list
        #cls._instances -= dead
        
'''
    Here we define the features of Game objects
    
    number of quarters
    abs value of point differential
    signed difference of scores for each quarter
    did home team win?
    winner pt total
    signed difference between top scorers pt totals
    home team wins in the series
    away team wins in the series  
'''

def fnc_1(game):
    return game.quarters

quarters = Feature('quarters', 10, fnc_1)


def fnc_2(game):
    return abs(game.scores['away'][0] - game.scores['home'][0])

point_difference = Feature('point_difference', 5, fnc_2)


def fnc_3(game):
    if game.winner == 'home':
        return game.scores['home'][1] - game.scores['away'][1]
    else:
        return game.scores['away'][1] - game.scores['home'][1]
    
q1_difference = Feature('q1_difference', 2, fnc_3)


def fnc_4(game):
    if game.winner == 'home':
        return game.scores['home'][2] - game.scores['away'][2]
    else:
        return game.scores['away'][2] - game.scores['home'][2]
    
q2_difference = Feature('q2_difference', 2, fnc_4)


def fnc_5(game):
    if game.winner == 'home':
        return game.scores['home'][3] - game.scores['away'][3]
    else:
        return game.scores['away'][3] - game.scores['home'][3]
    
q3_difference = Feature('q3_difference', 3, fnc_5)


def fnc_6(game):
    if game.winner == 'home':
        return game.scores['home'][4] - game.scores['away'][4]
    else:
        return game.scores['away'][4] - game.scores['home'][4]
    
q4_difference = Feature('q4_difference', 4, fnc_6)


def fnc_7(game):
    if game.winner == 'home':
        return 1
    else:
        return 0

win_at_home = Feature('win_at_home', 10, fnc_7)


def fnc_8(game):
    if game.winner == 'home':
        return game.scores['home'][0]
    else:
        return game.scores['away'][0]

winner_pts = Feature('winner_pts', 4, fnc_8)


def fnc_9(game):
    if game.winner == 'home':
        return game.pts['home']['pts'] - game.pts['away']['pts']
    else:
        return game.pts['away']['pts'] - game.pts['home']['pts']

pts_leader_difference = Feature('pts_leader_difference', 4, fnc_9)


def fnc_10(game):
    return game.home_wins

home_wins = Feature('home_wins',12, fnc_10)


def fnc_11(game):
    return game.away_wins

away_wins = Feature('away_wins',12,fnc_11)


def fnc_12(game):
    if 'EAST' in game.round:
        return 1
    elif 'WEST' in game.round:
        return -1
    else:
        return 0

conference = Feature('conference',5,fnc_12)

def fnc_13(game):
    if 'NBA' in game.round:
        return 5
    elif 'SEMIFINALS' in game.round:
        return 1
    elif 'FINALS' in game.round:
        return 3
    else:
        return 0
    
playoff_round = Feature('playoff_round',5,fnc_13)


#maybe include the triple double feature later



'''
    create the list of features defined above, as well as the list of their
    corresponding weights
'''

feature_list = Feature.getinstances()

weights = []
for feature in feature_list:
    weights.append(feature.weight)


'''
    a function that creates a feature vector (as a dictionary) for a given game
'''

def assemble_feature_vector(game):
    feature_dictionary = {}
    for feature in feature_list:
        feature_dictionary[feature.name] = feature.value(game)
    
    return feature_dictionary

def weight(feature_name):
    for feature in feature_list:
        if feature.name == feature_name:
            return feature.weight






