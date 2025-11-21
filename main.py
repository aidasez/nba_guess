import requests
import time
import json
from datetime import datetime, timedelta
import os
import subprocess
spreads = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=3e5956fb272da60f9991d0c26996e9fb&regions=uk&markets=spreads"
moneyline = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=3e5956fb272da60f9991d0c26996e9fb&regions=uk&markets=h2h"
response_spreads = requests.get(spreads)
response_spreads = response_spreads.json()
response_moneyline = requests.get(moneyline)
response_moneyline = response_moneyline.json()
date = datetime.now().strftime("%Y-%m-%d")
month = datetime.now().strftime("%m")
yesterday = datetime.now() - timedelta(days=1)
yesterday = yesterday.strftime("%Y-%m-%d")
def generate_index_html(base_dir=None):
    """
    Generates an index.html in the base_dir that links to all *_games.html files
    inside subfolders named with dates (ISO format).
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Find all folders in base_dir
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    folders.sort(reverse=True)  # latest first

    # Start building the index HTML
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NBA Games Index</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 50px;
            }
            h1 {
                margin-bottom: 30px;
            }
            .button-container {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                justify-content: center;
            }
            .button-container a {
                text-decoration: none;
                background-color: #4CAF50;
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }
            .button-container a:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>NBA Games</h1>
        <div class="button-container">
    """

    total_files = 0
    # Loop through folders
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        # Find *_games.html files
        html_files = [f for f in os.listdir(folder_path) if f.endswith("_games.html")]
        for html_file in html_files:
            relative_path = os.path.join(folder, html_file)
            # Use folder name (date) as button text
            button_text = folder
            index_html += f'            <a href="{relative_path}" target="_blank">{button_text}</a>\n'
            total_files += 1

    # Close HTML
    index_html += """
        </div>
    </body>
    </html>
    """

    # Write index.html to base_dir
    with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"index.html generated in {base_dir} with {total_files} game files from {len(folders)} folders.")
def upload_to_github(repo_dir, commit_message="Update NBA HTML files"):
    """
    Commits and pushes all changes in the specified repo_dir to GitHub.

    Parameters:
    - repo_dir: str, path to your git repository
    - commit_message: str, message for the commit
    """
    # Change working directory to the repo
    cwd = os.getcwd()
    os.chdir(repo_dir)

    try:
        # Stage all changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit changes
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push to the remote repository (default 'origin' and current branch)
        subprocess.run(["git", "push"], check=True)

        print("Successfully pushed changes to GitHub!")
    except subprocess.CalledProcessError as e:
        print("Error during git operations:", e)
    finally:
        # Return to original directory
        os.chdir(cwd)
def save_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(date, exist_ok=True)
    os.chdir(date)
    with open(f"{date}_moneyline.json","w") as json_file:
        json.dump(response_moneyline,json_file,indent=4)
    with open(f"{date}_spreads.json","w") as json_file:
        json.dump(response_spreads,json_file,indent=4)
    create_html()
    os.chdir(script_dir)
