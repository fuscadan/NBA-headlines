# -*- coding: utf-8 -*-
"""
Created on Sat May 18 17:56:28 2019

@author: danie
"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from sklearn import pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.externals import joblib
import pandas as pd
import games as g
import features as f
import dataframe_builder


'''
    given a list of dictionaries (each list entry storing a dictionary of
    features for a sample), vectorize the list into a list of feature vectors,
    and standardize those vectors.  Train a KNN model with K = 1.  The label of
    each training example is the headline from that game.  The model is saved
    to a file specified by 'knn_path'.
'''

knn_path = 'headline_knn.joblib'


if __name__ == '__main__':

    '''
        Here we load the raw game data from a csv file into a pandas dataframe
    '''
    
    raw_data_file_path = dataframe_builder.raw_data_file_path 
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
    
    
    #ready the pipeline for the KNN model and train it
    headline_knn = pipeline.Pipeline([('vectorizer', vectorizer) , ('standardizer' , standardizer) , ('knn', knn)])
    
    headline_knn.set_params(vectorizer__sparse=False,
                            knn__n_neighbors=1, 
                            knn__metric = 'wminkowski',
                            knn__metric_params = {'w' : weights} ).fit(X,y)
    
    #save the model to a file 'headline_knn.joblib'
    joblib.dump(headline_knn,knn_path)