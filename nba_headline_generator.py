# -*- coding: utf-8 -*-
"""
Created on Sat May 18 17:56:28 2019

@author: danie
"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from sklearn import pipeline
from sklearn.feature_extraction import DictVectorizer
import pandas as pd
import games as g
import features as f



'''
    given a list of dictionaries (each list entry storing a dictionary of
    features for a sample), vectorize the list into a list of feature vectors,
    and standardize that list.  To generate a headline for new game data, use
    KNN with n_neighbors = 1 and a specially constructed metric to find the
    closest historical game and take its headline (with team/player names,
    scores, etc. adjusted to the new context).
'''

'''
    Here we load the raw game data from a csv file into a pandas dataframe
'''

raw_data_file_path = 'raw_data.csv' 
raw_data = pd.read_csv(raw_data_file_path, index_col = 0)
id_list = raw_data.index


'''
    create the lists X and y for the feature vectors and labels respectively 
    of the training set
'''

X = []
y = []

for game_id in id_list:
    game = g.Game(game_id,df_path = raw_data_file_path)

    X.append(f.assemble_feature_vector(game))
    y.append([game.headline, game_id])


'''
    train the KNN model with K = 1 and a weighted Minkowski metric
'''

#instatiate the transforms and estimator we will use
vectorizer = DictVectorizer()
standardizer = preprocessing.StandardScaler()
knn = KNeighborsClassifier()

'''
    construct the list of weights to be used for the Minkowski metric. The
    vectorizer orders the features alphabetically, and we must ensure that the 
    list of weights matches this ordering. This is done by manually 
    constructing the list of feature names and sorting it. Then for each 
    feature name in this sorted list, the corresponding weight is called and 
    added to the list of weights.
'''

feature_names = []
for feature in f.feature_list:
    feature_names.append(feature.name)
feature_names.sort()

weights = []
for feature in feature_names:
    weights.append(f.weight(feature))


headline_knn = pipeline.Pipeline([('vectorizer', vectorizer) , ('standardizer' , standardizer) , ('knn', knn)])

headline_knn.set_params(vectorizer__sparse=False,
                        knn__n_neighbors=1, 
                        knn__metric = 'wminkowski',
                        knn__metric_params = {'w' : weights} ).fit(X,y)


'''
    load new game data as a dictionary
'''

game_id = 401131843
new_game = g.Game(game_id)
X_new = f.assemble_feature_vector(new_game)

'''
    find and print the headline from the closest historical game
'''

prediction = headline_knn.predict(X_new)

print(prediction[0])



