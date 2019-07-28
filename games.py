# -*- coding: utf-8 -*-
"""
Created on Thu May  9 17:53:10 2019

@author: danie
"""

'''
    Defines a class 'Game'.  When a Game object is created, game data is either
    scraped from espn.com or read from a csv file.  This data is stored as 
    attributes of the Game object.
    
    Parameters: Game(game_id, df_path = None)
        game_id - ESPN game ID given as either an integer or a string.
        df_path - file path of a .csv file containing data for the given ID. If
                  no file path is given, the game data is scraped from ESPN if
                  possible.
 
    Attributes:
        .headline - string containing the headline of the game
        .winner - string, either 'home' or 'away'
        .names - dictionary containing variants of the home and away team 
                 names
        .scores - dictionary containing the home and away team scores
        .quarters - integer number of quarters played (>4 if overtime)
        .pts - dictionary of stats of the game's point leaders
        .reb - dictionary of stats of the game's rebounding leaders
        .ast - dictionary of stats of the game's assist leaders
        .n_game - integer current game in the series
        .home_wins - int current number of wins for the home team in the series
        .away_wins - int current number of wins for the away team in the series
        
    Methods:
        .to_dict - collect all attributes as a dictionary in an appropriate 
                   format to pass to a pandas dataframe as a row
    
    Example: game_id = 230501002
        game summary url:  http://www.espn.com/nba/game?gameId=230501002
        
        game = Game(230501002)
        game.winner = 'home'
        game.names['home']['city'] = 'Boston'
        game.names['away']['team'] = 'Pacers'
        game.leaders['home']['pts'] = 'Paul Pierce'
        game.n_game = 6
        game.home_wins = 4
        game.headline = 'Pierce, Celtics eliminate Pacers with Game 6 rout'
'''


from bs4 import BeautifulSoup
import urllib3
import pandas as pd
import ast