def create_html():
    html_parent = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{date}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 10px;
            }}
            .game-box {{
                background-color: #fff;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                width: fit-content;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
                display: inline-block;         
                max-width: 90%;  
                word-wrap: break-word;
            }}
            .game-box h2 {{
                margin: 0 0 10px 0;
                font-size: 18px;
                text-align: center;      
                width: 100%;  
            }}
            .game-box p {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
    """
    for i in range(0,len(games)):
        if games[i][2] > 0 :
            plusminus = "+"
        else:
            plusminus = ""
        
        success_overall_winner = "?"
        success_spread_winner = "?"
        html_parent += f"""
        <div class="game-box">
        <h2>{games[i][0]["home_team"]}
        <p><em>  {games[i][0]["odds"]}</p></em> 
        {games[i][1]["away_team"]}
        <p><em>  {games[i][1]["odds"]}</p></em></h2>
        <p><strong>Spread: {plusminus}{games[i][2]}</strong></p>
        <p><strong>Odds of Spread:</strong> {games[i][3]}</p>
        <p><strong>Success: </strong> Overall: {success_overall_winner}, Spread: {success_spread_winner}  </p>
        </div>
        """
    html_parent += """
    </body>
    </html>
    """
    with open(f"{date}_games.html", "w") as f:
        f.write(html_parent)
        
def create_updated_html():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    date = yesterday
    os.chdir(date)
    html_parent = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{date}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 10px;
            }}
            .game-box {{
                background-color: #fff;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                width: fit-content;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
                display: inline-block;         
                max-width: 90%;  
                word-wrap: break-word;
            }}
            .game-box h2 {{
                margin: 0 0 10px 0;
                font-size: 18px;
                text-align: center;      
                width: 100%;  
            }}
            .game-box p {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
    """
    success_list = find_outcome()
    print(os.getcwd())
    os.chdir(date)
    with open(f"{date}_games.json", "r", encoding="utf-8") as f:
            games = json.load(f)
    
    team_order = []
    for match in games:
        team_order.append(match[0]["home_team"])   # add home team
        team_order.append(match[1]["away_team"])   # add away team

# now sort success_list by the index of the team name in team_order
    success_list = sorted(success_list, key=lambda x: team_order.index(x[1]))
            
            
            
    for i in range(0,len(games)):
        # if games[i][2] > 0 :
        #     plusminus = "+"
        # else:
        #     plusminus = ""
        print("success list",success_list)
        success_overall_winner_name = success_list[i][0][0]
        success_overall_loser_name = success_list[i][0][2]
        score1 = success_list[i][0][1]
        score2 = success_list[i][0][3]
        success_spread_winner = success_list[i][1]
        print("success_list",success_list)
        html_parent += f"""
        <div class="game-box">
        <h2>{games[i][0]["home_team"]}
        <p><em>  {games[i][0]["odds"]}</p></em> 
        {games[i][1]["away_team"]}
        <p><em>  {games[i][1]["odds"]}</p></em></h2>
        <p><strong>Score: {success_overall_winner_name} {score1} - {score2} {success_overall_loser_name}</strong></p>
        <p><strong>Spread: {games[i][2]}</strong></p>
        <p><strong>Odds of Spread:</strong> {games[i][3]}</p>
        <p><strong>Success: </strong> Overall: {success_overall_winner_name}, Spread: {success_spread_winner}  </p>
        </div>
        """
    html_parent += """
    </body>
    </html>
    """
    with open(f"{date}_updated_games.html", "w") as f:
        f.write(html_parent)
    os.chdir(script_dir)
    table_update(success_list,games)

def table_update(success_list,games):
    with open("table.html", "r") as f:
        table = f.read()
    table = table[:-2]
    with open("table.html", "w") as f:
        f.write(table) 
    html_parent = table
    
    for i in range (0,len(games)):
        home_team = games[i][0]["home_team"]
        away_team = games[i][1]["away_team"]
        home_team_moneyline = games[i][0]["odds"]
        away_team_moneyline = games[i][1]["odds"]
        spread = games[i][2]
        spread_odds = games[i][3]
        success_overall_winner = success_list[i][0][0]
        u1 = ""
        u2 = ""
        u3 = ""
        u4 = ""
        if home_team == success_overall_winner:
            u1 = "<u>"
            u2 = "</u>"
            score1 = success_list[i][0][1]
            score2 = success_list[i][0][3]
            
        else:
            u3 = "<u>"
            u4 = "</u>"
            score2 = success_list[i][0][1]
            score1 = success_list[i][0][3]
        
        print("success_list",success_list[i])
        success_spread_winner = success_list[i][1]
        html_parent += f"""
        <tr>
            <td>{u1}{home_team}{u2} vs {u3}{away_team}{u4}</td>
            <td>{u1}{score1}{u2} - {u3}{score2}{u4}</td>
            <td>{spread}</td>
            <td>{spread_odds}</td>
            <td>{u1}{home_team_moneyline}{u2} vs {u3}{away_team_moneyline}{u4}</td>
            <td>{success_overall_winner}</td>
            <td>{success_spread_winner}</td>
        </tr>"""
    html_parent += """
    </table>
    </html>
    """
    with open("table.html", "w") as f:
        f.write(html_parent)
            
def find_outcome():
    # Load yesterday's completed scores
    results_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?daysFrom=1&apiKey=3e5956fb272da60f9991d0c26996e9fb"
    response_result = requests.get(results_url).json()
    print("response result",response_result)
    success_list = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    date = yesterday
    
    for result in range(0,len(response_result)):
        print(response_result)
        # Skip games without scores or incomplete
        if not response_result[result]["completed"] == True:
            continue
        result = response_result[result]
        home_team_name = result['home_team']
        away_team_name = result['away_team']

        # Find scores safely
        if home_team_name == result["scores"][0]:
            count = 0
            counta= 1
        else:
            count = 1
            counta= 0
        home_score = int(result["scores"][counta]["score"])
        away_score = int(result["scores"][count]["score"])
        
        with open(f"{date}_games.json", "r", encoding="utf-8") as f:
            games = json.load(f)
        # Find corresponding game in your 'games' list
        for i in range (0,len(games)):
            if str(home_team_name) == str(games[i][0]["home_team"]):
                print("found", games[i][0]["home_team"],home_team_name)
                game_match = games[i]
        print("game",game_match)

        home_odds = int(game_match[0]['odds'])
        away_odds = int(game_match[1]['odds'])
        spread = game_match[3]

        # Determine winners
        overall_winner = "home" if home_score > away_score else "away"
        favourite = "home" if home_odds < away_odds else "away"  # lowest odds = favourite

        if favourite == "home":
            spread_winner = "home" if (home_score + spread) > away_score else "away"
        else:
            spread_winner = "home" if home_score > (away_score + spread) else "away"
        if spread_winner == "home":
            spread_winner = game_match[0]["home_team"]
        else:
            spread_winner = game_match[1]["away_team"]
        if overall_winner == "home":
            # overall_winner = f"{home_score} {game_match[0]["home_team"]} - {away_score} {game_match[1]["away_team"]} "
            overall_winner = [game_match[0]["home_team"],  home_score, 
                             game_match[1]["away_team"],  away_score]
        else:
            overall_winner = [game_match[1]["away_team"],  away_score, 
                             game_match[0]["home_team"],  home_score]
        success_list.append([overall_winner, spread_winner])
    os.chdir(script_dir)
    return success_list


            
            
        
        
    
    
def get_response_api():
    games = []

    for i in range(len(response_moneyline)):
        # --- SAFETY: ensure matching index exists in spreads ---
        if i >= len(response_spreads):
            continue
        print(response_moneyline)
        money = response_moneyline[i]
        spreads = response_spreads[i]

        # --- SAFETY: validate bookmakers / markets / outcomes exist ---
        if not money.get("bookmakers"):
            continue
        if not spreads.get("bookmakers"):
            continue

        money_bm = money["bookmakers"][0]
        spread_bm = spreads["bookmakers"][0]

        if not money_bm.get("markets"):
            continue
        if not spread_bm.get("markets"):
            continue

        money_market = money_bm["markets"][0]
        spread_market = spread_bm["markets"][0]

        if not money_market.get("outcomes"):
            continue
        if not spread_market.get("outcomes"):
            continue

        money_outcomes = money_market["outcomes"]
        spread_outcomes = spread_market["outcomes"]

        if len(money_outcomes) < 2:
            continue
        if len(spread_outcomes) < 2:
            continue

        # --- TEAMS ---
        home_team = spreads["home_team"]
        away_team = spreads["away_team"]

        # identify which outcome corresponds to home team
        # (API always places outcomes in order: away, home)
        away_name = money_outcomes[0]["name"]
        home_name = money_outcomes[1]["name"]

        # find correct odds
        if home_name == home_team:
            home_odds_moneyline = money_outcomes[1]["price"]
            away_odds_moneyline = money_outcomes[0]["price"]
            favourite_index = 1 if home_odds_moneyline > away_odds_moneyline else 0
        else:
            # API flipped ordering… we match by name
            home_idx = 0 if money_outcomes[0]["name"] == home_team else 1
            away_idx = 1 - home_idx
            home_odds_moneyline = money_outcomes[home_idx]["price"]
            away_odds_moneyline = money_outcomes[away_idx]["price"]

        # --- SPREAD ---
        # favourite_index is safe now (0 or 1)
        if spread_outcomes[0]["point"] >0:
            spread = spread_outcomes[1]["point"]
            favourite_index = 1
        else:
            favourite_index = 0
            spread = spread_outcomes[0]["point"]
        
        odds_spread = spread_outcomes[favourite_index]["price"]

        home = {"home_team": home_team, "odds": home_odds_moneyline}
        away = {"away_team": away_team, "odds": away_odds_moneyline}

        games.append([home, away, spread, odds_spread])
    os.makedirs(date, exist_ok=True)
    os.chdir(date)
    with open(f"{date}_games.json", "w", encoding="utf-8") as f:
        json.dump(games, f, indent=4)
    os.chdir(script_dir)
    return games
script_dir = os.path.dirname(os.path.abspath(__file__))
games = []
games = get_response_api()
save_file()
# update_html(f"2025-{month}-{yesterday}")
generate_index_html()
repo_dir = "C:\handicap_guess"
create_updated_html()
upload_to_github(repo_dir)