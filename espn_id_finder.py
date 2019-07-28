# -*- coding: utf-8 -*-
"""
Created on Tue May  7 15:58:08 2019

@author: danie
"""

'''
    This program creates a list of ESPN NBA game ID numbers by visiting each
    team's schedule page for each year in the selected range and scraping the 
    IDs for home games (to avoid double-counting).  Game IDs may be found for
    either the regular season or the postseason. 
    
    The ID numbers are saved to a file: 
        "espn_game_ids_(season type)_(start year)-(end year).txt"
'''

import urllib3
from bs4 import BeautifulSoup

#parameters for the scope of the scrape
start_year = 2003
end_year = 2018
season_type = 3     #see season_type_names below

#static elements of the urls that are to be looked up. Typical format below:
#http://www.espn.com/nba/team/schedule/_/name/wsh/season/2016/seasontype/2
schedule_root = 'http://www.espn.com/nba/team/schedule/_/name/'
team_abbreviations = ['atl', 'bos', 'bkn', 'cle', 'cha', 'chi', 'dal', 'den', 'det', 'gs', 'hou', 'ind', 'lac', 'lal', 'mem', 'mia', 'mil', 'min', 'no', 'ny', 'okc', 'orl', 'phi', 'phx', 'por', 'sac', 'sa', 'tor', 'utah', 'wsh']
season_type_names = {1 : 'preseason', 2 : 'regular_season' , 3 : 'postseason'} 

id_file_path = 'espn_game_ids_{0}_{1}-{2}.txt'.format(season_type_names[season_type],str(start_year),str(end_year))

if __name__ == '__main__':
    
    #open up a connection pool
    http = urllib3.PoolManager()
    
    #open up a text file to write the game IDs into
    with open(id_file_path, 'w') as id_file:
        
        for year in range(start_year,end_year+1):
            
            for team in team_abbreviations:
                #get the html from the appropriate url and parse it into a tree 
                #called 'soup'
                url = schedule_root + team + '/season/' + str(year) + '/seasontype/' + str(season_type)  
                r = http.request('GET', url)
                soup = BeautifulSoup(r.data, 'html.parser')
                
                #each 'a' tag in the tag with class 'ml4' links to a game in the 
                #season
                number_of_games_in_season = len(soup.select('.ml4 a'))
                
                for i in range(number_of_games_in_season):
                    #find the tag with the href link to the i^th game
                    game_link_tag = soup.select('.ml4 a')[i]
                    #find the tag with the "vs" or "@" string indicating whether 
                    #the game was at home or not
                    location_tag = game_link_tag.parent.parent.previous_sibling
                    
                    #grab the game ID as an integer
                    game_id = game_link_tag.get('href')[-9:]
                    #grab the 'vs' or '@' string
                    game_location = location_tag.select('.pr2')[0].text
                    
                    if game_location == 'vs':
                        id_file.write(game_id + '\n')
                        
    
    
