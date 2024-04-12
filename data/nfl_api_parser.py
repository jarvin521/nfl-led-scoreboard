import requests
import datetime
import time as t
#from utils import convert_time

URLs = ["http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard", "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard", \
    "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard", "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard", "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard" ]

# URLs = ["http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"]
# def get_game(team_name):
#     for i in range(5):
#         try:
#             res = requests.get(URL)
#             res = res.json()
#             for g in res['events']:
#                 if team_name in g['shortName']:
#                     info = g['competitions'][0]
#                     game = {'name': g['shortName'], 'date': g['date'],
#                             'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
#                             'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
#                             'down': info.get('situation', {}).get('shortDownDistanceText'), 'spot': info.get('situation', {}).get('possessionText'),
#                             'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
#                             'redzone': info.get('situation', {}).get('isRedZone'), 'possession': info.get('situation', {}).get('possession'), 'state': info['status']['type']['state']}
#                     return game
#         except requests.exceptions.RequestException as e:
#             print("Error encountered getting game info, can't hit ESPN api, retrying")
#             if i < 4:
#                 t.sleep(1)
#                 continue
#             else:
#                 print("Can't hit ESPN api after multiple retries, dying ", e)
#         except Exception as e:
#             print("something bad?", e)

def get_all_games():
    # for i in range(5):
    try:
        games = []
        for URL in URLs:
            response = requests.get(URL)    
            res = response.json()
            # i = 0
            for g in res['events']:
                info = g['competitions'][0]
                odds = info.get('odds', [{}])[0]
                if "nfl" in URL: 
                    if "Cincinnati Bengals" in g['name'] or "Minnesota Vikings" in g['name']:                       
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'nfl',
                            'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                            'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                            'down': info.get('situation', {}).get('shortDownDistanceText'), 'spot': info.get('situation', {}).get('possessionText'),
                            'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                            'redzone': info.get('situation', {}).get('isRedZone'), 'possession': info.get('situation', {}).get('possession'),
                            'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                        if odds: 
                            game['overUnder'] = odds.get('overUnder')
                            game['spread'] = odds.get('spread')
                        else:
                            game['overUnder'] = None
                            game['spread'] = None
                        games.append(game)
                if "college-football" in URL: 
                    if "Kentucky Wildcats" in g['name']:    
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'ncaa',
                            'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                            'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                            'down': info.get('situation', {}).get('shortDownDistanceText'), 'spot': info.get('situation', {}).get('possessionText'),
                            'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                            'redzone': info.get('situation', {}).get('isRedZone'), 'possession': info.get('situation', {}).get('possession'), 
                            'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                        if odds: 
                            game['overUnder'] = odds.get('overUnder')
                            game['spread'] = odds.get('spread')
                        else:
                            game['overUnder'] = None
                            game['spread'] = None
                        games.append(game)
                if "nba" in URL:
                    if "Minnesota Timberwolves" in g['name']:                       
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'nba',
                            'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                            'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                            'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                            'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                        if odds: 
                            game['overUnder'] = odds.get('overUnder')
                            game['spread'] = odds.get('spread')
                        else:
                            game['overUnder'] = None
                            game['spread'] = None
                        games.append(game)
                if "mens-college-basketball" in URL:
                    if "Kentucky Wildcats" in g['name']:                     
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'ncaa', 
                            'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                            'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                            'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                            'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                        if odds: 
                            game['overUnder'] = odds.get('overUnder')
                            game['spread'] = odds.get('spread')
                        else:
                            game['overUnder'] = None
                            game['spread'] = None
                        games.append(game)
                if "mlb" in URL:
                    if "Cincinnati Reds" in g['name'] or "Yankees" in g['name']:
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'mlb',
                            'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                            'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                            'quarter': info['status']['period'], 'balls': info.get('situation', {}).get('balls'), 'strikes': info.get('situation', {}).get('strikes'), 'outs': info.get('situation', {}).get('outs'),
                            'over': info['status']['type']['completed'],'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                        if odds: 
                            game['overUnder'] = odds.get('overUnder')
                            game['spread'] = odds.get('spread')
                        else:
                            game['overUnder'] = None
                            game['spread'] = None
                        games.append(game)
                    # i += 1
        return games
    except requests.exceptions.RequestException as e:
        print("Error encountered getting game info, can't hit ESPN api, retrying")
        # if i < 4:
        #     t.sleep(1)
        #     continue
        # else:
        #     print("Can't hit ESPN api after multiple retries, dying ", e)
    except Exception as e:
        print("something bad?", e)

# def which_game(games, fav_team):
#     # check for fav team first
#     for game in games:
#         if games[game]['hometeam'] == fav_team or games[game]['awayteam'] == fav_team:
#             return games[game]
#     # games should be sorted by date, earliest to latest
#     for game in games:
#         # testing purposes
#         # if games[game]['state'] == 'post':
#         #     return games[game]
#         if games[game]['state'] == 'in':
#             return games[game]
#         if games[game]['state'] == 'pre':
#             return games[game]
#         if games[game]['state'] == 'post':
#             return games[game]
#     return None

# def is_playoffs():
#     try:
#         res = requests.get(URL)
#         res = res.json()
#         return res['season']['type'] == 3
#     except requests.exceptions.RequestException:
#         print("Error encountered getting game info, can't hit ESPN api")
#     except Exception as e:
#         print("something bad?", e)