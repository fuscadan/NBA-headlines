# -*- coding: utf-8 -*-
"""
Created on Sat May 18 17:56:28 2019

@author: danie
"""

from sklearn.externals import joblib
import games as g
import features as f
import knn_model
import dataframe_builder
import argparse


def get_nearest_game(new_game, knn_path, raw_data_file_path):

    '''
        use the KNN model trained in 'knn_model.py' to find a suitable historical 
        template for the new headline we will generate.
            new_game - Game object for which we wish to find a nearest 
                historical game
            knn_path - string - location of the KNN model saved to file
            raw_data_file_path - string - location of the data file
                
            returns a Game object of the nearest historical game to new_game
    '''
    
    #assemble a feature vector for the given game
    X_new = f.assemble_feature_vector(new_game)
    
    #load the KNN model trained by 'knn_model.py'
    headline_knn = joblib.load(knn_path)
    
    #find the most similar historical game and pull its game ID for future 
    #reference
    prediction = headline_knn.predict(X_new)
    historical_id = int(prediction[0][1])
    
    #load the historical game's data as a Game object and return it    
    return g.Game(historical_id,df_path = raw_data_file_path) , historical_id


def find_replace(historical_game,new_game):

    '''
        find and replace names, scores, etc from the historical game's headline 
        with the new names.
            historical_game - Game object for the historical game whose
                headline will be used as a template
            new_game - Game object for the new game whose headline is to be
                generated from the template
        
            returns a string of the historical game's headline after many
            find/replace actions to update the context to the new game.
    '''
    
    new_headline = historical_game.headline
    
    #first swap out team nicknames with full names
    nicknames = ['Celts', '6ers', 'Sixers', 'Raps', 'Cavs', 'Wiz', 'Clips', 'Mavs', 'Pels', 'Griz', 'Grizz', 'Nugs', 'Wolves', 'T-Wolves', 'Blazers']
    full_names = ['Celtics', '76ers', '76ers', 'Raptors', 'Cavaliers', 'Wizards', 'Clippers', 'Mavericks', 'Pelicans', 'Grizzlies', 'Grizzlies', 'Nuggets', 'Timberwolves', 'Timberwolves', 'Trail Blazers']
    
    for i in range(len(nicknames)):
        new_headline = new_headline.replace(nicknames[i] , full_names[i])
    
    #need to use a placeholder like 'away_team' or else we might end up with the
    #same team name for both the home and away teams. Eg consider find/replacing
    #a historical bucks @ 76ers game with a new raptors @ bucks game.
    new_headline = new_headline.replace(historical_game.names['away']['team'], 'away_team')
    new_headline = new_headline.replace(historical_game.names['away']['city'], 'away_city')
    new_headline = new_headline.replace(historical_game.names['away']['abbr'], 'away_abbr')
    
    new_headline = new_headline.replace(historical_game.names['home']['team'], new_game.names['home']['team'])
    new_headline = new_headline.replace(historical_game.names['home']['city'], new_game.names['home']['city'])
    new_headline = new_headline.replace(historical_game.names['home']['abbr'], new_game.names['home']['abbr'])
    
    new_headline = new_headline.replace('away_team', new_game.names['away']['team'])
    new_headline = new_headline.replace('away_city', new_game.names['away']['city'])
    new_headline = new_headline.replace('away_abbr', new_game.names['away']['abbr'])
    
    
    if str(historical_game.scores['home'][0]) + '-' + str(historical_game.scores['away'][0]) in new_headline:
        new_headline = new_headline.replace(str(historical_game.scores['home'][0]) + '-' + str(historical_game.scores['away'][0]),
                                            str(new_game.scores['home'][0]) + '-' + str(new_game.scores['away'][0]))
    elif str(historical_game.scores['away'][0]) + '-' + str(historical_game.scores['home'][0]) in new_headline:
        new_headline = new_headline.replace(str(historical_game.scores['away'][0]) + '-' + str(historical_game.scores['home'][0]),
                                            str(new_game.scores['away'][0]) + '-' + str(new_game.scores['home'][0]))
    else:
        new_headline = new_headline.replace(' ' + str(historical_game.scores['away'][0]), 'away_score')
        new_headline = new_headline.replace(' ' + str(historical_game.scores['home'][0]), ' ' + str(new_game.scores['home'][0]))
        new_headline = new_headline.replace('away_score', ' ' + str(new_game.scores['away'][0]))
    
    
    new_headline = new_headline.replace(' ' + str(historical_game.pts['away']['pts']), 'away_pts_ldr_pts')
    new_headline = new_headline.replace(' ' + str(historical_game.pts['home']['pts']), ' ' + str(new_game.pts['home']['pts']))
    new_headline = new_headline.replace('away_pts_ldr_pts', ' ' + str(new_game.pts['away']['pts']))
    
    
    if historical_game.pts['away']['leader'] in new_headline:
        new_headline = new_headline.replace(historical_game.pts['away']['leader'], new_game.pts['away']['leader'])
    elif historical_game.pts['away']['leader'].split(' ')[0] in new_headline:
        new_headline = new_headline.replace(historical_game.pts['away']['leader'].split(' ')[0], new_game.pts['away']['leader'].split(' ')[-1])
    elif historical_game.pts['away']['leader'].split(' ')[-1] in new_headline:
        new_headline = new_headline.replace(historical_game.pts['away']['leader'].split(' ')[-1], new_game.pts['away']['leader'].split(' ')[-1])
    
    if historical_game.pts['home']['leader'] in new_headline:
        new_headline = new_headline.replace(historical_game.pts['home']['leader'], new_game.pts['home']['leader'])
    elif historical_game.pts['home']['leader'].split(' ')[0] in new_headline:
        new_headline = new_headline.replace(historical_game.pts['home']['leader'].split(' ')[0], new_game.pts['home']['leader'].split(' ')[-1])
    elif historical_game.pts['home']['leader'].split(' ')[-1] in new_headline:
        new_headline = new_headline.replace(historical_game.pts['home']['leader'].split(' ')[-1], new_game.pts['home']['leader'].split(' ')[-1])
        
    return new_headline



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', '--game_id', type=int,
                        help='input a valid ESPN game ID for a game you wish to generate a headline for. If no ID specified, the program runs with a hard-coded ID.')
    
    parser.add_argument('-t','--template', action='store_true',
                        help='print the template headline and game ID along with the new headline')
    
    parser.add_argument('-m','--model',
                        help='filename of the trained KNN model to use')
    
    args = parser.parse_args()
    
    #take the given game ID and create a Game object for it
    if args.game_id == None:
        game_id = 401126819
    else:
        game_id = args.game_id
        
    new_game = g.Game(game_id)
    
    #get the nearest game (as a Game object), according to the saved KNN model
    #and the saved data
    if args.model == None:
        knn_path = knn_model.knn_path
    else:
        knn_path = args.model
    
    raw_data_file_path = dataframe_builder.raw_data_file_path

    historical_game , historical_id = get_nearest_game(new_game, knn_path, raw_data_file_path)
    
    #create the headline for the new game by find/replacing names in the old
    #headline
    new_headline = find_replace(historical_game,new_game)

    #Print the generated headline, and print the template headline and game ID 
    #if that option is enabled.
    if args.template:
        print('\n Template headline: ' + historical_game.headline)
        print(' Template game ID: ' + str(historical_id))
    
    print('\n Generated headline for game with ESPN ID = ' + str(game_id) + ': \n\n   ' + new_headline + '\n')