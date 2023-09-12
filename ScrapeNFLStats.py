from bs4 import BeautifulSoup
import requests
import pandas as pd

file_path = 'PATH/2022_nfl_games.txt'
base_url = 'https://www.cbssports.com/nfl/gametracker/boxscore/'

#Read in file containing all 2022 games formatted correctly
file = open(file_path, 'r')
games = file.readlines()
games = [game.strip() for game in games]


def fetch_game_info(url_link, dt):
    try:
        source = requests.get(url_link)
        source.raise_for_status #Throw error in case that request doesn't work
        soup = BeautifulSoup(source.text,'html.parser')

        #Find Away and Home Team names, pass yds, rush yds, tot yds
        #Form Allowed Yards Dataframe, including opponent, rush, pass, tot
        ###############################################################
        teams = soup.find_all('div', class_= "abbr")
        away_tm = teams[0].get_text().strip()
        home_tm = teams[1].get_text().strip()
        
        home_stats = soup.find_all('td', class_="stat-value home")
        home_pass = home_stats[0].get_text()
        home_rush = home_stats[1].get_text()
        home_yds = home_stats[2].get_text()

        away_stats = soup.find_all('td', class_="stat-value away")
        away_pass = away_stats[0].get_text()
        away_rush = away_stats[1].get_text()
        away_yds = away_stats[2].get_text()

        # team, opponent, allowed pass, allowed rush, allowed total
        allowed_data = []
        allowed_data.append([away_tm, home_tm, home_pass, home_rush, home_yds, dt])
        allowed_data.append([home_tm, away_tm, away_pass, away_rush, away_yds, dt])
        allowed_stats = pd.DataFrame(allowed_data, columns=['TEAM', 'OPP', 'ALL_PASS', 'ALL_RUSH', 'ALL_TOT', 'Date'])

        #Find players names, positions, stat lines
        ###############################################################
        players = soup.find_all('tr', class_ = 'no-hover data-row')
        player_info_list = []
        for player in players:
            name = player.find('td', class_="name-element").a.text.strip()
            elts = [x.get_text() for x in player.find_all('td', class_="number-element")]
            pos = player.find('div', class_ = "player-name-num-pos").get_text()
            team = str(player.find('td', class_ = "hover-element"))
            loc1 = team.find("data-team-abbr")
            loc2 = team.find('" data-team-id')
            team = team[loc1+16:loc2]
            spce = pos.rfind(' ')
            pos = pos[(spce + 1):].strip()
            numelts = len(elts)
            player_info = {'name': name, 'pos' : pos, 'elts' : elts, 'numelts' : numelts, 'team' : team}
            player_info_list.append(player_info)
        ###############################################################
        

        #Store rushing stats, receiving stats in separate data frames
        ###############################################################
        rushing_data = []
        receiving_data = []
        for player_info in player_info_list:
            if (player_info['pos'] == 'WR' or player_info['pos'] == 'RB') and (player_info['numelts'] == 5 or player_info['numelts'] == 6):
                if player_info['numelts'] == 5:
                    tmp = [player_info['name']] + player_info['elts'] + [player_info['pos']] + [player_info['team']] + [dt]
                    rushing_data.append(tmp)

                if(player_info['numelts'] == 6): #receiving stats stats
                    tmp = [player_info['name']] + player_info['elts'] + [player_info['pos']] + [player_info['team']] + [dt]
                    receiving_data.append(tmp)
        rushing_stats = pd.DataFrame(rushing_data, columns=['RUSHING', 'ATT', 'YDS', 'TD', 'LG', 'FPTS', 'POS', 'TEAM', 'DATE'])
        receiving_stats = pd.DataFrame(receiving_data, columns=['RECEIVING', 'TAR', 'REC', 'YDS', 'TD', 'LG', 'FPTS', 'POS', 'TEAM', 'DATE'])
        ###############################################################
        return(allowed_stats, rushing_stats, receiving_stats)
        
    except Exception as e:
        print("error :(")

all_allowed_stats = pd.DataFrame(columns=['TEAM', 'OPP', 'ALL_PASS', 'ALL_RUSH', 'ALL_TOT', 'Date'])
all_rushing_stats = pd.DataFrame(columns=['RUSHING', 'ATT', 'YDS', 'TD', 'LG', 'FPTS', 'POS', 'TEAM', 'DATE'])
all_receiving_stats = pd.DataFrame(columns=['RECEIVING', 'TAR', 'REC', 'YDS', 'TD', 'LG', 'FPTS', 'POS', 'TEAM', 'DATE'])

a1 = pd.DataFrame() 
a2 = pd.DataFrame()
a3 = pd.DataFrame()

for game in games:
    a1, a2, a3 = fetch_game_info(base_url + game, game[4:12])
    all_allowed_stats = pd.concat([all_allowed_stats, a1], ignore_index=True, join='outer', axis=0)
    all_rushing_stats = pd.concat([all_rushing_stats, a2], ignore_index=True)
    all_receiving_stats = pd.concat([all_receiving_stats, a3], ignore_index=True)
    print(game)

all_allowed_stats.to_csv('PATH/all_allowed_stats.csv', index=False)
all_rushing_stats.to_csv('PATH/all_rushing_stats.csv', index=False)
all_receiving_stats.to_csv('PATH/all_receiving_stats.csv', index=False)