http = urllib3.PoolManager()
game_summary_root = 'http://www.espn.com/nba/game?gameId='

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Game:
    
    def __init__(self,game_id,df_path=None):
        if type(game_id) == str:
            game_id = int(game_id.strip())
        
        if df_path == None:
            
            url = game_summary_root + str(game_id)
            r = http.request('GET' , url)
            soup = BeautifulSoup(r.data, 'html.parser')
            
            '''
                The headline is pulled from the panel at the top middle, just below
                the top banner containing the scores.
            '''
    
            self.headline = soup.select('.top-stories__story-header h1')[0].text
            
            
            '''
                The playoff round of the current game is mentioned in a line of
                text above the box score. We pull that round here.
            '''
            #find the tag with the relevant text
            round_tag = soup.select('.game-details')[0]
            #parse the text and keep only the playoff round
            self.round = round_tag.text.split(' - ')[0]
            
            
            '''
                Here we pull data from the top banner on the game summary page. We 
                find the home team, away team, winner, box score, and whether the 
                game went to OT.
            '''
            
            #These are the relevant HTML tags, starting with the parent tag for the
            #top banner.
            top_banner = soup.select('.competitors')[0]
            #examine the tags containing the away and home team's data
            away_tag = top_banner.find_all('div' , attrs={'class': 'team away'})[0]
            home_tag = top_banner.find_all('div' , attrs={'class': 'team home'})[0]
            #examine the tag containing the box score
            score_tag = top_banner.select('.game-status')[0]
            away_scores_tags = list(score_tag.find_all('tr')[1].children)
            home_scores_tags = list(score_tag.find_all('tr')[2].children)
            
            
            #who won the game
            self.winner = top_banner.parent['class'][-1][:4]
            
            #get the variations of the home and away team's name and city
            self.names = { 'away' : {'team' : away_tag.select('.short-name')[0].text,
                                'city' : away_tag.select('.long-name')[0].text,
                                'abbr' : away_tag.select('.abbrev')[0].text} ,
                      'home' : {'team' : home_tag.select('.short-name')[0].text,
                                 'city' : home_tag.select('.long-name')[0].text,
                                 'abbr' : home_tag.select('.abbrev')[0].text} }
            
            #find the quarterly and total scores
            number_of_quarters = len(away_scores_tags) - 2
            
            #build lists containing the home and away team scores. Total scores at 
            #index 0, quarterly scores stored at the following indices.
            away_scores = [int(away_scores_tags[number_of_quarters + 1].text)]
            for quarter in range(number_of_quarters):
                away_scores.append(int(away_scores_tags[quarter + 1].text))
            
            home_scores = [int(home_scores_tags[number_of_quarters + 1].text)]
            for quarter in range(number_of_quarters):
                home_scores.append(int(home_scores_tags[quarter + 1].text))
            
            self.scores = { 'away' : away_scores, 'home' : home_scores}
            
            self.quarters = number_of_quarters
            
            '''
                Here we collect data from the "Game Leaders" panel appearing on the
                left.
            '''
            
            #finds game leaders in points, rebounds and assists. There are three 
            #<div> tags with the class 'leader-column'; one for the game leaders in
            #each of points, rebounds and assists. The beautifulsoup object 
            #leader_panel is a list of these three tags in that order. Each of 
            #these tags contains two tags of class 'long-name', each containing the
            #full name of either the away or home team's leader in a stat category. 
            leader_tags = soup.select('.leader-column')
            
            #examine the tags containing the leading point scorer stats        
            away_pts_tags = leader_tags[0].select('.game-leader-details')[0].find_all('dd')
            home_pts_tags = leader_tags[0].select('.game-leader-details')[1].find_all('dd')
            
            self.pts = { 'away' : {'leader' : leader_tags[0].select('.long-name')[0].text,
                                   'pts' : int(away_pts_tags[0].select('.value')[0].text),
                                   'fg' : away_pts_tags[1].select('.value')[0].text,
                                   'ft' : away_pts_tags[2].select('.value')[0].text} ,
                        'home' : {'leader' : leader_tags[0].select('.long-name')[1].text,
                                   'pts' : int(home_pts_tags[0].select('.value')[0].text),
                                   'fg' : home_pts_tags[1].select('.value')[0].text,
                                   'ft' : home_pts_tags[2].select('.value')[0].text} }
    
            away_reb_tags = leader_tags[1].select('.game-leader-details')[0].find_all('dd')
            home_reb_tags = leader_tags[1].select('.game-leader-details')[1].find_all('dd')
            
            self.reb = { 'away' : {'leader' : leader_tags[1].select('.long-name')[0].text,
                                   'reb' : int(away_reb_tags[0].select('.value')[0].text),
                                   'dreb' : int(away_reb_tags[1].select('.value')[0].text),
                                   'oreb' : int(away_reb_tags[2].select('.value')[0].text)} ,
                        'home' : {'leader' : leader_tags[1].select('.long-name')[1].text,
                                   'reb' : int(home_reb_tags[0].select('.value')[0].text),
                                   'dreb' : int(home_reb_tags[1].select('.value')[0].text),
                                   'oreb' : int(home_reb_tags[2].select('.value')[0].text)} }
        
            away_ast_tags = leader_tags[2].select('.game-leader-details')[0].find_all('dd')
            home_ast_tags = leader_tags[2].select('.game-leader-details')[1].find_all('dd')
            
            self.ast = { 'away' : {'leader' : leader_tags[2].select('.long-name')[0].text,
                                   'ast' : int(away_ast_tags[0].select('.value')[0].text),
                                   'to' : int(away_ast_tags[1].select('.value')[0].text),
                                   'min' : int(away_ast_tags[2].select('.value')[0].text)} ,
                        'home' : {'leader' : leader_tags[2].select('.long-name')[1].text,
                                   'ast' : int(home_ast_tags[0].select('.value')[0].text),
                                   'to' : int(home_ast_tags[1].select('.value')[0].text),
                                   'min' : int(home_ast_tags[2].select('.value')[0].text)} }
            
            '''
                To compute the standings in the playoff series at the time of the 
                game's conclusion, data from the 'series-wrap' panel appearing on 
                the right (just below "NBA news") is collected, and the number of 
                wins in the series is counted for each team.
                NOTE:
                The "home_team_win_total" counts the number of wins for the home 
                team of the current game. It is not the number of times a game in 
                the series was won by the team hosting the match.
            '''
            
            #examine the parent tag of the 'series-wrap' panel
            series_wrap_tag = soup.select('.series-wrap')  
            #find the tag containing the data for the game with the current game_id
            current_game_tag = series_wrap_tag[0].find_all('a' , attrs={'data-gameid': str(game_id)})[0].parent
            #find which game in the series the current game is
            current_game_number = int(current_game_tag.find_all('div', class_='cscore_series')[0].text[-1:])
            
            #initialize win total counters
            home_team_win_total = 0
            away_team_win_total = 0
            
            #count the number of wins for the current home and away teams
            for i in range(current_game_number):
                #find the first and second names appearing in the currently 
                #examined box of the series wrap panel.
                first_name = current_game_tag.select('.cscore_name--abbrev')[0].text
                second_name = current_game_tag.select('.cscore_name--abbrev')[1].text
                #formatting in each box of the series wrap panel either bolds the 
                #'home' or 'away' team. The variable 'bold_name' is either 'home' 
                #or 'away', whichever is being bolded.
                bold_name = current_game_tag['class'][2][8:12]
            
                if (first_name == self.names['home']['abbr'] and bold_name == 'away') or (second_name == self.names['home']['abbr'] and bold_name == 'home'):
                    home_team_win_total += 1
                else:
                    away_team_win_total += 1
                #advance to the next tag, which contains the outcome of the 
                #previous game
                if current_game_tag.next_sibling != None:
                    current_game_tag = current_game_tag.next_sibling
            
            self.home_wins = home_team_win_total
            self.away_wins = away_team_win_total
            self.n_game = current_game_number
            
        else:
            df = pd.read_csv(df_path, index_col = 0)
            game_row = df.loc[game_id]
            
            self.headline = game_row['headline']
            self.round = game_row['round']
            self.winner = game_row['winner']            
            self.names = ast.literal_eval(game_row['names'])
            self.scores = ast.literal_eval(game_row['scores'])
            self.quarters = game_row['quarters']
            self.pts = ast.literal_eval(game_row['pts'])
            self.reb = ast.literal_eval(game_row['reb'])
            self.ast = ast.literal_eval(game_row['ast'])
            self.n_game = game_row['n_game']
            self.home_wins = game_row['home_wins']
            self.away_wins = game_row['away_wins']
    
    
    #method to collect all attributes as a dictionary in an appropriate format
    #to pass to a pandas dataframe as a row
    def to_dict(self):
        return {'headline' : [self.headline] ,
                'round' : [self.round],
                'winner' : [self.winner] , 
                'names' : [self.names] , 
                'scores' : [self.scores] ,
                'quarters' : [self.quarters] ,
                'pts' : [self.pts] , 
                'reb' : [self.reb] ,
                'ast' : [self.ast] ,
                'n_game' : [self.n_game] ,
                'home_wins' : [self.home_wins] ,
                'away_wins' : [self.away_wins] }



#meant to test the games module if it is run as the main program
if __name__ == '__main__':
    game_id = '401029410\n'
    
    game = Game(game_id, 'raw_data.csv')
    print('headline: ', game.headline)
    print('\n round: ', game.round)
    print('\n winning team: ', game.winner)
    print('\n team names: \n', game.names)
    print('\n number of quarters played: ', game.quarters)
    print('\n total and quarterly scores: \n', game.scores)
    print('\n points leaders stats: \n', game.pts)
    print('\n rebounding leaders stats: \n', game.reb)
    print('\n assist leaders stats: \n', game.ast)
    print('\n game number in the series: ', game.n_game)
    print('\n number of wins for current away team: ', game.away_wins)
    print('\n number of wins for current home team: ', game.home_wins)