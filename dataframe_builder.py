# -*- coding: utf-8 -*-
"""
Created on Sat May 18 21:08:21 2019

@author: danie
"""
'''
    simple script to scrape basic NBA game data from ESPN using the'espn_nba' 
    module and store the data in a pandas dataframe
'''

import pandas as pd
import espn_nba

#give the file path of the text file containing the list of espn game ids.
id_file_path = 'espn_game_ids_postseason_2003-2018.txt'

#read the game ids from the text file.
with open(id_file_path , 'r') as id_file:
    id_list = id_file.readlines()

#initialize the pandas dataframe that will hold all the raw game data
df = pd.DataFrame()

#add raw game data row by row into the dataframe df
for game_id in id_list:
    #a few game pages have variations in the standard html structure that 
    #will not be parsed correctly by the BeautifulSoup code in the Game class.
    #A simple try catch handles these exceptions.
    try:
        game = espn_nba.Game(game_id)
        
        new_row = pd.DataFrame(game.to_dict() , index=[game_id])
        
        df = df.append(new_row)
    except:
        print('missing data at game id ' + game_id)

#export the dataframe containing raw game data to a csv file
df.to_csv('raw_data.csv')
    